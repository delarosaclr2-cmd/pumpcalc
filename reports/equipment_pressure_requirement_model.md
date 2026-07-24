# Equipment Pressure Requirement Model — Hito 5.4A

## PressureRequirement data model

| Field | Type | Description |
|-------|------|-------------|
| term_id | str | Unique identifier |
| name | str | Human-readable name |
| term_type | PressureTermType | INSTRUMENT_PRESSURE_DROP, EQUIPMENT_INTERNAL_PRESSURE_DROP, MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE, RECEIVING_VESSEL_OPERATING_PRESSURE |
| value | float | Numerical value |
| unit | str | psi, psig, psia, bar(g), etc. |
| pressure_reference | PressureReference | GAUGE, ABSOLUTE, DIFFERENTIAL, VACUUM, UNKNOWN |
| flow_dependency | FlowDependency | FLOW_INDEPENDENT, QUADRATIC_WITH_FLOW, MANUFACTURER_CURVE, USER_DEFINED, UNKNOWN |
| design_flow_gpm | float or None | Associated design flow rate |
| active | bool | Whether term contributes to balance |
| source_type | str | WORKBOOK_MANUAL_INPUT, etc. |
| source_sheet | str or None | Source workbook sheet |
| source_cell | str or None | Source cell reference |
| source_comment | str or None | Cell comment text |
| confidence | str | PROVISIONAL, HIGH, USER_CONFIRMED_SEMANTICS |
| user_confirmed | bool | Whether confirmed by user |
| notes | str or None | Free-text notes |
| start_node | str or None | Hydraulic node (start) |
| end_node | str or None | Hydraulic node (end) |
| combination_rule | str | MAXIMUM_REQUIREMENT, ADDITIVE, ALTERNATIVE_SCENARIOS, USER_DEFINED |

## Current case terms

| ID | Name | Type | Value | Ref | Flow Dep | SG | Legacy (ft) | Validated (ft) | Confirmed |
|----|------|------|-------|-----|----------|----|------------|---------------|-----------|
| DISCHARGE_INSTRUMENT_FT_001 | Perdida del transmisor de flujo | INSTRUMENT_PRESSURE_DROP | 0.36 psi | DIFFERENTIAL | UNKNOWN | 0.995 | 0.8316 | 0.8349 | True |
| EQUIPMENT_MINIMUM_INLET_PRESSURE_001 | Presion minima requerida en la entrada del equipo | MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE | 79.77 psi | UNKNOWN | FLOW_INDEPENDENT | 0.995 | 184.2687 | 185.0097 | True |

## Confirmed classifications

### U39 — INSTRUMENT_PRESSURE_DROP
- Cell: TABLA DE ACCESORIOS DESCARGA!U39
- Value: 0.36 psi (differential)
- Comment: "PERDIDAS POR TRANSMISOR DE FLUJO"
- Reference: DIFFERENTIAL (confirmed)
- Flow dependency: UNKNOWN (do not assume Q^2 without curve)
- Confidence: HIGH (user confirmed)

### U40 — MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE
- Cell: TABLA DE ACCESORIOS DESCARGA!U40
- Value: 79.77 psi
- Comment: "PRESION DE OPERACION DEL EQUIPO"
- Reference: UNKNOWN (pending user confirmation)
- Flow dependency: FLOW_INDEPENDENT (does not vary with flow)
- Confidence: USER_CONFIRMED_SEMANTICS (semantics confirmed, reference pending)

## Hito 5.4A additions

### Source boundary definition
- Boundary type: FREE_SURFACE (open tank)
- Atmospheric pressure: 14.7 psia
- Vessel pressure: 0.0 psig
- Computed source_abs: 14.7 psia

### Boundary pressure rules
- **GAUGE**: pressure_difference = required_value; dest_abs = source_abs + value
- **ABSOLUTE**: pressure_difference = required_abs - source_abs; dest_abs = required_value
- **DIFFERENTIAL**: same as GAUGE (pressure_difference = value)
- **UNKNOWN**: returns PRESSURE_REFERENCE_REQUIRED

### Current absolute result
- Required: 79.77 psia (ABSOLUTE)
- Source: 14.7 psia
- Difference: 65.07 psi
- Head: ~150.92 ft