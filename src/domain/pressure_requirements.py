"""
Pressure Requirements - Typed pressure terms, requirements, and head conversion.
"""
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum

from src.domain.system_boundaries import (
    PressureReference, PressureBoundaryResult, CalculationStatus,
    compute_boundary_absolute_pressure,
)
from src.domain.accessory_losses import (
    legacy_psi_to_ft, validated_psi_to_ft,
    PressureClassification,
)


class PressureTermType(str, Enum):
    INSTRUMENT_PRESSURE_DROP = "INSTRUMENT_PRESSURE_DROP"
    EQUIPMENT_INTERNAL_PRESSURE_DROP = "EQUIPMENT_INTERNAL_PRESSURE_DROP"
    MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE = "MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE"
    RECEIVING_VESSEL_OPERATING_PRESSURE = "RECEIVING_VESSEL_OPERATING_PRESSURE"


class FlowDependency(str, Enum):
    FLOW_INDEPENDENT = "FLOW_INDEPENDENT"
    QUADRATIC_WITH_FLOW = "QUADRATIC_WITH_FLOW"
    MANUFACTURER_CURVE = "MANUFACTURER_CURVE"
    USER_DEFINED = "USER_DEFINED"
    UNKNOWN = "UNKNOWN"


class CombinationRule(str, Enum):
    MAXIMUM_REQUIREMENT = "MAXIMUM_REQUIREMENT"
    ADDITIVE = "ADDITIVE"
    ALTERNATIVE_SCENARIOS = "ALTERNATIVE_SCENARIOS"
    USER_DEFINED = "USER_DEFINED"


class PressureBoundaryWarning(str, Enum):
    PRESSURE_REFERENCE_REQUIRED = "PRESSURE_REFERENCE_REQUIRED"
    PRESSURE_BOUNDARY_OVERLAP = "PRESSURE_BOUNDARY_OVERLAP"
    POSSIBLE_DOUBLE_COUNTING = "POSSIBLE_DOUBLE_COUNTING"
    ABSOLUTE_PRESSURE_REQUIRES_REFERENCE_BOUNDARY = "ABSOLUTE_PRESSURE_REQUIRES_REFERENCE_BOUNDARY"
    ADDITIVE_RULE_REQUIRES_CONFIRMATION = "ADDITIVE_RULE_REQUIRES_CONFIRMATION"
    DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE = "DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE"


WATER_DENSITY_LBM_FT3 = 62.4
PSI_TO_PSF = 144.0


def pressure_term_to_head(
    value_psi: float,
    pressure_reference: str,
    source_boundary_abs_psia: float,
    specific_gravity: float,
    destination_atmospheric_pressure_psia: Optional[float] = None,
) -> PressureBoundaryResult:
    """Convert a pressure term to head difference using correct reference semantics.

    Rules:
    - DIFFERENTIAL: diff = value, dest_abs = source_abs + diff (U39 rule)
    - GAUGE: dest_abs = dest_atm + value, diff = dest_abs - source_abs
    - ABSOLUTE: dest_abs = value, diff = dest_abs - source_abs
    - VACUUM: dest_abs = dest_atm - value, diff = dest_abs - source_abs
    - UNKNOWN: returns PRESSURE_REFERENCE_REQUIRED
    """
    ref = pressure_reference.upper()

    if ref == PressureReference.DIFFERENTIAL.value:
        diff_psi = value_psi
        dest_abs = source_boundary_abs_psia + value_psi

    elif ref == PressureReference.GAUGE.value:
        atm = destination_atmospheric_pressure_psia if destination_atmospheric_pressure_psia is not None else source_boundary_abs_psia
        dest_abs = atm + value_psi
        diff_psi = dest_abs - source_boundary_abs_psia

    elif ref == PressureReference.ABSOLUTE.value:
        dest_abs = value_psi
        diff_psi = dest_abs - source_boundary_abs_psia

    elif ref == PressureReference.VACUUM.value:
        atm = destination_atmospheric_pressure_psia if destination_atmospheric_pressure_psia is not None else source_boundary_abs_psia
        dest_abs = atm - value_psi
        diff_psi = dest_abs - source_boundary_abs_psia
        if dest_abs < 0:
            return PressureBoundaryResult(
                source_boundary_abs_psia=round(source_boundary_abs_psia, 6),
                destination_required_abs_psia=round(dest_abs, 6),
                pressure_difference_psi=round(diff_psi, 6),
                pressure_head_difference_ft=0.0,
                calculation_status=CalculationStatus.INVALID_ABSOLUTE_PRESSURE.value,
            )
    else:
        return PressureBoundaryResult(
            source_boundary_abs_psia=round(source_boundary_abs_psia, 6),
            destination_required_abs_psia=0.0,
            pressure_difference_psi=0.0,
            pressure_head_difference_ft=0.0,
            calculation_status=CalculationStatus.PRESSURE_REFERENCE_REQUIRED.value,
        )

    head_ft = diff_psi * PSI_TO_PSF / (WATER_DENSITY_LBM_FT3 * specific_gravity)

    status = CalculationStatus.OK.value
    if diff_psi < 0:
        status = CalculationStatus.DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE.value

    return PressureBoundaryResult(
        source_boundary_abs_psia=round(source_boundary_abs_psia, 6),
        destination_required_abs_psia=round(dest_abs, 6),
        pressure_difference_psi=round(diff_psi, 6),
        pressure_head_difference_ft=round(head_ft, 6),
        calculation_status=status,
    )


