"""
Input loader - Single authoritative source of all workbook inputs.
Each field carries its provenance (unit, source_sheet, source_cell, confidence)
so calculators never need to hardcode case-specific values.
"""
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, field, asdict
from pydantic import BaseModel, Field, field_validator, model_validator
from src.domain.fluids import Fluid
import re

# A1-style cell reference validation pattern
# Matches: A1, $A$1, AA1, XFD1048576, A1:B5, $A$1:$B$5
# Does NOT match: A0, AA0, 1A, columns beyond XFD, empty string
_A1_PATTERN = re.compile(
    r"^(\$?[A-Z]{1,3})(\$?\d{1,7})"
    r"(?::(\$?[A-Z]{1,3})(\$?\d{1,7}))?$"
)

# Maximum Excel column index: XFD = 16384
_MAX_COLUMN = 16384


def _column_index(col_str: str) -> int:
    """Convert Excel column letters to 1-based index (A=1, Z=26, AA=27, ..., XFD=16384)."""
    # Strip leading $
    col_str = col_str.lstrip("$")
    result = 0
    for ch in col_str:
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result


def _is_valid_a1_reference(location: str) -> bool:
    """Validate an A1-style cell or range reference."""
    if not location or not location.strip():
        return False
    m = _A1_PATTERN.match(location.strip())
    if not m:
        return False
    # Check all column parts are within XFD limit
    for i in [1, 3]:
        col_part = m.group(i)
        if col_part and _column_index(col_part) > _MAX_COLUMN:
            return False
    # Check all row parts are non-zero
    for i in [2, 4]:
        row_part = m.group(i)
        if row_part and int(row_part.lstrip("$")) == 0:
            return False
    # Single cell or range must have start row > 0
    start_row = int(m.group(2).lstrip("$"))
    if start_row == 0:
        return False
    return True


@dataclass
class FieldProvenance:
    """Provenance metadata for a single input field."""
    value: float
    unit: str
    source_sheet: str = ""
    source_cell: str = ""
    confidence: str = "UNVERIFIED"


class SourceProvenance(BaseModel):
    """Provenance metadata tracking origin of a data value."""
    source_workbook: str
    source_sheet: Optional[str] = None
    source_location: str
    source_type: Literal[
        "WORKBOOK_CELL",
        "WORKBOOK_TEXT",
        "EMBEDDED_CURVE_IMAGE",
    ]
    confidence: Literal["HIGH", "MEDIUM", "LOW", "UNVERIFIED"]
    notes: str = ""

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        allowed = {"WORKBOOK_CELL", "WORKBOOK_TEXT", "EMBEDDED_CURVE_IMAGE"}
        if v not in allowed:
            raise ValueError(f"source_type must be one of {allowed}, got '{v}'")
        return v

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v):
        allowed = {"HIGH", "MEDIUM", "LOW", "UNVERIFIED"}
        if v not in allowed:
            raise ValueError(f"confidence must be one of {allowed}, got '{v}'")
        return v

    @field_validator("source_workbook", "source_location")
    @classmethod
    def validate_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field must be a non-empty string")
        return v

    @model_validator(mode="after")
    def validate_cell_has_sheet(self):
        if self.source_type == "WORKBOOK_CELL" and not self.source_sheet:
            raise ValueError("WORKBOOK_CELL provenance must specify source_sheet")
        return self

    @model_validator(mode="after")
    def validate_a1_reference(self):
        if self.source_type in ("WORKBOOK_CELL", "WORKBOOK_TEXT") and self.source_location:
            if not _is_valid_a1_reference(self.source_location):
                raise ValueError(
                    f"source_location must be a valid A1-style cell reference "
                    f"for source_type={self.source_type}, got '{self.source_location}'"
                )
        return self


