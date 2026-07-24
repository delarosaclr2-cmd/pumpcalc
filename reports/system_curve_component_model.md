# System Curve Component Model — Hito 5.4

## Component classification

| Component | Flow Dependence | Rationale |
|-----------|----------------|-----------|
| static_elevation_head_ft | FLOW_INDEPENDENT | Elevation difference between tanks is constant regardless of flow rate |
| surface_pressure_difference_ft | FLOW_INDEPENDENT | Open tank at both ends, no additional pressurization |
| pipe_major_losses_ft | QUADRATIC_WITH_FLOW | Darcy-Weisbach major losses are approximately proportional to Q² |
| accessory_minor_losses_ft | QUADRATIC_WITH_FLOW | Leq/D and K-method minor losses are proportional to V², hence ~Q² |
| instrument_pressure_drop_ft | UNKNOWN | Differential pressure across flow transmitter at design flow (770.5 GPM); confirm if fixed at all flows |
| equipment_pressure_drop_ft | UNKNOWN | Do not assume Q² dependence without manufacturer curve or test data |
| equipment_internal_pressure_drop_ft | UNKNOWN | Internal equipment pressure drop; do not assume Q² without manufacturer curve |
| required_residual_pressure_head_ft | FLOW_INDEPENDENT | Required minimum pressure at discharge point is typically independent of flow |
| unclassified_required_pressure_head_ft | UNKNOWN | Nature of 'PRESION DE OPERACION DEL EQUIPO' is unknown — could be static required pressure, equipment drop, or other |
| minimum_required_equipment_inlet_pressure_head_ft | FLOW_INDEPENDENT | Minimum required pressure at equipment inlet is typically a fixed static requirement independent of flow |
| receiving_vessel_operating_pressure_head_ft | FLOW_INDEPENDENT | Vessel operating pressure is typically a fixed boundary condition independent of flow |

## System curve formula

```
H_system(Q) =
    H_static
    + H_surface_pressure
    + H_minimum_required_inlet_pressure      ← U40: FLOW_INDEPENDENT
    + H_receiving_vessel_pressure
    + H_pipe(Q)                              ← QUADRATIC_WITH_FLOW
    + H_accessories(Q)                       ← QUADRATIC_WITH_FLOW
    + H_instrument(Q)                        ← U39: UNKNOWN (not automatically Q²)
    + H_equipment(Q)                         ← UNKNOWN or MANUFACTURER_CURVE
```

## Rules
- U40 (minimum required inlet pressure) must NOT vary with Q².
- U39 (instrument drop) must NOT default to Q² without curve or documented criterion.
- Equipment internal drop should use manufacturer curve when available.
