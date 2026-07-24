# Hito 5.4 — Modelo de requisitos de presión de equipos — Summary

## 1. U39 confirmed classification
**INSTRUMENT_PRESSURE_DROP** (perdidas por transmisor de flujo, user confirmed)

## 2. U40 confirmed classification
**MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE** (presion de operacion del equipo, user confirmed)

## 3. U39 individual value
0.36 psi (differential)

## 4. U40 individual value
79.77 psi

## 5. Total sum in psi
0.36 + 79.77 = **80.13 psi**

## 6. Legacy conversion (×2.31)
- U39: 0.36 × 2.31 = **0.8316 ft**
- U40: 79.77 × 2.31 = **184.2687 ft**
- Total: 185.1003 ft

## 7. Validated conversion (×144/(62.4×SG))
- Factor: 2.319289 ft/psi (SG = 0.995)
- U39: 0.834944 ft
- U40: 185.009664 ft
- Total: 185.844608 ft

## 8. Pending pressure reference for U40
**UNKNOWN** — must confirm whether 79.77 psi is GAUGE or ABSOLUTE

## 9. Semantic composition of TDH Legacy
| Component | Value (ft) |
|-----------|-----------|
| Static elevation | 5.279580 |
| Surface pressure diff | 0.0 |
| Pipe major losses | 1.696094 |
| Accessory minor losses | 3.475140 |
| Instrument pressure drop | 0.831600 |
| Minimum required inlet pressure | 184.268700 |
| **Total TDH** | **195.551113** |

## 10. TDH — gauge scenario (VALIDATED_U40_AS_GAUGE)
**196.295421 ft** (assuming U40 is GAUGE, SG-based conversion)

## 11. Absolute scenario status
**NOT_CALCULABLE_MISSING_SUCTION_BOUNDARY_PRESSURE**

## 12. Default combination rule
**ALTERNATIVE_SCENARIOS** — boundary pressures on same node are treated as alternatives, not summed

## 13. Double-counting warnings
- No double-counting warnings for current case (single boundary term)

## 14. Flow-independent components
- static_elevation_head_ft
- surface_pressure_difference_ft
- minimum_required_equipment_inlet_pressure_head_ft
- required_residual_pressure_head_ft (if applicable)
- receiving_vessel_operating_pressure_head_ft (if applicable)

## 15. Flow-dependent components
- pipe_major_losses_ft: QUADRATIC_WITH_FLOW
- accessory_minor_losses_ft: QUADRATIC_WITH_FLOW
- instrument_pressure_drop_ft: UNKNOWN (do not auto-assume Q²)
- equipment_internal_pressure_drop_ft: UNKNOWN or MANUFACTURER_CURVE

## 16. Future configuration UI structure
See `reports/future_pressure_configuration_ui.md` for full specification.
Table with 14+ columns, 4 term types, 7+ units, 10+ controls, and 7 warning types.

## 17. Tests executed
150 + 26 = **176 total** (all pass)

## 18. Files created or updated
### New reports
- reports/equipment_pressure_requirement_model.md / .csv
- reports/pressure_boundary_combination_rules.md
- reports/pressure_term_scenarios.md / .csv
- reports/system_curve_component_model.md
- reports/future_pressure_configuration_ui.md
- reports/hito_5_4_summary.md

### Updated reports
- reports/pressure_head_semantics.md / .csv
- reports/semantic_head_balance.md / .csv
- reports/system_head_component_classification.md / .csv
- reports/data_lineage.csv
- reports/hydraulic_discrepancies.md

### New test file
- tests/unit/test_hito_5_4.py (26 tests)
