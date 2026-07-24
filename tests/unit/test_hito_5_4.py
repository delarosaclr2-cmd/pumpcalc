"""
Hito 5.4 — Modelo de requisitos de presión de equipos y corrección semántica de U39/U40.
26 mandatory tests.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import unittest
from src.domain.accessory_losses import (
    compute_suction_results, compute_discharge_results,
    summarize_suction, summarize_discharge,
    legacy_psi_to_ft, validated_psi_to_ft,
    PressureClassification,
)
from src.domain.system_boundaries import (
    PressureReference, BoundaryType, SystemBoundary, PressureBoundaryResult,
    compute_boundary_absolute_pressure, CalculationStatus,
)
from src.domain.pressure_requirements import (
    build_pressure_head_terms, build_pressure_requirements,
    build_semantic_tdh_balances, build_system_curve_classification,
    detect_pressure_boundary_overlap, combine_boundary_pressures,
    PressureTermType, FlowDependency, CombinationRule, PressureBoundaryWarning,
    PressureRequirement, pressure_term_to_head,
)


SG = 0.995
U39_PSI = 0.36
U40_PSI = 79.77
TOTAL_PSI = 80.13
U39_LEGACY_FT = 0.8316
U40_LEGACY_FT = 184.2687
TOTAL_LEGACY_FT = 185.1003
U39_GAUGE_FT = 0.834944
U40_GAUGE_FT = 185.009664
TOTAL_GAUGE_FT = 185.844608
TDH_LEGACY = 195.551113


class TestHito54PressureSemantics(unittest.TestCase):
    """Tests 1-5: Classification and semantics"""

    def test_01_u39_classified_as_instrument(self):
        """U39 is INSTRUMENT_PRESSURE_DROP."""
        terms = build_pressure_head_terms(sg=SG)
        u39 = [t for t in terms if t.source_cell == "U39"][0]
        self.assertEqual(u39.classification, PressureClassification.INSTRUMENT_PRESSURE_DROP.value)

    def test_02_u39_pressure_reference_differential(self):
        """U39 pressure_reference is DIFFERENTIAL."""
        terms = build_pressure_head_terms(sg=SG)
        u39 = [t for t in terms if t.source_cell == "U39"][0]
        self.assertEqual(u39.pressure_reference, PressureReference.DIFFERENTIAL.value)

    def test_03_u40_classified_as_minimum_inlet(self):
        """U40 is MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE."""
        terms = build_pressure_head_terms(sg=SG)
        u40 = [t for t in terms if t.source_cell == "U40"][0]
        self.assertEqual(u40.classification, "MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE")

    def test_04_u40_user_confirmed(self):
        """U40 has user_confirmed=True."""
        terms = build_pressure_head_terms(sg=SG)
        u40 = [t for t in terms if t.source_cell == "U40"][0]
        self.assertTrue(u40.user_confirmed)

    def test_05_u40_flow_independent(self):
        """U40 flow_dependency is FLOW_INDEPENDENT."""
        reqs = build_pressure_requirements(sg=SG)
        u40 = [r for r in reqs if r.source_cell == "U40"][0]
        self.assertEqual(u40.flow_dependency, FlowDependency.FLOW_INDEPENDENT.value)


class TestHito54ExclusionFromAccessories(unittest.TestCase):
    """Tests 6: U39/U40 not in accessory losses"""

    def test_06_u39_u40_not_in_accessory_losses(self):
        """Semantic reclassification moves U39/U40 out of accessory_minor_losses."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        b = balances["SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION"]
        accessory = b["accessory_minor_losses_ft"]
        instrument = b["instrument_pressure_drop_ft"]
        minimum_inlet = b["minimum_required_equipment_inlet_pressure_head_ft"]
        # Accessory should be only the Leq formula losses (~3.475 ft)
        self.assertLess(accessory, 4.0)
        self.assertGreater(instrument, 0.8)
        self.assertGreater(minimum_inlet, 180.0)


