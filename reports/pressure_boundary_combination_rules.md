# Pressure Boundary Combination Rules — Hito 5.4A

## Combination rules

| Rule | Description | When to use |
|------|-------------|-------------|
| MAXIMUM_REQUIREMENT | The higher of two overlapping requirements dominates | Opposite ends of same pipe, safety margin |
| ADDITIVE | Both requirements must be met in series | Sequential equipment, series configuration |
| ALTERNATIVE_SCENARIOS | Each term generates a separate TDH scenario | GAUGE vs ABSOLUTE pressure reference alternatives |
| USER_DEFINED | Custom rule set by user | Site-specific rules |

## Current application

- U39 (INSTRUMENT_PRESSURE_DROP) and U40 (MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE) are treated as ALTERNATIVE_SCENARIOS.
- They do not share a common node (no overlap detected).
- U39 is located at the discharge pipe (flow transmitter).
- U40 is at the equipment inlet (operating pressure requirement).

## Hito 5.4A Boundary hierarchy

| Boundary type | Used for |
|--------------|----------|
| FREE_SURFACE | Open tank, vented vessel |
| VESSEL_GAS_SPACE | Pressurized vessel gas space |
| PUMP_SUCTION_FLANGE | NPSHa calculation node |
| PIPE_NODE | Intermediate pipe analysis |
| EQUIPMENT_INLET | Equipment pressure requirement |
| EQUIPMENT_OUTLET | Equipment discharge boundary |

## Scenario combination

Current 6 scenarios:

- WORKBOOK_LEGACY: A. WORKBOOK_LEGACY: U39/U40 inside accessory_minor, legacy ×2.31 conversion
- SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION: B. SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION: U39→instrument_drop, U40→minimum_inlet, legacy ×2.31
- VALIDATED_U40_AS_GAUGE: C. VALIDATED_U40_AS_GAUGE: SG-based conversion (SG=0.995), gauge pressure assumption
- VALIDATED_U40_AS_ABSOLUTE: D. VALIDATED_U40_AS_ABSOLUTE: U40=79.77 psia − source 14.7 psia = 65.07 psi diff, SG-based conversion
- U40_REFERENCE_UNKNOWN: E. U40_REFERENCE_UNKNOWN: Pressure reference not specified — no definitive validated TDH
- U40_EXCLUDED: F. U40_EXCLUDED: Sensitivity only — U40 excluded (not recommended as correction)

## Absolute scenario requires boundary reference

- D (ABSOLUTE): uses source_boundary_absolute_pressure_psia = 14.7 (computed from atm + vessel gauge)
- E (UNKNOWN): PRESSURE_REFERENCE_REQUIRED until user specifies reference
- The absolute vs gauge combination follows ALTERNATIVE_SCENARIOS (each produces a separate TDH)