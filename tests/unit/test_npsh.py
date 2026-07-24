"""
Unit tests for NPSH calculations.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import unittest
import math
import warnings as _warnings_module
from src.domain.npsh import (
    NPSHInputs, NPSHMarginResult, calculate_npsha, npsha_legacy,
    evaluate_npsh_margin,
    NPSH_MARGIN_CALCULATED,
    NPSH_MARGIN_NOT_EVALUABLE_MISSING_NPSHR,
    NPSH_MARGIN_NOT_CLASSIFIED_NO_POLICY,
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


class TestNPSHMarginEvaluation(unittest.TestCase):
    """Test NPSH margin evaluation function."""

    def test_margin_calculation(self):
        """Test correct margin calculation with valid inputs."""
        result = evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=20.0)
        self.assertAlmostEqual(result.npsh_margin_ft, 10.0)
        self.assertEqual(result.calculation_status, NPSH_MARGIN_CALCULATED)

    def test_availability_ratio(self):
        """Test correct npsh_availability_ratio calculation."""
        result = evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=20.0)
        self.assertAlmostEqual(result.npsh_availability_ratio, 1.5)

    def test_margin_fraction(self):
        """Test correct npsh_margin_fraction calculation."""
        result = evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=20.0)
        self.assertAlmostEqual(result.npsh_margin_fraction, 0.5)

    def test_missing_npshr(self):
        """Test None NPSHr returns NOT_EVALUABLE_MISSING_NPSHR."""
        result = evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=None)
        self.assertIsNone(result.npsh_margin_ft)
        self.assertIsNone(result.npsh_availability_ratio)
        self.assertIsNone(result.npsh_margin_fraction)
        self.assertEqual(result.calculation_status, NPSH_MARGIN_NOT_EVALUABLE_MISSING_NPSHR)
        self.assertEqual(result.acceptance_status, NPSH_MARGIN_NOT_EVALUABLE_MISSING_NPSHR)
        self.assertTrue(any("NPSHr not provided" in w for w in result.warnings))

    def test_npshr_zero_raises(self):
        """Test NPSHr == 0 raises ValueError."""
        with self.assertRaises(ValueError):
            evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=0.0)

    def test_npshr_negative_raises(self):
        """Test negative NPSHr raises ValueError."""
        with self.assertRaises(ValueError):
            evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=-5.0)

    def test_npshr_nan_raises(self):
        """Test NaN NPSHr raises ValueError."""
        with self.assertRaises(ValueError):
            evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=float('nan'))

    def test_npshr_inf_raises(self):
        """Test infinite NPSHr raises ValueError."""
        with self.assertRaises(ValueError):
            evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=float('inf'))

    def test_npsha_nan_raises(self):
        """Test NaN NPSHa raises ValueError."""
        with self.assertRaises(ValueError):
            evaluate_npsh_margin(npsha_ft=float('nan'), npshr_ft=20.0)

    def test_npsha_inf_raises(self):
        """Test infinite NPSHa raises ValueError."""
        with self.assertRaises(ValueError):
            evaluate_npsh_margin(npsha_ft=float('inf'), npshr_ft=20.0)

    def test_negative_npsha_math_valid(self):
        """Test negative NPSHa still produces valid math with warning."""
        result = evaluate_npsh_margin(npsha_ft=-5.0, npshr_ft=20.0)
        self.assertAlmostEqual(result.npsh_margin_ft, -25.0)
        self.assertAlmostEqual(result.npsh_availability_ratio, -0.25)
        self.assertAlmostEqual(result.npsh_margin_fraction, -1.25)
        self.assertEqual(result.calculation_status, NPSH_MARGIN_CALCULATED)
        self.assertTrue(any("NPSHa is negative" in w for w in result.warnings))

    def test_positive_margin_not_auto_accepted(self):
        """Test positive margin does NOT imply acceptance."""
        result = evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=20.0)
        self.assertEqual(result.acceptance_status, NPSH_MARGIN_NOT_CLASSIFIED_NO_POLICY)

    def test_fields_none_when_npshr_missing(self):
        """Test numeric fields are None when NPSHr is missing."""
        result = evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=None)
        self.assertIsNone(result.npsh_margin_ft)
        self.assertIsNone(result.npsh_availability_ratio)
        self.assertIsNone(result.npsh_margin_fraction)

    def test_existing_calculate_npsha_unchanged(self):
        """Test calculate_npsha() behaviour is preserved."""
        from src.domain.npsh import NPSHInputs
        inputs = NPSHInputs(
            p_atm_abs_psi=14.7,
            p_vessel=0.0,
            p_vessel_type="gauge",
            specific_gravity=1.0,
            vapor_pressure_psi=0.5,
            liquid_surface_elev_ft=10.0,
            pump_centerline_elev_ft=0.0,
            suction_fitting_losses_ft=1.0,
            suction_pipe_losses_ft=2.0,
        )
        result = calculate_npsha(inputs)
        expected_npsha = (14.7 * 2.31 / 1.0) + 10.0 - 1.0 - 2.0 - (0.5 * 2.31 / 1.0)
        self.assertAlmostEqual(result.npsha_ft, expected_npsha)
        self.assertTrue(hasattr(result, 'status'))
        self.assertEqual(result.status, "NPSH_MARGIN_NOT_EVALUABLE")

    def test_no_acceptance_thresholds(self):
        """Test that no acceptance thresholds are defined or implied."""
        result = evaluate_npsh_margin(npsha_ft=30.0, npshr_ft=20.0)
        self.assertEqual(result.acceptance_status, NPSH_MARGIN_NOT_CLASSIFIED_NO_POLICY)
        self.assertNotIn("OK", result.acceptance_status)
        self.assertNotIn("LOW", result.acceptance_status)


class TestNPSHrConversion(unittest.TestCase):
    """Test convert_npshr_to_ft function."""

    def test_meters_to_feet(self):
        """Test conversion from meters to feet (test 1)."""
        from src.domain.npsh import convert_npshr_to_ft
        result = convert_npshr_to_ft(6.0, "m")
        self.assertAlmostEqual(result, 19.68504, places=4)

    def test_feet_identity(self):
        """Test identity when unit is already feet (test 2)."""
        from src.domain.npsh import convert_npshr_to_ft
        result = convert_npshr_to_ft(20.0, "ft")
        self.assertEqual(result, 20.0)

    def test_zero_value_rejected(self):
        """Test zero value raises ValueError (test 3a)."""
        from src.domain.npsh import convert_npshr_to_ft
        with self.assertRaises(ValueError):
            convert_npshr_to_ft(0.0, "m")

    def test_negative_value_rejected(self):
        """Test negative value raises ValueError (test 3b)."""
        from src.domain.npsh import convert_npshr_to_ft
        with self.assertRaises(ValueError):
            convert_npshr_to_ft(-5.0, "m")

    def test_nan_value_rejected(self):
        """Test NaN value raises ValueError (test 3c)."""
        from src.domain.npsh import convert_npshr_to_ft
        with self.assertRaises(ValueError):
            convert_npshr_to_ft(float("nan"), "m")

    def test_inf_value_rejected(self):
        """Test infinite value raises ValueError (test 3d)."""
        from src.domain.npsh import convert_npshr_to_ft
        with self.assertRaises(ValueError):
            convert_npshr_to_ft(float("inf"), "m")

    def test_unknown_unit_rejected(self):
        """Test unknown unit raises ValueError (test 4)."""
        from src.domain.npsh import convert_npshr_to_ft
        with self.assertRaises(ValueError):
            convert_npshr_to_ft(6.0, "cm")


class TestNPSHrReferenceCheck(unittest.TestCase):
    """Test check_npshr_reference_identity function."""

    def test_numerical_match(self):
        """Test all fields match returns MATCHED (test 10)."""
        from src.domain.npsh import check_npshr_reference_identity, NPSHR_REFERENCE_MATCHED
        result = check_npshr_reference_identity(
            operating_flow_gpm=500.0, operating_tdh_ft=100.0,
            operating_speed_rpm=1800.0, operating_impeller_diameter_mm=200.0,
            reference_flow_gpm=500.0, reference_tdh_ft=100.0,
            reference_speed_rpm=1800.0, reference_impeller_diameter_mm=200.0,
        )
        self.assertEqual(result.status, NPSHR_REFERENCE_MATCHED)
        self.assertEqual(result.missing_fields, [])
        self.assertEqual(result.mismatched_fields, [])

    def test_incomplete_reference(self):
        """Test missing reference fields returns INCOMPLETE (test 11)."""
        from src.domain.npsh import check_npshr_reference_identity, NPSHR_REFERENCE_INCOMPLETE
        result = check_npshr_reference_identity(
            operating_flow_gpm=500.0, operating_tdh_ft=100.0,
            operating_speed_rpm=1800.0, operating_impeller_diameter_mm=200.0,
            reference_flow_gpm=None, reference_tdh_ft=100.0,
            reference_speed_rpm=1800.0, reference_impeller_diameter_mm=200.0,
        )
        self.assertEqual(result.status, NPSHR_REFERENCE_INCOMPLETE)
        self.assertIn("reference_flow_gpm", result.missing_fields)

    def test_flow_mismatch(self):
        """Test flow mismatch returns MISMATCH with flow_gpm (test 12)."""
        from src.domain.npsh import check_npshr_reference_identity, NPSHR_REFERENCE_MISMATCH
        result = check_npshr_reference_identity(
            operating_flow_gpm=500.0, operating_tdh_ft=100.0,
            operating_speed_rpm=1800.0, operating_impeller_diameter_mm=200.0,
            reference_flow_gpm=550.0, reference_tdh_ft=100.0,
            reference_speed_rpm=1800.0, reference_impeller_diameter_mm=200.0,
        )
        self.assertEqual(result.status, NPSHR_REFERENCE_MISMATCH)
        self.assertIn("flow_gpm", result.mismatched_fields)

    def test_tdh_mismatch(self):
        """Test TDH mismatch returns MISMATCH with tdh_ft (test 13)."""
        from src.domain.npsh import check_npshr_reference_identity, NPSHR_REFERENCE_MISMATCH
        result = check_npshr_reference_identity(
            operating_flow_gpm=500.0, operating_tdh_ft=100.0,
            operating_speed_rpm=1800.0, operating_impeller_diameter_mm=200.0,
            reference_flow_gpm=500.0, reference_tdh_ft=120.0,
            reference_speed_rpm=1800.0, reference_impeller_diameter_mm=200.0,
        )
        self.assertEqual(result.status, NPSHR_REFERENCE_MISMATCH)
        self.assertIn("tdh_ft", result.mismatched_fields)

    def test_speed_mismatch(self):
        """Test speed mismatch returns MISMATCH with speed_rpm (test 14)."""
        from src.domain.npsh import check_npshr_reference_identity, NPSHR_REFERENCE_MISMATCH
        result = check_npshr_reference_identity(
            operating_flow_gpm=500.0, operating_tdh_ft=100.0,
            operating_speed_rpm=1800.0, operating_impeller_diameter_mm=200.0,
            reference_flow_gpm=500.0, reference_tdh_ft=100.0,
            reference_speed_rpm=1600.0, reference_impeller_diameter_mm=200.0,
        )
        self.assertEqual(result.status, NPSHR_REFERENCE_MISMATCH)
        self.assertIn("speed_rpm", result.mismatched_fields)

    def test_impeller_mismatch(self):
        """Test impeller mismatch returns MISMATCH with impeller_diameter_mm (test 15)."""
        from src.domain.npsh import check_npshr_reference_identity, NPSHR_REFERENCE_MISMATCH
        result = check_npshr_reference_identity(
            operating_flow_gpm=500.0, operating_tdh_ft=100.0,
            operating_speed_rpm=1800.0, operating_impeller_diameter_mm=200.0,
            reference_flow_gpm=500.0, reference_tdh_ft=100.0,
            reference_speed_rpm=1800.0, reference_impeller_diameter_mm=220.0,
        )
        self.assertEqual(result.status, NPSHR_REFERENCE_MISMATCH)
        self.assertIn("impeller_diameter_mm", result.mismatched_fields)

    def test_multiple_mismatches(self):
        """Test multiple mismatches listed together (test 16)."""
        from src.domain.npsh import check_npshr_reference_identity, NPSHR_REFERENCE_MISMATCH
        result = check_npshr_reference_identity(
            operating_flow_gpm=500.0, operating_tdh_ft=100.0,
            operating_speed_rpm=1800.0, operating_impeller_diameter_mm=200.0,
            reference_flow_gpm=550.0, reference_tdh_ft=120.0,
            reference_speed_rpm=1600.0, reference_impeller_diameter_mm=200.0,
        )
        self.assertEqual(result.status, NPSHR_REFERENCE_MISMATCH)
        self.assertIn("flow_gpm", result.mismatched_fields)
        self.assertIn("tdh_ft", result.mismatched_fields)
        self.assertIn("speed_rpm", result.mismatched_fields)
        self.assertNotIn("impeller_diameter_mm", result.mismatched_fields)


class TestNPSHrIntegration(unittest.TestCase):
    """Test NPSHr integration in validated calculation pipeline."""

    def test_pipeline_without_npshr(self):
        """Test pipeline still works when NPSHr is None (test 17)."""
        from src.application.validated_calculator import calculate_validated
        from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance
        inputs = create_synthetic_inputs(npshr=None)
        result = calculate_validated(inputs)
        self.assertIsNone(result.npshr_source_value)
        self.assertIsNone(result.npshr_source_unit)
        self.assertIsNone(result.npshr_ft)
        self.assertIsNone(result.npshr_reference_status)
        self.assertEqual(result.npsh_margin_calculation_status, "NPSH_MARGIN_NOT_EVALUABLE_MISSING_NPSHR")

    def test_pipeline_reference_incomplete(self):
        """Test pipeline blocks margin when reference is incomplete (test 18)."""
        from src.application.validated_calculator import calculate_validated
        from src.domain.npsh import NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_INCOMPLETE
        inputs = create_synthetic_inputs(npshr_incomplete=True, npshr_field="flow_gpm")
        result = calculate_validated(inputs)
        self.assertIsNotNone(result.npshr_ft)
        self.assertEqual(result.npshr_reference_status, "NPSHR_REFERENCE_INCOMPLETE")
        self.assertIsNone(result.npsh_margin_ft)
        self.assertEqual(result.npsh_margin_calculation_status, NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_INCOMPLETE)

    def test_pipeline_reference_mismatch(self):
        """Test pipeline blocks margin when reference mismatches (test 19)."""
        from src.application.validated_calculator import calculate_validated
        from src.domain.npsh import NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_MISMATCH
        inputs = create_synthetic_inputs(npshr_mismatch=True)
        result = calculate_validated(inputs)
        self.assertIsNotNone(result.npshr_ft)
        self.assertEqual(result.npshr_reference_status, "NPSHR_REFERENCE_MISMATCH")
        self.assertIsNone(result.npsh_margin_ft)
        self.assertEqual(result.npsh_margin_calculation_status, NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_MISMATCH)

    def test_pipeline_reference_matched(self):
        """Test pipeline calculates margin when reference matches (test 20)."""
        from src.application.validated_calculator import calculate_validated
        from src.domain.npsh import NPSH_MARGIN_CALCULATED, NPSH_MARGIN_NOT_CLASSIFIED_NO_POLICY
        inputs = create_synthetic_inputs(npshr_match=True)
        result = calculate_validated(inputs)
        self.assertIsNotNone(result.npshr_ft)
        self.assertEqual(result.npshr_reference_status, "NPSHR_REFERENCE_MATCHED")
        self.assertIsNotNone(result.npsh_margin_ft)
        self.assertEqual(result.npsh_margin_calculation_status, NPSH_MARGIN_CALCULATED)

    def test_margin_only_calculated_when_reference_matches(self):
        """Test margin is only calculated when reference matches (test 21)."""
        from src.application.validated_calculator import calculate_validated

        # Without NPSHr
        r1 = calculate_validated(create_synthetic_inputs(npshr=None))
        self.assertIsNone(r1.npsh_margin_ft)

        # With mismatched NPSHr
        r2 = calculate_validated(create_synthetic_inputs(npshr_mismatch=True))
        self.assertIsNone(r2.npsh_margin_ft)

        # With matched NPSHr
        r3 = calculate_validated(create_synthetic_inputs(npshr_match=True))
        self.assertIsNotNone(r3.npsh_margin_ft)

    def test_no_acceptance_classification_in_pipeline(self):
        """Test pipeline never auto-accepts margin (test 22)."""
        from src.application.validated_calculator import calculate_validated
        from src.domain.npsh import NPSH_MARGIN_NOT_CLASSIFIED_NO_POLICY
        inputs = create_synthetic_inputs(npshr_match=True)
        result = calculate_validated(inputs)
        self.assertEqual(result.npsh_margin_acceptance_status, NPSH_MARGIN_NOT_CLASSIFIED_NO_POLICY)

    def test_npsh_margin_status_preserved(self):
        """Test legacy npsh_margin_status is preserved (test 23)."""
        from src.application.validated_calculator import calculate_validated
        from src.domain.npsh import NPSH_MARGIN_NOT_EVALUABLE, NPSH_MARGIN_NOT_EVALUABLE_MISSING_NPSHR

        # Without NPSHr: status should be NPSH_MARGIN_NOT_EVALUABLE (legacy)
        inputs = create_synthetic_inputs(npshr=None)
        result = calculate_validated(inputs)
        self.assertEqual(result.npsh_margin_status, NPSH_MARGIN_NOT_EVALUABLE)

        # With NPSHr matched: should still have NPSH_MARGIN_NOT_EVALUABLE from calculate_npsha
        inputs2 = create_synthetic_inputs(npshr_match=True)
        result2 = calculate_validated(inputs2)
        self.assertEqual(result2.npsh_margin_status, NPSH_MARGIN_NOT_EVALUABLE)

    def test_calculate_npsha_preserved(self):
        """Test calculate_npsha() behaviour preserved (test 24)."""
        from src.domain.npsh import calculate_npsha, NPSHInputs
        inputs = NPSHInputs(
            p_atm_abs_psi=14.7, p_vessel=0.0, p_vessel_type="gauge",
            specific_gravity=1.0, vapor_pressure_psi=0.5,
            liquid_surface_elev_ft=10.0, pump_centerline_elev_ft=0.0,
            suction_fitting_losses_ft=1.0, suction_pipe_losses_ft=2.0,
        )
        result = calculate_npsha(inputs)
        self.assertEqual(result.status, "NPSH_MARGIN_NOT_EVALUABLE")
        self.assertAlmostEqual(result.npsha_ft, (14.7 * 2.31 / 1.0) + 10.0 - 1.0 - 2.0 - (0.5 * 2.31 / 1.0))

    def test_cautious_negative_npsha_warning(self):
        """Test negative NPSHa has cautious warning (test 25)."""
        from src.domain.npsh import evaluate_npsh_margin
        result = evaluate_npsh_margin(npsha_ft=-5.0, npshr_ft=20.0)
        self.assertTrue(any("physical interpretation requires engineering review" in w for w in result.warnings))

    def test_real_case_npshr_converted(self):
        """Test real case loads NPSHr and converts to ft (test 26)."""
        from src.application.validated_calculator import calculate_validated
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        self.assertIsNotNone(inputs.npshr)
        result = calculate_validated(inputs)
        self.assertIsNotNone(result.npshr_source_value)
        self.assertEqual(result.npshr_source_value, inputs.npshr.value)
        self.assertEqual(result.npshr_source_unit, inputs.npshr.unit)
        # Verify conversion matches domain function
        from src.domain.npsh import convert_npshr_to_ft
        expected = convert_npshr_to_ft(inputs.npshr.value, inputs.npshr.unit)
        self.assertAlmostEqual(result.npshr_ft, expected, places=4)

    def test_real_case_blocked_by_mismatch(self):
        """Test real case margin blocked by TDH and speed mismatch (test 27)."""
        from src.application.validated_calculator import calculate_validated
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        result = calculate_validated(inputs)
        self.assertEqual(result.npshr_reference_status, "NPSHR_REFERENCE_MISMATCH")
        self.assertIsNone(result.npsh_margin_ft)
        self.assertIn("tdh_ft", result.npshr_reference_mismatched_fields)

    def test_real_case_margin_fields_none(self):
        """Test real case margin fields are None when blocked (test 28)."""
        from src.application.validated_calculator import calculate_validated
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        result = calculate_validated(inputs)
        self.assertIsNone(result.npsh_margin_ft)
        self.assertIsNone(result.npsh_availability_ratio)
        self.assertIsNone(result.npsh_margin_fraction)

    def test_real_case_npshr_provenance_present(self):
        """Test provenance present in results for real case (test 29)."""
        from src.application.validated_calculator import calculate_validated
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        result = calculate_validated(inputs)
        self.assertIsNotNone(result.npshr_traceability)
        self.assertIn("source_value", result.npshr_traceability)
        self.assertIn("value_provenance", result.npshr_traceability)
        self.assertEqual(result.npshr_traceability["source_value"], getattr(inputs.npshr, "value", None))
        self.assertEqual(result.npshr_traceability["value_provenance"]["source_type"], "WORKBOOK_CELL")


class TestNPSHrModelValidation(unittest.TestCase):
    """Test NPSHrReference and SourceProvenance model validations."""

    def test_old_case_without_npshr_loads(self):
        """Test old JSON without npshr field loads with npshr=None (test 5)."""
        from src.infrastructure.input_loader import WorkbookInputs
        inputs = WorkbookInputs(
            flow_gpm=100.0, density_lbm_ft3=62.0,
            specific_gravity=1.0, dynamic_viscosity_cp=1.0,
            temperature_f=60.0, vapor_pressure_value=0.5,
            vapor_pressure_unit="psia",
            suction_required_diameter_in=6.0,
            suction_nominal_diameter_in=6.0,
            suction_absolute_roughness_ft=0.0001,
            suction_length_ft=10.0, suction_static_head_ft=5.0,
            suction_fitting_losses_ft=0.5,
            discharge_required_diameter_in=4.0,
            discharge_nominal_diameter_in=4.0,
            discharge_absolute_roughness_ft=0.0001,
            discharge_length_ft=50.0, discharge_static_head_ft=20.0,
            discharge_fitting_losses_ft=2.0,
            atmospheric_pressure_psia=14.7,
            pump_efficiency=0.7, pump_rpm=3600.0,
        )
        self.assertIsNone(inputs.npshr)
        self.assertIsNone(inputs.pump_impeller_diameter_mm)

    def test_provenance_required_for_reference_data(self):
        """Test reference data without provenance raises error (test 6/7)."""
        from src.infrastructure.input_loader import NPSHrReference, SourceProvenance
        with self.assertRaises(ValueError):
            NPSHrReference(
                value=6.0, unit="m",
                value_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A1", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
                flow_gpm=500.0,
                flow_provenance=None,
            )

    def test_provenance_without_data_rejected(self):
        """Test provenance without data raises error (test 8)."""
        from src.infrastructure.input_loader import NPSHrReference, SourceProvenance
        with self.assertRaises(ValueError):
            NPSHrReference(
                value=6.0, unit="m",
                value_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A1", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
                flow_gpm=None,
                flow_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A1", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
            )

    def test_provenance_rows_export(self):
        """Test to_provenance_rows includes NPSHr fields (test 9)."""
        from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance, NPSHrReference
        inputs = WorkbookInputs(
            flow_gpm=100.0, density_lbm_ft3=62.0,
            specific_gravity=1.0, dynamic_viscosity_cp=1.0,
            temperature_f=60.0, vapor_pressure_value=0.5,
            vapor_pressure_unit="psia",
            suction_required_diameter_in=6.0,
            suction_nominal_diameter_in=6.0,
            suction_absolute_roughness_ft=0.0001,
            suction_length_ft=10.0, suction_static_head_ft=5.0,
            suction_fitting_losses_ft=0.5,
            discharge_required_diameter_in=4.0,
            discharge_nominal_diameter_in=4.0,
            discharge_absolute_roughness_ft=0.0001,
            discharge_length_ft=50.0, discharge_static_head_ft=20.0,
            discharge_fitting_losses_ft=2.0,
            atmospheric_pressure_psia=14.7,
            pump_efficiency=0.7, pump_rpm=3600.0,
            npshr=NPSHrReference(
                value=6.0, unit="m",
                value_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A1", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
                flow_gpm=500.0,
                flow_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A2", source_type="WORKBOOK_CELL",
                    confidence="MEDIUM",
                ),
                impeller_diameter_mm=200.0,
                impeller_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A3", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
                curve_reference="CV-001",
                curve_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A4", source_type="WORKBOOK_CELL",
                    confidence="MEDIUM",
                ),
            ),
            pump_impeller_diameter_mm=200.0,
            pump_impeller_provenance=SourceProvenance(
                source_workbook="test.xlsm", source_sheet="Sheet1",
                source_location="A3", source_type="WORKBOOK_CELL",
                confidence="HIGH",
            ),
        )
        rows = inputs.to_provenance_rows()
        var_ids = [r["variable_id"] for r in rows]
        self.assertIn("npshr.value", var_ids)
        self.assertIn("npshr.flow_gpm", var_ids)
        self.assertIn("npshr.impeller_diameter_mm", var_ids)
        self.assertIn("npshr.curve_reference", var_ids)
        self.assertIn("pump_impeller_diameter_mm", var_ids)
        # Verify source_type and confidence are separate
        npshr_value_row = [r for r in rows if r["variable_id"] == "npshr.value"][0]
        self.assertEqual(npshr_value_row["source_type"], "WORKBOOK_CELL")
        self.assertEqual(npshr_value_row["confidence"], "HIGH")


class TestNoWorkbookValuesInCode(unittest.TestCase):
    """Test no real workbook values appear in production code or synthetic fixtures (test 30)."""

    def test_no_real_case_values_in_domain_code(self):
        """Test domain code contains no real-case numeric literals."""
        import ast, os
        npsh_path = os.path.join("C:/PUMPCALC", "src", "domain", "npsh.py")
        with open(npsh_path, "r") as f:
            tree = ast.parse(f.read())
        numeric_constants = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                numeric_constants.add(node.value)
        # 6.34 is the real NPSHr from workbook - must not appear in domain code
        self.assertNotIn(6.34, numeric_constants)
        # 190 is real impeller diameter
        self.assertNotIn(190.0, numeric_constants)
        # 3550 and 3600 are RPM values
        self.assertNotIn(3550.0, numeric_constants)

    def test_no_real_case_values_in_synthetic_tests(self):
        """Test synthetic test fixtures do not use real workbook values."""
        inputs = create_synthetic_inputs(npshr_match=True)
        self.assertIsNotNone(inputs.npshr)
        # Confirm pump_rpm is synthetic (1800), not real-case 3600
        self.assertEqual(inputs.pump_rpm, 1800.0)
        self.assertIsNotNone(inputs.pump_impeller_diameter_mm)
        self.assertEqual(inputs.pump_impeller_diameter_mm, 200.0)


def create_synthetic_inputs(
    npshr=None,
    npshr_incomplete=False,
    npshr_field="flow_gpm",
    npshr_mismatch=False,
    npshr_match=False,
    current=False,
):
    """Create synthetic WorkbookInputs for testing.

    Uses only synthetic values, never real workbook data.
    """
    from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance, NPSHrReference

    base = dict(
        flow_gpm=500.0, density_lbm_ft3=62.0,
        specific_gravity=1.0, dynamic_viscosity_cp=1.0,
        temperature_f=60.0, vapor_pressure_value=0.5,
        vapor_pressure_unit="psia",
        suction_required_diameter_in=6.0,
        suction_nominal_diameter_in=6.0,
        suction_absolute_roughness_ft=0.0001,
        suction_length_ft=10.0, suction_static_head_ft=5.0,
        suction_fitting_losses_ft=0.5,
        discharge_required_diameter_in=4.0,
        discharge_nominal_diameter_in=4.0,
        discharge_absolute_roughness_ft=0.0001,
        discharge_length_ft=50.0, discharge_static_head_ft=20.0,
        discharge_fitting_losses_ft=2.0,
        atmospheric_pressure_psia=14.7,
        pump_efficiency=0.7, pump_rpm=1800.0,
    )

    if current:
        from src.infrastructure.input_loader import create_workbook_inputs
        return create_workbook_inputs()

    if npshr_match:
        prov = SourceProvenance(
            source_workbook="synthetic.xlsm", source_sheet="Data",
            source_location="B1", source_type="WORKBOOK_CELL",
            confidence="HIGH",
        )
        # Compute TDH from the base inputs to set reference TDH correctly
        from src.application.validated_calculator import calculate_validated
        base_no_npshr = WorkbookInputs(**base)
        tdh_computed = calculate_validated(base_no_npshr).tdh_ft
        ref = NPSHrReference(
            value=15.0, unit="ft",
            value_provenance=prov,
            flow_gpm=500.0,
            flow_provenance=prov,
            duty_tdh_ft=tdh_computed,
            duty_tdh_provenance=prov,
            speed_rpm=1800.0,
            speed_provenance=prov,
            impeller_diameter_mm=200.0,
            impeller_provenance=prov,
        )
        base.update(dict(
            pump_rpm=1800.0,
            pump_impeller_diameter_mm=200.0,
            pump_impeller_provenance=prov,
            npshr=ref,
        ))
        return WorkbookInputs(**base)

    if npshr_mismatch:
        prov = SourceProvenance(
            source_workbook="synthetic.xlsm", source_sheet="Data",
            source_location="B1", source_type="WORKBOOK_CELL",
            confidence="HIGH",
        )
        ref = NPSHrReference(
            value=15.0, unit="ft",
            value_provenance=prov,
            flow_gpm=500.0,
            flow_provenance=prov,
            duty_tdh_ft=150.0,
            duty_tdh_provenance=prov,
            speed_rpm=1800.0,
            speed_provenance=prov,
            impeller_diameter_mm=200.0,
            impeller_provenance=prov,
        )
        base.update(dict(
            pump_rpm=1800.0,
            pump_impeller_diameter_mm=200.0,
            pump_impeller_provenance=prov,
            npshr=ref,
        ))
        return WorkbookInputs(**base)

    if npshr_incomplete:
        prov = SourceProvenance(
            source_workbook="synthetic.xlsm", source_sheet="Data",
            source_location="B1", source_type="WORKBOOK_CELL",
            confidence="HIGH",
        )
        kwargs = dict(
            value=15.0, unit="ft",
            value_provenance=prov,
        )
        if npshr_field == "flow_gpm":
            kwargs.update(flow_gpm=500.0, flow_provenance=prov)
        elif npshr_field == "tdh":
            kwargs.update(duty_tdh_ft=100.0, duty_tdh_provenance=prov)
        else:
            kwargs.update(speed_rpm=1800.0, speed_provenance=prov)
        ref = NPSHrReference(**kwargs)
        base.update(dict(
            pump_rpm=1800.0,
            npshr=ref,
        ))
        return WorkbookInputs(**base)

    if npshr is None:
        return WorkbookInputs(**base)

    # Default: use the provided npshr object
    base["npshr"] = npshr
    return WorkbookInputs(**base)


class TestSourceProvenanceValidation(unittest.TestCase):
    """Test SourceProvenance validation rules (test 31-33)."""

    def test_non_empty_source_workbook(self):
        """Test source_workbook must not be empty (test 31a)."""
        from src.infrastructure.input_loader import SourceProvenance
        with self.assertRaises(ValueError):
            SourceProvenance(
                source_workbook="", source_location="A1",
                source_type="WORKBOOK_CELL", confidence="HIGH",
            )

    def test_non_empty_source_location(self):
        """Test source_location must not be empty (test 31b)."""
        from src.infrastructure.input_loader import SourceProvenance
        with self.assertRaises(ValueError):
            SourceProvenance(
                source_workbook="test.xlsm", source_location="",
                source_type="WORKBOOK_CELL", confidence="HIGH",
            )

    def test_valid_a1_reference(self):
        """Test valid A1 reference accepted (test 32a)."""
        from src.infrastructure.input_loader import SourceProvenance
        p = SourceProvenance(
            source_workbook="test.xlsm", source_sheet="Sheet1",
            source_location="A1", source_type="WORKBOOK_CELL",
            confidence="HIGH",
        )
        self.assertEqual(p.source_location, "A1")

    def test_valid_a1_range_reference(self):
        """Test valid A1 range reference accepted (test 32b)."""
        from src.infrastructure.input_loader import SourceProvenance
        p = SourceProvenance(
            source_workbook="test.xlsm", source_sheet="Sheet1",
            source_location="A1:B5", source_type="WORKBOOK_CELL",
            confidence="HIGH",
        )
        self.assertEqual(p.source_location, "A1:B5")

    def test_invalid_a1_reference_rejected(self):
        """Test invalid A1 reference raises (test 32c)."""
        from src.infrastructure.input_loader import SourceProvenance
        with self.assertRaises(ValueError):
            SourceProvenance(
                source_workbook="test.xlsm", source_sheet="Sheet1",
                source_location="NOT_A_CELL", source_type="WORKBOOK_CELL",
                confidence="HIGH",
            )

    def test_xfd_column_accepted(self):
        """Test maximum column XFD accepted (test 32d)."""
        from src.infrastructure.input_loader import SourceProvenance
        p = SourceProvenance(
            source_workbook="test.xlsm", source_sheet="Sheet1",
            source_location="XFD1", source_type="WORKBOOK_CELL",
            confidence="HIGH",
        )
        self.assertEqual(p.source_location, "XFD1")

    def test_beyond_xfd_rejected(self):
        """Test column beyond XFD rejected (test 32e)."""
        from src.infrastructure.input_loader import SourceProvenance
        with self.assertRaises(ValueError):
            SourceProvenance(
                source_workbook="test.xlsm", source_sheet="Sheet1",
                source_location="XFE1", source_type="WORKBOOK_CELL",
                confidence="HIGH",
            )

    def test_embedded_image_no_a1_check(self):
        """Test EMBEDDED_CURVE_IMAGE does not require A1 reference (test 32f)."""
        from src.infrastructure.input_loader import SourceProvenance
        p = SourceProvenance(
            source_workbook="test.xlsm", source_sheet="Sheet1",
            source_location="Embedded image image8.png; top-left anchor A64",
            source_type="EMBEDDED_CURVE_IMAGE", confidence="MEDIUM",
        )
        self.assertIn("image8.png", p.source_location)


class TestImpellerSymmetryValidation(unittest.TestCase):
    """Test pump_impeller_diameter_mm symmetry validation (test 34)."""

    def test_symmetry_both_present(self):
        """Test both diameter and provenance present is valid (test 34a)."""
        from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance
        inputs = WorkbookInputs(
            flow_gpm=100.0, density_lbm_ft3=62.0,
            specific_gravity=1.0, dynamic_viscosity_cp=1.0,
            temperature_f=60.0, vapor_pressure_value=0.5,
            vapor_pressure_unit="psia",
            suction_required_diameter_in=6.0,
            suction_nominal_diameter_in=6.0,
            suction_absolute_roughness_ft=0.0001,
            suction_length_ft=10.0, suction_static_head_ft=5.0,
            suction_fitting_losses_ft=0.5,
            discharge_required_diameter_in=4.0,
            discharge_nominal_diameter_in=4.0,
            discharge_absolute_roughness_ft=0.0001,
            discharge_length_ft=50.0, discharge_static_head_ft=20.0,
            discharge_fitting_losses_ft=2.0,
            atmospheric_pressure_psia=14.7,
            pump_efficiency=0.7, pump_rpm=1800.0,
            pump_impeller_diameter_mm=200.0,
            pump_impeller_provenance=SourceProvenance(
                source_workbook="test.xlsm", source_sheet="Sheet1",
                source_location="A1", source_type="WORKBOOK_CELL",
                confidence="HIGH",
            ),
        )
        self.assertEqual(inputs.pump_impeller_diameter_mm, 200.0)

    def test_symmetry_both_absent(self):
        """Test both diameter and provenance absent is valid (test 34b)."""
        from src.infrastructure.input_loader import WorkbookInputs
        inputs = WorkbookInputs(
            flow_gpm=100.0, density_lbm_ft3=62.0,
            specific_gravity=1.0, dynamic_viscosity_cp=1.0,
            temperature_f=60.0, vapor_pressure_value=0.5,
            vapor_pressure_unit="psia",
            suction_required_diameter_in=6.0,
            suction_nominal_diameter_in=6.0,
            suction_absolute_roughness_ft=0.0001,
            suction_length_ft=10.0, suction_static_head_ft=5.0,
            suction_fitting_losses_ft=0.5,
            discharge_required_diameter_in=4.0,
            discharge_nominal_diameter_in=4.0,
            discharge_absolute_roughness_ft=0.0001,
            discharge_length_ft=50.0, discharge_static_head_ft=20.0,
            discharge_fitting_losses_ft=2.0,
            atmospheric_pressure_psia=14.7,
            pump_efficiency=0.7, pump_rpm=1800.0,
        )
        self.assertIsNone(inputs.pump_impeller_diameter_mm)

    def test_symmetry_value_without_provenance_raises(self):
        """Test diameter without provenance raises (test 34c)."""
        from src.infrastructure.input_loader import WorkbookInputs
        with self.assertRaises(ValueError):
            WorkbookInputs(
                flow_gpm=100.0, density_lbm_ft3=62.0,
                specific_gravity=1.0, dynamic_viscosity_cp=1.0,
                temperature_f=60.0, vapor_pressure_value=0.5,
                vapor_pressure_unit="psia",
                suction_required_diameter_in=6.0,
                suction_nominal_diameter_in=6.0,
                suction_absolute_roughness_ft=0.0001,
                suction_length_ft=10.0, suction_static_head_ft=5.0,
                suction_fitting_losses_ft=0.5,
                discharge_required_diameter_in=4.0,
                discharge_nominal_diameter_in=4.0,
                discharge_absolute_roughness_ft=0.0001,
                discharge_length_ft=50.0, discharge_static_head_ft=20.0,
                discharge_fitting_losses_ft=2.0,
                atmospheric_pressure_psia=14.7,
                pump_efficiency=0.7, pump_rpm=1800.0,
                pump_impeller_diameter_mm=200.0,
            )

    def test_symmetry_provenance_without_value_raises(self):
        """Test provenance without diameter raises (test 34d)."""
        from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance
        with self.assertRaises(ValueError):
            WorkbookInputs(
                flow_gpm=100.0, density_lbm_ft3=62.0,
                specific_gravity=1.0, dynamic_viscosity_cp=1.0,
                temperature_f=60.0, vapor_pressure_value=0.5,
                vapor_pressure_unit="psia",
                suction_required_diameter_in=6.0,
                suction_nominal_diameter_in=6.0,
                suction_absolute_roughness_ft=0.0001,
                suction_length_ft=10.0, suction_static_head_ft=5.0,
                suction_fitting_losses_ft=0.5,
                discharge_required_diameter_in=4.0,
                discharge_nominal_diameter_in=4.0,
                discharge_absolute_roughness_ft=0.0001,
                discharge_length_ft=50.0, discharge_static_head_ft=20.0,
                discharge_fitting_losses_ft=2.0,
                atmospheric_pressure_psia=14.7,
                pump_efficiency=0.7, pump_rpm=1800.0,
                pump_impeller_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A1", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
            )


class TestProvenanceRowsExport(unittest.TestCase):
    """Test to_provenance_rows() export completeness (test 35)."""

    def test_rows_have_source_workbook(self):
        """Test every provenance row has source_workbook (test 35a)."""
        from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance, NPSHrReference
        inputs = WorkbookInputs(
            flow_gpm=100.0, density_lbm_ft3=62.0,
            specific_gravity=1.0, dynamic_viscosity_cp=1.0,
            temperature_f=60.0, vapor_pressure_value=0.5,
            vapor_pressure_unit="psia",
            suction_required_diameter_in=6.0,
            suction_nominal_diameter_in=6.0,
            suction_absolute_roughness_ft=0.0001,
            suction_length_ft=10.0, suction_static_head_ft=5.0,
            suction_fitting_losses_ft=0.5,
            discharge_required_diameter_in=4.0,
            discharge_nominal_diameter_in=4.0,
            discharge_absolute_roughness_ft=0.0001,
            discharge_length_ft=50.0, discharge_static_head_ft=20.0,
            discharge_fitting_losses_ft=2.0,
            atmospheric_pressure_psia=14.7,
            pump_efficiency=0.7, pump_rpm=1800.0,
            npshr=NPSHrReference(
                value=15.0, unit="ft",
                value_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="A1", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
            ),
        )
        rows = inputs.to_provenance_rows()
        for row in rows:
            self.assertIn("source_workbook", row,
                          f"Row {row['variable_id']} missing source_workbook")

    def test_embedded_image_cell_is_none(self):
        """Test EMBEDDED_CURVE_IMAGE row has source_cell=None (test 35b)."""
        from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance, NPSHrReference
        inputs = WorkbookInputs(
            flow_gpm=100.0, density_lbm_ft3=62.0,
            specific_gravity=1.0, dynamic_viscosity_cp=1.0,
            temperature_f=60.0, vapor_pressure_value=0.5,
            vapor_pressure_unit="psia",
            suction_required_diameter_in=6.0,
            suction_nominal_diameter_in=6.0,
            suction_absolute_roughness_ft=0.0001,
            suction_length_ft=10.0, suction_static_head_ft=5.0,
            suction_fitting_losses_ft=0.5,
            discharge_required_diameter_in=4.0,
            discharge_nominal_diameter_in=4.0,
            discharge_absolute_roughness_ft=0.0001,
            discharge_length_ft=50.0, discharge_static_head_ft=20.0,
            discharge_fitting_losses_ft=2.0,
            atmospheric_pressure_psia=14.7,
            pump_efficiency=0.7, pump_rpm=1800.0,
            npshr=NPSHrReference(
                value=15.0, unit="ft",
                value_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="Embedded curve image",
                    source_type="EMBEDDED_CURVE_IMAGE",
                    confidence="MEDIUM",
                ),
            ),
        )
        rows = inputs.to_provenance_rows()
        npshr_row = [r for r in rows if r["variable_id"] == "npshr.value"][0]
        self.assertIsNone(npshr_row["source_cell"])
        self.assertIsNotNone(npshr_row["source_location"])

    def test_workbook_cell_has_cell_and_location(self):
        """Test WORKBOOK_CELL row has both source_cell and source_location (test 35c)."""
        from src.infrastructure.input_loader import WorkbookInputs, SourceProvenance, NPSHrReference
        inputs = WorkbookInputs(
            flow_gpm=100.0, density_lbm_ft3=62.0,
            specific_gravity=1.0, dynamic_viscosity_cp=1.0,
            temperature_f=60.0, vapor_pressure_value=0.5,
            vapor_pressure_unit="psia",
            suction_required_diameter_in=6.0,
            suction_nominal_diameter_in=6.0,
            suction_absolute_roughness_ft=0.0001,
            suction_length_ft=10.0, suction_static_head_ft=5.0,
            suction_fitting_losses_ft=0.5,
            discharge_required_diameter_in=4.0,
            discharge_nominal_diameter_in=4.0,
            discharge_absolute_roughness_ft=0.0001,
            discharge_length_ft=50.0, discharge_static_head_ft=20.0,
            discharge_fitting_losses_ft=2.0,
            atmospheric_pressure_psia=14.7,
            pump_efficiency=0.7, pump_rpm=1800.0,
            npshr=NPSHrReference(
                value=15.0, unit="ft",
                value_provenance=SourceProvenance(
                    source_workbook="test.xlsm", source_sheet="Sheet1",
                    source_location="B3", source_type="WORKBOOK_CELL",
                    confidence="HIGH",
                ),
            ),
        )
        rows = inputs.to_provenance_rows()
        npshr_row = [r for r in rows if r["variable_id"] == "npshr.value"][0]
        self.assertEqual(npshr_row["source_cell"], "B3")
        self.assertEqual(npshr_row["source_location"], "B3")


class TestRealCaseCorrectedProvenance(unittest.TestCase):
    """Test real-case corrected provenance (test 36)."""

    def test_speed_provenance_corrected_sheet(self):
        """Test speed provenance points to RESUMEN PARA PDF (test 36a)."""
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        self.assertIsNotNone(inputs.npshr)
        speed_prov = inputs.npshr.speed_provenance
        self.assertIsNotNone(speed_prov)
        self.assertEqual(speed_prov.source_sheet, "RESUMEN PARA PDF")
        self.assertIn("image8.png", speed_prov.source_location)

    def test_speed_provenance_embedded_image_type(self):
        """Test speed provenance source_type is EMBEDDED_CURVE_IMAGE (test 36b)."""
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        self.assertIsNotNone(inputs.npshr)
        speed_prov = inputs.npshr.speed_provenance
        self.assertIsNotNone(speed_prov)
        self.assertEqual(speed_prov.source_type, "EMBEDDED_CURVE_IMAGE")

    def test_curve_reference_stays_as_cell(self):
        """Test curve_reference provenance stays WORKBOOK_CELL on 005PU001 (test 36c)."""
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        self.assertIsNotNone(inputs.npshr)
        curve_prov = inputs.npshr.curve_provenance
        self.assertIsNotNone(curve_prov)
        self.assertEqual(curve_prov.source_type, "WORKBOOK_CELL")
        self.assertEqual(curve_prov.source_sheet, "005PU001")
        self.assertEqual(curve_prov.source_location, "D25")

    def test_npshr_traceability_has_all_fields(self):
        """Test npshr_traceability contains all reference fields (test 36d)."""
        from src.application.validated_calculator import calculate_validated
        from src.infrastructure.input_loader import create_workbook_inputs
        inputs = create_workbook_inputs()
        result = calculate_validated(inputs)
        self.assertIsNotNone(result.npshr_traceability)
        self.assertIn("value_provenance", result.npshr_traceability)
        self.assertIn("flow_gpm", result.npshr_traceability)
        self.assertIn("flow_provenance", result.npshr_traceability)
        self.assertIn("duty_tdh_ft", result.npshr_traceability)
        self.assertIn("duty_tdh_provenance", result.npshr_traceability)
        self.assertIn("speed_rpm", result.npshr_traceability)
        self.assertIn("speed_provenance", result.npshr_traceability)
        self.assertIn("curve_reference", result.npshr_traceability)
        self.assertIn("curve_provenance", result.npshr_traceability)


if __name__ == '__main__':
    unittest.main()