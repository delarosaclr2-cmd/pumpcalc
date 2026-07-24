"""
Pipes module - Pipe geometry and flow calculations.
"""
from typing import Optional, List
from dataclasses import dataclass
import math
from src.domain.units import Q_, ureg, reynolds_imperial, velocity_head, ft_to_m, inch_to_m


def required_diameter_from_flow_velocity(flow_gpm: float, target_velocity_fps: float) -> float:
    """Compute required inside diameter (inches) from flow and target velocity.

    Derivation:
        Q (ft³/s) = Q_gpm / 448.831
        A (ft²)  = Q_ft3s / V_fps = π × D_ft² / 4
        D_ft     = sqrt(4 × Q_ft3s / (π × V_fps))
        D_in     = D_ft × 12
        D_in     = 12 × sqrt(4 × Q_gpm / (448.831 × π × V_fps))
        D_in     = 12 × sqrt(4 / (448.831 × π)) × sqrt(Q_gpm / V_fps)

    The constant C = 12 × sqrt(4 / (448.831 × π)) ≈ 0.639.

    Args:
        flow_gpm: Flow rate in US gallons per minute.
        target_velocity_fps: Target velocity in ft/s.

    Returns:
        Required inside diameter in inches.
    """
    C = 12.0 * math.sqrt(4.0 / (448.831 * math.pi))
    return C * math.sqrt(flow_gpm / target_velocity_fps)


@dataclass
class Pipe:
    """Pipe geometry with units."""
    nominal_diameter_in: float  # inches
    schedule: str  # e.g., 'STD', 'XS', 'XXS', 'SCH 40'
    inner_diameter_in: float  # inches
    length_ft: float
    roughness_ft: float  # absolute roughness in feet
    material: str = "Steel"
    
    @property
    def inner_diameter_m(self) -> float:
        return self.inner_diameter_in * 0.0254
    
    @property
    def length_m(self) -> float:
        return self.length_ft * 0.3048
    
    @property
    def roughness_m(self) -> float:
        return self.roughness_ft * 0.3048
    
    @property
    def cross_sectional_area_ft2(self) -> float:
        """Cross-sectional area in ft²."""
        import math
        d_ft = self.inner_diameter_in / 12.0
        return math.pi * d_ft**2 / 4
    
    @property
    def cross_sectional_area_m2(self) -> float:
        """Cross-sectional area in m²."""
        return self.cross_sectional_area_ft2 * 0.092903


@dataclass
class Fitting:
    """Pipe fitting with K factor or equivalent length."""
    name: str
    quantity: int
    k_factor: Optional[float] = None  # resistance coefficient K
    leq_over_d: Optional[float] = None  # equivalent length / diameter
    diameter_in: Optional[float] = None  # fitting diameter (if different from pipe)
    method: str = "K"  # "K" or "Leq"
    source: str = "Crane TP-410"


class PipeLine:
    """Collection of pipes and fittings for a flow path."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.pipes: List[Pipe] = []
        self.fittings: List[Fitting] = []
    
    def add_pipe(self, pipe: Pipe):
        self.pipes.append(pipe)
    
    def add_fitting(self, fitting: Fitting):
        self.fittings.append(fitting)
    
    @property
    def total_length_ft(self) -> float:
        return sum(p.length_ft for p in self.pipes)
    
    def get_velocity_fts(self, Q_gpm: float) -> float:
        """Calculate velocity in ft/s for given flow rate (uses first pipe diameter)."""
        if not self.pipes:
            return 0
        A = self.pipes[0].cross_sectional_area_ft2
        if A == 0:
            return 0
        # Q in ft³/s = Q_gpm / 448.831
        Q_ft3s = Q_gpm / 448.831
        return Q_ft3s / A


def create_pipe_from_workbook(side: str) -> Pipe:
    """Create pipe from workbook data.
    
    Args:
        side: 'suction' or 'discharge'
    """
    if side == 'suction':
        return Pipe(
            nominal_diameter_in=10,
            schedule='STD',
            inner_diameter_in=10.02,  # approximate for 10" STD
            length_ft=6.96,  # 2.12 m * 3.281
            roughness_ft=0.00012,  # Stainless steel
            material="Acero Inox SS"
        )
    elif side == 'discharge':
        return Pipe(
            nominal_diameter_in=6,
            schedule='STD',
            inner_diameter_in=6.065,  # 6" STD
            length_ft=36.0,  # from RAMALES
            roughness_ft=0.00012,  # Stainless steel
            material="Acero Inox SS"
        )
    else:
        raise ValueError("side must be 'suction' or 'discharge'")


if __name__ == '__main__':
    # Test
    suction = create_pipe_from_workbook('suction')
    discharge = create_pipe_from_workbook('discharge')
    
    print(f"Suction: {suction.nominal_diameter_in} in, ID={suction.inner_diameter_in:.3f} in, "
          f"L={suction.length_ft:.2f} ft, eps={suction.roughness_ft:.6f} ft")
    print(f"Discharge: {discharge.nominal_diameter_in} in, ID={discharge.inner_diameter_in:.3f} in, "
          f"L={discharge.length_ft:.2f} ft, eps={discharge.roughness_ft:.6f} ft")
    
    # Test velocity
    Q = 770.5  # GPM
    v_suction = suction.get_velocity_fts(Q)
    v_discharge = discharge.get_velocity_fts(Q)
    print(f"\nAt Q={Q} GPM:")
    print(f"  Suction velocity: {v_suction:.2f} ft/s")
    print(f"  Discharge velocity: {v_discharge:.2f} ft/s")