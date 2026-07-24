"""
Fittings module - Accessory/minor loss calculations.
"""
from typing import List, Optional
from dataclasses import dataclass
from src.domain.units import Q_, ureg


@dataclass
class FittingLoss:
    """Minor loss calculation for a fitting."""
    name: str
    quantity: int
    k_factor: Optional[float] = None
    leq_over_d: Optional[float] = None
    diameter_in: float = 0
    velocity_fts: float = 0
    method: str = "K"  # "K" or "Leq"
    source: str = "Crane TP-410"
    
    def loss_ft(self, friction_factor: float = None) -> float:
        """Calculate head loss in feet."""
        if self.method == "K" and self.k_factor is not None:
            # h = K * V² / (2g)
            g = 32.174
            return self.quantity * self.k_factor * self.velocity_fts**2 / (2 * g)
        elif self.method == "Leq" and self.leq_over_d is not None and friction_factor is not None:
            # h = f * (Leq/D) * V² / (2g)
            g = 32.174
            return self.quantity * friction_factor * self.leq_over_d * self.velocity_fts**2 / (2 * g)
        return 0.0
    
    def loss_ft_crane(self, friction_factor: float = None) -> float:
        """Calculate using Crane TP-410 method (matches workbook).
        
        Workbook formula: =((D*F)*(H2^2)/(32.4*2))*H
        Where D = ft (equivalent length from table), F = K factor, 
        H2 = velocity (ft/s), 32.4*2 = 64.8 ≈ 2g, H = quantity
        
        This is: h = f * (Leq/D) * V²/(2g) where Leq/D = ft_from_table / D_ft
        But the workbook uses: D (ft) * F (K) * V² / (2g) * quantity
        This seems to be mixing methods.
        """
        if self.method == "Leq" and friction_factor is not None and self.diameter_in > 0:
            D_ft = self.diameter_in / 12.0
            # Leq = (D * F) where D is from table in ft, F is K factor
            # h = f * (Leq/D) * V²/(2g)
            leq = self.leq_over_d * D_ft  # equivalent length
            g = 32.174
            return self.quantity * friction_factor * (leq / D_ft) * self.velocity_fts**2 / (2 * g)
        elif self.method == "K" and self.k_factor is not None:
            g = 32.174
            return self.quantity * self.k_factor * self.velocity_fts**2 / (2 * g)
        return 0.0


@dataclass
class FittingTable:
    """Table of fittings for a pipeline."""
    name: str
    fittings: List[FittingLoss]
    pipe_velocity_fts: float = 0
    pipe_friction_factor: float = 0
    
    def total_loss_ft(self) -> float:
        """Total minor losses in feet."""
        return sum(f.loss_ft_crane(self.pipe_friction_factor) for f in self.fittings)


# Standard K factors from Crane TP-410
CRANE_K_FACTORS = {
    # Valves
    "Gate valve, full open": 0.19,
    "Gate valve, 1/2 open": 0.54,
    "Gate valve, 3/4 open": 0.75,
    "Globe valve, full open": 10.0,
    "Angle valve, full open": 5.0,
    "Ball valve, full open": 0.05,
    "Butterfly valve, full open": 0.30,
    "Check valve, swing": 2.0,
    "Check valve, lift": 10.0,
    
    # Fittings
    "Elbow 90° standard": 0.30,
    "Elbow 90° long radius": 0.20,
    "Elbow 45° standard": 0.15,
    "Tee, flow through run": 0.20,
    "Tee, flow through branch": 1.0,
    "Reducer, gradual (10°)": 0.05,
    "Reducer, sudden (20°)": 0.25,
    "Expansion, sudden": 1.0,
    "Expansion, gradual": 0.15,
    
    # Entrance/Exit
    "Entrance, bellmouth": 0.05,
    "Entrance, square edge": 0.50,
    "Entrance, re-entrant": 1.0,
    "Exit, pipe": 1.0,
}


def create_fitting_table_from_workbook(side: str) -> FittingTable:
    """Create fitting table from workbook data."""
    if side == 'suction':
        # From TABLA DE ACCESORIOS SUCCION
        # Velocity from CAIDA PRESION DE TUBERIA!V6 = 3.12 ft/s
        return FittingTable(
            name="Suction Accessories",
            fittings=[
                FittingLoss("Gate valve, full open", 1, k_factor=0.19, diameter_in=8, velocity_fts=3.12),
                FittingLoss("Gate valve, 1/2 open", 1, k_factor=0.54, diameter_in=12, velocity_fts=3.12),
                FittingLoss("Gate valve, 3/4 open", 1, k_factor=0.75, diameter_in=17, velocity_fts=3.12),
                FittingLoss("Globe valve, full open", 1, k_factor=10.0, diameter_in=340, velocity_fts=3.12),
                # Add more from workbook
            ],
            pipe_velocity_fts=3.12,
            pipe_friction_factor=0.015
        )
    elif side == 'discharge':
        # From TABLA DE ACCESORIOS DESCARGA
        # Velocity from H2 = 8.6 ft/s
        return FittingTable(
            name="Discharge Accessories",
            fittings=[
                FittingLoss("Gate valve, full open", 2, k_factor=0.19, diameter_in=8, velocity_fts=8.6),
                FittingLoss("Gate valve, 1/2 open", 2, k_factor=0.54, diameter_in=12, velocity_fts=8.6),
                # ... more from workbook
            ],
            pipe_velocity_fts=8.6,
            pipe_friction_factor=0.015
        )
    else:
        raise ValueError("side must be 'suction' or 'discharge'")


if __name__ == '__main__':
    # Test
    table = create_fitting_table_from_workbook('suction')
    print(f"Suction fittings total loss: {table.total_loss_ft():.6f} ft")
    print(f"Pipe friction factor: {table.pipe_friction_factor:.5f}")
    print(f"Velocity: {table.pipe_velocity_fts:.2f} ft/s")