@dataclass
class PressureHeadTerm:
    name: str
    value: float
    pressure_unit: str
    pressure_reference: str
    classification: str
    specific_gravity: float
    legacy_head_ft: float
    validated_head_ft: float
    source_sheet: str
    source_cell: str
    confidence: str
    user_confirmed: bool = False
    pressure_reference_notes: str = ""


@dataclass
class PressureRequirement:
    term_id: str
    name: str
    term_type: str
    value: float
    unit: str
    pressure_reference: str
    flow_dependency: str
    design_flow_gpm: Optional[float] = None
    active: bool = True
    source_type: str = "WORKBOOK_MANUAL_INPUT"
    source_sheet: Optional[str] = None
    source_cell: Optional[str] = None
    source_comment: Optional[str] = None
    confidence: str = "PROVISIONAL"
    user_confirmed: bool = False
    notes: Optional[str] = None
    start_node: Optional[str] = None
    end_node: Optional[str] = None
    pressure_drop_curve: Optional[str] = None
    combination_rule: str = "ALTERNATIVE_SCENARIOS"


# ---- Factory / builder functions ----

def build_pressure_head_terms(sg: float = 0.995) -> List[PressureHeadTerm]:
    terms = []
    u39_legacy = legacy_psi_to_ft(0.36)
    u39_validated = validated_psi_to_ft(0.36, sg)
    terms.append(PressureHeadTerm(
        name="PERDIDAS POR TRANSMISOR DE FLUJO",
        value=0.36,
        pressure_unit="PSI",
        pressure_reference=PressureReference.DIFFERENTIAL.value,
        classification=PressureClassification.INSTRUMENT_PRESSURE_DROP.value,
        specific_gravity=sg,
        legacy_head_ft=round(u39_legacy, 6),
        validated_head_ft=round(u39_validated, 6),
        source_sheet="TABLA DE ACCESORIOS DESCARGA",
        source_cell="U39",
        confidence="HIGH",
        user_confirmed=True,
    ))
    u40_legacy = legacy_psi_to_ft(79.77)
    u40_validated = validated_psi_to_ft(79.77, sg)
    terms.append(PressureHeadTerm(
        name="PRESION DE OPERACION DEL EQUIPO",
        value=79.77,
        pressure_unit="PSI",
        pressure_reference=PressureReference.UNKNOWN.value,
        classification="MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE",
        specific_gravity=sg,
        legacy_head_ft=round(u40_legacy, 6),
        validated_head_ft=round(u40_validated, 6),
        source_sheet="TABLA DE ACCESORIOS DESCARGA",
        source_cell="U40",
        confidence="USER_CONFIRMED_SEMANTICS",
        user_confirmed=True,
        pressure_reference_notes="Pressure reference (GAUGE/ABSOLUTE) not yet confirmed by user. Validated conversion requires pressure_reference.",
    ))
    return terms