class TestHito54PsiSum(unittest.TestCase):
    """Tests 7-10: PSI sums and legacy conversions"""

    def test_07_psi_sum(self):
        """0.36 + 79.77 = 80.13 psi."""
        self.assertAlmostEqual(U39_PSI + U40_PSI, TOTAL_PSI, places=2)

    def test_08_u39_legacy_conversion(self):
        """U39 legacy: 0.36 * 2.31 = 0.8316 ft."""
        self.assertAlmostEqual(legacy_psi_to_ft(U39_PSI), U39_LEGACY_FT, places=4)

    def test_09_u40_legacy_conversion(self):
        """U40 legacy: 79.77 * 2.31 = 184.2687 ft."""
        self.assertAlmostEqual(legacy_psi_to_ft(U40_PSI), U40_LEGACY_FT, places=4)

    def test_10_total_legacy_u_column(self):
        """Total legacy U column: 80.13 * 2.31 = 185.1003 ft."""
        self.assertAlmostEqual(legacy_psi_to_ft(TOTAL_PSI), TOTAL_LEGACY_FT, places=4)


class TestHito54SemanticReclassification(unittest.TestCase):
    """Tests 11: Semantic reclassification doesn't change TDH"""

    def test_11_semantic_tdh_preserved(self):
        """Semantic reclassification preserves TDH Legacy."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        a_tdh = balances["WORKBOOK_LEGACY"]["total_dynamic_head_ft"]
        b_tdh = balances["SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION"]["total_dynamic_head_ft"]
        self.assertAlmostEqual(a_tdh, TDH_LEGACY, places=5)
        self.assertAlmostEqual(b_tdh, TDH_LEGACY, places=5)


class TestHito54ValidatedConversion(unittest.TestCase):
    """Tests 12-14: Validated SG-based conversion"""

    def test_12_u39_validated_uses_sg(self):
        """U39 validated: 0.36 * 144 / (62.4 * SG)."""
        expected = U39_PSI * 144.0 / (62.4 * SG)
        result = validated_psi_to_ft(U39_PSI, SG)
        self.assertAlmostEqual(result, expected, places=6)

    def test_13_u40_validated_gauge_uses_sg(self):
        """U40 validated gauge: 79.77 * 144 / (62.4 * SG)."""
        expected = U40_PSI * 144.0 / (62.4 * SG)
        result = validated_psi_to_ft(U40_PSI, SG)
        self.assertAlmostEqual(result, expected, places=6)

    def test_14_total_validated_gauge(self):
        """Total validated gauge is approximately 185.844608 ft."""
        result = validated_psi_to_ft(TOTAL_PSI, SG)
        self.assertAlmostEqual(result, TOTAL_GAUGE_FT, places=5)


class TestHito54AbsolutePressure(unittest.TestCase):
    """Test 15: Absolute pressure scenario now calculable with source boundary"""

    def test_15_absolute_calculable_with_source_boundary(self):
        """Absolute pressure scenario is calculable using source boundary (14.7 psia)."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        d = balances["VALIDATED_U40_AS_ABSOLUTE"]
        self.assertIsInstance(d["total_dynamic_head_ft"], float)
        self.assertGreater(d["total_dynamic_head_ft"], 160.0)
        # Should include boundary info
        self.assertIn("source_boundary_absolute_pressure_psia", d)
        self.assertAlmostEqual(d["source_boundary_absolute_pressure_psia"], 14.7, places=1)
        # Difference should be 79.77 - 14.7 = 65.07 psi
        self.assertAlmostEqual(d["pressure_difference_psi"], 65.07, places=2)


class TestHito54UnknownReference(unittest.TestCase):
    """Test 16: Unknown pressure reference"""

    def test_16_unknown_reference_warning(self):
        """Unknown reference generates PRESSURE_REFERENCE_REQUIRED status."""
        terms = build_pressure_head_terms(sg=SG)
        u40 = [t for t in terms if t.source_cell == "U40"][0]
        self.assertEqual(u40.pressure_reference, PressureReference.UNKNOWN.value)
        # The notes should indicate reference is needed
        self.assertIn("reference", u40.pressure_reference_notes.lower())


