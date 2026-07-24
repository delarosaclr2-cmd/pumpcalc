# Hito 5.2 — Refactor and Boundary Definition Complete

**Date:** 2026-07-22  
**Status:** All 99 tests pass, all reports regenerate from a single execution.

## Hito 5.2A — Refactor (Previous)

### 1. Input Sanitisation (`src/infrastructure/input_loader.py`)
- Flat `WorkbookInputs` Pydantic model with 28+ fields, each typed with provenance
- Single `create_workbook_inputs()` factory for the current case

### 2. Legacy Calculator (`src/application/legacy_calculator.py`)
- No hardcoded case values; all from `WorkbookInputs`
- Named constants for workbook formulas

### 3. Validated Calculator (`src/application/validated_calculator.py`)
- Returns `ValidatedResults` dataclass — every field computed
- Colebrook-White friction, proper NPSH dimensional analysis, full TDH balance
- Two torque fields, two specific speed fields

## Hito 5.2B — Boundary Definition (This Session)

### 4. Diameter Separation
- **Required diameter** (velocity-based sizing) separated from **selected diameter** (actual pipe spec)
- All hydraulics (Re, velocity, Colebrook, Darcy-Weisbach) use **selected inside diameter**
- New function `required_diameter_from_flow_velocity()` in `src/domain/pipes.py`
- 0.639 factor derived: `C = 12 × sqrt(4 / (448.831 × π))`
- `diameter_status` field: "OK" or "MISSING_SELECTED_DIAMETER"
- Analytical unit test added (6 test cases)

### 5. TDH Boundary Definition
- **Surface-to-surface** (workbook method, no velocity head): 195.13 ft
- **Flange-to-flange** (pump energy addition): 6.28 ft
- C9 classified as TANK_FREE_SURFACE_ELEVATION (formula =500/304.8)
- C20 classified as TANK_FREE_SURFACE_ELEVATION (hardcoded 6.92)
- Both computed and reported; primary = surface-to-surface

### 6. NPSH Boundary Definition
- **From free surface** (workbook method, no velocity head): 33.88 ft
- **From suction flange** (includes velocity head): 34.03 ft
- Workbook formula confirmed as surface-based
- Both computed and reported; primary = surface-based

### 7. Vapor Pressure Audit
- Unit validated to `{psia, ft_H2O, ft_fluid, Pa}`
- Source cell: `VELOCIDADES RECOMENDADAS!AA13`
- Current value: 0.8 psia (confirmed)
- `vapor_pressure_source_cell` field added to inputs

### 8. Test Results (99 total)
- **57 unit tests** — friction, NPSH, power, units, diameter — all pass
- **23 regression tests** — fixture-based for both calculators + boundary methods — all pass
- **19 integrity tests** — AST hardcoding check, cross-report, NPSH proof, torque RPM — all pass

### 9. Reports Generated
| Report | Description |
|--------|------------|
| `head_balance.csv` | TDH/NPSH/power comparison legacy vs validated |
| `friction_factor_evidence.csv` | Colebrook vs Haaland vs Swamee-Jain |
| `friction_impact_scenarios.csv` | A-D scenario comparison |
| `tdh_boundary_comparison.csv` | Surface vs flange TDH |
| `npsh_boundary_comparison.csv` | Surface vs flange NPSH |
| `hardcoding_audit.csv` | All literals with line numbers and classifications |
| `data_lineage.csv` | Full traceability for every result |
| `hydraulic_boundary_definition.md` | TDH/NPSH boundary documentation |
| `diameter_selection_audit.md` | Required vs selected diameter audit |
| `current_case_inputs_v2.csv` | All input variables with provenance |

### 10. Architecture
```
create_workbook_inputs()
    → WorkbookInputs (flat, 31+ fields)
        → calculate_legacy(inputs) → LegacyResults
        → calculate_validated(inputs) → ValidatedResults
            ├── suction_required_diameter_in
            ├── discharge_required_diameter_in
            ├── suction_selected_inside_diameter_in
            ├── discharge_selected_inside_diameter_in
            ├── tdh_surface_to_surface_ft
            ├── tdh_flange_to_flange_ft
            ├── npsha_from_surface_ft
            ├── npsha_from_flange_ft
            ├── pump_rpm
            └── legacy_torque_rpm
        → compute_scenarios(inputs, validated) → scenarios A-D
```

No case-specific values appear outside `input_loader.py:create_workbook_inputs()`.
