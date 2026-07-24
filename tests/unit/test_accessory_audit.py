"""
Hito 5.3 - Accessory Loss Audit Tests.
15 mandatory tests across 4 categories.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import unittest
from src.domain.accessory_losses import (
    workbook_loss_ft, standard_leq_loss_ft, k_method_loss_ft,
    compute_suction_results, compute_discharge_results,
    summarize_suction, summarize_discharge,
    detect_double_counting, build_pareto_leq_only, build_pareto_full_discharge, build_scenario_comparisons,
    AccessoryRowResult, SUCCION_VELOCITY, DESCARGA_VELOCITY,
    G_STANDARD, G_WORKBOOK, PSI_TO_FT_H2O, normalize_name, lookup_k_factor,
    CRANE_K_FACTORS, SUCCION_ROWS, DESCARGA_ROWS,
)


# ============================================================================
# Category 1: Formula reconstruction tests (5 tests)
# ============================================================================
class TestFormulaReconstruction(unittest.TestCase):
    """Verify independent reconstruction of the workbook formula."""

    def test_workbook_loss_suction_row6(self):
        """Test suction row 6 with known values."""
        # Valvula de Compuerta 100% Abierta
        # f=0.014, Leq/D=8, V=3.12 ft/s, Q=1
        # Excel: 0.01682488888888889
        result = workbook_loss_ft(0.014, 8, 3.12, 1)
        self.assertAlmostEqual(result, 0.01682488888888889, places=15)

    def test_workbook_loss_discharge_row7(self):
        """Test discharge row 7 with known values."""
        # Valvula de Compuerta 100% Abierta
        # f=0.015, Leq/D=8, V=8.6 ft/s, Q=2
        # Excel: 0.2739259259259259
        result = workbook_loss_ft(0.015, 8, 8.6, 2)
        self.assertAlmostEqual(result, 0.2739259259259259, places=15)

    def test_workbook_loss_discharge_row15(self):
        """Test discharge row 15 (Valvula de angulo de Retencion)."""
        # f=0.015, Leq/D=150, V=8.6 ft/s, Q=1
        # Excel: 2.5680555555555555
        result = workbook_loss_ft(0.015, 150, 8.6, 1)
        self.assertAlmostEqual(result, 2.5680555555555555, places=15)

    def test_workbook_loss_discharge_row39(self):
        """Test discharge row 39 (Codo Soldado 90-deg Radio Largo)."""
        # f=0.015, Leq/D=12, V=8.6 ft/s, Q=3
        # Excel: 0.6163333333333332
        result = workbook_loss_ft(0.015, 12, 8.6, 3)
        self.assertAlmostEqual(result, 0.6163333333333332, places=15)

    def test_g_bias_direction(self):
        """Verify g approximation understates losses."""
        # Standard g=32.174 gives larger loss than workbook g=32.4
        std = standard_leq_loss_ft(0.015, 8, 8.6, 2)
        wb = workbook_loss_ft(0.015, 8, 8.6, 2)
        self.assertGreater(std, wb)
        # Ratio should be 32.4/32.174 ≈ 1.007
        ratio = std / wb
        self.assertAlmostEqual(ratio, G_WORKBOOK / G_STANDARD, places=5)


# ============================================================================
# Category 2: Excel total reconciliation tests (3 tests)
# ============================================================================
class TestTotalReconciliation(unittest.TestCase):
    """Verify our independent totals match Excel exactly."""

    def test_suction_total_matches_c11(self):
        """Suction I40 = SUM(I6:I39) must equal Excel C11 value."""
        results = compute_suction_results()
        summary = summarize_suction(results)
        self.assertAlmostEqual(summary.excel_total_ft, 0.01682488888888889, places=15)
        self.assertEqual(summary.excel_formula, "=SUM(I6:I39)")

    def test_discharge_total_matches_c24(self):
        """Discharge I41 = O41+U41 must equal Excel C24 value."""
        results = compute_discharge_results()
        summary = summarize_discharge(results)
        self.assertAlmostEqual(summary.excel_total_ft, 188.55861481481483, places=12)
        # Pressure share should be ~98.2%
        self.assertGreater(summary.pressure_share_pct, 95.0)

    def test_both_tables_only_active_rows_contributing(self):
        """Verify only rows with non-zero quantity or pressure contribute."""
        suction = compute_suction_results()
        discharge = compute_discharge_results()
        for r in suction:
            if r.workbook_loss_ft > 0:
                self.assertGreater(r.quantity, 0)
        for r in discharge:
            if r.pressure_loss_ft > 0:
                self.assertIsNotNone(r.pressure_psi)


# ============================================================================
# Category 3: Double counting and anomaly detection tests (4 tests)
# ============================================================================
class TestDoubleCountingAndAnomalies(unittest.TestCase):
    """Verify anomaly detection logic."""

    def test_double_counting_detected(self):
        """Row 39 should be flagged for dual entry."""
        discharge = compute_discharge_results()
        findings = detect_double_counting(discharge)
        row39_issues = [f for f in findings if f["row"] == 39]
        self.assertTrue(any("DUAL_ENTRY" in f["issues"] for f in row39_issues))

    def test_zero_quantity_pressure_detected(self):
        """Row 40 should be flagged for zero-quantity pressure."""
        discharge = compute_discharge_results()
        findings = detect_double_counting(discharge)
        row40_issues = [f for f in findings if f["row"] == 40]
        self.assertTrue(any("ZERO_QUANTITY_PRESSURE" in f["issues"] for f in row40_issues))

    def test_pressure_dominates_discharge_pareto(self):
        """Pressure column should dominate discharge total."""
        discharge = compute_discharge_results()
        summary = summarize_discharge(discharge)
        self.assertGreater(summary.total_pressure_loss_ft, 100.0)
        self.assertLess(summary.total_leq_formula_loss_ft, 10.0)

    def test_no_active_rows_in_suction_beyond_row6(self):
        """Only suction row 6 should have non-zero quantity."""
        results = compute_suction_results()
        active = [r for r in results if r.quantity > 0]
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].row, 6)


# ============================================================================
# Category 4: Scenario and method comparison tests (3 tests)
# ============================================================================
class TestScenarioComparison(unittest.TestCase):
    """Verify scenario comparisons produce expected values."""

    def test_legacy_vs_excel_close(self):
        """Legacy hardcoded values should be within 0.01% of Excel."""
        scenarios = build_scenario_comparisons()
        delta = abs(scenarios["LEGACY"]["delta_from_excel_pct"])
        self.assertLess(delta, 0.01)

    def test_leq_formula_only_is_tiny(self):
        """Leq-formula-only scenario should be ~98% less than Excel."""
        scenarios = build_scenario_comparisons()
        delta = scenarios["LEQ_FORMULA_ONLY"]["delta_from_excel_pct"]
        self.assertLess(delta, -95.0)

    def test_pressure_based_dominates(self):
        """Pressure-based scenario should be close to Excel total."""
        scenarios = build_scenario_comparisons()
        delta = abs(scenarios["PRESSURE_BASED"]["delta_from_excel_pct"])
        self.assertLess(delta, 5.0)


# ============================================================================
# Category 5: Edge cases and data integrity tests (5 tests)
# ============================================================================
class TestDataIntegrity(unittest.TestCase):
    """Verify data integrity of the module."""

    def test_all_suction_rows_have_factors(self):
        """Every suction row should have a K factor."""
        results = compute_suction_results()
        for r in results:
            kf = lookup_k_factor(r.name)
            self.assertIsNotNone(kf, f"No K factor for {r.name}")

    def test_all_discharge_rows_have_factors(self):
        """Every discharge row should have a K factor."""
        results = compute_discharge_results()
        for r in results:
            kf = lookup_k_factor(r.name)
            self.assertIsNotNone(kf, f"No K factor for {r.name}")

    def test_suction_velocity_consistent(self):
        """All suction rows use same velocity."""
        results = compute_suction_results()
        velocities = set(r.velocity_fts for r in results)
        self.assertEqual(velocities, {SUCCION_VELOCITY})

    def test_discharge_velocity_consistent(self):
        """All discharge rows use same velocity."""
        results = compute_discharge_results()
        velocities = set(r.velocity_fts for r in results)
        self.assertEqual(velocities, {DESCARGA_VELOCITY})

    def test_pressure_conversion_factor(self):
        """PSI to ft conversion should use 2.31 factor."""
        # 1 PSI = 2.31 ft of water (SG=1.0 approximation)
        self.assertAlmostEqual(PSI_TO_FT_H2O, 2.31, places=2)

    def test_all_methods_leq_over_d(self):
        """All rows should be classified as LEQ_OVER_D method."""
        for r in compute_suction_results():
            self.assertEqual(r.method.value, "LEQ_OVER_D")
        for r in compute_discharge_results():
            self.assertEqual(r.method.value, "LEQ_OVER_D")

    def test_normalize_name(self):
        """Name normalization should work for matching."""
        self.assertEqual(normalize_name("Codo  Soldado 90 (Radio Corto)"),
                         "Codo Soldado 90 Radio Corto")


if __name__ == '__main__':
    unittest.main()
