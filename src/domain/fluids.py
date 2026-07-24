"""
Fluids module - Fluid properties and calculations.
"""
from typing import Optional
from dataclasses import dataclass
from src.domain.units import Q_, ureg


@dataclass
class Fluid:
    """Fluid properties with explicit units."""
    name: str
    density: Q_  # kg/m³
    specific_gravity: float  # dimensionless
    dynamic_viscosity: Q_  # Pa·s
    kinematic_viscosity: Q_  # m²/s
    temperature: Q_  # K
    vapor_pressure: Q_  # Pa
    
    @classmethod
    def from_imperial(cls, name: str, rho_lbm_ft3: float, mu_cP: float, 
                      temp_F: float, vp_psia: float, sg: float = None):
        """Create Fluid from imperial units."""
        rho = Q_(rho_lbm_ft3, 'pound / foot ** 3')
        mu = Q_(mu_cP, 'centipoise')
        temp = Q_(temp_F, 'degF').to('kelvin')
        vp = Q_(vp_psia, 'psi')
        
        if sg is None:
            sg = rho_lbm_ft3 / 62.4  # approximate at 60°F
        
        # Calculate kinematic viscosity
        nu = mu / rho
        
        return cls(
            name=name,
            density=rho,
            specific_gravity=sg,
            dynamic_viscosity=mu,
            kinematic_viscosity=nu,
            temperature=temp,
            vapor_pressure=vp
        )
    
    def get_density_lbm_ft3(self) -> float:
        """Get density in lbm/ft³."""
        return self.density.to('pound / foot ** 3').magnitude
    
    def get_viscosity_cP(self) -> float:
        """Get dynamic viscosity in cP."""
        return self.dynamic_viscosity.to('centipoise').magnitude
    
    def get_vapor_pressure_psi(self) -> float:
        """Get vapor pressure in psia."""
        return self.vapor_pressure.to('psi').magnitude
    
    def get_vapor_pressure_ft_h2o(self) -> float:
        """Get vapor pressure in ft water column."""
        return self.vapor_pressure.to('ft_H2O').magnitude


def create_water_95F() -> Fluid:
    """Create water fluid properties at 95°F (from workbook data)."""
    # From workbook: Item 9 (95°F), SG=0.995, viscosity from OUTPIPES table
    # Item 6 (Agua Blanca): density=62 lbm/ft³, viscosity=0.52 cP
    # At 95°F: from gravedadespecifica table Item 9: SG=0.995
    # Vapor pressure: from presionvapor table Item 9: 0.8 psia
    return Fluid.from_imperial(
        name="Agua Blanca",
        rho_lbm_ft3=62.0,
        mu_cP=0.52,
        temp_F=95.0,
        vp_psia=0.8,
        sg=0.995
    )


def create_fluid_from_workbook(fluid_code: int) -> Optional[Fluid]:
    """Create fluid from workbook fluid code."""
    # This would map to the workbook tables
    # For now return water at 95°F
    if fluid_code in [6, 9]:
        return create_water_95F()
    return None