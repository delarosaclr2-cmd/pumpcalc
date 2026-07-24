# Domain Module Responsibility — Hito 5.4B

## system_boundaries.py

- Boundary types (OPEN_VESSEL, PRESSURIZED_VESSEL, etc.)
- Pressure conversion from boundary to absolute
- Pressure difference between boundaries
- Status and warnings (CalculationStatus, PressureBoundaryWarning)

## pressure_requirements.py

- Requirement types (PressureTermType)
- Pressure references (PressureReference)
- Conversion of pressure terms to head
- Combination rules
- Semantic TDH balances
- System curve component classification

## accessory_losses.py

- K coefficients (K_coefficient)
- Leq/D (equivalent length / diameter ratio)
- Equivalent length calculation
- Accessory inventory and reconstruction
- Minor loss audit and Pareto analysis

## Boundaries

| Module | Imports from |
|--------|-------------|
| system_boundaries | units, (stdlib) |
| pressure_requirements | system_boundaries, accessory_losses, units |
| accessory_losses | units, fluids |

No circular dependencies detected.
No accessory_losses -> system_boundaries or accessory_losses -> pressure_requirements imports exist.
