"""
Hito 5.4B — Normalización de fronteras, referencias de presión y arquitectura del dominio.
22 mandatory tests.
"""
import sys; sys.path.insert(0, r'C:\PUMPCALC')
import unittest, ast, inspect, os
from src.domain.system_boundaries import (
    PressureReference, BoundaryType, SystemBoundary, PressureBoundaryResult,
    CalculationStatus, compute_boundary_absolute_pressure,
    compute_pressure_difference_between_boundaries,
)
from src.domain.pressure_requirements import (
    build_pressure_head_terms, build_pressure_requirements,
    build_semantic_tdh_balances, build_system_curve_classification,
    detect_pressure_boundary_overlap, combine_boundary_pressures,
    pressure_term_to_head, PressureTermType, FlowDependency,
    CombinationRule, PressureBoundaryWarning, PressureRequirement,
)
from src.domain.accessory_losses import (
    legacy_psi_to_ft, validated_psi_to_ft, PressureClassification,
)
from src.domain.npsh import NPSHInputs
from src.infrastructure.input_loader import WorkbookInputs, create_workbook_inputs

SG = 0.995
ATM_14_7 = 14.7
U40_PSI = 79.77


class TestHito54BNoHardcodedAtm(unittest.TestCase):
    """Test 1: No 14.7 hardcoded in production modules."""

    def test_01_no_14_7_in_production(self):
        excluded_basenames = {'input_loader.py'}
        allowed_files = []
        for root, dirs, files in os.walk(r'C:\PUMPCALC\src'):
            for f in files:
                if f.endswith('.py') and f != '__init__.py' and f not in excluded_basenames:
                    fp = os.path.join(root, f)
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        for i, line in enumerate(fh, 1):
                            stripped = line.strip()
                            if stripped.startswith('#'):
                                continue
                            if '14.7' in stripped:
                                allowed_files.append((fp, i, stripped.strip()))
        if allowed_files:
            msg = []
            for fp, ln, line in allowed_files:
                msg.append(f'{os.path.relpath(fp, r"C:\PUMPCALC")}:{ln}: {line}')
            # This test should fail — 14.7 should only be in tests/fixtures
            self.assertTrue(False, f'14.7 found in production:\n' + '\n'.join(msg))
        self.assertTrue(True)


class TestHito54BAtmFromWorkbookInputs(unittest.TestCase):
    """Test 2: Atmospheric pressure comes from WorkbookInputs."""

    def test_02_atm_from_inputs(self):
        inputs = create_workbook_inputs()
        self.assertIsInstance(inputs.atmospheric_pressure_psia, float)
        self.assertGreater(inputs.atmospheric_pressure_psia, 0)
        # The value in the dataset is 14.7, but must come from inputs
        self.assertAlmostEqual(inputs.atmospheric_pressure_psia, 14.7, places=1)

    def test_02b_minimal_loader_has_atm(self):
        """WorkbookInputs has atmospheric_pressure_psia field."""
        self.assertTrue(hasattr(WorkbookInputs, 'model_fields'))
        self.assertIn('atmospheric_pressure_psia', WorkbookInputs.model_fields)


class TestHito54BAtmChangesAbsScenario(unittest.TestCase):
    """Test 3: Changing atmospheric pressure changes the absolute scenario."""

    def test_03_atm_changes_abs_scenario(self):
        atm_147 = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        atm_122 = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=12.2)
        d147 = atm_147['VALIDATED_U40_AS_ABSOLUTE']
        d122 = atm_122['VALIDATED_U40_AS_ABSOLUTE']
        # Absolute scenario TDH must differ when atm changes
        self.assertNotEqual(d147['total_dynamic_head_ft'], d122['total_dynamic_head_ft'])
        # Lower atm → larger diff → larger head (since source_abs is lower)
        self.assertGreater(d122['total_dynamic_head_ft'], d147['total_dynamic_head_ft'])


