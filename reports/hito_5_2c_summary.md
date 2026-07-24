# Hito 5.2C — Summary: Corrección de diámetros seleccionados y equivalencia de fronteras

## Corrections Applied

### 1. G8/V8 Reclassified as Required Diameters
- `suction_inside_diameter_in` → `suction_required_diameter_in` (V8 = V7×sqrt(V5/V6))
- `discharge_inside_diameter_in` → `discharge_required_diameter_in` (G8 = G7×sqrt(G5/G6))
- Added `suction_selected_inside_diameter_in` (Optional[float], default None)
- Added `discharge_selected_inside_diameter_in` (Optional[float], default None)
- Added pipe schedule fields with status `MISSING_SELECTED_PIPE_SCHEDULE`

### 2. NPSHa Flange Route — Velocity Head Double Count Corrected
- **Old:** `NPSHa_flange = NPSHa_surface + velocity_head` (34.03 ft) — WRONG
- **New:** `NPSHa_flange == NPSHa_surface` via Bernoulli cancellation (33.88 ft)
- Both routes now produce identical values: `equivalence_diff = 0.0 ft`

### 3. TDH Flange-to-Flange — Requires Pressure Data
- **Old:** `tdh_flange_to_flange = elevation_diff + velocity_head_diff` (6.28 ft) — WRONG
- **New:** `tdh_flange_to_flange = None` (TDH_FLANGE_NOT_CALCULABLE)
- Partial term renamed: `partial_geometric_kinetic_difference_ft` (6.28 ft)
- **This is NOT pump TDH** — pressure term is missing

### 4. Boundary Condition Status
- `tdh_boundary_method` = `BOUNDARY_CONDITION_UNVERIFIED` (C9/C20 need physical confirmation)
- `npsh_boundary_method` = `FROM_FREE_SURFACE` (confirmed via formula analysis)

## Answers to Deliverable Questions

### 1. Origen real del diámetro seleccionado
No hay un diámetro seleccionado confirmado. La cédula no está disponible en el workbook (hoja ESPECIFICACIÓN DE TUBERIA vacía, tabla OUTPIPES sin datos de espesor). El material es "Acero Inox SS" (desde OUTPIPES).

### 2. Cédula encontrada o estado faltante
`MISSING_SELECTED_PIPE_SCHEDULE` — no se encontró cédula explícita en el workbook.

### 3. ID real de succión
**None** — no se puede calcular sin cédula confirmada. Se usa el diámetro requerido (10.044 in) como referencia para hidráulica.

### 4. ID real de descarga
**None** — no se puede calcular sin cédula confirmada. Se usa el diámetro requerido (6.050 in) como referencia para hidráulica.

### 5. NPSHa por ruta de superficie
33.88 ft (via `npsha_from_surface_ft`)

### 6. NPSHa por ruta de brida
33.88 ft (via `npsha_from_flange_ft`)

### 7. Diferencia entre ambas rutas
0.0 ft (abs diff < 1e-8) — ambas rutas son EQUIVALENTES por cancelación Bernoulli.

### 8. TDH surface-to-surface
195.13 ft

### 9. Estado del TDH flange-to-flange
`TDH_FLANGE_NOT_CALCULABLE` — faltan presiones de brida (`suction_flange_pressure`, `discharge_flange_pressure`, `suction_flange_elevation`, `discharge_flange_elevation`).

### 10. Pruebas ejecutadas
**128 tests** en total (57 unit + 23 regression + 25 integrity + 23 Hito 5.2C-specific), todos pasan.

Nuevas pruebas específicas de Hito 5.2C:
1. `test_g8_v8_are_required_diameters` — G8/V8 clasificados como requeridos
2. `test_selected_diameter_not_replaced_by_required` — No se sustituye requerido por seleccionado
3. `test_missing_schedule_generates_status` — Falta de cédula genera MISSING_SELECTED_PIPE_SCHEDULE
4. `test_npsha_surface_equals_flange` — Ambas rutas NPSHa producen mismo valor
5. `test_npsha_no_double_velocity_head` — No se suma carga de velocidad dos veces
6. `test_tdh_flange_not_calculable` — TDH flange requiere diferencia de presión
7. `test_tank_elevations_not_flange_elevations` — Tanques no son bridas
8. `test_partial_geometric_not_called_tdh` — 6.28 ft no se denomina TDH
9. `test_tdh_surface_reproducible` — TDH surface-to-surface reproducible
10. `test_g8_v8_classified_as_required_diameter` (integración) — Reports corregidos

### 11. Archivos actualizados

| Archivo | Cambio |
|---------|--------|
| `src/infrastructure/input_loader.py` | Rename fields, add schedule/selected ID fields, update validators |
| `src/application/validated_calculator.py` | NPSH equivalence, TDH not calculable, partial term, BOUNDARY_UNVERIFIED |
| `src/application/legacy_calculator.py` | Use required diameter as fallback |
| `tests/fixtures/current_case.json` | Updated for 5.2C field names and values |
| `tests/regression/test_regression.py` | 23 tests updated for new field classifications |
| `tests/integration/test_integrity.py` | 10 new Hito 5.2C tests, AST allowed literals updated |
| `reports/npsh_boundary_comparison.csv` | Equivalence columns, Bernoulli derivation |
| `reports/tdh_boundary_comparison.csv` | MISSING flange TDH, partial term, input status |
| `reports/diameter_selection_audit.md` | Full rewrite: required vs selected, schedule scenarios |
| `reports/hydraulic_boundary_definition.md` | Full rewrite: NPSH equivalence, TDH correction, UNVERIFIED status |
| `reports/data_lineage.csv` | Updated field names and derivation paths |
| `reports/hito_5_2c_summary.md` | New: this file |