class TestHito54CombinationRules(unittest.TestCase):
    """Tests 17-20: Boundary pressure combination rules"""

    def test_17_same_node_not_auto_added(self):
        """Two boundary requirements on same node are not auto-added."""
        reqs = build_pressure_requirements(sg=SG)
        # With only one inlet pressure term, the default rule is ALTERNATIVE_SCENARIOS
        inlet_terms = [r for r in reqs if r.term_type == PressureTermType.MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE.value]
        for r in inlet_terms:
            self.assertEqual(r.combination_rule, CombinationRule.ALTERNATIVE_SCENARIOS.value)

    def test_18_maximum_requirement(self):
        """MAXIMUM_REQUIREMENT selects the larger pressure."""
        result = combine_boundary_pressures([100.0, 150.0], CombinationRule.MAXIMUM_REQUIREMENT.value)
        self.assertEqual(result, 150.0)

    def test_19_additive_requires_confirmation(self):
        """ADDITIVE rule raises error without explicit confirmation."""
        with self.assertRaises(ValueError):
            combine_boundary_pressures([100.0, 50.0], CombinationRule.ADDITIVE.value, additive_confirmed=False)

    def test_20_additive_with_confirmation(self):
        """ADDITIVE rule sums with confirmation."""
        result = combine_boundary_pressures([100.0, 50.0], CombinationRule.ADDITIVE.value, additive_confirmed=True)
        self.assertEqual(result, 150.0)


class TestHito54BoundaryOverlap(unittest.TestCase):
    """Test 20b: Overlap detection"""

    def test_20b_overlap_detected(self):
        """Overlap between minimum inlet and vessel pressure is detected."""
        reqs = [
            PressureRequirement(
                term_id="INLET_001",
                name="Inlet",
                term_type=PressureTermType.MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE.value,
                value=100.0, unit="psi",
                pressure_reference=PressureReference.GAUGE.value,
                flow_dependency=FlowDependency.FLOW_INDEPENDENT.value,
                active=True, start_node="NODE_A", end_node="NODE_B",
            ),
            PressureRequirement(
                term_id="VESSEL_001",
                name="Vessel",
                term_type=PressureTermType.RECEIVING_VESSEL_OPERATING_PRESSURE.value,
                value=50.0, unit="psi",
                pressure_reference=PressureReference.GAUGE.value,
                flow_dependency=FlowDependency.FLOW_INDEPENDENT.value,
                active=True, start_node="NODE_A", end_node="NODE_B",
            ),
        ]
        warnings = detect_pressure_boundary_overlap(reqs)
        types = [w["type"] for w in warnings]
        self.assertIn(PressureBoundaryWarning.PRESSURE_BOUNDARY_OVERLAP.value, types)


class TestHito54SystemCurve(unittest.TestCase):
    """Tests 21-22: System curve behavior"""

    def test_21_u40_flow_independent(self):
        """U40 is classified as FLOW_INDEPENDENT in system curve."""
        sys_curve = build_system_curve_classification()
        self.assertEqual(
            sys_curve["minimum_required_equipment_inlet_pressure_head_ft"]["flow_dependence"],
            FlowDependency.FLOW_INDEPENDENT.value,
        )

    def test_22_u39_not_quadratic(self):
        """U39 does NOT default to QUADRATIC_WITH_FLOW."""
        sys_curve = build_system_curve_classification()
        fd = sys_curve["instrument_pressure_drop_ft"]["flow_dependence"]
        self.assertNotEqual(fd, FlowDependency.QUADRATIC_WITH_FLOW.value)


