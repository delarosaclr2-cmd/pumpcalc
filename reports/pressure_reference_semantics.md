# Pressure Reference Semantics - Hito 5.4B

## Definitions

| Reference | Rule | Example |
|-----------|------|---------|
| GAUGE | dest_abs = dest_atm + psig, diff = dest_abs - source_abs | 79.77 psig -> 94.47 psia |
| DIFFERENTIAL | diff = value, dest_abs = source_abs + diff | 0.36 psi -> 0.36 psi diff |
| ABSOLUTE | dest_abs = value, diff = dest_abs - source_abs | 79.77 psia -> 65.07 psi diff |
| VACUUM | dest_abs = dest_atm - vacuum, diff = dest_abs - source_abs | 5.0 psi vac -> 9.7 psia |

## Current Case

- Source atmospheric: 14.7 psia
- Source vessel: 0 psig -> source_abs = 14.7 psia
- U40 (gauge): 79.77 psig -> diff = 79.77 psi
- U40 (absolute): 79.77 psia -> diff = 65.07 psi
- U39: 0.36 psi differential

### PressureHeadTerms (2 items)

| Cell | Value | Reference | Classification | Flow Dep |
|------|-------|-----------|----------------|----------|
| U39 | 0.36 | DIFFERENTIAL | INSTRUMENT_PRESSURE_DROP | N/A |
| U40 | 79.77 | UNKNOWN | MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE | N/A |
