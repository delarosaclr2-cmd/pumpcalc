# Pressure Head Semantics — Hito 5.4

## Typed PressureHeadTerm model

| Source | Name | Value (PSI) | Ref | Classification | SG | Legacy (ft) | Validated (ft) | Confidence | Confirmed |
|--------|------|-------------|-----|---------------|----|------------|---------------|-----------|---------|
| U39 | PERDIDAS POR TRANSMISOR DE FLUJO | 0.36 | DIFFERENTIAL | INSTRUMENT_PRESSURE_DROP | 0.995 | 0.8316 | 0.834944 | HIGH | True |
| U40 | PRESION DE OPERACION DEL EQUIPO | 79.77 | UNKNOWN | MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE | 0.995 | 184.2687 | 185.009664 | USER_CONFIRMED_SEMANTICS | True |

## Classification rationale (Hito 5.4 confirmed)

### U39 (0.36 PSI)
- **Classification**: INSTRUMENT_PRESSURE_DROP (confirmed)
- **Reference**: DIFFERENTIAL (confirmed by user)
- **Confidence**: HIGH
- Comment: "PERDIDAS POR TRANSMISOR DE FLUJO" — explicitly identified as flow transmitter loss
- Flow dependency: UNKNOWN (do not auto-assume Q²)

### U40 (79.77 PSI)
- **Classification**: MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE (confirmed)
- **Reference**: UNKNOWN (pending)
- **Confidence**: USER_CONFIRMED_SEMANTICS (semantics confirmed, reference pending)
- Comment: "PRESION DE OPERACION DEL EQUIPO" — manually added to guarantee minimum inlet pressure
- Flow dependency: FLOW_INDEPENDENT (does not vary with flow)
- User confirmed: True
