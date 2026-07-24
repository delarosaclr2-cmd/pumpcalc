# Future Pressure Configuration UI Specification — Hito 5.4

## Section: Requisitos de presión del sistema y equipos

A configurable table to manage pressure terms that are not standard pipe/accessory losses.

### Table columns

| Column | Type | Notes |
|--------|------|-------|
| Activo | checkbox | Whether term contributes |
| Nombre | text | Human-readable label |
| Tipo de término | dropdown | See types below |
| Valor | number | Pressure value |
| Unidad | dropdown | psig, psia, psi(diff), bar(g), bar(a), kPa(g), kPa(a), mH2O, ft agua, ft fluido |
| Referencia de presión | dropdown | GAUGE, ABSOLUTE, DIFFERENTIAL, VACUUM, UNKNOWN |
| Dependencia con caudal | dropdown | FLOW_INDEPENDENT, QUADRATIC_WITH_FLOW, MANUFACTURER_CURVE, USER_DEFINED, UNKNOWN |
| Caudal de diseño | number (optional) | Design flow rate in GPM |
| Nodo inicial | text (optional) | Hydraulic node ID |
| Nodo final | text (optional) | Hydraulic node ID |
| Fuente | text | Source of the value (workbook cell, manual input, etc.) |
| Regla de combinación | dropdown | MAXIMUM_REQUIREMENT, ADDITIVE, ALTERNATIVE_SCENARIOS, USER_DEFINED |
| Confianza | text | Confidence level |
| Notas | text (optional) | Free-text notes |

### Selectable term types

- Caída de presión de instrumento (INSTRUMENT_PRESSURE_DROP)
- Caída de presión interna del equipo (EQUIPMENT_INTERNAL_PRESSURE_DROP)
- Presión mínima requerida en la entrada (MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE)
- Presión normal de operación del recipiente (RECEIVING_VESSEL_OPERATING_PRESSURE)

### Controls

- Add term
- Delete term
- Duplicate term
- Activate/deactivate term
- Select pressure reference
- Select flow dependency
- Enter design flow rate
- Upload ΔP–Q curve (list of (flow_gpm, pressure_drop_psi) points)
- Select start/end nodes
- Select combination rule
- Show conversion to ft and m of fluid
- Show whether term is treated as loss or boundary condition
- Warn on potential overlaps

### Warnings

| Code | Condition |
|------|-----------|
| PRESSURE_REFERENCE_REQUIRED | pressure_reference is UNKNOWN |
| PRESSURE_BOUNDARY_OVERLAP | Two boundary conditions share a node |
| POSSIBLE_DOUBLE_COUNTING | Term appears in multiple categories |
| MISSING_DESIGN_FLOW | Flow-dependent term has no design flow |
| MISSING_PRESSURE_CURVE | Equipment drop without ΔP–Q curve |
| ABSOLUTE_PRESSURE_REQUIRES_REFERENCE_BOUNDARY | Absolute pressure without suction boundary |
| ADDITIVE_RULE_REQUIRES_CONFIRMATION | ADDITIVE combination without explicit confirmation |

### Loss vs Boundary classification

| Term type | Classification |
|-----------|--------------|
| INSTRUMENT_PRESSURE_DROP | **Loss** (irreversible) |
| EQUIPMENT_INTERNAL_PRESSURE_DROP | **Loss** (irreversible) |
| MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE | **Boundary condition** (not a loss) |
| RECEIVING_VESSEL_OPERATING_PRESSURE | **Boundary condition** (not a loss) |

### Current case mapping

| Source | Type | Loss or Boundary | Included in accessory_minor_losses? |
|--------|------|-----------------|-------------------------------------|
| U39 (0.36 psi) | INSTRUMENT_PRESSURE_DROP | Loss | **No** — separated |
| U40 (79.77 psi) | MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE | Boundary | **No** — separated |
