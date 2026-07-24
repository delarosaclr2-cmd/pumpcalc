"""
Tolerances for comparison.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class Tolerances:
    """Tolerance definitions for each variable type."""
    
    RELATIVE_TOLERANCES: Dict[str, float] = None
    ABSOLUTE_TOLERANCES: Dict[str, float] = None
    
    def __post_init__(self):
        if self.RELATIVE_TOLERANCES is None:
            self.RELATIVE_TOLERANCES = {
                # Exact conversions (pint-based)
                'conversion': 1e-9,
                
                # Reynolds number
                'reynolds': 0.001,  # 0.1%
                
                # Velocity
                'velocity': 0.001,  # 0.1%
                
                # Friction factor
                'friction_factor': 0.01,  # 1%
                
                # Head losses
                'head_loss': 0.01,  # 1%
                'major_loss': 0.01,
                'minor_loss': 0.01,
                
                # NPSH
                'npsha': 0.01,  # 1%
                
                # TDH
                'tdh': 0.01,  # 1%
                
                # Power
                'hydraulic_power': 0.01,  # 1%
                'shaft_power': 0.01,
                'motor_power': 0.01,
                
                # Torque
                'torque': 0.01,  # 1%
                
                # Specific speed
                'specific_speed': 0.01,  # 1%
                
                # Diameter
                'diameter': 0.001,  # 0.1%
                
                # Pressure
                'pressure': 0.01,
                
                # Flow
                'flow': 0.001,  # 0.1%
            }
        
        if self.ABSOLUTE_TOLERANCES is None:
            self.ABSOLUTE_TOLERANCES = {
                'reynolds': 100,  # 100 Re units
                'velocity': 0.01,  # ft/s
                'head': 0.01,  # ft
                'power': 0.001,  # HP
                'torque': 0.1,  # lb-ft
                'specific_speed': 1,  # Ns units
                'diameter': 0.001,  # in
                'pressure': 0.01,  # psi
            }
    
    def get_tolerance(self, variable_type: str, is_relative: bool = True) -> float:
        """Get tolerance for a variable type."""
        if is_relative:
            return self.RELATIVE_TOLERANCES.get(variable_type, 0.01)
        return self.ABSOLUTE_TOLERANCES.get(variable_type, 0.01)
    
    def check_within_tolerance(self, excel_val: float, calc_val: float, variable_type: str) -> bool:
        """Check if calculated value is within tolerance of Excel value."""
        if excel_val == 0:
            return abs(calc_val) < self.get_tolerance(variable_type, False)
        
        rel_diff = abs(calc_val - excel_val) / abs(excel_val)
        abs_diff = abs(calc_val - excel_val)
        
        rel_tol = self.get_tolerance(variable_type, True)
        abs_tol = self.get_tolerance(variable_type, False)
        
        return rel_diff <= rel_tol or abs_diff <= abs_tol


TOLERANCES = Tolerances()


def get_status(excel_val: float, legacy_val: float, validated_val: float, var_type: str) -> str:
    """Determine comparison status."""
    tol = TOLERANCES
    
    legacy_ok = tol.check_within_tolerance(excel_val, legacy_val, var_type)
    validated_ok = tol.check_within_tolerance(excel_val, validated_val, var_type)
    
    if legacy_ok and validated_ok:
        return "MATCH"
    elif legacy_ok and not validated_ok:
        return "LEGACY_MATCH_ONLY"
    elif not legacy_ok and validated_ok:
        return "VALIDATED_MATCH_ONLY"
    else:
        return "MISMATCH"


if __name__ == '__main__':
    tol = Tolerances()
    print("Tolerance Definitions:")
    print("=" * 60)
    for var, tol_val in tol.RELATIVE_TOLERANCES.items():
        print(f"  {var:<25} {tol_val*100:.2f}%")
    print()
    for var, tol_val in tol.ABSOLUTE_TOLERANCES.items():
        print(f"  {var:<25} {tol_val}")