def build_pressure_requirements(sg: float = 0.995) -> List[PressureRequirement]:
    requirements = []
    u39_valid = validated_psi_to_ft(0.36, sg)
    requirements.append(PressureRequirement(
        term_id="DISCHARGE_INSTRUMENT_FT_001",
        name="Perdida del transmisor de flujo",
        term_type=PressureTermType.INSTRUMENT_PRESSURE_DROP.value,
        value=0.36,
        unit="psi",
        pressure_reference=PressureReference.DIFFERENTIAL.value,
        flow_dependency=FlowDependency.UNKNOWN.value,
        design_flow_gpm=770.5,
        active=True,
        source_type="WORKBOOK_MANUAL_INPUT",
        source_sheet="TABLA DE ACCESORIOS DESCARGA",
        source_cell="U39",
        source_comment="PERDIDAS POR TRANSMISOR DE FLUJO",
        confidence="HIGH",
        user_confirmed=True,
        notes="Caida diferencial del transmisor de flujo agregada manualmente.",
    ))
    u40_valid = validated_psi_to_ft(79.77, sg)
    requirements.append(PressureRequirement(
        term_id="EQUIPMENT_MINIMUM_INLET_PRESSURE_001",
        name="Presion minima requerida en la entrada del equipo",
        term_type=PressureTermType.MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE.value,
        value=79.77,
        unit="psi",
        pressure_reference=PressureReference.UNKNOWN.value,
        flow_dependency=FlowDependency.FLOW_INDEPENDENT.value,
        design_flow_gpm=None,
        active=True,
        source_type="WORKBOOK_MANUAL_INPUT",
        source_sheet="TABLA DE ACCESORIOS DESCARGA",
        source_cell="U40",
        source_comment="PRESION DE OPERACION DEL EQUIPO",
        confidence="USER_CONFIRMED_SEMANTICS",
        user_confirmed=True,
        notes="Valor agregado manualmente para garantizar la presion minima necesaria en la entrada del equipo receptor.",
    ))
    return requirements


def combine_boundary_pressures(
    pressures: List[float],
    rule: str = CombinationRule.ALTERNATIVE_SCENARIOS.value,
    additive_confirmed: bool = False,
) -> float:
    if rule == CombinationRule.MAXIMUM_REQUIREMENT.value:
        return max(pressures)
    elif rule == CombinationRule.ADDITIVE.value:
        if not additive_confirmed:
            raise ValueError("ADDITIVE rule requires explicit confirmation")
        return sum(pressures)
    elif rule == CombinationRule.ALTERNATIVE_SCENARIOS.value:
        return max(pressures)
    else:
        raise ValueError(f"Unknown combination rule: {rule}")


def detect_pressure_boundary_overlap(requirements: List[PressureRequirement]) -> List[Dict]:
    warnings = []
    inlet_terms = [r for r in requirements
                   if r.term_type == PressureTermType.MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE.value
                   and r.active]
    vessel_terms = [r for r in requirements
                    if r.term_type == PressureTermType.RECEIVING_VESSEL_OPERATING_PRESSURE.value
                    and r.active]
    for inlet in inlet_terms:
        for vessel in vessel_terms:
            if inlet.start_node == vessel.start_node or inlet.end_node == vessel.end_node:
                warnings.append({
                    "type": PressureBoundaryWarning.PRESSURE_BOUNDARY_OVERLAP.value,
                    "description": f"Minimum inlet pressure '{inlet.term_id}' and vessel operating pressure '{vessel.term_id}' share a node",
                    "term_ids": [inlet.term_id, vessel.term_id],
                    "shared_node": inlet.start_node or inlet.end_node,
                    "suggested_rule": CombinationRule.ALTERNATIVE_SCENARIOS.value,
                })
    return warnings


# ---- TDH balance scenarios ----

