# Canonical Boundary Head Balance - Hito 5.4B

Dataset: C:\PUMPCALC\data\cases\current_workbook_case.json
Dataset hash: f5cc84dfddcc
Dataset version: 1.0

## Current Case

- Source atmospheric pressure: 14.7 psia (from dataset)
- Source vessel pressure: 0 psig (open to atmosphere)
- Source absolute pressure: compute_boundary_absolute_pressure(14.7, 0, GAUGE) = 14.7 psia

### U40 Gauge

- Destination required pressure: 79.77 psig
- Destination absolute pressure: 14.7 + 79.77 = 94.47 psia
- Boundary difference: 79.77 psi
- Boundary pressure head (equipment inlet): 185.01 ft
- Total required pump head: 196.30 ft

### U40 Absolute
- Destination required pressure: 79.77 psia
- Source absolute: 14.7 psia
- Boundary difference: 65.07 psi
- Boundary pressure head (equipment inlet): 150.92 ft
- Total required pump head: 162.20 ft

## All scenarios

| Key | TDH (ft) | Static (ft) | Major (ft) | Minor (ft) | Pressure diff (ft) |
|-----|----------|-------------|------------|------------|-------------------|
| SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION | 195.55 | 5.28 | 1.70 | 3.48 | 184.27 |
| U40_EXCLUDED | 11.28 | 5.28 | 1.70 | 3.48 | 0.00 |
| U40_REFERENCE_UNKNOWN | PRESSURE_REFERENCE_REQUIRED | - | - | - | - |
| VALIDATED_U40_AS_ABSOLUTE | 162.20 | 5.28 | 1.70 | 3.48 | 150.92 |
| VALIDATED_U40_AS_GAUGE | 196.30 | 5.28 | 1.70 | 3.48 | 185.01 |
| WORKBOOK_LEGACY | 195.55 | 5.28 | 1.70 | 188.58 | 0.00 |