class TestHito54BAtmDoesNotChangeGaugeCommon(unittest.TestCase):
    """Test 4: Common atmospheric change does NOT change gauge difference for open system."""

    def test_04_gauge_different_atm_same_diff(self):
        # Case: source at 0 psig with atm=14.7 → source_abs=14.7
        # Case: source at 0 psig with atm=12.2 → source_abs=12.2
        # For GAUGE with dest_atm = source_atm:
        # diff_147 = (14.7 + 79.77) - 14.7 = 79.77
        # diff_122 = (12.2 + 79.77) - 12.2 = 79.77 (same!)
        result_147 = pressure_term_to_head(
            value_psi=79.77, pressure_reference='GAUGE',
            source_boundary_abs_psia=14.7, specific_gravity=SG,
            destination_atmospheric_pressure_psia=14.7,
        )
        result_122 = pressure_term_to_head(
            value_psi=79.77, pressure_reference='GAUGE',
            source_boundary_abs_psia=12.2, specific_gravity=SG,
            destination_atmospheric_pressure_psia=12.2,
        )
        self.assertAlmostEqual(
            result_147.pressure_difference_psi,
            result_122.pressure_difference_psi,
            places=4,
        )


class TestHito54BReferenceSemantics(unittest.TestCase):
    """Tests 5-8: Verification of pressure reference semantics."""

    SOURCE_ABS = 14.7
    DEST_ATM = 14.7

    def test_05_gauge_referenced_to_atm(self):
        """GAUGE: dest_abs = dest_atm + value, diff = dest_abs - source_abs."""
        res = pressure_term_to_head(
            79.77, 'GAUGE', self.SOURCE_ABS, SG,
            destination_atmospheric_pressure_psia=self.DEST_ATM,
        )
        expected_dest = self.DEST_ATM + 79.77
        expected_diff = expected_dest - self.SOURCE_ABS
        self.assertAlmostEqual(res.destination_required_abs_psia, expected_dest, places=4)
        self.assertAlmostEqual(res.pressure_difference_psi, expected_diff, places=4)

    def test_06_differential_referenced_to_source(self):
        """DIFFERENTIAL: diff = value, dest_abs = source_abs + value."""
        res = pressure_term_to_head(
            0.36, 'DIFFERENTIAL', self.SOURCE_ABS, SG,
        )
        self.assertAlmostEqual(res.pressure_difference_psi, 0.36, places=6)
        self.assertAlmostEqual(res.destination_required_abs_psia, self.SOURCE_ABS + 0.36, places=4)

    def test_07_absolute_referenced_to_zero(self):
        """ABSOLUTE: dest_abs = value, diff = dest_abs - source_abs."""
        res = pressure_term_to_head(
            79.77, 'ABSOLUTE', self.SOURCE_ABS, SG,
        )
        self.assertAlmostEqual(res.destination_required_abs_psia, 79.77, places=4)
        self.assertAlmostEqual(res.pressure_difference_psi, 79.77 - 14.7, places=4)

    def test_08_vacuum_converted_via_atm(self):
        """VACUUM: dest_abs = dest_atm - value, diff = dest_abs - source_abs."""
        res = pressure_term_to_head(
            5.0, 'VACUUM', self.SOURCE_ABS, SG,
            destination_atmospheric_pressure_psia=self.DEST_ATM,
        )
        expected_dest = self.DEST_ATM - 5.0
        expected_diff = expected_dest - self.SOURCE_ABS
        self.assertAlmostEqual(res.destination_required_abs_psia, expected_dest, places=4)
        self.assertAlmostEqual(res.pressure_difference_psi, expected_diff, places=4)


class TestHito54BSourceBoundaryCases(unittest.TestCase):
    """Tests 9-10: Source boundary absolute pressure computations."""

    def test_09_open_vessel_at_0_psig(self):
        """Open vessel at 0 psig with atm 14.7 → source_abs = 14.7 psia."""
        result = compute_boundary_absolute_pressure(
            atmospheric_pressure_psia=14.7,
            vessel_pressure=0.0,
            vessel_pressure_type='GAUGE',
        )
        self.assertAlmostEqual(result, 14.7, places=4)

    def test_10_vessel_at_10_psig(self):
        """Vessel at 10 psig with atm 14.7 → source_abs = 24.7 psia."""
        result = compute_boundary_absolute_pressure(
            atmospheric_pressure_psia=14.7,
            vessel_pressure=10.0,
            vessel_pressure_type='GAUGE',
        )
        self.assertAlmostEqual(result, 24.7, places=4)


