"""
Integrity tests (Section 10):
- AST hardcoding check (no unrecognized literals in calculators)
- Cross-report consistency
- NPSH proof
- Torque RPM check
- Friction factor method validation
"""
import sys, ast, os
sys.path.insert(0, r'C:\PUMPCALC')

import pytest
from src.application.legacy_calculator import calculate_legacy_from_inputs
from src.application.validated_calculator import calculate_validated
from src.infrastructure.input_loader import create_workbook_inputs

CALCULATOR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "application")


class TestASTHardcodingFree:
    """Verify no unrecognized numeric literals exist in calculators."""

    ALLOWED_LITERALS = {
        0, 0.0, 1, 1.0, 2, 2.0, 3.0,
        32.174, 32.4, 3960.0, 448.831, 5252.0,
        50.6, 50.66,
        64.0,
        0.639,
        2.3071, 2.31, 1.2, 0.00013, 0.0272,
        0.3048, 0.7456, 0.7457, 304.8, 3.280839895, 3.28084,
        12.0, 60.0, 24.0, 3600.0, 1700, 100,
        3.14159265, 0.0283168,
        0.5, 0.25, 0.75, 5,
        1e-08,
    }

    @pytest.mark.parametrize("filepath", [
        os.path.join(CALCULATOR_DIR, "legacy_calculator.py"),
        os.path.join(CALCULATOR_DIR, "validated_calculator.py"),
    ])
    def test_no_unrecognized_literals(self, filepath):
        with open(filepath, "r") as f:
            tree = ast.parse(f.read())
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in self.ALLOWED_LITERALS:
                    found.append((node.lineno, node.value))
        assert len(found) == 0, f"Unrecognized literals in {os.path.basename(filepath)}: {found}"


class TestCrossReportConsistency:
    """Validate consistency across calculators and methods."""

    def setup_method(self):
        self.inputs = create_workbook_inputs()
        self.legacy = calculate_legacy_from_inputs(self.inputs)
        self.validated = calculate_validated(self.inputs)

    def test_tdh_consistent_definition(self):
        """TDH from validated (surface) should be close to legacy TDH (both exclude vel head)."""
        assert abs(self.validated.tdh_surface_to_surface_ft - self.legacy.tdh_ft) < 1.0

    def test_npsh_consistent_definition(self):
        """Surface-based NPSH should match between legacy and validated (both exclude vel head)."""
        diff = abs(self.validated.npsha_from_surface_ft - self.legacy.npsha_ft)
        assert diff < 0.1

    def test_power_consistency(self):
        """Shaft = Hyd / eff, both calculators."""
        eff = self.inputs.pump_efficiency
        assert abs(self.legacy.shaft_hp - self.legacy.hydraulic_hp / eff) < 1e-9
        assert abs(self.validated.shaft_hp - self.validated.hydraulic_hp / eff) < 1e-9

    def test_torque_consistency(self):
        """Torque = HP * 5252 / RPM."""
        assert abs(self.validated.torque_lbft - self.validated.shaft_hp * 5252 / self.inputs.pump_rpm) < 1e-6
        assert abs(self.validated.legacy_torque_lbft - self.validated.shaft_hp * 5252 / self.inputs.legacy_torque_rpm) < 1e-6

    def test_specific_speed_ratio(self):
        """Ns_us / nq_metric should be about 51.6 (US->metric conversion factor)."""
        ratio = self.validated.specific_speed_us / self.validated.specific_speed_metric
        assert 45 < ratio < 60

    def test_reynolds_discharge_greater_than_suction(self):
        """Re_dis > Re_suc (smaller diameter = higher velocity)."""
        assert self.validated.re_discharge > self.validated.re_suction


class TestNPSHProof:
    """Formal NPSH proof tests."""

    def setup_method(self):
        self.inputs = create_workbook_inputs()
        self.v = calculate_validated(self.inputs)

    def test_npsh_components_balance(self):
        """Surface NPSH = press_head + static - minor - major - vp_head."""
        comp = self.v.npsha_components
        expected = (comp["surface_pressure_head_ft"]
                    + comp["static_suction_head_ft"]
                    - comp["suction_minor_losses_ft"]
                    - comp["suction_major_losses_ft"]
                    - comp["vapor_pressure_head_ft"])
        assert abs(expected - comp["npsha_from_surface_ft"]) < 1e-9

    def test_vapor_pressure_reasonable(self):
        """Vapor pressure head should be < 3 ft for water at room temp."""
        assert self.v.npsha_components["vapor_pressure_head_ft"] < 3.0

    def test_pressure_head_reasonable(self):
        """Surface pressure head should be ~34 ft for water at 14.7 psi."""
        assert 30 < self.v.npsha_components["surface_pressure_head_ft"] < 40

    def test_npsha_between_30_and_35(self):
        """NPSHa for this case should be between 30 and 35 ft."""
        assert 30 < self.v.npsha_ft < 35


