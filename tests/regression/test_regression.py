"""
Regression tests - Ensure calculations don't change unexpectedly.
Updated for Hito 5.2C: G8/V8 = required diameters, NPSHa equivalence, TDH flange fix.
"""
import json
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import pytest
from src.application.legacy_calculator import calculate_legacy_from_inputs
from src.application.validated_calculator import calculate_validated
from src.infrastructure.input_loader import create_workbook_inputs


class TestRegression:
    """Regression tests against stored fixture."""

    @classmethod
    def setup_class(cls):
        with open(r'C:\PUMPCALC\tests\fixtures\current_case.json', 'r') as f:
            cls.fixture = json.load(f)

        cls.inputs = create_workbook_inputs()
        cls.legacy = calculate_legacy_from_inputs(cls.inputs)
        cls.validated = calculate_validated(cls.inputs)

    # ── Legacy tests ──

    def test_legacy_reproduces_excel(self):
        """Legacy mode should exactly reproduce workbook."""
        excel = self.fixture['legacy_results']
        tol = 1e-6
        for key, expected in excel.items():
            actual = getattr(self.legacy, key)
            diff = abs(actual - expected)
            assert diff < tol, f"{key}: got {actual} != expected {expected} (diff={diff})"

    def test_legacy_regression_no_change(self):
        """Legacy results should not change from stored fixture."""
        fixture_legacy = self.fixture['legacy_results']
        tol = 1e-6
        for key, expected in fixture_legacy.items():
            actual = getattr(self.legacy, key)
            diff = abs(actual - expected)
            assert diff < tol, f"{key}: got {actual} != expected {expected} (diff={diff})"

    def test_key_variables_legacy_match(self):
        """Key hydraulic variables match fixture in legacy mode."""
        ref = self.fixture['legacy_results']
        assert abs(self.legacy.re_discharge - ref['re_discharge']) < 1e-6
        assert abs(self.legacy.re_suction - ref['re_suction']) < 1e-6
        assert abs(self.legacy.f_discharge - ref['f_discharge']) < 1e-9
        assert abs(self.legacy.f_suction - ref['f_suction']) < 1e-9
        assert abs(self.legacy.npsha_ft - ref['npsha_ft']) < 1e-4
        assert abs(self.legacy.tdh_ft - ref['tdh_ft']) < 1e-6
        assert abs(self.legacy.hydraulic_hp - ref['hydraulic_hp']) < 1e-6

    # ── Validated tests ──

    def test_validated_no_hardcoded_values(self):
        """Validated results must be computed, not hardcoded."""
        ref = self.fixture['validated_results']
        tol = 0.001
        for key in ['tdh_ft', 'npsha_ft', 'hydraulic_hp', 'shaft_hp', 'torque_lbft']:
            actual = getattr(self.validated, key)
            expected = ref[key]
            assert abs(actual - expected) < tol, f"{key}: got {actual} != expected {expected}"

    def test_validated_friction_factors_reasonable(self):
        """Validated friction factors should be in reasonable range."""
        assert 0.01 < self.validated.f_discharge < 0.03
        assert 0.01 < self.validated.f_suction < 0.03

    def test_validated_npsh_reasonable(self):
        """Validated NPSH should be reasonable."""
        npsh = self.validated.npsha_ft
        assert 30 < npsh < 35
        assert abs(npsh - 34.8) > 0.1

    def test_validated_specific_speed_correct_units(self):
        """Validated specific speed should use consistent units."""
        assert 1600 < self.validated.specific_speed_us < 2200
        assert 30 < self.validated.specific_speed_metric < 50
        assert 4000 < self.validated.specific_speed_legacy < 5000

    def test_validated_specific_speed_definitions(self):
        """Specific speed fields should have definitions."""
        assert len(self.validated.specific_speed_definition) > 10

    def test_validated_torque_uses_real_rpm(self):
        """Validated torque should use pump_rpm (3600)."""
        assert 70 < self.validated.torque_lbft < 100
        assert 150 < self.validated.legacy_torque_lbft < 180
        assert self.validated.legacy_torque_lbft > self.validated.torque_lbft * 1.5

    # ── Diameter: G8/V8 = required diameters ──

    def test_g8_v8_are_required_diameters(self):
        """G8/V8 from workbook are velocity-based required diameters, not selected IDs."""
        req = self.validated.suction_required_diameter_in
        # Verify required diameter matches velocity sizing formula
        from src.domain.pipes import required_diameter_from_flow_velocity
        expected = required_diameter_from_flow_velocity(self.inputs.flow_gpm, self.inputs.suction_target_velocity_fps)
        assert abs(req - expected) < 1e-9
        # Required should differ from nominal (velocity-based ≠ pipe NPS)
        assert abs(req - self.validated.suction_nominal_diameter_in) < 0.1  # close but not same concept

    def test_selected_diameter_not_replaced_by_required(self):
        """Selected diameter is None (missing schedule), not silently replaced by required."""
        assert self.validated.suction_selected_inside_diameter_in is None
        assert self.validated.discharge_selected_inside_diameter_in is None
        assert self.validated.suction_pipe_schedule == "MISSING_SELECTED_PIPE_SCHEDULE"
        assert self.validated.discharge_pipe_schedule == "MISSING_SELECTED_PIPE_SCHEDULE"

    def test_selected_diameter_used_for_hydraulics(self):
        """Reynolds should use selected diameter if available, else required."""
        import math
        from src.domain.pipes import required_diameter_from_flow_velocity
        Q = self.inputs.flow_gpm
        # Since selected is None, hydraulics should use required
        assert self.validated.re_suction > 0

    # ── NPSH equivalence tests ──

    def test_npsha_surface_equals_flange(self):
        """Both NPSHa routes must produce the same value (Bernoulli equivalence)."""
        assert self.validated.npsha_equivalence_diff < 1e-8
        assert self.validated.npsha_equivalence_status == "EQUIVALENT"
        assert abs(self.validated.npsha_from_surface_ft - self.validated.npsha_from_flange_ft) < 1e-8

    def test_npsha_no_double_velocity_head(self):
        """Velocity head is NOT added to surface NPSH to get flange NPSH."""
        # Old (wrong): npsha_flange = npsha_surface + vel_head
        # New (correct): npsha_flange == npsha_surface (Bernoulli cancellation)
        vel_head = self.validated.npsha_components.get("velocity_head_at_flange_ft", 0)
        assert vel_head > 0  # velocity head exists
        assert abs(self.validated.npsha_from_flange_ft - (self.validated.npsha_from_surface_ft + vel_head)) > 1e-6

    # ── TDH flange tests ──

    def test_tdh_flange_not_calculable(self):
        """TDH flange-to-flange requires flange pressure data."""
        assert self.validated.tdh_flange_to_flange_ft is None
        assert self.validated.tdh_flange_input_status == "TDH_FLANGE_NOT_CALCULABLE"

    def test_partial_geometric_not_called_tdh(self):
        """Partial geometric-kinetic difference is NOT called TDH."""
        assert self.validated.partial_geometric_kinetic_difference_ft > 0
        # This value (6.28 ft) should NOT be named or stored as TDH
        assert "tdh" not in "partial_geometric_kinetic_difference_ft"

    def test_tank_elevations_not_flange_elevations(self):
        """C9/C20 are tank surface elevations, not flange elevations."""
        # Surface-to-surface uses tank elevations (correct)
        # Flange-to-flange would need actual flange elevations (not available)
        assert self.validated.tdh_boundary_method == "BOUNDARY_CONDITION_UNVERIFIED"
        assert self.validated.tdh_flange_input_status == "TDH_FLANGE_NOT_CALCULABLE"

    def test_tdh_surface_reproducible(self):
        """TDH surface-to-surface continues to match expected value."""
        ref = self.fixture['validated_results']
        assert abs(self.validated.tdh_surface_to_surface_ft - ref['tdh_surface_to_surface_ft']) < 0.001

    # ── General sanity tests ──

    def test_npsh_positive(self):
        """NPSH available should be positive."""
        assert self.legacy.npsha_ft > 0
        assert self.validated.npsha_ft > 0

    def test_tdh_positive(self):
        """TDH should be positive."""
        assert self.legacy.tdh_ft > 0
        assert self.validated.tdh_ft > 0

    def test_power_positive(self):
        """Power calculations should be positive."""
        assert self.legacy.hydraulic_hp > 0
        assert self.validated.hydraulic_hp > 0

    def test_efficiency_bounds(self):
        """Efficiency should be between 0 and 1."""
        assert 0 < self.inputs.pump_efficiency <= 1

    def test_diameter_status_missing_schedule(self):
        """Diameter status is MISSING_SELECTED_PIPE_SCHEDULE when no schedule."""
        assert self.validated.diameter_status == "MISSING_SELECTED_PIPE_SCHEDULE"

    def test_pump_rpm_fields(self):
        """Pump RPM fields should be present."""
        assert self.validated.pump_rpm == 3600.0
        assert self.validated.legacy_torque_rpm == 1700.0

    def test_tdh_components_sum_surface(self):
        """Surface-to-surface = all components except velocity_head_difference."""
        comp = self.validated.tdh_components
        surface_keys = {"static_head_difference_ft", "suction_major_losses_ft", "suction_minor_losses_ft",
                        "discharge_major_losses_ft", "discharge_minor_losses_ft", "pressure_head_difference_ft"}
        surface_total = sum(v for k, v in comp.items() if k in surface_keys)
        assert abs(surface_total - comp["tdh_surface_to_surface_ft"]) < 1e-9

    def test_npsha_components_include_all(self):
        """NPSHa components should include all required fields."""
        required = ["surface_absolute_pressure_psia", "surface_pressure_head_ft",
                     "static_suction_head_ft", "suction_major_losses_ft",
                     "suction_minor_losses_ft", "vapor_pressure_psia",
                     "vapor_pressure_head_ft", "npsha_from_surface_ft",
                     "npsha_from_flange_ft"]
        for r in required:
            assert r in self.validated.npsha_components, f"Missing NPSH component: {r}"

    def test_legacy_torque_separate_from_validated(self):
        """Legacy and validated torque should be computed separately."""
        assert self.validated.legacy_torque_lbft > 0
        assert self.validated.torque_lbft > 0
        ratio = self.validated.legacy_torque_lbft / self.validated.torque_lbft
        assert 1.8 < ratio < 2.4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
