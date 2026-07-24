"""
NPSH module - Net Positive Suction Head calculations.
"""
from dataclasses import dataclass
from typing import Optional, Literal
from src.domain.units import Q_, ureg, psi_to_ft_h2o, ft_h2o_to_ft_fluid


PressureType = Literal["absolute", "gauge", "vacuum"]


@dataclass
class NPSHInputs:
    """Complete inputs for NPSH calculation."""
    
    # Pressures at liquid surface
    p_atm_abs_psi: float = 14.696  # psia, atmospheric pressure at site
    p_vessel: float = 0.0  # pressure in vessel (psig if gauge, psia if absolute)
    p_vessel_type: PressureType = "gauge"  # "absolute", "gauge", "vacuum"
    
    # Fluid properties
    specific_gravity: float = 1.0
    vapor_pressure_psi: float = 0.8  # psia
    
    # Elevations
    pump_centerline_elev_ft: float = 0.0  # ft, reference elevation
    liquid_surface_elev_ft: float = 1.64  # ft, elevation of liquid surface
    min_liquid_level_elev_ft: Optional[float] = None  # ft, minimum operating level
    
    # Suction line losses
    suction_fitting_losses_ft: float = 0.0  # ft
    suction_pipe_losses_ft: float = 0.0  # ft
    
    # Velocity head at pump suction (optional)
    velocity_head_ft: float = 0.0  # ft


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
    
    # Status checks
    status = "OK"
    if npsha_ft < 0:
        status = "NEGATIVE_NPSH"
        warnings.append("NPSHa is negative - cavitation certain")
    if npsha_ft < 5:
        status = "LOW_NPSH"
        warnings.append("NPSHa below 5 ft - margin may be insufficient")
    
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


def npsha_from_workbook() -> NPSHResult:
    """Calculate NPSHa using workbook inputs."""
    inputs = NPSHInputs(
        p_atm_abs_psi=14.7,
        p_vessel=0.0,
        p_vessel_type="gauge",
        specific_gravity=0.995,
        vapor_pressure_psi=0.8,
        liquid_surface_elev_ft=1.64,
        pump_centerline_elev_ft=0.0,
        suction_fitting_losses_ft=0.0168,
        suction_pipe_losses_ft=0.0261,
        velocity_head_ft=0.0
    )
    return calculate_npsha(inputs)


def compare_npsha_legacy_vs_validated() -> dict:
    """Compare legacy workbook formula vs validated calculation."""
    
    # Legacy workbook formula (E14)
    legacy = npsha_legacy(
        p_atm_psi=14.7,
        p_vessel_psi=0.0,  # Assuming gauge
        sg=0.995,
        static_head_ft=1.64,
        suction_fitting_losses_ft=0.0168,
        suction_pipe_losses_ft=0.0261,
        vapor_pressure_ft=1.8457  # from E9
    )
    
    # Validated
    validated = npsha_from_workbook()
    
    return {
        "legacy_npsha_ft": legacy,
        "validated_npsha_ft": validated.npsha_ft,
        "difference_ft": validated.npsha_ft - legacy,
        "legacy_components": {
            "pressure_term": (14.7 + 0.0) * 2.31 / 0.995,
            "static_head": 1.64,
            "fitting_losses": -0.0168,
            "pipe_losses": -0.0261,
            "vapor_pressure": -1.8457
        },
        "validated_components": {
            "pressure_head_ft": validated.pressure_head_ft,
            "elevation_head_ft": validated.elevation_head_ft,
            "fitting_losses_ft": validated.suction_fitting_losses_ft,
            "pipe_losses_ft": validated.suction_pipe_losses_ft,
            "vapor_pressure_head_ft": validated.vapor_pressure_head_ft
        }
    }


if __name__ == '__main__':
    result = npsha_from_workbook()
    print("NPSH Available (Validated):")
    print(f"  NPSHa = {result.npsha_ft:.2f} ft ({result.npsha_m:.2f} m)")
    print(f"  Status: {result.status}")
    print()
    print("Components:")
    print(f"  Pressure head: {result.pressure_head_ft:.4f} ft")
    print(f"  Elevation head: {result.elevation_head_ft:.4f} ft")
    print(f"  Velocity head: {result.velocity_head_ft:.4f} ft")
    print(f"  Fitting losses: {result.suction_fitting_losses_ft:.4f} ft")
    print(f"  Pipe losses: {result.suction_pipe_losses_ft:.4f} ft")
    print(f"  Vapor pressure: {result.vapor_pressure_head_ft:.4f} ft")
    print()
    print("Inputs:")
    print(f"  P_surface_abs: {result.p_surface_abs_psi:.2f} psia")
    print(f"  P_vapor_abs: {result.p_vapor_abs_psi:.2f} psia")
    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(f"  - {w}")
    
    print("\n" + "="*50)
    print("Legacy vs Validated Comparison:")
    cmp = compare_npsha_legacy_vs_validated()
    print(f"  Legacy NPSHa: {cmp['legacy_npsha_ft']:.4f} ft")
    print(f"  Validated NPSHa: {cmp['validated_npsha_ft']:.4f} ft")
    print(f"  Difference: {cmp['difference_ft']:.4f} ft")
    print("\nValidated components:")
    for k, v in cmp['validated_components'].items():
        print(f"  {k}: {v:.4f} ft")