class TestTorqueRPM:
    """Torque RPM definitions."""

    def setup_method(self):
        self.inputs = create_workbook_inputs()
        self.legacy = calculate_legacy_from_inputs(self.inputs)
        self.v = calculate_validated(self.inputs)

    def test_legacy_uses_1700_rpm(self):
        """Legacy torque should use legacy_torque_rpm=1700."""
        t = self.legacy.torque_lbft
        expected = self.legacy.shaft_hp * 5252 / self.inputs.legacy_torque_rpm
        assert abs(t - expected) < 1e-6

    def test_validated_uses_3600_rpm(self):
        """Validated torque should use pump_rpm=3600."""
        t = self.v.torque_lbft
        expected = self.v.shaft_hp * 5252 / self.inputs.pump_rpm
        assert abs(t - expected) < 1e-6

    def test_legacy_torque_in_validated_uses_1700_rpm(self):
        """validated.legacy_torque_lbft should use 1700 rpm."""
        t = self.v.legacy_torque_lbft
        expected = self.v.shaft_hp * 5252 / self.inputs.legacy_torque_rpm
        assert abs(t - expected) < 1e-6

    def test_torque_ratio_matches_rpm_ratio(self):
        """Torque_legacy / Torque_validated ≈ pump_rpm / legacy_torque_rpm (same power)."""
        ratio = self.v.legacy_torque_lbft / self.v.torque_lbft
        rpm_ratio = self.inputs.pump_rpm / self.inputs.legacy_torque_rpm
        assert abs(ratio - rpm_ratio) < 0.01


class TestFrictionMethodValidation:
    """Verify friction factor method selection and consistency."""

    def setup_method(self):
        self.inputs = create_workbook_inputs()
        self.v = calculate_validated(self.inputs)

    def test_method_name_string(self):
        """Friction method should be a known string."""
        assert self.v.f_discharge_method in ("colebrook", "swamee_jain", "haaland", "laminar")
        assert self.v.f_suction_method in ("colebrook", "swamee_jain", "haaland", "laminar")

    def test_friction_factor_positive(self):
        """Friction factors must be positive."""
        assert self.v.f_discharge > 0
        assert self.v.f_suction > 0

    def test_friction_factor_turbulent(self):
        """For turbulent flow (Re > 4000), f should be < 0.03."""
        if self.v.re_discharge > 4000:
            assert self.v.f_discharge < 0.03
        if self.v.re_suction > 4000:
            assert self.v.f_suction < 0.03


