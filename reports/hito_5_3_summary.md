# Hito 5.3 Summary — Accessory Loss Audit

## Objective
Independently reconstruct every row of both accessory tables (`TABLA DE ACCESORIOS DESCARGA` and `TABLA DE ACCESORIOS SUCCION`), classify each method, detect double counting, and generate scenario comparisons for the dominant discharge fitting loss (188.56 ft, ~96% of TDH).

## Key Findings

### 1. Suction Table (TABLA DE ACCESORIOS SUCCION)
- **34 rows** (6-39), **1 active** (Row 6: Valvula de Compuerta 100% Abierta, qty=1)
- **Total**: I40 = SUM(I6:I39) = **0.0168248889 ft** → matches C11 exactly
- Velocity: cross-sheet reference `'CAIDA PRESION DE TUBERIA'!$V$6` = **3.12 ft/s**
- Formula: `=((D*F)*(V6^2)/(32.4*2))*H` — standard Leq/D method with g≈32.4

### 2. Discharge Table (TABLA DE ACCESORIOS DESCARGA)
- **34 rows** (7-40), **4 active** (3 with Leq formula + 1 with pressure entry)
- **Two completely independent loss systems** in the same table:

| Component | Feet | % of Total |
|-----------|------|-----------|
| O column (Leq formula, group 1) | 3.4583 | 1.83% |
| U column (pressure × 2.31) | 185.1003 | 98.17% |
| Total (I41 = O41+U41) | **188.5586** | 100% |

### 3. The Dominant "Accessory Loss" is NOT a Minor Loss
- **98.2%** of the discharge fitting loss (185.1 of 188.56 ft) comes from the **U column** — labeled "ESPESADOR DISCOS CARA" (Thickness of Disc Face)
- This is a direct pressure entry (79.77 PSI + 0.36 PSI) converted to feet via ×2.31
- **It is not a Darcy-Weisbach minor loss** — it bypasses the standard Leq/D calculation entirely

### 4. Anomalies Detected

| Issue | Row | Details |
|-------|-----|---------|
| Double counting | 39 | Both Leq formula (0.62 ft) AND pressure (0.36 PSI → 0.83 ft) for the same 90° LR elbow |
| Zero-quantity pressure | 40 | 79.77 PSI with quantity H=0 — the dominant entry has no quantity |
| 79.77 PSI coincidence | 40 | Matches total pipe friction pressure drop (~79.84 PSI), suggesting possible copy-paste error |

### 5. g-Approximation Bias
- Workbook uses **g = 32.4** instead of **g = 32.174 ft/s²**
- This understates all velocity-based losses by **~0.70%** (systematic)

### 6. Scenario Comparison

| Scenario | Suction (ft) | Discharge (ft) | Total (ft) | Δ from Excel |
|----------|-------------|---------------|-----------|-------------|
| LEGACY (hardcoded) | 0.016800 | 188.560000 | 188.576800 | +0.001% |
| EXCEL TOTAL | 0.016825 | 188.558615 | 188.575440 | 0.00% |
| LEQ FORMULA ONLY | 0.016825 | 3.458315 | 3.475140 | -98.16% |
| STANDARD LEQ | 0.016943 | 3.482607 | 3.499550 | -98.14% |
| K-METHOD ONLY | 0.028743 | 6.873264 | 6.902007 | -96.34% |
| PRESSURE BASED | 0.000000 | 185.100300 | 185.100300 | -1.84% |

## Deliverables

### New files
- `src/domain/accessory_losses.py` — independent 3-method calculation engine (68 rows, 22 tests-worth of math)
- `tests/unit/test_accessory_audit.py` — 22 Hito 5.3-specific tests (5 categories, all pass)

### New reports
- `reports/accessory_table_structure.csv` / `.md` — column-by-column comparison of both tables
- `reports/accessory_inventory.csv` — all 68 rows with 3-method comparison
- `reports/accessory_total_reconciliation.csv` / `.md` — how I40 and I41 totals are built
- `reports/accessory_row_comparison.csv` — per-row method comparison
- `reports/double_counting_audit.csv` / `.md` — detected double-counting issues
- `reports/pareto_analysis_discharge.csv` / `suction.csv` / `.md` — Pareto analysis
- `reports/accessory_scenario_comparison.csv` / `.md` — 6-scenario comparison
- `reports/accessory_reasonableness.csv` — physical reasonableness checks

### Updated files
- `reports/data_lineage.csv` — added `accessory_audit` lineage entry
- `src/application/validated_calculator.py` — added `accessory_audit` dict to `ValidatedResults` with full audit data
- `tests/integration/test_integrity.py` — added 32.4 to allowed literals

### Test Results
- **150 tests pass** (was 128 before Hito 5.3, +22 new)
- All 5 categories (formula reconstruction, total reconciliation, double counting, scenario comparison, data integrity) verified

## Pending / Next Steps
- The primary calculation still uses the hardcoded Excel values (188.5586 ft, 0.0168 ft) — the accessory audit is observation-only
- A decision is needed on whether the 79.77 PSI pressure entry is a legitimate accessory loss or a data entry error (possible pipe friction misattribution)
- If confirmed as error, the discharge fitting loss would drop from 188.56 ft to ~3.46 ft, reducing TDH by 96%
- Recommend verifying the 79.77 PSI value against P&ID or pressure-drop calculations before any correction
