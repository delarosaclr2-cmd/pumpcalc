"""
Units module - Centralized unit registry and conversions using pint.
"""
from pint import UnitRegistry
from typing import Union, Optional
import warnings

# Create unit registry
ureg = UnitRegistry()
ureg.define('gpm = gallon / minute = GPM')
ureg.define('ft_H2O = 2989.06692 * pascal')
ureg.define('ft_fluid = ft_H2O * dimensionless')  # ft of specific fluid

Q_ = ureg.Quantity


class UnitSystem:
    """Unit system handling with explicit conversions."""
    
    def __init__(self, system: str = 'SI'):
        """
        Initialize unit system.
        
        Args:
            system: 'SI' or 'IMPERIAL'
        """
        self.system = system.upper()
        
    def to_si(self, value: Union[float, Q_], unit: str) -> Q_:
        """Convert value to SI base units."""
        if isinstance(value, Q_):
            return value.to_base_units()
        return Q_(value, unit).to_base_units()
    
    def to_imperial(self, value: Union[float, Q_], unit: str) -> Q_:
        """Convert value to imperial units."""
        if isinstance(value, Q_):
            return value.to(self._imperial_unit(unit))
        return Q_(value, unit).to(self._imperial_unit(unit))
    
    def _imperial_unit(self, unit: str) -> str:
        """Map SI unit to preferred imperial unit."""
        mapping = {
            'meter': 'foot',
            'metre': 'foot',
            'pascal': 'psi',
            'kilogram': 'pound',
            'cubic_meter': 'gallon',
            'cubic_meter_per_second': 'gpm',
            'meter_per_second': 'foot_per_second',
            'watt': 'horsepower',
            'newton': 'pound_force',
        }
        return mapping.get(unit, unit)


# Common conversion functions - using working pint unit names
def gpm_to_m3h(gpm: float) -> float:
    """Convert GPM to m³/h."""
    return Q_(gpm, 'gpm').to('m**3 / hour').magnitude


def gpm_to_lpm(gpm: float) -> float:
    """Convert GPM to L/min."""
    return Q_(gpm, 'gpm').to('liter / minute').magnitude


def ft_to_m(ft: float) -> float:
    """Convert feet to meters."""
    return Q_(ft, 'foot').to('meter').magnitude


def m_to_ft(m: float) -> float:
    """Convert meters to feet."""
    return Q_(m, 'meter').to('foot').magnitude


def inch_to_m(inch: float) -> float:
    """Convert inches to meters."""
    return Q_(inch, 'inch').to('meter').magnitude


def psi_to_pa(psi: float) -> float:
    """Convert psi to Pa."""
    return Q_(psi, 'psi').to('pascal').magnitude


def pa_to_psi(pa: float) -> float:
    """Convert Pa to psi."""
    return Q_(pa, 'pascal').to('psi').magnitude


def psi_to_ft_h2o(psi: float) -> float:
    """Convert psi to feet of water column (at 4°C, SG=1)."""
    return Q_(psi, 'psi').to('ft_H2O').magnitude


def ft_h2o_to_psi(ft: float) -> float:
    """Convert feet of water to psi."""
    return Q_(ft, 'ft_H2O').to('psi').magnitude


def cP_to_Pa_s(cp: float) -> float:
    """Convert centipoise to Pa·s."""
    return Q_(cp, 'centipoise').to('pascal * second').magnitude


def lbm_ft3_to_kg_m3(lbm_ft3: float) -> float:
    """Convert lbm/ft³ to kg/m³."""
    return Q_(lbm_ft3, 'pound / foot ** 3').to('kilogram / meter ** 3').magnitude


def kg_m3_to_lbm_ft3(kg_m3: float) -> float:
    """Convert kg/m³ to lbm/ft³."""
    return Q_(kg_m3, 'kilogram / meter ** 3').to('pound / foot ** 3').magnitude


