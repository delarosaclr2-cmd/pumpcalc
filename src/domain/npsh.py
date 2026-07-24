"""
NPSH module - Net Positive Suction Head calculations.
"""

from dataclasses import dataclass
from typing import Optional, Literal
from src.domain.units import Q_, ureg, psi_to_ft_h2o, ft_h2o_to_ft_fluid

NPSH_MARGIN_NOT_EVALUABLE = "NPSH_MARGIN_NOT_EVALUABLE"

PressureType = Literal["absolute", "gauge", "vacuum"]


@dataclass
class NPSHInputs:
    """Complete inputs for NPSH calculation."""

    # Pressures at liquid surface
    p_atm_abs_psi: float  # psia, atmospheric — required, no default
    p_vessel: float = 0.0  # pressure in vessel (psig if gauge, psia if absolute)
    p_vessel_type: PressureType = "gauge"  # "absolute", "gauge", "vacuum"

    # Fluid properties
    specific_gravity: float = 1.0
    vapor_pressure_psi: float = 0.0  # psia

    # Elevations
    pump_centerline_elev_ft: float = 0.0  # ft, reference elevation
    liquid_surface_elev_ft: float = 0.0  # ft, elevation of liquid surface
    min_liquid_level_elev_ft: Optional[float] = None  # ft, minimum operating level

    # Suction line losses
    suction_fitting_losses_ft: float = 0.0  # ft
    suction_pipe_losses_ft: float = 0.0  # ft

    # Velocity head at pump suction (optional)
    velocity_head_ft: float = 0.0  # ft

    def __post_init__(self):
        if self.p_atm_abs_psi <= 0:
            raise ValueError(f"p_atm_abs_psi must be > 0, got {self.p_atm_abs_psi}")
        if self.specific_gravity <= 0:
            raise ValueError(f"specific_gravity must be > 0, got {self.specific_gravity}")


@dataclass
class NPSHResult:
    """NPSH calculation results."""
    npsha_ft: float
    npsha_m: float
    
    # Components
    pressure_head_ft: float  # (Psurface_abs)/γ
    elevation_head_ft: float  # Hs = z_surface - z_pump
    velocity_head_ft: float
    suction_fitting_losses_ft: float
    suction_pipe_losses_ft: float
    vapor_pressure_head_ft: float
    
    # Inputs used
    p_surface_abs_psi: float
    p_vapor_abs_psi: float
    
    # Status
    status: str = "OK"
    warnings: list = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


def npsha_legacy(
    p_atm_psi: float,
    p_vessel_psi: float,
    sg: float,
    static_head_ft: float,
    suction_fitting_losses_ft: float,
    suction_pipe_losses_ft: float,
    vapor_pressure_ft: float
) -> float:
    """
    Legacy workbook NPSH formula:
    NPSHa = ((Patm + Pvessel) * 2.31 / SG) + Hs - Hf_acc - Hf_pipe - Pv
    
    NOTE: This assumes Pvessel is gauge pressure!
    If Pvessel is absolute, this double-counts atmospheric pressure.
    """
    # ((C8+E8)*(2.31/E11))+C9-C11-C14-E9
    pressure_term = (p_atm_psi + p_vessel_psi) * 2.31 / sg
    npsha = pressure_term + static_head_ft - suction_fitting_losses_ft - suction_pipe_losses_ft - vapor_pressure_ft
    return npsha