class NPSHrReference(BaseModel):
    """NPSH Required value with full provenance and reference conditions."""
    value: float
    unit: Literal["ft", "m"]
    value_provenance: SourceProvenance

    flow_gpm: Optional[float] = None
    flow_provenance: Optional[SourceProvenance] = None

    duty_tdh_ft: Optional[float] = None
    duty_tdh_provenance: Optional[SourceProvenance] = None

    speed_rpm: Optional[float] = None
    speed_provenance: Optional[SourceProvenance] = None

    impeller_diameter_mm: Optional[float] = None
    impeller_provenance: Optional[SourceProvenance] = None

    curve_reference: Optional[str] = None
    curve_provenance: Optional[SourceProvenance] = None

    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        import math
        if not math.isfinite(v) or v <= 0:
            raise ValueError(f"npshr value must be finite and > 0, got {v}")
        return v

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v):
        allowed = {"ft", "m"}
        if v not in allowed:
            raise ValueError(f"unit must be 'ft' or 'm', got '{v}'")
        return v

    @field_validator("flow_gpm")
    @classmethod
    def validate_flow_gpm(cls, v):
        import math
        if v is not None and (not math.isfinite(v) or v <= 0):
            raise ValueError(f"flow_gpm must be finite and > 0, got {v}")
        return v

    @field_validator("duty_tdh_ft")
    @classmethod
    def validate_duty_tdh_ft(cls, v):
        import math
        if v is not None and (not math.isfinite(v) or v <= 0):
            raise ValueError(f"duty_tdh_ft must be finite and > 0, got {v}")
        return v

    @field_validator("speed_rpm")
    @classmethod
    def validate_speed_rpm(cls, v):
        import math
        if v is not None and (not math.isfinite(v) or v <= 0):
            raise ValueError(f"speed_rpm must be finite and > 0, got {v}")
        return v

    @field_validator("impeller_diameter_mm")
    @classmethod
    def validate_impeller_diameter_mm(cls, v):
        import math
        if v is not None and (not math.isfinite(v) or v <= 0):
            raise ValueError(f"impeller_diameter_mm must be finite and > 0, got {v}")
        return v

    @model_validator(mode="after")
    def validate_provenance_pairs(self):
        """Each populated reference datum must have provenance; vice versa."""
        pairs = [
            ("flow_gpm", "flow_provenance"),
            ("duty_tdh_ft", "duty_tdh_provenance"),
            ("speed_rpm", "speed_provenance"),
            ("impeller_diameter_mm", "impeller_provenance"),
            ("curve_reference", "curve_provenance"),
        ]
        for value_name, prov_name in pairs:
            val = getattr(self, value_name)
            prov = getattr(self, prov_name)
            if val is not None and prov is None:
                raise ValueError(f"{value_name} is populated but {prov_name} is missing")
            if val is None and prov is not None:
                raise ValueError(f"{prov_name} is populated but {value_name} is missing")
        return self


DEFAULT_CURRENT_CASE_PATH = None


