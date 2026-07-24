# Source Boundary Definition

## System Boundary Node

The source boundary is the physical location where pressure is referenced.

| Field | Value |
|-------|-------|
| boundary_type | FREE_SURFACE (tank/vented) |
| atmospheric_pressure_psia | 14.7 (sea level) |
| vessel_pressure | 0.0 psig |
| vessel_pressure_type | GAUGE |
| computed_source_abs_psia | 14.7 |

## BoundaryType Enum

| Value | Description |
|-------|-------------|
| FREE_SURFACE | Free Surface |
| VESSEL_GAS_SPACE | Vessel Gas Space |
| PUMP_SUCTION_FLANGE | Pump Suction Flange |
| PIPE_NODE | Pipe Node |
| EQUIPMENT_INLET | Equipment Inlet |
| EQUIPMENT_OUTLET | Equipment Outlet |

## GAUGE vs ABSOLUTE vs VACUUM

- **GAUGE**: source_abs = atm + vessel_pressure
- **ABSOLUTE**: source_abs = vessel_pressure (already absolute)
- **VACUUM**: source_abs = atm - vessel_pressure

## Current Case: Open Tank at Atmospheric Pressure

`source_abs = 14.7 + 0.0 = 14.7 psia`