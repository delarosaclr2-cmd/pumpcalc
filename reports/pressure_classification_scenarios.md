# Pressure Classification Scenarios

## Provisional Classification

- **U40 (79.77 PSI)**: `EQUIPMENT_PRESSURE_DROP` — per cell comment 'PRESION DE OPERACION DEL EQUIPO' and RESUMEN PARA PDF label 'Perdidas en descarga por instrumentos y equipos'
- **U39 (0.36 PSI)**: `ACCESSORY_MINOR_LOSS` — per cell comment 'PERDIDAS POR TRANSMISOR DE FLUJO' (Flow Transmitter Losses)

## Three TDH Scenarios

| Scenario | Suction Fit (ft) | Discharge Fit (ft) | Total Fit (ft) | Process Pressure (ft) | TDH (ft) | Note |
|---|---|---|---|---|---|---|
| LEGACY (hardcoded) | 0.016800 | 188.560000 | 188.576800 | N/A | 195.551113 | Hardcoded constants (pre-audit) |
| TDH_WITH_PRESSURE_INPUT | 0.016825 | 188.558615 | 188.575440 | 0.0 | 195.551113 | Current behavior: pressure column inside discharge fitting losses |
| TDH_WITHOUT_PRESSURE_INPUT | 0.016825 | 3.458315 | 3.475140 | 0.0 | 10.450813 | Pressure column excluded from fitting losses |
| TDH_WITH_PRESSURE_RECLASSIFIED_AS_PROCESS_REQUIREMENT | 0.016825 | 3.458315 | 3.475140 | 185.100300 | 195.551113 | Pressure column moved to separate process_required_pressure_head_ft |

## Analysis

1. **TDH_WITH_PRESSURE_INPUT** (current): Discharge fitting losses = 188.56 ft, which includes 185.1 ft from the pressure column.
2. **TDH_WITHOUT_PRESSURE_INPUT**: Excludes the pressure column from fitting losses. Discharge fitting losses drop to ~3.46 ft.
3. **TDH_WITH_PRESSURE_RECLASSIFIED_AS_PROCESS_REQUIREMENT**: Same total head as current, but the pressure column is separated into its own category `process_required_pressure_head_ft` rather than being classified as a fitting/minor loss.

No scenario has been selected as definitive. The reclassified scenario preserves the workbook's total head while providing transparency about the nature of the 79.77 PSI entry.