class WorkbookInputs(BaseModel):
    """Complete workbook inputs - single source of truth for all calculations.
    
    Every case-specific value originates here. Calculators must NOT hardcode
    values like 770.5, 62.0, 0.0272, etc.
    
    Dataset provenance:
    - dataset_path: path to the JSON file the data was loaded from
    - dataset_hash: SHA-256 prefix of the JSON payload
    - dataset_version: version string from the dataset
    """

    # — Process & Fluid —
    flow_gpm: float = Field(gt=0, description="Flow rate in GPM")
    density_lbm_ft3: float = Field(gt=0, description="Mass density in lbm/ft3")
    specific_gravity: float = Field(gt=0, le=2, description="Specific gravity (water=1)")
    dynamic_viscosity_cp: float = Field(gt=0, description="Dynamic viscosity in centipoise")
    temperature_f: float = Field(ge=32, le=212, description="Operating temperature in F")
    vapor_pressure_value: float = Field(ge=0, description="Vapor pressure (absolute)")
    vapor_pressure_unit: str = Field(default="psia", description="Unit: psia, ft_H2O, ft_fluid, Pa")
    vapor_pressure_source_cell: str = Field(default="AA13", description="Workbook cell for vapor pressure")

    # — Suction pipe —
    suction_target_velocity_fps: float = Field(default=3.12, description="Target velocity in ft/s (V6)")
    suction_required_diameter_in: float = Field(gt=0, description="Required diameter from velocity sizing in inches (V8 = V7*sqrt(V5/V6))")
    suction_nominal_diameter_in: float = Field(gt=0, description="Nominal diameter in inches (V12)")
    suction_absolute_roughness_ft: float = Field(ge=0, description="Absolute roughness in ft")
    suction_length_ft: float = Field(ge=0, description="Total pipe length in ft")
    suction_static_head_ft: float = Field(description="Static suction lift/head in ft (C9)")
    suction_fitting_losses_ft: float = Field(ge=0, description="Fitting (minor) losses in ft (C11)")
    # Selected pipe spec (from schedule lookup, not velocity sizing)
    suction_selected_inside_diameter_in: Optional[float] = Field(default=None, description="Selected inside diameter from pipe schedule in inches")
    suction_pipe_schedule: str = Field(default="MISSING_SELECTED_PIPE_SCHEDULE", description="Pipe schedule (e.g. STD, XS, SCH 40)")
    suction_wall_thickness_in: Optional[float] = Field(default=None, description="Wall thickness in inches")
    suction_outside_diameter_in: Optional[float] = Field(default=None, description="Outside diameter in inches")
    suction_pipe_material: str = Field(default="Steel", description="Pipe material")

    # — Discharge pipe —
    discharge_target_velocity_fps: float = Field(default=8.6, description="Target velocity in ft/s (G6)")
    discharge_required_diameter_in: float = Field(gt=0, description="Required diameter from velocity sizing in inches (G8 = G7*sqrt(G5/G6))")
    discharge_nominal_diameter_in: float = Field(gt=0, description="Nominal diameter in inches (G12)")
    discharge_absolute_roughness_ft: float = Field(ge=0, description="Absolute roughness in ft")
    discharge_length_ft: float = Field(ge=0, description="Total pipe length in ft")
    discharge_static_head_ft: float = Field(description="Discharge static head in ft (C20)")
    discharge_fitting_losses_ft: float = Field(ge=0, description="Fitting (minor) losses in ft (C24)")
    # Selected pipe spec (from schedule lookup, not velocity sizing)
    discharge_selected_inside_diameter_in: Optional[float] = Field(default=None, description="Selected inside diameter from pipe schedule in inches")
    discharge_pipe_schedule: str = Field(default="MISSING_SELECTED_PIPE_SCHEDULE", description="Pipe schedule (e.g. STD, XS, SCH 40)")
    discharge_wall_thickness_in: Optional[float] = Field(default=None, description="Wall thickness in inches")
    discharge_outside_diameter_in: Optional[float] = Field(default=None, description="Outside diameter in inches")
    discharge_pipe_material: str = Field(default="Steel", description="Pipe material")

    # — Pressures —
    atmospheric_pressure_psia: float = Field(gt=0, description="Atmospheric pressure in psia")
    vessel_pressure: float = Field(default=0, description="Vessel/gauge pressure")
    vessel_pressure_type: str = Field(default="gauge", description="gauge | absolute | vacuum")

    # — Pump —
    pump_efficiency: float = Field(gt=0, le=1, description="Pump hydraulic efficiency (0-1)")
    motor_efficiency: Optional[float] = Field(default=None, ge=0, le=1, description="Motor efficiency (0-1)")
    pump_rpm: float = Field(gt=0, description="Pump rotational speed in RPM")
    legacy_torque_rpm: float = Field(default=1700, description="RPM used in legacy torque formula")
    service_factor: float = Field(default=1.0, ge=1, description="Service factor")
    number_of_stages: int = Field(default=1, ge=1, description="Number of stages")
    number_of_suction_eyes: int = Field(default=1, ge=1, description="Number of suction eyes")
    pump_impeller_diameter_mm: Optional[float] = Field(default=None, ge=0, description="Pump impeller diameter in mm")
    pump_impeller_provenance: Optional[SourceProvenance] = Field(default=None, description="Provenance of pump impeller diameter")

    # — NPSH Required —
    npshr: Optional[NPSHrReference] = Field(default=None, description="NPSH Required reference data")

    # — Legacy hardcoded friction factors (for reproduction only) —
    legacy_f_discharge: float = Field(default=0.0272, description="Hardcoded discharge f from G17")
    legacy_f_suction_method: str = Field(default="64/Re", description="Method for legacy suction f")

    # — Dataset provenance —
    source_workbook: Optional[str] = Field(default=None, description="Original workbook file name (e.g. POTENCIA Y TDH.xlsm)")
    dataset_path: Optional[str] = Field(default=None, description="Path to the JSON dataset file")
    dataset_hash: Optional[str] = Field(default=None, description="SHA-256 prefix of the dataset payload")
    dataset_version: Optional[str] = Field(default=None, description="Version string from the dataset")

    model_config = {"arbitrary_types_allowed": True, "validate_assignment": True}

    @field_validator("vapor_pressure_unit")
    @classmethod
    def validate_vapor_pressure_unit(cls, v):
        allowed = {"psia", "ft_H2O", "ft_fluid", "Pa"}
        if v not in allowed:
            raise ValueError(f"vapor_pressure_unit must be one of {allowed}, got '{v}'")
        return v

    @field_validator("atmospheric_pressure_psia")
    @classmethod
    def validate_atmospheric_pressure(cls, v):
        if v <= 0:
            raise ValueError(f"atmospheric_pressure_psia must be > 0, got {v}")
        return v

    @field_validator("specific_gravity")
    @classmethod
    def validate_specific_gravity(cls, v):
        if v <= 0:
            raise ValueError(f"specific_gravity must be > 0, got {v}")
        return v

    @field_validator("vessel_pressure")
    @classmethod
    def validate_vessel_pressure(cls, v, info):
        ptype = info.data.get("vessel_pressure_type")
        patm = info.data.get("atmospheric_pressure_psia")
        if ptype == "vacuum" and patm is not None:
            if v >= patm:
                raise ValueError(f"Vacuum ({v}) must be less than atmospheric pressure ({patm})")
        return v

    @model_validator(mode="after")
    def validate_impeller_symmetry(self):
        has_val = self.pump_impeller_diameter_mm is not None
        has_prov = self.pump_impeller_provenance is not None
        if has_val != has_prov:
            missing = "pump_impeller_diameter_mm" if not has_val else "pump_impeller_provenance"
            raise ValueError(
                f"pump_impeller_diameter_mm and pump_impeller_provenance must both be "
                f"present or both absent; missing {missing}"
            )
        return self

    def to_provenance_rows(self) -> list:
        """Return list of dicts for CSV export with separated source_type and confidence."""
        wb = self.source_workbook or ""

        def _r(key, desc, unit, sheet="", cell="", source_type="WORKBOOK", confidence="UNVERIFIED", notes="", source_location=""):
            return dict(
                variable_id=key,
                description=desc,
                value=str(getattr(self, key)),
                unit=unit,
                source_workbook=wb,
                source_sheet=sheet,
                source_cell=cell or None,
                source_location=source_location or cell or None,
                source_formula="",
                data_type="INPUT",
                source_type=source_type,
                confidence=confidence,
                notes=notes,
            )

        def _prov_row(variable_id, description, value, unit, prov):
            """Build a provenance row from a SourceProvenance object."""
            source_cell = prov.source_location if prov.source_type == "WORKBOOK_CELL" else None
            source_location = prov.source_location if prov.source_type != "WORKBOOK_CELL" else prov.source_location
            return dict(
                variable_id=variable_id,
                description=description,
                value=str(value),
                unit=unit,
                source_workbook=prov.source_workbook or wb,
                source_sheet=prov.source_sheet or "",
                source_cell=source_cell,
                source_location=source_location,
                source_formula="",
                data_type="INPUT",
                source_type=prov.source_type,
                confidence=prov.confidence,
                notes=prov.notes,
            )

        rows = [
            _r("flow_gpm", "Flow Rate", "GPM", "CAIDA PRESION DE TUBERIA", "G5", "WORKBOOK_CELL", "HIGH"),
            _r("density_lbm_ft3", "Fluid Density", "lbm/ft3", "CAIDA PRESION DE TUBERIA", "G9", "WORKBOOK_CELL", "HIGH"),
            _r("specific_gravity", "Specific Gravity", "-", "CALCULO DE BOMBA", "E11", "WORKBOOK_CELL", "HIGH"),
            _r("dynamic_viscosity_cp", "Dynamic Viscosity", "cP", "CAIDA PRESION DE TUBERIA", "G10", "WORKBOOK_CELL", "HIGH"),
            _r("temperature_f", "Operating Temperature", "degF", "VELOCIDADES RECOMENDADAS", "AA13", "WORKBOOK_CELL", "UNVERIFIED",
               notes="Same cell as vapor pressure; verify independently"),
            _r("vapor_pressure_value", "Vapor Pressure (abs)", self.vapor_pressure_unit, "VELOCIDADES RECOMENDADAS", self.vapor_pressure_source_cell, "WORKBOOK_CELL", "UNVERIFIED",
               notes="Confirm unit is psia, not ft H2O"),
            _r("vapor_pressure_source_cell", "Vapor Pressure Source Cell", "-", "VELOCIDADES RECOMENDADAS", self.vapor_pressure_source_cell, "WORKBOOK_CELL", "MEDIUM"),
            _r("suction_target_velocity_fps", "Suction Target Velocity", "ft/s", "CAIDA PRESION DE TUBERIA", "V6", "WORKBOOK_CELL", "MEDIUM"),
            _r("suction_required_diameter_in", "Suction Required Diameter (velocity sizing)", "in", "CAIDA PRESION DE TUBERIA", "V8", "WORKBOOK_CELL", "HIGH",
               notes="V8 = V7*sqrt(V5/V6) — velocity-based sizing, NOT selected pipe ID"),
            _r("suction_nominal_diameter_in", "Suction Nominal Diameter", "in", "CAIDA PRESION DE TUBERIA", "V12", "WORKBOOK_CELL", "HIGH"),
            _r("suction_selected_inside_diameter_in", "Suction Selected ID (pipe schedule)", "in", "OUTPIPES/ESPECIFICACION", "-", "WORKBOOK", "UNVERIFIED",
               notes="ID = OD - 2*wall; needs schedule confirmation", source_location="Table lookup: OD - 2*wall"),
            _r("suction_pipe_schedule", "Suction Pipe Schedule", "-", "OUTPIPES/ESPECIFICACION", "-", "WORKBOOK", "UNVERIFIED",
               notes="Search VELOCIDADES RECOMENDADAS OUTPIPES table", source_location="Table lookup"),
            _r("suction_absolute_roughness_ft", "Suction Roughness", "ft", "CAIDA PRESION DE TUBERIA", "V14", "WORKBOOK_CELL", "HIGH"),
            _r("suction_length_ft", "Suction Pipe Length", "ft", "CALCULO DE BOMBA", "C12", "WORKBOOK_CELL", "UNVERIFIED"),
            _r("suction_static_head_ft", "Suction Static Head", "ft", "CALCULO DE BOMBA", "C9", "WORKBOOK_CELL", "UNVERIFIED"),
            _r("suction_fitting_losses_ft", "Suction Fitting Losses", "ft", "CALCULO DE BOMBA", "C11", "WORKBOOK_CELL", "HIGH"),
            _r("suction_pipe_material", "Suction Pipe Material", "-", "OUTPIPES/ESPECIFICACION", "-", "WORKBOOK", "UNVERIFIED", source_location="Table lookup"),
            _r("discharge_target_velocity_fps", "Discharge Target Velocity", "ft/s", "CAIDA PRESION DE TUBERIA", "G6", "WORKBOOK_CELL", "MEDIUM"),
            _r("discharge_required_diameter_in", "Discharge Required Diameter (velocity sizing)", "in", "CAIDA PRESION DE TUBERIA", "G8", "WORKBOOK_CELL", "HIGH",
               notes="G8 = G7*sqrt(G5/G6) — velocity-based sizing, NOT selected pipe ID"),
            _r("discharge_nominal_diameter_in", "Discharge Nominal Diameter", "in", "CAIDA PRESION DE TUBERIA", "G12", "WORKBOOK_CELL", "HIGH"),
            _r("discharge_selected_inside_diameter_in", "Discharge Selected ID (pipe schedule)", "in", "OUTPIPES/ESPECIFICACION", "-", "WORKBOOK", "UNVERIFIED",
               notes="ID = OD - 2*wall; needs schedule confirmation", source_location="Table lookup: OD - 2*wall"),
            _r("discharge_pipe_schedule", "Discharge Pipe Schedule", "-", "OUTPIPES/ESPECIFICACION", "-", "WORKBOOK", "UNVERIFIED",
               notes="Search VELOCIDADES RECOMENDADAS OUTPIPES table", source_location="Table lookup"),
            _r("discharge_absolute_roughness_ft", "Discharge Roughness", "ft", "CAIDA PRESION DE TUBERIA", "G14", "WORKBOOK_CELL", "HIGH"),
            _r("discharge_length_ft", "Discharge Pipe Length", "ft", "CALCULO DE BOMBA", "C25", "WORKBOOK_CELL", "HIGH"),
            _r("discharge_static_head_ft", "Discharge Static Head", "ft", "CALCULO DE BOMBA", "C20", "WORKBOOK_CELL", "UNVERIFIED"),
            _r("discharge_fitting_losses_ft", "Discharge Fitting Losses", "ft", "CALCULO DE BOMBA", "C24", "WORKBOOK_CELL", "HIGH"),
            _r("discharge_pipe_material", "Discharge Pipe Material", "-", "OUTPIPES/ESPECIFICACION", "-", "WORKBOOK", "UNVERIFIED", source_location="Table lookup"),
            _r("atmospheric_pressure_psia", "Atmospheric Pressure", "psia", "CALCULO DE BOMBA", "C8", "WORKBOOK_CELL", "MEDIUM"),
            _r("vessel_pressure", "Vessel Pressure", "psig", "CALCULO DE BOMBA", "E8", "WORKBOOK_CELL", "HIGH"),
            _r("pump_efficiency", "Pump Efficiency", "-", "CALCULO DE BOMBA", "C22", "WORKBOOK_CELL", "MEDIUM"),
            _r("pump_rpm", "Pump RPM", "rpm", "CALCULO DE BOMBA", "C29", "WORKBOOK_CELL", "HIGH"),
            _r("legacy_torque_rpm", "Legacy Torque RPM", "rpm", "CALCULO DE BOMBA", "E23", "WORKBOOK_CELL", "LOW",
               notes="Hardcoded 1700 rpm in workbook formula; verify actual motor nameplate"),
            _r("service_factor", "Service Factor", "-", "CALCULO DE BOMBA", "C6", "WORKBOOK_CELL", "MEDIUM"),
            _r("number_of_stages", "Number of Stages", "-", "-", "-", "ASSUMPTION", "MEDIUM",
               notes="Default=1; not traced to workbook cell", source_location="Assumption (default=1)"),
            _r("number_of_suction_eyes", "Suction Eyes", "-", "-", "-", "ASSUMPTION", "MEDIUM",
               notes="Default=1; not traced to workbook cell", source_location="Assumption (default=1)"),
        ]

        # NPSHr provenance rows (only if npshr is populated)
        if self.npshr is not None:
            rows.append(_prov_row("npshr.value", "NPSH Required", self.npshr.value, self.npshr.unit, self.npshr.value_provenance))
            if self.npshr.flow_gpm is not None and self.npshr.flow_provenance is not None:
                rows.append(_prov_row("npshr.flow_gpm", "NPSHr Reference Flow", self.npshr.flow_gpm, "GPM", self.npshr.flow_provenance))
            if self.npshr.duty_tdh_ft is not None and self.npshr.duty_tdh_provenance is not None:
                rows.append(_prov_row("npshr.duty_tdh_ft", "NPSHr Reference TDH", self.npshr.duty_tdh_ft, "ft", self.npshr.duty_tdh_provenance))
            if self.npshr.speed_rpm is not None and self.npshr.speed_provenance is not None:
                rows.append(_prov_row("npshr.speed_rpm", "NPSHr Reference Speed", self.npshr.speed_rpm, "rpm", self.npshr.speed_provenance))
            if self.npshr.impeller_diameter_mm is not None and self.npshr.impeller_provenance is not None:
                rows.append(_prov_row("npshr.impeller_diameter_mm", "NPSHr Reference Impeller Diameter", self.npshr.impeller_diameter_mm, "mm", self.npshr.impeller_provenance))
            if self.npshr.curve_reference is not None and self.npshr.curve_provenance is not None:
                rows.append(_prov_row("npshr.curve_reference", "NPSHr Curve Reference", self.npshr.curve_reference, "-", self.npshr.curve_provenance))

        if self.pump_impeller_diameter_mm is not None and self.pump_impeller_provenance is not None:
            rows.append(_prov_row("pump_impeller_diameter_mm", "Pump Impeller Diameter", self.pump_impeller_diameter_mm, "mm", self.pump_impeller_provenance))

        return rows