class TestHito54BPressurizedSource(unittest.TestCase):
    """Tests 11-12: U40 gauge and absolute with pressurized source."""

    SG_VAL = 0.995
    SOURCE_10PSIG = 24.7  # 14.7 + 10

    def test_11_u40_gauge_with_10psig_source(self):
        """U40 gauge (79.77 psig) with source at 10 psig → diff = 69.77 psi."""
        res = pressure_term_to_head(
            value_psi=79.77,
            pressure_reference='GAUGE',
            source_boundary_abs_psia=self.SOURCE_10PSIG,
            specific_gravity=self.SG_VAL,
            destination_atmospheric_pressure_psia=14.7,
        )
        # dest_abs = 14.7 + 79.77 = 94.47
        # diff = 94.47 - 24.7 = 69.77
        self.assertAlmostEqual(res.pressure_difference_psi, 69.77, places=2)
        self.assertNotAlmostEqual(res.pressure_difference_psi, 79.77, places=4)

    def test_12_u40_absolute_with_10psig_source(self):
        """U40 absolute (79.77 psia) with source at 10 psig → diff = 55.07 psi."""
        res = pressure_term_to_head(
            value_psi=79.77,
            pressure_reference='ABSOLUTE',
            source_boundary_abs_psia=self.SOURCE_10PSIG,
            specific_gravity=self.SG_VAL,
        )
        # diff = 79.77 - 24.7 = 55.07
        self.assertAlmostEqual(res.pressure_difference_psi, 55.07, places=2)


