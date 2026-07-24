# Semantic Head Balance — Hito 5.4A

## 6 TDH scenarios (A–F)

### Common components
- Static elevation head: 5.27958 ft
- Surface pressure difference: 0.0 ft
- Pipe major losses: 1.696094 ft

**WORKBOOK_LEGACY**: TDH = 195.551113 ft — A. WORKBOOK_LEGACY: U39/U40 inside accessory_minor, legacy ×2.31 conversion

- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 188.57544
- discharge_fitting_losses_legacy_ft: 188.57544

**SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION**: TDH = 195.551113 ft — B. SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION: U39→instrument_drop, U40→minimum_inlet, legacy ×2.31

- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.8316
- unclassified_required_pressure_head_ft: 184.2687
- minimum_required_equipment_inlet_pressure_head_ft: 184.2687
- discharge_fitting_losses_legacy_ft: 188.57544

**VALIDATED_U40_AS_GAUGE**: TDH = 196.295421 ft — C. VALIDATED_U40_AS_GAUGE: SG-based conversion (SG=0.995), gauge pressure assumption

- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.834944
- unclassified_required_pressure_head_ft: 185.009664
- minimum_required_equipment_inlet_pressure_head_ft: 185.009664
- discharge_fitting_losses_legacy_ft: 188.57544

**VALIDATED_U40_AS_ABSOLUTE**: TDH = 162.201876 ft — D. VALIDATED_U40_AS_ABSOLUTE: U40=79.77 psia − source 14.7 psia = 65.07 psi diff, SG-based conversion

- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.834944
- unclassified_required_pressure_head_ft: 150.916119
- minimum_required_equipment_inlet_pressure_head_ft: 150.916119
- discharge_fitting_losses_legacy_ft: 188.57544

**U40_REFERENCE_UNKNOWN**: TDH = PRESSURE_REFERENCE_REQUIRED ft — E. U40_REFERENCE_UNKNOWN: Pressure reference not specified — no definitive validated TDH

- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.834944
- discharge_fitting_losses_legacy_ft: 188.57544

**U40_EXCLUDED**: TDH = 11.282413 ft — F. U40_EXCLUDED: Sensitivity only — U40 excluded (not recommended as correction)

- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.8316
- discharge_fitting_losses_legacy_ft: 4.30674

### Key observations
1. WORKBOOK_LEGACY == SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION (same TDH, different composition)
2. VALIDATED_U40_AS_GAUGE adjusts for SG correction
3. VALIDATED_U40_AS_ABSOLUTE now calculable with source boundary (14.7 psia)
4. U40_REFERENCE_UNKNOWN requires pressure reference specification
5. U40_EXCLUDED is sensitivity only — not a recommended correction