def calculate_npsha(inputs: NPSHInputs) -> NPSHResult:
    """
    Calculate NPSH Available using fundamental equation.
    
    NPSHa = (Psurface_abs - Pvap_abs)/γ + (z_surface - z_pump) - hf_suction - hv_suction
    
    Where:
    - Psurface_abs = Patm_abs + Pvessel_gauge (if vessel is open to atmosphere)
    - γ = specific weight = SG * 62.4 lb/ft³
    - hf = friction + minor losses
    """
    warnings = []
    
    # 1. Absolute pressure at liquid surface
    if inputs.p_vessel_type == "absolute":
        p_surface_abs = inputs.p_vessel
        warnings.append("Vessel pressure treated as absolute")
    elif inputs.p_vessel_type == "gauge":
        p_surface_abs = inputs.p_atm_abs_psi + inputs.p_vessel
    elif inputs.p_vessel_type == "vacuum":
        # Vacuum given as positive psia below atmospheric
        p_surface_abs = inputs.p_atm_abs_psi - inputs.p_vessel
        warnings.append("Vessel vacuum subtracted from atmospheric")
    else:
        p_surface_abs = inputs.p_atm_abs_psi + inputs.p_vessel
        warnings.append("Unknown pressure type, assuming gauge")
    
    # 2. Pressure head: Psurface_abs / γ = Psurface_abs * 144 / (SG * 62.4)
    # Using 2.31 ft/psi for SG=1: H_ft = P_psi * 2.31 / SG
    pressure_head_ft = p_surface_abs * 2.31 / inputs.specific_gravity
    
    # 3. Elevation head (static suction head)
    elevation_head_ft = inputs.liquid_surface_elev_ft - inputs.pump_centerline_elev_ft
    
    # 4. Velocity head
    velocity_head_ft = inputs.velocity_head_ft
    
    # 5. Suction losses
    suction_fitting_losses_ft = inputs.suction_fitting_losses_ft
    suction_pipe_losses_ft = inputs.suction_pipe_losses_ft
    
    # 6. Vapor pressure head
    # Convert vapor pressure from psi to ft of fluid
    vapor_pressure_head_ft = inputs.vapor_pressure_psi * 2.31 / inputs.specific_gravity
    
    # 7. NPSHa
    npsha_ft = (pressure_head_ft 
                + elevation_head_ft 
                + velocity_head_ft
                - suction_fitting_losses_ft
                - suction_pipe_losses_ft
                - vapor_pressure_head_ft)
    
    npsha_m = npsha_ft * 0.3048
    
    # Status checks (no NPSHr available, cannot evaluate margin)
    status = "OK"
    if npsha_ft < 0:
        status = "NEGATIVE_NPSH"
        warnings.append("NPSHa is negative - cavitation certain")
    else:
        status = "NPSH_MARGIN_NOT_EVALUABLE"
        warnings.append("NPSHr not available - margin cannot be evaluated")
    
    return NPSHResult(
        npsha_ft=npsha_ft,
        npsha_m=npsha_m,
        pressure_head_ft=pressure_head_ft,
        elevation_head_ft=elevation_head_ft,
        velocity_head_ft=velocity_head_ft,
        suction_fitting_losses_ft=suction_fitting_losses_ft,
        suction_pipe_losses_ft=suction_pipe_losses_ft,
        vapor_pressure_head_ft=vapor_pressure_head_ft,
        p_surface_abs_psi=p_surface_abs,
        p_vapor_abs_psi=inputs.vapor_pressure_psi,
        status=status,
        warnings=warnings
    )


if __name__ == '__main__':
    # Example: python -m src.domain.npsh  (reads dataset from JSON, not hardcoded)
    import json, pathlib
    _path = pathlib.Path(__file__).parents[2] / 'data' / 'cases' / 'current_workbook_case.json'
    if _path.exists():
        _data = json.loads(_path.read_text())
        _inputs = NPSHInputs(p_atm_abs_psi=_data['atmospheric_pressure_psia'],
                             p_vessel=_data['vessel_pressure'],
                             p_vessel_type=_data['vessel_pressure_type'],
                             specific_gravity=_data['specific_gravity'],
                             vapor_pressure_psi=_data['vapor_pressure_value'],
                             liquid_surface_elev_ft=_data['suction_static_head_ft'],
                             suction_fitting_losses_ft=_data['suction_fitting_losses_ft'],
                             suction_pipe_losses_ft=_data['suction_length_ft'] * 0.01)
        _result = calculate_npsha(_inputs)
        print(f"NPSHa = {_result.npsha_ft:.2f} ft ({_result.npsha_m:.2f} m) — Status: {_result.status}")
    else:
        print("Run pytest to verify NPSH — no dataset found at", _path)