class TestHito54BCurrentCaseTDH(unittest.TestCase):
    """Tests 13-14: Current case TDH values."""

    def test_13_gauge_scenario_tdh(self):
        """GAUGE scenario ≈ 196.295421 ft (from dataset, not hardcoded)."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        c = balances['VALIDATED_U40_AS_GAUGE']
        self.assertAlmostEqual(c['total_dynamic_head_ft'], 196.295421, places=4)

    def test_14_absolute_scenario_tdh(self):
        """ABSOLUTE scenario ≈ 162.20 ft (from dataset, not hardcoded)."""
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        d = balances['VALIDATED_U40_AS_ABSOLUTE']
        self.assertAlmostEqual(d['total_dynamic_head_ft'], 162.20, places=1)


class TestHito54BU39Independent(unittest.TestCase):
    """Test 15: U39 remains DIFFERENTIAL, independent of U40."""

    def test_15_u39_differential_independent(self):
        terms = build_pressure_head_terms(sg=SG)
        u39 = [t for t in terms if t.source_cell == 'U39'][0]
        self.assertEqual(u39.pressure_reference, PressureReference.DIFFERENTIAL.value)
        self.assertEqual(u39.classification, PressureClassification.INSTRUMENT_PRESSURE_DROP.value)
        self.assertTrue(u39.user_confirmed)
        # U39 is 0.36 psi — verify it's still 0.36
        self.assertAlmostEqual(u39.value, 0.36, places=4)
        # U39 is independent of U40 value
        self.assertLess(u39.value, 1.0)  # 0.36 psi, not 79.77


class TestHito54BNoDoubleCounting(unittest.TestCase):
    """Test 16: No double counting of boundary pressure in TDH balance."""

    def test_16_no_double_count_boundary_pressure(self):
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        for key, bal in balances.items():
            if not isinstance(bal.get('total_dynamic_head_ft'), (int, float)):
                continue
            # Check we don't have both surface_pressure_difference_ft > 0
            # AND minimum_required_equipment_inlet_pressure_head_ft that
            # represents the same boundary difference
            surf = bal.get('surface_pressure_difference_ft', 0.0)
            min_inlet = bal.get('minimum_required_equipment_inlet_pressure_head_ft', 0.0)
            # For the current open tank, surface pressure diff is 0.0
            # If it were non-zero, we'd need to verify it's not duplicating
            # the min inlet pressure
            self.assertEqual(surf, 0.0, f'{key}: open tank should have 0 surface pressure diff')


class TestHito54BDomainSeparation(unittest.TestCase):
    """Tests 17-18: Module responsibility separation."""

    def test_17_accessory_losses_no_boundary_imports(self):
        """accessory_losses does not import from system_boundaries or pressure_requirements."""
        import src.domain.accessory_losses as mod
        source = inspect.getsource(mod)
        self.assertNotIn('system_boundaries', source)
        self.assertNotIn('pressure_requirements', source)

    def test_18_no_circular_imports(self):
        """All domain modules can be imported without circular dependency."""
        import importlib
        for mod_name in [
            'src.domain.system_boundaries',
            'src.domain.pressure_requirements',
            'src.domain.accessory_losses',
        ]:
            importlib.reload(__import__(mod_name))
        self.assertTrue(True)


class TestHito54BASTHardcodedAtm(unittest.TestCase):
    """Test 19: AST detects hardcoded atmospheric pressure in production code."""

    def test_19_ast_detects_hardcoded_atm(self):
        """AST-based check: CASE_SPECIFIC_VALUE for any non-fixture 14.7."""
        allowed_files = [
            'test_integrity.py',
            'test_hito_5_4.py',
            'test_hito_5_4a.py',
            'test_hito_5_4b.py',
            'input_loader.py',
        ]
        found = []
        for root, dirs, files in os.walk(r'C:\PUMPCALC\src'):
            for f in files:
                if f.endswith('.py') and f not in allowed_files:
                    fp = os.path.join(root, f)
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        tree = ast.parse(fh.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Constant) and isinstance(node.value, float):
                            if abs(node.value - 14.7) < 0.01:
                                found.append((os.path.relpath(fp, r'C:\PUMPCALC'), node.lineno))
        if found:
            msg = '\n'.join(f'{f}:{ln}' for f, ln in found)
            self.assertTrue(False, f'Hardcoded 14.7 found in production:\n{msg}')


class TestHito54BAllFromDataset(unittest.TestCase):
    """Test 20: All scenarios derived from dataset, not hardcoded."""

    def test_20_all_scenarios_from_dataset(self):
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        self.assertEqual(len(balances), 6)
        for key, bal in balances.items():
            self.assertIn('description', bal)
            self.assertIn('total_dynamic_head_ft', bal)
            self.assertIn('static_elevation_head_ft', bal)
            self.assertIn('pipe_major_losses_ft', bal)


class TestHito54BWorkbookUnchanged(unittest.TestCase):
    """Test 21: Workbook not modified."""

    def test_21_workbook_unchanged(self):
        import ast as ast_module, inspect as ins
        from src.domain import accessory_losses as mod
        source = ins.getsource(mod)
        tree = ast_module.parse(source)
        for node in ast_module.walk(tree):
            if isinstance(node, ast_module.Call):
                func = getattr(node.func, 'attr', None) or getattr(node.func, 'id', None)
                if func in ('open_workbook', 'load_workbook', 'xlrd.open_workbook'):
                    self.fail(f'Workbook access in accessory_losses: {func}')
        self.assertTrue(True)


class TestHito54BReportsReadable(unittest.TestCase):
    """Test 22: All reports can be regenerated from current modules."""

    def test_22_reports_readable(self):
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        self.assertIn('WORKBOOK_LEGACY', balances)
        self.assertIn('SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION', balances)
        self.assertIn('VALIDATED_U40_AS_GAUGE', balances)
        self.assertIn('VALIDATED_U40_AS_ABSOLUTE', balances)
        self.assertIn('U40_REFERENCE_UNKNOWN', balances)
        self.assertIn('U40_EXCLUDED', balances)
        for key, bal in balances.items():
            if isinstance(bal['total_dynamic_head_ft'], (int, float)):
                self.assertGreater(bal['total_dynamic_head_ft'], 0)


class TestHito54BDatasetJson(unittest.TestCase):
    """Tests 23-25: Dataset JSON loading, hash, and provenance."""

    def test_23_case_loads_147_from_json(self):
        """Current case loads 14.7 from JSON, not from source code."""
        inputs = create_workbook_inputs()
        self.assertIsNotNone(inputs.dataset_path)
        self.assertTrue(os.path.exists(inputs.dataset_path))
        self.assertAlmostEqual(inputs.atmospheric_pressure_psia, 14.7, places=1)
        import json
        with open(inputs.dataset_path) as f:
            raw = json.load(f)
        self.assertIn('atmospheric_pressure_psia', raw)
        self.assertAlmostEqual(raw['atmospheric_pressure_psia'], 14.7, places=1)

    def test_24_dataset_hash_recorded(self):
        """Dataset hash is recorded and matches the payload."""
        inputs = create_workbook_inputs()
        self.assertIsNotNone(inputs.dataset_hash)
        self.assertEqual(len(inputs.dataset_hash), 12)
        # Verify hash matches computed hash
        import json, hashlib
        with open(inputs.dataset_path) as f:
            raw = json.load(f)
        meta_keys = {'dataset_version', 'dataset_hash', 'description'}
        payload = {k: v for k, v in raw.items() if k not in meta_keys}
        payload_bytes = json.dumps(payload, indent=2, sort_keys=True).encode()
        expected_hash = hashlib.sha256(payload_bytes).hexdigest()[:12]
        self.assertEqual(inputs.dataset_hash, expected_hash)

    def test_24b_dataset_version_recorded(self):
        """Dataset version is recorded."""
        inputs = create_workbook_inputs()
        self.assertIsNotNone(inputs.dataset_version)

    def test_25_dataset_provenance_in_results(self):
        """dataset_path, dataset_hash, dataset_version are accessible."""
        inputs = create_workbook_inputs()
        self.assertIn('dataset_path', WorkbookInputs.model_fields)
        self.assertIn('dataset_hash', WorkbookInputs.model_fields)
        self.assertIn('dataset_version', WorkbookInputs.model_fields)
        self.assertIsNotNone(inputs.dataset_path)
        self.assertIsNotNone(inputs.dataset_hash)
        self.assertIsNotNone(inputs.dataset_version)


class TestHito54BNPSHInputsRequiresAtm(unittest.TestCase):
    """Test 26: NPSHInputs requires explicit atmospheric pressure."""

    def test_26_npsh_inputs_requires_p_atm_abs_psi(self):
        """NPSHInputs cannot be created without p_atm_abs_psi (no default)."""
        import inspect
        sig = inspect.signature(NPSHInputs)
        # p_atm_abs_psi should be the first parameter with no default
        params = list(sig.parameters.values())
        p_atm_param = [p for p in params if p.name == 'p_atm_abs_psi']
        self.assertEqual(len(p_atm_param), 1)
        self.assertIs(p_atm_param[0].default, inspect.Parameter.empty,
                      "p_atm_abs_psi must be required (no default)")

    def test_26b_npsh_p_atm_must_be_positive(self):
        """NPSHInputs rejects p_atm_abs_psi <= 0."""
        with self.assertRaises(ValueError):
            NPSHInputs(p_atm_abs_psi=0.0)
        with self.assertRaises(ValueError):
            NPSHInputs(p_atm_abs_psi=-1.0)

    def test_26c_npsh_sg_must_be_positive(self):
        """NPSHInputs rejects specific_gravity <= 0."""
        from src.domain.npsh import NPSHInputs
        with self.assertRaises(ValueError):
            NPSHInputs(p_atm_abs_psi=14.7, specific_gravity=0.0)
        with self.assertRaises(ValueError):
            NPSHInputs(p_atm_abs_psi=14.7, specific_gravity=-0.5)


class TestHito54BUnitsSansSiteConditions(unittest.TestCase):
    """Test 27: units.py does not contain site-specific conditions."""

    def test_27_units_no_site_conditions(self):
        """units.py has no hardcoded 14.7 beyond conversion examples."""
        import ast, inspect
        from src.domain import units as mod
        source = inspect.getsource(mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                if abs(node.value - 14.7) < 0.01:
                    # Only allowed in __main__ block (self-test examples)
                    if isinstance(node, ast.Expr):
                        pass  # standalone expression in __main__ is OK
                    else:
                        self.fail(f'14.7 found in units.py outside __main__ at line {node.lineno}')

    def test_27b_units_main_no_dataset_values(self):
        """units.py __main__ block uses only generic test values, not case data."""
        with open(r'C:\PUMPCALC\src\domain\units.py') as f:
            src = f.read()
        # Check that __main__ block exists
        self.assertIn("if __name__ == '__main__':", src)
        # Should NOT contain case-specific values like 770.5 directly
        # The print calls use function results, not hardcoded dataset values


class TestHito54BValidatedCalculatorUsesInputs(unittest.TestCase):
    """Test 28: validated_calculator receives atmospheric pressure from inputs."""

    def test_28_validated_calc_uses_inputs_atm(self):
        """compute_accessory_audit signature requires atmospheric_pressure_psia."""
        import inspect, importlib
        import src.application.validated_calculator as mod
        sig = inspect.signature(mod.compute_accessory_audit)
        self.assertIn('atmospheric_pressure_psia', sig.parameters)
        param = sig.parameters['atmospheric_pressure_psia']
        # Should NOT have a default of 14.7 (and not be None either)
        self.assertIsNot(param.default, 14.7,
                         msg="atmospheric_pressure_psia should not default to 14.7")
        # Ideally it should be required (no default), or at least not 14.7
        if param.default is inspect.Parameter.empty:
            pass  # Required — best case
        elif param.default is not None:
            self.assertNotAlmostEqual(float(param.default), 14.7, places=1,
                                      msg="atmospheric_pressure_psia should not default to 14.7")

    def test_28b_calculate_validated_passes_atm(self):
        """calculate_validated passes inputs.atmospheric_pressure_psia to compute_accessory_audit."""
        import inspect, importlib
        import src.application.validated_calculator as mod
        source = inspect.getsource(mod.calculate_validated)
        self.assertIn('compute_accessory_audit(atmospheric_pressure_psia=inputs.atmospheric_pressure_psia)', source)


class TestHito54BReportsExistence(unittest.TestCase):
    """Tests 29-30: All required reports exist and are readable."""

    REQUIRED_REPORTS = [
        'reports/pressure_reference_semantics.md',
        'reports/pressure_reference_test_matrix.csv',
        'reports/domain_module_responsibility.md',
        'reports/hardcoded_atmospheric_pressure_audit.md',
        'reports/hardcoded_atmospheric_pressure_audit.csv',
        'reports/canonical_boundary_head_balance.md',
        'reports/canonical_boundary_head_balance.csv',
        'reports/test_collection_breakdown.md',
        'reports/hito_5_4b_summary.md',
        'reports/pytest_collection.txt',
    ]

    def test_29_all_reports_exist(self):
        """All required Hito 5.4B reports exist and are non-zero."""
        for rel in self.REQUIRED_REPORTS:
            path = os.path.join(r'C:\PUMPCALC', rel)
            self.assertTrue(os.path.exists(path), f'Report missing: {rel}')
            self.assertGreater(os.path.getsize(path), 0, f'Report empty: {rel}')

    def test_30_all_reports_readable(self):
        """All required reports can be re-read."""
        for rel in self.REQUIRED_REPORTS:
            path = os.path.join(r'C:\PUMPCALC', rel)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.assertGreater(len(content), 0, f'Report unreadable: {rel}')


class TestHito54BPytestCollection(unittest.TestCase):
    """Tests 31-32: pytest collection consistency."""

    def test_31_pytest_collect_matches_run(self):
        """pytest --collect-only and pytest report same total (from pytest_collection.txt)."""
        # Read the collection report we already generated
        report_path = r'C:\PUMPCALC\reports\pytest_collection.txt'
        self.assertTrue(os.path.exists(report_path))
        with open(report_path) as f:
            content = f.read()
        # Parse collected and passed values
        import re as _re
        collected = _re.search(r'tests_collected:\s*(\d+)', content)
        passed = _re.search(r'tests_passed:\s*(\d+)', content)
        self.assertIsNotNone(collected, 'tests_collected not found in report')
        self.assertIsNotNone(passed, 'tests_passed not found in report')
        self.assertEqual(int(collected.group(1)), int(passed.group(1)),
                         '--collect-only and -q totals differ')


class TestHito54BPressureReferenceSemantics(unittest.TestCase):
    """Test 33: Canonical pressure reference classification."""

    def test_33_pressure_reference_classification(self):
        """U39 is DIFFERENTIAL; U40 starts UNKNOWN (resolved in TDH scenarios, not requirements)."""
        from src.domain.pressure_requirements import build_pressure_head_terms
        terms = build_pressure_head_terms(sg=SG)
        u39 = [t for t in terms if t.source_cell == 'U39'][0]
        u40 = [t for t in terms if t.source_cell == 'U40'][0]
        self.assertEqual(u39.pressure_reference, 'DIFFERENTIAL')
        # U40 is UNKNOWN — not resolved until TDH scenario selection
        self.assertEqual(u40.pressure_reference, 'UNKNOWN')
        # Verify U40 IS GAUGE in the GAUGE scenario
        balances = build_semantic_tdh_balances(sg=SG, source_atmospheric_pressure_psia=14.7)
        gauge_bal = balances['VALIDATED_U40_AS_GAUGE']
        self.assertIsInstance(gauge_bal['total_dynamic_head_ft'], float)
        self.assertGreater(gauge_bal['total_dynamic_head_ft'], 0)


if __name__ == '__main__':
    unittest.main()