import os as _os
import json as _json
import hashlib as _hashlib

DEFAULT_CURRENT_CASE_PATH = _os.path.join(
    _os.path.dirname(__file__), '..', '..', 'data', 'cases', 'current_workbook_case.json'
)


def load_workbook_inputs_from_json(path: str) -> WorkbookInputs:
    """Load workbook inputs from a JSON dataset file."""
    with open(path, 'r', encoding='utf-8') as f:
        raw = _json.load(f)

    # Compute hash of the payload (without metadata fields)
        meta_keys = {'dataset_version', 'dataset_hash', 'description'}
        payload = {k: v for k, v in raw.items() if k not in meta_keys}
    payload_bytes = _json.dumps(payload, indent=2, sort_keys=True).encode()
    computed_hash = _hashlib.sha256(payload_bytes).hexdigest()[:12]

    # Build kwargs for WorkbookInputs (only known fields)
    field_names = set(WorkbookInputs.model_fields.keys())
    kwargs = {k: v for k, v in raw.items() if k in field_names}

    # Attach provenance
    kwargs['dataset_path'] = _os.path.abspath(path)
    kwargs['dataset_hash'] = raw.get('dataset_hash', computed_hash)
    kwargs['dataset_version'] = raw.get('dataset_version', 'unknown')

    return WorkbookInputs(**kwargs)


