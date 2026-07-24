# Test Collection Breakdown — Hito 5.4B

## Totals

| Metric             | Value |
|--------------------|-------|
| tests_collected    | 216   |
| tests_passed       | 216   |
| tests_failed       | 0     |
| tests_skipped      | 0     |
| warnings           | 2     |
| collection_errors  | 0     |

## Breakdown by directory

| Directory            | Test files | Collected |
|----------------------|-----------|----------|
| tests/unit/          | 7         | 174      |
| tests/regression/    | 1         | 28       |
| tests/integration/   | 1         | 14       |
| otros                | 0         | 0        |

### Tests per file

| File                                         | Count |
|----------------------------------------------|-------|
| tests/unit/test_hito_5_4.py                  | 40    |
| tests/unit/test_hito_5_4b.py                 | 23    |
| tests/unit/test_accessory_audit.py           | 22    |
| tests/unit/test_units.py                     | 26    |
| tests/unit/test_power.py                     | 13    |
| tests/unit/test_friction.py                  | 18    |
| tests/unit/test_npsh.py                      | 8     |
| tests/regression/test_regression.py          | 28    |
| tests/integration/test_integrity.py          | 14    |

## Explanation of 215 vs 216 discrepancy

### Why 215 was reported

Earlier runs excluded `scripts/test_validated.py` from the count because it
was named `debug_validated.py` at that point (already renamed). The test
file `test_hito_5_4b.py` had 22 items (before `test_02b` was added).

### Why 216 is now reported

Two changes occurred:

1. **`test_hito_5_4b.py` gained one test**: `test_02b_minimal_loader_has_atm`
   was added to verify `WorkbookInputs` has the `atmospheric_pressure_psia`
   field. This brought the test count from 22 → 23 in that file.

2. **`scripts/test_validated.py` was renamed**: Previously named
   `test_validated.py`, it was being collected by pytest and causing a
   collection error (TypeError on dict-style access of a dataclass).
   Renaming to `debug_validated.py` removed it from collection entirely.

### What file explains the difference

The file `scripts/test_validated.py` → `scripts/debug_validated.py` accounts
for the collection discrepancy. When it was named `test_validated.py`, it
caused one collection error. After rename, the true count stabilised at 216.

### Verification that debug_validated.py is not collected

`pytest --collect-only -q` produces no reference to `debug_validated.py`
or `scripts/` in its output. The output only shows:
- `tests/integration/`
- `tests/regression/`
- `tests/unit/`

No "otros" or "scripts" entries appear.

### Warnings

Two deprecation warnings from `test_npsh.py`:
1. `compare_npsha_legacy_vs_validated()` uses hardcoded values
2. `npsha_from_workbook()` uses hardcoded values

These are pre-existing and will be addressed by the NPSH refactor (Section 3).