def hp_to_kw(hp: float) -> float:
    """Convert horsepower to kilowatts."""
    return Q_(hp, 'horsepower').to('kilowatt').magnitude


def kw_to_hp(kw: float) -> float:
    """Convert kilowatts to horsepower."""
    return Q_(kw, 'kilowatt').to('horsepower').magnitude


def ft_h2o_to_ft_fluid(ft_h2o: float, sg: float) -> float:
    """Convert feet of water to feet of fluid with given specific gravity."""
    return ft_h2o / sg


def ft_fluid_to_ft_h2o(ft_fluid: float, sg: float) -> float:
    """Convert feet of fluid to feet of water."""
    return ft_fluid * sg


def velocity_head(v: float, g: float = 32.174) -> float:
    """Calculate velocity head in feet.
    
    Args:
        v: velocity in ft/s
        g: gravitational acceleration in ft/s² (default 32.174)
    Returns:
        velocity head in feet
    """
    return v**2 / (2 * g)


def reynolds_imperial(Q_gpm: float, D_in: float, rho_lbm_ft3: float, mu_cP: float) -> float:
    """Calculate Reynolds number in imperial units.
    
    Re = 50.66 * Q * rho / (D * mu)
    
    Args:
        Q_gpm: flow rate in GPM
        D_in: diameter in inches
        rho_lbm_ft3: mass density in lbm/ft³
        mu_cP: dynamic viscosity in centipoise
    Returns:
        Reynolds number (dimensionless)
    """
    return 50.66 * Q_gpm * rho_lbm_ft3 / (D_in * mu_cP)


def reynolds_si(Q_m3s: float, D_m: float, rho_kg_m3: float, mu_Pa_s: float) -> float:
    """Calculate Reynolds number in SI units.
    
    Re = rho * V * D / mu
    
    Args:
        Q_m3s: flow rate in m³/s
        D_m: diameter in meters
        rho_kg_m3: density in kg/m³
        mu_Pa_s: dynamic viscosity in Pa·s
    Returns:
        Reynolds number (dimensionless)
    """
    A = 3.14159265359 * D_m**2 / 4
    V = Q_m3s / A
    return rho_kg_m3 * V * D_m / mu_Pa_s


# Convenience functions for common imperial constants
IMPERIAL_CONSTANTS = {
    'GPM_TO_FT3S': 1/448.831,  # 1 GPM = 1/448.831 ft³/s
    'FT3S_TO_GPM': 448.831,
    'PSI_TO_FT_H2O': 2.3067,  # at SG=1, 60°F
    'FT_H2O_TO_PSI': 1/2.3067,
    'LBM_FT3_TO_SG': 1/62.37,  # at 60°F
    'CP_TO_LBM_FT_S': 6.7197e-4,  # 1 cP = 6.7197e-4 lbm/(ft·s)
    'IN_TO_FT': 1/12,
    'MM_TO_FT': 1/304.8,
    'M_TO_FT': 3.28084,
    'G_TO_LBM': 1/453.592,
    'CM_TO_FT': 1/30.48,
}


def get_constant(name: str) -> float:
    """Get an imperial constant by name."""
    return IMPERIAL_CONSTANTS.get(name, None)


if __name__ == '__main__':
    # Self-test: verify conversion accuracy with known reference values
    _p = psi_to_pa(1.0)
    print(f"psi_to_pa(1.0) = {_p:.2f} Pa")
    print(f"ft_h2o_to_psi(33.91) = {ft_h2o_to_psi(33.91):.2f}")
    print(f"hp_to_kw(52.58) = {hp_to_kw(52.58):.2f}")
    print(f"reynolds_imperial(770.5, 6.048, 62, 0.52) = {reynolds_imperial(770.5, 6.048, 62, 0.52):.0f}")
    print(f"Re = {reynolds_si(770.5/448.831, 6.048*0.0254, 62*16.018, 0.52*0.001):.0f}")