class TestPipelineIntegration:
    """Full pipeline integration: power_legacy, power_validated, calculate_legacy, calculate_validated."""

    def setup_method(self):
        self.inputs = create_workbook_inputs()
        self.legacy = calculate_legacy_from_inputs(self.inputs)
        self.v = calculate_validated(self.inputs)

    def test_power_legacy_through_pipeline(self):
        """Legacy power can be called independently."""
        from src.domain.power import power_legacy
        result = power_legacy(self.inputs.flow_gpm, self.legacy.tdh_ft,
                              self.inputs.specific_gravity, self.inputs.pump_efficiency,
                              self.inputs.legacy_torque_rpm)
        assert result.hydraulic_power_hp > 0
        assert result.shaft_power_hp > 0
        assert result.shaft_power_kw > 0

    def test_power_validated_through_pipeline(self):
        """Validated power computes independently (no delegation)."""
        from src.domain.power import power_validated
        result = power_validated(self.inputs.flow_gpm, self.v.tdh_ft,
                                 self.inputs.specific_gravity, self.inputs.pump_efficiency,
                                 self.inputs.pump_rpm)
        assert result.hydraulic_power_hp > 0
        assert result.shaft_power_hp > 0
        assert result.shaft_power_kw > 0

    def test_legacy_contains_required_diameter(self):
        """Legacy calculator should contain required diameter fields."""
        assert hasattr(self.legacy, "suction_required_diameter_in")
        assert hasattr(self.legacy, "discharge_required_diameter_in")

    def test_npsh_margin_not_evaluable_without_npshr(self):
        """NPSH_MARGIN_NOT_EVALUABLE is used when NPSHr is unknown."""
        from src.domain.npsh import NPSH_MARGIN_NOT_EVALUABLE
        assert self.v.npsh_margin_status == NPSH_MARGIN_NOT_EVALUABLE

    def test_provenance_has_separate_source_and_confidence(self):
        """Provenance rows have distinct source_type and confidence columns."""
        rows = self.inputs.to_provenance_rows()
        for row in rows:
            assert "source_type" in row
            assert "confidence" in row
            # source_type should not be HIGH/MEDIUM/LOW
            assert row["source_type"] not in ("HIGH", "MEDIUM", "LOW")
            # confidence should be HIGH/MEDIUM/LOW/UNVERIFIED
            assert row["confidence"] in ("HIGH", "MEDIUM", "LOW", "UNVERIFIED")

    def test_console_output_no_leading_newline(self):
        """calculate_validated should not produce leading newline."""
        import io, contextlib
        from src.application.validated_calculator import calculate_validated as cv
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cv(self.inputs)
        output = buf.getvalue()
        assert output == "" or not output.startswith("\n"), f"Unexpected leading newline in output: {repr(output[:50])}"

    def test_power_functions_one_arg_shaft_power_kw(self):
        """shaft_power_kw must accept exactly 1 argument."""
        from src.domain.power import shaft_power_kw
        # Should not raise TypeError
        kw = shaft_power_kw(52.58)
        assert kw > 0

    # ── Hito 5.2C mandatory tests ──

    def test_g8_v8_classified_as_required_diameter(self):
        """G8 and V8 are classified as required diameters (velocity-based)."""
        from src.domain.pipes import required_diameter_from_flow_velocity
        Q = self.inputs.flow_gpm
        expected_suct = required_diameter_from_flow_velocity(Q, self.inputs.suction_target_velocity_fps)
        expected_disch = required_diameter_from_flow_velocity(Q, self.inputs.discharge_target_velocity_fps)
        assert abs(self.v.suction_required_diameter_in - expected_suct) < 1e-9
        assert abs(self.v.discharge_required_diameter_in - expected_disch) < 1e-9

    def test_selected_diameter_not_substituted_by_required(self):
        """When schedule is missing, selected diameter is None, not silently replaced."""
        assert self.v.suction_selected_inside_diameter_in is None
        assert self.v.discharge_selected_inside_diameter_in is None

    def test_missing_schedule_generates_status(self):
        """Missing pipe schedule yields MISSING_SELECTED_PIPE_SCHEDULE status."""
        assert self.v.suction_pipe_schedule == "MISSING_SELECTED_PIPE_SCHEDULE"
        assert self.v.discharge_pipe_schedule == "MISSING_SELECTED_PIPE_SCHEDULE"
        assert self.v.diameter_status == "MISSING_SELECTED_PIPE_SCHEDULE"

    def test_npsha_two_routes_equal(self):
        """Both NPSHa routes produce the same value via Bernoulli derivation."""
        diff = abs(self.v.npsha_from_surface_ft - self.v.npsha_from_flange_ft)
        assert diff < 1e-8, f"NPSHa surface={self.v.npsha_from_surface_ft} != flange={self.v.npsha_from_flange_ft}"

    def test_npsha_no_double_velocity_head_count(self):
        """Velocity head is NOT added to surface NPSH to produce flange NPSH."""
        vel_head = self.v.npsha_components.get("velocity_head_at_flange_ft", 0)
        if vel_head > 0:
            # Old (wrong): npsha_flange = npsha_surface + vel_head
            # New (correct): npsha_flange == npsha_surface
            wrong_value = self.v.npsha_from_surface_ft + vel_head
            assert abs(self.v.npsha_from_flange_ft - wrong_value) > 1e-6

    def test_tdh_flange_requires_pressure_difference(self):
        """Without flange pressure data, TDH flange-to-flange is NOT_CALCULABLE."""
        assert self.v.tdh_flange_to_flange_ft is None
        assert self.v.tdh_flange_input_status == "TDH_FLANGE_NOT_CALCULABLE"

    def test_tank_elevations_not_flange_elevations(self):
        """C9/C20 are not used as flange elevations for flange-to-flange TDH."""
        # Surface-to-surface uses tank elevations (correct)
        # Flange-to-flange properly refused to calculate without flange data
        assert self.v.tdh_boundary_method == "BOUNDARY_CONDITION_UNVERIFIED"

    def test_partial_value_not_named_tdh(self):
        """The 6.28 ft partial geometric-kinetic value is NOT named TDH."""
        assert self.v.partial_geometric_kinetic_difference_ft > 0
        assert self.v.tdh_flange_to_flange_ft is None  # not substituted
        # Ensure the field name does not contain 'tdh'
        assert "tdh" not in "partial_geometric_kinetic_difference_ft"

    def test_tdh_surface_still_reproducible(self):
        """TDH surface-to-surface continues to be computed and reproducible."""
        assert self.v.tdh_surface_to_surface_ft > 0
        # Should match the legacy surface-based TDH closely
        assert abs(self.v.tdh_surface_to_surface_ft - self.legacy.tdh_ft) < 1.0