def create_workbook_inputs() -> WorkbookInputs:
    """Legacy alias — loads from the default JSON dataset."""
    return load_workbook_inputs_from_json(DEFAULT_CURRENT_CASE_PATH)


def create_workbook_inputs_legacy() -> WorkbookInputs:
    """Synonym for backwards compatibility."""
    return create_workbook_inputs()


if __name__ == '__main__':
    inputs = create_workbook_inputs()
    print(f"WorkbookInputs: flow={inputs.flow_gpm} GPM, SG={inputs.specific_gravity}")
    print(f"  Dataset: path={inputs.dataset_path}, hash={inputs.dataset_hash}, version={inputs.dataset_version}")
    print(f"  Suction: req ID={inputs.suction_required_diameter_in:.4f} in, NPS={inputs.suction_nominal_diameter_in} in, schedule={inputs.suction_pipe_schedule}, selected ID={inputs.suction_selected_inside_diameter_in}")
    print(f"  Discharge: req ID={inputs.discharge_required_diameter_in:.4f} in, NPS={inputs.discharge_nominal_diameter_in} in, schedule={inputs.discharge_pipe_schedule}, selected ID={inputs.discharge_selected_inside_diameter_in}")
    print(f"  Pump: eff={inputs.pump_efficiency}, rpm={inputs.pump_rpm}")
