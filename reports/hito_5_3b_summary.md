# Hito 5.3B — Cierre semantico de entradas de presion — Summary

## 1. Provisional classifications
- **U39**: INSTRUMENT_PRESSURE_DROP (perdidas por transmisor de flujo)
- **U40**: UNCLASSIFIED_REQUIRED_PRESSURE (presion de operacion del equipo — not confirmed as drop)

## 2. Pressure reference
- U39: UNKNOWN (no pressure reference specified in cell or comment)
- U40: UNKNOWN (no pressure reference specified in cell or comment)

## 3. Legacy conversion (×2.31)
- U39: 0.36 PSI × 2.31 = 0.831600 ft
- U40: 79.77 PSI × 2.31 = 184.268700 ft

## 4. Validated conversion (×144/(62.4 × SG))
- Validated factor: 2.319289 ft/psi (SG = 0.995)
- U39: 0.36 PSI × 2.319289 = 0.834944 ft
- U40: 79.77 PSI × 2.319289 = 185.009664 ft

## 5. TDH summary
- **WORKBOOK_LEGACY**: 195.551113 ft — A. WORKBOOK_LEGACY: U39 and U40 inside accessory losses, ×2.31 conversion
- **PRESSURE_TERMS_RECLASSIFIED**: 195.551113 ft — B. PRESSURE_TERMS_RECLASSIFIED: U39→instrument_drop, U40→unclassified, legacy conversion
- **VALIDATED_PRESSURE_CONVERSION**: 196.295421 ft — C. VALIDATED_PRESSURE_CONVERSION: SG-based conversion (SG=0.995)
- **U40_AS_EQUIPMENT_DROP**: 195.551113 ft — D. U40_AS_EQUIPMENT_DROP: U40 treated as equipment pressure drop
- **U40_AS_RESIDUAL_PRESSURE**: 195.551113 ft — E. U40_AS_RESIDUAL_PRESSURE: U40 treated as required residual pressure
- **U40_EXCLUDED_FOR_SENSITIVITY_ONLY**: 11.282413 ft — F. U40_EXCLUDED_FOR_SENSITIVITY_ONLY: U40 excluded (not recommended as correction)

## 6. Flow-independent components
- static_elevation_head_ft: STATIC_INDEPENDENT_OF_FLOW
- surface_pressure_difference_ft: STATIC_INDEPENDENT_OF_FLOW
- required_residual_pressure_head_ft: STATIC_INDEPENDENT_OF_FLOW (if applicable)

## 7. Flow-dependent components
- pipe_major_losses_ft: QUADRATIC_WITH_FLOW
- accessory_minor_losses_ft: QUADRATIC_WITH_FLOW
- instrument_pressure_drop_ft: UNKNOWN_FLOW_DEPENDENCE (confirm at design flow)
- equipment_pressure_drop_ft: UNKNOWN_FLOW_DEPENDENCE (requires manufacturer data)
- unclassified_required_pressure_head_ft: UNKNOWN_FLOW_DEPENDENCE

## 8. Data needed to classify U40 definitively
1. Confirm whether 79.77 PSI is GAUGE, ABSOLUTE, or DIFFERENTIAL pressure reference
2. Identify the "equipo" (equipment) named in the cell comment and obtain its datasheet
3. Determine if this is inlet pressure, outlet pressure, or differential across the equipment
4. Check if the value is at design flow or is a fixed pressure requirement
5. Verify whether the equipment is in the suction or discharge line relative to the pump
6. Obtain the equipment manufacturer's head-loss curve if it is a drop
7. Check if a residual pressure is contractually required at the discharge terminus
8. Cross-reference with P&ID to confirm whether this is a vessel operating pressure

## 9. New reports generated
- reports/pressure_head_semantics.md / .csv
- reports/pressure_conversion_comparison.md / .csv
- reports/semantic_head_balance.md / .csv
- reports/system_head_component_classification.md / .csv
- reports/hito_5_3b_summary.md

## 10. Updated reports
- reports/data_lineage.csv
- reports/hydraulic_discrepancies.md
