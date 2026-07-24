"""
Unit tests for NPSH calculations.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import unittest
import math
import warnings as _warnings_module
from src.domain.npsh import (
    NPSHInputs, calculate_npsha, npsha_legacy,
)


# --- Helper functions moved out of npsh.py (previously hardcoded case data) ---

def npsha_from_workbook() -> 'NPSHResult':
    """Reproduce workbook NPSH for regression testing (case-data values)."""
    from src.domain.npsh import calculate_npsha
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
        p_vessel_psi=0.0,
        sg=0.995,
        static_head_ft=1.64,
        suction_fitting_losses_ft=0.0168,
        suction_pipe_losses_ft=0.0261,
        vapor_pressure_ft=1.8457
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


class TestNPSHCalculations(unittest.TestCase):
    """Test NPSH available calculations."""

    def test_legacy_matches_excel(self):
        """Test legacy formula matches Excel exactly."""
        # Excel values: C8=14.7, E8=0, E11=0.995, C9=1.64, C11=0.0168, C14=0.0261, E9=1.846
        # Using 2.31 conversion factor (workbook uses 2.31)
        result = npsha_legacy(
            p_atm_psi=14.7,
            p_vessel_psi=0.0,
            sg=0.995,
            static_head_ft=1.6404199475065617,  # 500/304.8
            suction_fitting_losses_ft=0.0168,
            suction_pipe_losses_ft=0.02610505266548906,
            vapor_pressure_ft=1.845738396624473
        )
        # Excel value: 33.87938980028249
        self.assertAlmostEqual(result, 33.87939, places=4)

    def test_legacy_formula_structure(self):
        """Test legacy formula structure matches workbook."""
        # Formula: ((Patm + Pvessel) * 2.31 / SG) + Hs - Hf_acc - Hf_pipe - Pv
        patm = 14.7
        pvessel = 0.0
        sg = 0.995
        hs = 1.64
        hf_acc = 0.0168
        hf_pipe = 0.0261
        pv = 1.846
        
        manual = ((patm + pvessel) * 2.31 / sg) + hs - hf_acc - hf_pipe - pv
        legacy = npsha_legacy(14.7, 0.0, 0.995, 1.64, 0.0168, 0.0261, 1.846)
        
        self.assertAlmostEqual(manual, legacy, places=10)

    def test_validated_vs_legacy(self):
        """Test validated vs legacy difference."""
        comparison = compare_npsha_legacy_vs_validated()
        
        legacy_npsha = comparison['legacy_npsha_ft']
        validated_npsha = comparison['validated_npsha_ft']
        
        # Validated is slightly LOWER than legacy due to vapor pressure conversion differences
        # Legacy uses table value (1.8457 ft water), validated converts from psi using 2.31/SG
        # The difference is very small (~0.01 ft)
        self.assertLess(validated_npsha, legacy_npsha)
        
        # Difference is very small (~0.01 ft)
        diff = legacy_npsha - validated_npsha
        self.assertAlmostEqual(diff, 0.01, places=2)

    def test_pressure_head_conversion(self):
        """Test pressure to head conversion."""
        # P * 2.31 / SG = head in ft
        p_abs = 14.7  # psia
        sg = 0.995
        head = 14.7 * 2.3067 / 0.995  # Using 2.3067 ft/psi
        expected = 14.7 * 2.3067 / 0.995
        
        # Using 2.31
        head_231 = 14.7 * 2.31 / 0.995
        self.assertAlmostEqual(head_231, 34.12, places=1)

    def test_vapor_pressure_conversion(self):
        """Test vapor pressure head conversion."""
        pv_psi = 0.8  # psia
        sg = 0.995
        
        # In ft water (legacy)
        pv_ft_water = pv_psi * 2.31
        self.assertAlmostEqual(pv_ft_water, 1.848, places=3)
        
        # In ft of fluid (validated)
        pv_ft_fluid = pv_psi * 2.3067 / sg
        self.assertAlmostEqual(pv_ft_fluid, 1.856, places=2)

    def test_pressure_types(self):
        """Test different pressure types (absolute, gauge, vacuum)."""
        from src.domain.npsh import calculate_npsha
        
        # Gauge pressure (standard)
        inputs_gauge = NPSHInputs(
            p_atm_abs_psi=14.7,
            p_vessel=0.0,
            p_vessel_type="gauge",
            specific_gravity=1.0,
            vapor_pressure_psi=0.5,
            liquid_surface_elev_ft=10.0,
            pump_centerline_elev_ft=0.0,
            suction_fitting_losses_ft=1.0,
            suction_pipe_losses_ft=2.0
        )
        result_gauge = calculate_npsha(inputs_gauge)
        
        # Absolute pressure
        inputs_abs = NPSHInputs(
            p_atm_abs_psi=14.7,
            p_vessel=14.7,  # same as atm
            p_vessel_type="absolute",
            specific_gravity=1.0,
            vapor_pressure_psi=0.5,
            liquid_surface_elev_ft=10.0,
            pump_centerline_elev_ft=0.0,
            suction_fitting_losses_ft=1.0,
            suction_pipe_losses_ft=2.0
        )
        result_abs = calculate_npsha(inputs_abs)
        
        # Should be the same when vessel is at atmospheric
        self.assertAlmostEqual(result_gauge.npsha_ft, result_abs.npsha_ft, places=4)

    def test_vacuum_vessel(self):
        """Test vacuum vessel pressure."""
        from src.domain.npsh import calculate_npsha
        
        inputs_vac = NPSHInputs(
            p_atm_abs_psi=14.7,
            p_vessel=5.0,  # 5 psi vacuum
            p_vessel_type="vacuum",
            specific_gravity=1.0,
            vapor_pressure_psi=0.5,
            liquid_surface_elev_ft=10.0,
            pump_centerline_elev_ft=0.0,
            suction_fitting_losses_ft=1.0,
            suction_pipe_losses_ft=2.0
        )
        result = calculate_npsha(inputs_vac)
        
        # Vacuum subtracts from atmospheric: 14.7 - 5.0 = 9.7 psia
        # NPSHa = 9.7 * 2.31 + 10 - 1 - 2 - 0.5*2.31 = 22.4 + 10 - 3 - 1.15 = 28.25 ft
        # Should be reduced compared to no vacuum
        expected_p_surface = 14.7 - 5.0  # 9.7 psia
        self.assertAlmostEqual(result.p_surface_abs_psi, expected_p_surface, places=2)
        # NPSHa should be lower than atmospheric case but still positive
        self.assertGreater(result.npsha_ft, 20.0)
        self.assertLess(result.npsha_ft, 30.0)

    def test_negative_npsha(self):
        """Test case where NPSHa is negative."""
        from src.domain.npsh import calculate_npsha
        
        inputs = NPSHInputs(
            p_atm_abs_psi=14.7,
            p_vessel=0.0,
            p_vessel_type="gauge",
            specific_gravity=1.0,
            vapor_pressure_psi=10.0,  # Very high vapor pressure
            liquid_surface_elev_ft=0.0,
            pump_centerline_elev_ft=20.0,  # Pump well above liquid
            suction_fitting_losses_ft=5.0,
            suction_pipe_losses_ft=10.0
        )
        result = calculate_npsha(inputs)
        
        self.assertLess(result.npsha_ft, 0)
        self.assertIn(result.status, ["NEGATIVE_NPSH", "LOW_NPSH"])


if __name__ == '__main__':
    unittest.main()