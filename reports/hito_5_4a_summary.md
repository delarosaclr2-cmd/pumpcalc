# Hito 5.4A — Absolute Pressure Boundary Model

## Summary

This milestone implements a complete absolute pressure boundary model for the TDH calculation pipeline.

## What Changed

1. **BoundaryType enum** — 6 boundary types (FREE_SURFACE through EQUIPMENT_OUTLET)

2. **SystemBoundary dataclass** — Typed boundary node with pressure, elevation, confidence

3. **PressureBoundaryResult dataclass** — Result container for boundary pressure computations

4. **compute_source_boundary_absolute_pressure()** — Three reference variants (GAUGE, ABSOLUTE, VACUUM)

5. **required_boundary_pressure_head()** — Core function with 4 reference rules

6. **build_semantic_tdh_balances() updated** —
   - D (ABSOLUTE): now calculable using source boundary (14.7 psia)
   - E (UNKNOWN): new scenario returning PRESSURE_REFERENCE_REQUIRED
   - F (U40_EXCLUDED): sensitivity scenario

7. **DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE warning** — Negative differences allowed

## Current Case Results

| Scenario | TDH (ft) | Notes |
|---|---|---|
| WORKBOOK_LEGACY | 195.551113 | A. WORKBOOK_LEGACY |
| SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION | 195.551113 | B. SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION |
| VALIDATED_U40_AS_GAUGE | 196.295421 | C. VALIDATED_U40_AS_GAUGE |
| VALIDATED_U40_AS_ABSOLUTE | 162.201876 | D. VALIDATED_U40_AS_ABSOLUTE |
| U40_REFERENCE_UNKNOWN | PRESSURE_REFERENCE_REQUIRED | E. U40_REFERENCE_UNKNOWN |
| U40_EXCLUDED | 11.282413 | F. U40_EXCLUDED |

## Negative Difference Handling

- DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE is a WARNING, not an error

## Next Steps (Hito 5.5)

- Full integration with pump selection and NPSH calculations
- Source boundary pressure from workbook inputs