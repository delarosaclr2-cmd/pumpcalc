"""
System Boundaries - Typed boundary nodes and absolute pressure computations.
"""
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class PressureReference(Enum):
    GAUGE = "GAUGE"
    ABSOLUTE = "ABSOLUTE"
    DIFFERENTIAL = "DIFFERENTIAL"
    VACUUM = "VACUUM"
    UNKNOWN = "UNKNOWN"


class BoundaryType(str, Enum):
    FREE_SURFACE = "FREE_SURFACE"
    VESSEL_GAS_SPACE = "VESSEL_GAS_SPACE"
    PUMP_SUCTION_FLANGE = "PUMP_SUCTION_FLANGE"
    PIPE_NODE = "PIPE_NODE"
    EQUIPMENT_INLET = "EQUIPMENT_INLET"
    EQUIPMENT_OUTLET = "EQUIPMENT_OUTLET"


class CalculationStatus(str, Enum):
    OK = "OK"
    PRESSURE_REFERENCE_REQUIRED = "PRESSURE_REFERENCE_REQUIRED"
    MISSING_ATMOSPHERIC_PRESSURE = "MISSING_ATMOSPHERIC_PRESSURE"
    INVALID_ABSOLUTE_PRESSURE = "INVALID_ABSOLUTE_PRESSURE"
    DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE = "DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE"
    PRESSURE_BOUNDARY_OVERLAP = "PRESSURE_BOUNDARY_OVERLAP"
    POSSIBLE_DOUBLE_COUNTING = "POSSIBLE_DOUBLE_COUNTING"


@dataclass
class SystemBoundary:
    boundary_id: str
    boundary_type: str
    pressure_value: float
    pressure_reference: str
    atmospheric_pressure_psia: Optional[float] = None
    elevation_ft: float = 0.0
    node_id: Optional[str] = None
    source_type: str = "UNKNOWN"
    source_sheet: Optional[str] = None
    source_cell: Optional[str] = None
    confidence: str = "PROVISIONAL"
    notes: Optional[str] = None

    def absolute_pressure_psia(self) -> float:
        ref = self.pressure_reference.upper()
        if ref == PressureReference.GAUGE.value:
            if self.atmospheric_pressure_psia is None:
                raise ValueError(f"Cannot compute absolute pressure for GAUGE boundary {self.boundary_id}: missing atmospheric_pressure_psia")
            return self.atmospheric_pressure_psia + self.pressure_value
        elif ref == PressureReference.ABSOLUTE.value:
            return self.pressure_value
        elif ref == PressureReference.VACUUM.value:
            if self.atmospheric_pressure_psia is None:
                raise ValueError(f"Cannot compute absolute pressure for VACUUM boundary {self.boundary_id}: missing atmospheric_pressure_psia")
            return self.atmospheric_pressure_psia - self.pressure_value
        elif ref == PressureReference.DIFFERENTIAL.value:
            raise ValueError(f"Cannot compute absolute pressure for DIFFERENTIAL boundary {self.boundary_id}: differential has no absolute datum")
        else:
            raise ValueError(f"Cannot compute absolute pressure for boundary {self.boundary_id} with reference {ref}")


@dataclass
class PressureBoundaryResult:
    source_boundary_abs_psia: float
    destination_required_abs_psia: float
    pressure_difference_psi: float
    pressure_head_difference_ft: float
    calculation_status: str = "OK"


def compute_boundary_absolute_pressure(
    atmospheric_pressure_psia: Optional[float] = None,
    vessel_pressure: float = 0.0,
    vessel_pressure_type: str = "GAUGE",
) -> float:
    ref = vessel_pressure_type.upper()
    if ref == PressureReference.GAUGE.value:
        if atmospheric_pressure_psia is None:
            raise ValueError("GAUGE pressure requires atmospheric_pressure_psia")
        return atmospheric_pressure_psia + vessel_pressure
    elif ref == PressureReference.ABSOLUTE.value:
        return vessel_pressure
    elif ref == PressureReference.VACUUM.value:
        if atmospheric_pressure_psia is None:
            raise ValueError("VACUUM pressure requires atmospheric_pressure_psia")
        return atmospheric_pressure_psia - vessel_pressure
    else:
        raise ValueError(f"Unknown vessel_pressure_type: {vessel_pressure_type}")


def compute_pressure_difference_between_boundaries(
    source_boundary: SystemBoundary,
    destination_boundary: SystemBoundary,
) -> PressureBoundaryResult:
    try:
        source_abs = source_boundary.absolute_pressure_psia()
    except (ValueError, TypeError) as e:
        return PressureBoundaryResult(
            source_boundary_abs_psia=0.0,
            destination_required_abs_psia=0.0,
            pressure_difference_psi=0.0,
            pressure_head_difference_ft=0.0,
            calculation_status="MISSING_ATMOSPHERIC_PRESSURE",
        )
    try:
        dest_abs = destination_boundary.absolute_pressure_psia()
    except (ValueError, TypeError) as e:
        return PressureBoundaryResult(
            source_boundary_abs_psia=round(source_abs, 6),
            destination_required_abs_psia=0.0,
            pressure_difference_psi=0.0,
            pressure_head_difference_ft=0.0,
            calculation_status="PRESSURE_REFERENCE_REQUIRED",
        )

    diff_psi = dest_abs - source_abs
    status = "OK"
    if diff_psi < 0:
        status = CalculationStatus.DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE.value
    return PressureBoundaryResult(
        source_boundary_abs_psia=round(source_abs, 6),
        destination_required_abs_psia=round(dest_abs, 6),
        pressure_difference_psi=round(diff_psi, 6),
        pressure_head_difference_ft=0.0,
        calculation_status=status,
    )