_DEFAULT_STATIC_HEAD_DIFF = 5.279580052493438
_DEFAULT_SUCT_MAJOR = 0.026105052665489056
_DEFAULT_DISCH_MAJOR = 1.6699886165203006


def build_semantic_tdh_balances(
    static_head_diff_ft: float = _DEFAULT_STATIC_HEAD_DIFF,
    suction_major_losses_ft: float = _DEFAULT_SUCT_MAJOR,
    discharge_major_losses_ft: float = _DEFAULT_DISCH_MAJOR,
    sg: float = 0.995,
    source_atmospheric_pressure_psia: Optional[float] = None,
    destination_atmospheric_pressure_psia: Optional[float] = None,
    source_vessel_pressure: float = 0.0,
    source_vessel_pressure_type: str = "GAUGE",
) -> Dict:
    if source_atmospheric_pressure_psia is None:
        raise ValueError("build_semantic_tdh_balances requires source_atmospheric_pressure_psia from inputs")
    if destination_atmospheric_pressure_psia is None:
        destination_atmospheric_pressure_psia = source_atmospheric_pressure_psia

    from src.domain.accessory_losses import compute_discharge_results, compute_suction_results, summarize_discharge, summarize_suction
    discharge = compute_discharge_results()
    d_sum = summarize_discharge(discharge)
    suction = compute_suction_results()
    s_sum = summarize_suction(suction)

    leq_only_discharge = d_sum.total_leq_formula_loss_ft
    leq_only_suction = s_sum.total_leq_formula_loss_ft
    accessory_minor = leq_only_suction + leq_only_discharge

    u39_legacy = legacy_psi_to_ft(0.36)
    u40_legacy = legacy_psi_to_ft(79.77)
    u39_validated = validated_psi_to_ft(0.36, sg)
    u40_validated = validated_psi_to_ft(79.77, sg)

    pipe_major = suction_major_losses_ft + discharge_major_losses_ft
    surface_pressure_diff = 0.0

    source_abs = compute_boundary_absolute_pressure(
        atmospheric_pressure_psia=source_atmospheric_pressure_psia,
        vessel_pressure=source_vessel_pressure,
        vessel_pressure_type=source_vessel_pressure_type,
    )

    def _build(
        accessory_minor_ft: float,
        instrument_drop_ft: float,
        equipment_internal_drop_ft: float,
        min_inlet_pressure_ft: float,
        vessel_operating_pressure_ft: float,
        residual_pressure_ft: float,
        discharge_legacy_ft: float,
        label: str,
    ) -> Dict:
        total = (static_head_diff_ft + surface_pressure_diff + pipe_major
                 + accessory_minor_ft + instrument_drop_ft
                 + equipment_internal_drop_ft + residual_pressure_ft
                 + min_inlet_pressure_ft + vessel_operating_pressure_ft)
        return {
            "description": label,
            "static_elevation_head_ft": round(static_head_diff_ft, 6),
            "surface_pressure_difference_ft": round(surface_pressure_diff, 6),
            "pipe_major_losses_ft": round(pipe_major, 6),
            "accessory_minor_losses_ft": round(accessory_minor_ft, 6),
            "instrument_pressure_drop_ft": round(instrument_drop_ft, 6),
            "equipment_pressure_drop_ft": round(equipment_internal_drop_ft, 6),
            "equipment_internal_pressure_drop_ft": round(equipment_internal_drop_ft, 6),
            "required_residual_pressure_head_ft": round(residual_pressure_ft, 6),
            "unclassified_required_pressure_head_ft": round(min_inlet_pressure_ft, 6),
            "minimum_required_equipment_inlet_pressure_head_ft": round(min_inlet_pressure_ft, 6),
            "receiving_vessel_operating_pressure_head_ft": round(vessel_operating_pressure_ft, 6),
            "discharge_fitting_losses_legacy_ft": round(discharge_legacy_ft, 6),
            "total_dynamic_head_ft": round(total, 6),
        }

    # A
    a_minor = accessory_minor + u39_legacy + u40_legacy
    a = _build(
        accessory_minor_ft=a_minor,
        instrument_drop_ft=0.0,
        equipment_internal_drop_ft=0.0,
        min_inlet_pressure_ft=0.0,
        vessel_operating_pressure_ft=0.0,
        residual_pressure_ft=0.0,
        discharge_legacy_ft=a_minor,
        label="A. WORKBOOK_LEGACY: U39/U40 inside accessory_minor, legacy x2.31 conversion",
    )

    # B
    b_legacy = accessory_minor + u39_legacy + u40_legacy
    b = _build(
        accessory_minor_ft=accessory_minor,
        instrument_drop_ft=round(u39_legacy, 6),
        equipment_internal_drop_ft=0.0,
        min_inlet_pressure_ft=round(u40_legacy, 6),
        vessel_operating_pressure_ft=0.0,
        residual_pressure_ft=0.0,
        discharge_legacy_ft=b_legacy,
        label="B. SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION: U39->instrument_drop, U40->minimum_inlet, legacy x2.31",
    )

    # C. GAUGE scenario: uses correct gauge semantics
    c_gauge_result = pressure_term_to_head(
        value_psi=79.77,
        pressure_reference=PressureReference.GAUGE.value,
        source_boundary_abs_psia=source_abs,
        specific_gravity=sg,
        destination_atmospheric_pressure_psia=destination_atmospheric_pressure_psia,
    )
    c_legacy = accessory_minor + u39_legacy + u40_legacy
    c = _build(
        accessory_minor_ft=accessory_minor,
        instrument_drop_ft=round(u39_validated, 6),
        equipment_internal_drop_ft=0.0,
        min_inlet_pressure_ft=round(c_gauge_result.pressure_head_difference_ft, 6),
        vessel_operating_pressure_ft=0.0,
        residual_pressure_ft=0.0,
        discharge_legacy_ft=c_legacy,
        label="C. VALIDATED_U40_AS_GAUGE: U40=79.77 psig, dest_atm={:.1f} psia, source_abs={:.1f} psia -> diff={:.4f} psi".format(
            destination_atmospheric_pressure_psia, source_abs, c_gauge_result.pressure_difference_psi),
    )

    # D. ABSOLUTE scenario
    d_abs_result = pressure_term_to_head(
        value_psi=79.77,
        pressure_reference=PressureReference.ABSOLUTE.value,
        source_boundary_abs_psia=source_abs,
        specific_gravity=sg,
    )
    d_legacy = accessory_minor + u39_legacy + u40_legacy
    d = _build(
        accessory_minor_ft=accessory_minor,
        instrument_drop_ft=round(u39_validated, 6),
        equipment_internal_drop_ft=0.0,
        min_inlet_pressure_ft=round(d_abs_result.pressure_head_difference_ft, 6),
        vessel_operating_pressure_ft=0.0,
        residual_pressure_ft=0.0,
        discharge_legacy_ft=d_legacy,
        label="D. VALIDATED_U40_AS_ABSOLUTE: U40=79.77 psia - source {:.4f} psia = {:.4f} psi diff".format(
            source_abs, d_abs_result.pressure_difference_psi),
    )
    d["source_boundary_absolute_pressure_psia"] = d_abs_result.source_boundary_abs_psia
    d["destination_required_absolute_pressure_psia"] = d_abs_result.destination_required_abs_psia
    d["pressure_difference_psi"] = d_abs_result.pressure_difference_psi
    d["pressure_head_difference_ft"] = d_abs_result.pressure_head_difference_ft

    # E. UNKNOWN scenario
    e_legacy = accessory_minor + u39_legacy + u40_legacy
    e_status = pressure_term_to_head(
        value_psi=79.77,
        pressure_reference=PressureReference.UNKNOWN.value,
        source_boundary_abs_psia=source_abs,
        specific_gravity=sg,
    )
    e = _build(
        accessory_minor_ft=accessory_minor,
        instrument_drop_ft=round(u39_validated, 6),
        equipment_internal_drop_ft=0.0,
        min_inlet_pressure_ft=0.0,
        vessel_operating_pressure_ft=0.0,
        residual_pressure_ft=0.0,
        discharge_legacy_ft=e_legacy,
        label="E. U40_REFERENCE_UNKNOWN: Pressure reference not specified - no definitive validated TDH",
    )
    e["total_dynamic_head_ft"] = e_status.calculation_status
    e["source_boundary_absolute_pressure_psia"] = e_status.source_boundary_abs_psia
    e["destination_required_absolute_pressure_psia"] = "PRESSURE_REFERENCE_REQUIRED"
    e["pressure_difference_psi"] = "PRESSURE_REFERENCE_REQUIRED"

    # F. U40_EXCLUDED
    f_legacy = accessory_minor + u39_legacy
    f = _build(
        accessory_minor_ft=accessory_minor,
        instrument_drop_ft=round(u39_legacy, 6),
        equipment_internal_drop_ft=0.0,
        min_inlet_pressure_ft=0.0,
        vessel_operating_pressure_ft=0.0,
        residual_pressure_ft=0.0,
        discharge_legacy_ft=f_legacy,
        label="F. U40_EXCLUDED: Sensitivity only - U40 excluded (not recommended as correction)",
    )

    return {
        "WORKBOOK_LEGACY": a,
        "SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION": b,
        "VALIDATED_U40_AS_GAUGE": c,
        "VALIDATED_U40_AS_ABSOLUTE": d,
        "U40_REFERENCE_UNKNOWN": e,
        "U40_EXCLUDED": f,
    }


