# Absolute Pressure Boundary Model

## Source Boundary Definition

| Parameter | Value |
|-----------|-------|
| Atmospheric pressure (psia) | 14.7 |
| Vessel pressure | 0.0 |
| Vessel pressure type | GAUGE |
| Source boundary absolute pressure (psia) | 14.7 |

## Required Boundary Pressure Head

| Required Pressure Reference | Value (psia) | Source (psia) | Difference (psi) | Head (ft) | Status |
|---|---|---|---|---|---|
| GAUGE | 79.77 | 14.7 | 79.7700 | 185.0097 | CALCULATED |
| ABSOLUTE | 79.77 | 14.7 | 65.0700 | 150.9161 | CALCULATED |
| DIFFERENTIAL | 10.0 | 14.7 | 10.0000 | 23.1929 | CALCULATED |
| UNKNOWN | 79.77 | 14.7 | N/A | N/A | PRESSURE_REFERENCE_REQUIRED |

## Formulas

- **GAUGE**: `pressure_difference = required_value`
- **ABSOLUTE**: `pressure_difference = required_abs - source_abs`
- **DIFFERENTIAL**: `pressure_difference = required_value` (same as GAUGE)
- **UNKNOWN**: `status = PRESSURE_REFERENCE_REQUIRED`
- **Head**: `pressure_difference * 144 / (62.4 * SG)`