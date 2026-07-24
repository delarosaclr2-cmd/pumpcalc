# Pressure Term Scenarios — Hito 5.4A

## 6 parallel scenarios (A–F)

### WORKBOOK_LEGACY: A. WORKBOOK_LEGACY: U39/U40 inside accessory_minor, legacy ×2.31 conversion

- **Total TDH**: 195.551113 ft
- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 188.57544
- discharge_fitting_losses_legacy_ft: 188.57544

### SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION: B. SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION: U39→instrument_drop, U40→minimum_inlet, legacy ×2.31

- **Total TDH**: 195.551113 ft
- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.8316
- unclassified_required_pressure_head_ft: 184.2687
- minimum_required_equipment_inlet_pressure_head_ft: 184.2687
- discharge_fitting_losses_legacy_ft: 188.57544

### VALIDATED_U40_AS_GAUGE: C. VALIDATED_U40_AS_GAUGE: SG-based conversion (SG=0.995), gauge pressure assumption

- **Total TDH**: 196.295421 ft
- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.834944
- unclassified_required_pressure_head_ft: 185.009664
- minimum_required_equipment_inlet_pressure_head_ft: 185.009664
- discharge_fitting_losses_legacy_ft: 188.57544

### VALIDATED_U40_AS_ABSOLUTE: D. VALIDATED_U40_AS_ABSOLUTE: U40=79.77 psia − source 14.7 psia = 65.07 psi diff, SG-based conversion

- **Total TDH**: 162.201876 ft
- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.834944
- unclassified_required_pressure_head_ft: 150.916119
- minimum_required_equipment_inlet_pressure_head_ft: 150.916119
- discharge_fitting_losses_legacy_ft: 188.57544

### U40_REFERENCE_UNKNOWN: E. U40_REFERENCE_UNKNOWN: Pressure reference not specified — no definitive validated TDH

- **Total TDH**: PRESSURE_REFERENCE_REQUIRED ft
- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.834944
- discharge_fitting_losses_legacy_ft: 188.57544

### U40_EXCLUDED: F. U40_EXCLUDED: Sensitivity only — U40 excluded (not recommended as correction)

- **Total TDH**: 11.282413 ft
- static_elevation_head_ft: 5.27958
- pipe_major_losses_ft: 1.696094
- accessory_minor_losses_ft: 3.47514
- instrument_pressure_drop_ft: 0.8316
- discharge_fitting_losses_legacy_ft: 4.30674

### Boundary metadata for ABSOLUTE scenario
- source_boundary_absolute_pressure_psia: 14.7
- destination_required_absolute_pressure_psia: 79.77
- pressure_difference_psi: 65.07
- pressure_head_difference_ft: 150.916119

## Key observations

1. **A == B**: WORKBOOK_LEGACY and SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION have the same TDH but different composition.
2. **C (Gauge)**: TDH increases slightly when SG-based conversion is applied.
3. **D (Absolute)**: Now calculable with source boundary (14.7 psia). Difference = 65.07 psi, Head = 150.916119 ft.
4. **E (Unknown)**: Returns PRESSURE_REFERENCE_REQUIRED -- user must specify pressure reference.
5. **F (Excluded)**: TDH collapses to ~11.28 ft -- sensitivity only, NOT a recommended correction.