def build_system_curve_classification() -> Dict:
    return {
        "static_elevation_head_ft": {
            "flow_dependence": FlowDependency.FLOW_INDEPENDENT.value,
            "rationale": "Elevation difference between tanks is constant regardless of flow rate",
        },
        "surface_pressure_difference_ft": {
            "flow_dependence": FlowDependency.FLOW_INDEPENDENT.value,
            "rationale": "Open tank at both ends, no additional pressurization",
        },
        "pipe_major_losses_ft": {
            "flow_dependence": FlowDependency.QUADRATIC_WITH_FLOW.value,
            "rationale": "Darcy-Weisbach major losses are approximately proportional to Q^2",
        },
        "accessory_minor_losses_ft": {
            "flow_dependence": FlowDependency.QUADRATIC_WITH_FLOW.value,
            "rationale": "Leq/D and K-method minor losses are proportional to V^2, hence ~Q^2",
        },
        "instrument_pressure_drop_ft": {
            "flow_dependence": FlowDependency.UNKNOWN.value,
            "rationale": "Differential pressure across flow transmitter at design flow (770.5 GPM); confirm if fixed at all flows",
        },
        "equipment_pressure_drop_ft": {
            "flow_dependence": FlowDependency.UNKNOWN.value,
            "rationale": "Do not assume Q^2 dependence without manufacturer curve or test data",
        },
        "equipment_internal_pressure_drop_ft": {
            "flow_dependence": FlowDependency.UNKNOWN.value,
            "rationale": "Internal equipment pressure drop; do not assume Q^2 without manufacturer curve",
        },
        "required_residual_pressure_head_ft": {
            "flow_dependence": FlowDependency.FLOW_INDEPENDENT.value,
            "rationale": "Required minimum pressure at discharge point is typically independent of flow",
        },
        "unclassified_required_pressure_head_ft": {
            "flow_dependence": FlowDependency.UNKNOWN.value,
            "rationale": "Nature of 'PRESION DE OPERACION DEL EQUIPO' is unknown",
        },
        "minimum_required_equipment_inlet_pressure_head_ft": {
            "flow_dependence": FlowDependency.FLOW_INDEPENDENT.value,
            "rationale": "Minimum required pressure at equipment inlet is typically a fixed static requirement independent of flow",
        },
        "receiving_vessel_operating_pressure_head_ft": {
            "flow_dependence": FlowDependency.FLOW_INDEPENDENT.value,
            "rationale": "Vessel operating pressure is typically a fixed boundary condition independent of flow",
        },
    }