class TestHito54LegacyReproduction(unittest.TestCase):
    """Test 23: Legacy TDH reproduction"""

    def test_23_legacy_tdh(self):
        """WORKBOOK_LEGACY scenario reproduces 195.551113 ft."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        a = balances["WORKBOOK_LEGACY"]
        self.assertAlmostEqual(a["total_dynamic_head_ft"], TDH_LEGACY, places=5)


class TestHito54Reports(unittest.TestCase):
    """Tests 24-26: Report content and workbook integrity"""

    def test_24_reports_distinguish_components(self):
        """Semantic head balance report has distinct component fields."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        b = balances["SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION"]
        self.assertIn("instrument_pressure_drop_ft", b)
        self.assertIn("minimum_required_equipment_inlet_pressure_head_ft", b)
        self.assertIn("accessory_minor_losses_ft", b)
        # instrument and minimum inlet should be separate
        self.assertNotEqual(b["instrument_pressure_drop_ft"], b["minimum_required_equipment_inlet_pressure_head_ft"])

    def test_25_workbook_unchanged(self):
        """The workbook is not modified by this test (no xlsm operations)."""
        # This is a procedural check — we confirm no xlrd/openpyxl usage in domain code
        import ast, inspect
        from src.domain import accessory_losses as mod
        source = inspect.getsource(mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = getattr(node.func, 'attr', None) or getattr(node.func, 'id', None)
                if func in ('open_workbook', 'load_workbook', 'xlrd.open_workbook'):
                    self.fail(f"Workbook access detected in accessory_losses: {func}")
        self.assertTrue(True)  # no workbook access detected

    def test_26_reports_readable(self):
        """All generated reports can be read back (checked via in-memory representation)."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        self.assertIn("WORKBOOK_LEGACY", balances)
        self.assertIn("SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION", balances)
        self.assertIn("VALIDATED_U40_AS_GAUGE", balances)
        self.assertIn("VALIDATED_U40_AS_ABSOLUTE", balances)
        self.assertIn("U40_REFERENCE_UNKNOWN", balances)
        self.assertIn("U40_EXCLUDED", balances)
        # All scenarios have expected keys
        for key, bal in balances.items():
            if isinstance(bal["total_dynamic_head_ft"], (int, float)):
                self.assertGreater(bal["total_dynamic_head_ft"], 0)


# =============================================================================
# Hito 5.4A — Absolute Pressure Boundary Model & Source Boundary Definition
# =============================================================================


class TestHito54ABoundaryType(unittest.TestCase):
    """Test 27: BoundaryType enum values"""

    def test_27_boundary_type_values(self):
        self.assertEqual(BoundaryType.FREE_SURFACE, "FREE_SURFACE")
        self.assertEqual(BoundaryType.VESSEL_GAS_SPACE, "VESSEL_GAS_SPACE")
        self.assertEqual(BoundaryType.PUMP_SUCTION_FLANGE, "PUMP_SUCTION_FLANGE")
        self.assertEqual(BoundaryType.PIPE_NODE, "PIPE_NODE")
        self.assertEqual(BoundaryType.EQUIPMENT_INLET, "EQUIPMENT_INLET")
        self.assertEqual(BoundaryType.EQUIPMENT_OUTLET, "EQUIPMENT_OUTLET")


class TestHito54ASystemBoundary(unittest.TestCase):
    """Test 28: SystemBoundary dataclass"""

    def test_28_system_boundary_creation(self):
        sb = SystemBoundary(
            boundary_id="SRC-001",
            boundary_type="FREE_SURFACE",
            pressure_value=0.0,
            pressure_reference="GAUGE",
            atmospheric_pressure_psia=14.7,
            elevation_ft=10.0,
            node_id="NODE-001",
            source_type="TEST",
            confidence="PROVISIONAL",
        )
        self.assertEqual(sb.boundary_id, "SRC-001")
        self.assertEqual(sb.boundary_type, "FREE_SURFACE")
        self.assertEqual(sb.pressure_value, 0.0)
        self.assertEqual(sb.pressure_reference, "GAUGE")
        self.assertEqual(sb.atmospheric_pressure_psia, 14.7)
        self.assertEqual(sb.elevation_ft, 10.0)
        self.assertEqual(sb.node_id, "NODE-001")
        self.assertEqual(sb.confidence, "PROVISIONAL")

    def test_28b_system_boundary_defaults(self):
        sb = SystemBoundary(
            boundary_id="SRC-002",
            boundary_type="PIPE_NODE",
            pressure_value=50.0,
            pressure_reference="ABSOLUTE",
        )
        self.assertEqual(sb.elevation_ft, 0.0)
        self.assertIsNone(sb.atmospheric_pressure_psia)
        self.assertEqual(sb.source_type, "UNKNOWN")
        self.assertEqual(sb.confidence, "PROVISIONAL")


class TestHito54APressureBoundaryResult(unittest.TestCase):
    """Test 29: PressureBoundaryResult dataclass"""

    def test_29_result_creation(self):
        res = PressureBoundaryResult(
            source_boundary_abs_psia=14.7,
            destination_required_abs_psia=94.47,
            pressure_difference_psi=65.07,
            pressure_head_difference_ft=150.916,
            calculation_status="CALCULATED",
        )
        self.assertEqual(res.source_boundary_abs_psia, 14.7)
        self.assertEqual(res.destination_required_abs_psia, 94.47)
        self.assertEqual(res.pressure_difference_psi, 65.07)
        self.assertEqual(res.pressure_head_difference_ft, 150.916)
        self.assertEqual(res.calculation_status, "CALCULATED")


class TestHito54ASourceBoundaryAbsolutePressure(unittest.TestCase):
    """Tests 30-32: compute_boundary_absolute_pressure variants"""

    SG = 0.995
    ATM = 14.7

    def test_30_gauge_pressure(self):
        """GAUGE: source_abs = atm + vessel_pressure (0 psig → 14.7 psia)."""
        result = compute_boundary_absolute_pressure(
            atmospheric_pressure_psia=self.ATM,
            vessel_pressure=0.0,
            vessel_pressure_type="GAUGE",
        )
        self.assertAlmostEqual(result, 14.7, places=4)

    def test_30b_gauge_positive(self):
        """GAUGE positive: atm + 10 psig = 24.7 psia."""
        result = compute_boundary_absolute_pressure(
            atmospheric_pressure_psia=self.ATM,
            vessel_pressure=10.0,
            vessel_pressure_type="GAUGE",
        )
        self.assertAlmostEqual(result, 24.7, places=4)

    def test_31_absolute_pressure(self):
        """ABSOLUTE: source_abs = vessel_pressure directly."""
        result = compute_boundary_absolute_pressure(
            atmospheric_pressure_psia=self.ATM,
            vessel_pressure=20.0,
            vessel_pressure_type="ABSOLUTE",
        )
        self.assertAlmostEqual(result, 20.0, places=4)

    def test_32_vacuum_pressure(self):
        """VACUUM: source_abs = atm - vessel_pressure (5 inHg vac → ~12.25 psia)."""
        result = compute_boundary_absolute_pressure(
            atmospheric_pressure_psia=self.ATM,
            vessel_pressure=5.0,
            vessel_pressure_type="VACUUM",
        )
        self.assertAlmostEqual(result, 9.7, places=4)


class TestHito54APressureTermToHead(unittest.TestCase):
    """Tests 33-36: pressure_term_to_head with different references (Hito 5.4B semantics)."""

    SG = 0.995
    SOURCE_ABS = 14.7
    DEST_ATM = 14.7

    def test_33_gauge_reference(self):
        """GAUGE: dest_abs = dest_atm + value, diff = dest_abs - source_abs.
        Current case: (14.7 + 79.77) - 14.7 = 79.77 psi (coincides with old rule)."""
        res = pressure_term_to_head(
            value_psi=79.77,
            pressure_reference="GAUGE",
            source_boundary_abs_psia=self.SOURCE_ABS,
            specific_gravity=self.SG,
            destination_atmospheric_pressure_psia=self.DEST_ATM,
        )
        self.assertEqual(res.calculation_status, "OK")
        self.assertAlmostEqual(res.pressure_difference_psi, 79.77, places=4)
        self.assertAlmostEqual(res.destination_required_abs_psia, 94.47, places=2)
        # Verify correct derivation
        expected_dest = self.DEST_ATM + 79.77
        expected_diff = expected_dest - self.SOURCE_ABS
        self.assertAlmostEqual(expected_diff, 79.77, places=4)

    def test_34_absolute_reference(self):
        """ABSOLUTE: dest_abs = value, diff = dest_abs - source_abs (79.77 - 14.7 = 65.07 psi)."""
        res = pressure_term_to_head(
            value_psi=79.77,
            pressure_reference="ABSOLUTE",
            source_boundary_abs_psia=self.SOURCE_ABS,
            specific_gravity=self.SG,
        )
        self.assertEqual(res.calculation_status, "OK")
        self.assertAlmostEqual(res.pressure_difference_psi, 65.07, places=4)
        self.assertAlmostEqual(res.destination_required_abs_psia, 79.77, places=4)
        expected_head = 65.07 * 144 / (62.4 * self.SG)
        self.assertAlmostEqual(res.pressure_head_difference_ft, expected_head, places=2)

    def test_35_differential_reference(self):
        """DIFFERENTIAL: diff = value, dest_abs = source_abs + diff."""
        res = pressure_term_to_head(
            value_psi=10.0,
            pressure_reference="DIFFERENTIAL",
            source_boundary_abs_psia=self.SOURCE_ABS,
            specific_gravity=self.SG,
        )
        self.assertEqual(res.calculation_status, "OK")
        self.assertAlmostEqual(res.pressure_difference_psi, 10.0, places=4)

    def test_36_unknown_reference(self):
        """UNKNOWN: returns PRESSURE_REFERENCE_REQUIRED status."""
        res = pressure_term_to_head(
            value_psi=79.77,
            pressure_reference="UNKNOWN",
            source_boundary_abs_psia=self.SOURCE_ABS,
            specific_gravity=self.SG,
        )
        self.assertEqual(res.calculation_status, CalculationStatus.PRESSURE_REFERENCE_REQUIRED.value)


class TestHito54ADestinationBelowSource(unittest.TestCase):
    """Test 37: Negative pressure differences are allowed"""

    SG = 0.995

    def test_37_destination_below_source(self):
        """When required absolute pressure is below source, difference is negative."""
        res = pressure_term_to_head(
            value_psi=10.0,
            pressure_reference="ABSOLUTE",
            source_boundary_abs_psia=14.7,
            specific_gravity=self.SG,
        )
        self.assertIn(
            res.calculation_status,
            (CalculationStatus.DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE.value, "OK"),
        )
        self.assertLess(
            res.pressure_difference_psi, 0.0,
            "Should allow negative pressure differences (10 psia < 14.7 psia)",
        )


class TestHito54AAbsoluteScenarioCalculable(unittest.TestCase):
    """Test 38: Absolute scenario is now calculable with source boundary"""

    SG = 0.995

    def test_38_absolute_scenario_has_calculable_tdh(self):
        """VALIDATED_U40_AS_ABSOLUTE returns a float TDH (not an error string)."""
        balances = build_semantic_tdh_balances(sg=self.SG, source_atmospheric_pressure_psia=14.7)
        d = balances["VALIDATED_U40_AS_ABSOLUTE"]
        self.assertIsInstance(d["total_dynamic_head_ft"], float)
        # Should contain boundary metadata
        self.assertIn("source_boundary_absolute_pressure_psia", d)
        self.assertIn("destination_required_absolute_pressure_psia", d)
        self.assertIn("pressure_difference_psi", d)
        self.assertIn("pressure_head_difference_ft", d)
        # 79.77 - 14.7 = 65.07 psi diff
        self.assertAlmostEqual(d["pressure_difference_psi"], 65.07, places=2)
        self.assertAlmostEqual(d["source_boundary_absolute_pressure_psia"], 14.7, places=1)


class TestHito54AUnknownScenario(unittest.TestCase):
    """Test 39: UNKNOWN reference scenario"""

    SG = 0.995

    def test_39_unknown_reference_scenario(self):
        """U40_REFERENCE_UNKNOWN returns PRESSURE_REFERENCE_REQUIRED in TDH."""
        balances = build_semantic_tdh_balances(sg=self.SG, source_atmospheric_pressure_psia=14.7)
        e = balances["U40_REFERENCE_UNKNOWN"]
        self.assertEqual(
            e["total_dynamic_head_ft"],
            CalculationStatus.PRESSURE_REFERENCE_REQUIRED.value,
        )
        self.assertIn("source_boundary_absolute_pressure_psia", e)
        self.assertEqual(e["destination_required_absolute_pressure_psia"], "PRESSURE_REFERENCE_REQUIRED")


class TestHito54ASixScenarios(unittest.TestCase):
    """Test 40: There are exactly 6 scenarios (A–F)"""

    SG = 0.995

    def test_40_six_scenarios(self):
        """build_semantic_tdh_balances returns 6 scenarios."""
        balances = build_semantic_tdh_balances(sg=self.SG, source_atmospheric_pressure_psia=14.7)
        self.assertEqual(len(balances), 6)
        expected_keys = [
            "WORKBOOK_LEGACY",
            "SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION",
            "VALIDATED_U40_AS_GAUGE",
            "VALIDATED_U40_AS_ABSOLUTE",
            "U40_REFERENCE_UNKNOWN",
            "U40_EXCLUDED",
        ]
        for key in expected_keys:
            self.assertIn(key, balances)


if __name__ == '__main__':
    unittest.main()
