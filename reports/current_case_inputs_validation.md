# Current Case Inputs Validation Report

**Generated:** 2026-07-22T12:17:00.256422

## Summary

- **Old CSV:** `C:\PUMPCALC\reports\current_case_inputs.csv`
- **V2 CSV:** `C:\PUMPCALC\reports\current_case_inputs_v2.csv`
- **Variables:** 28
- **Columns:** 11
- **Validation errors (old):** 4
- **Warnings:** 0

## Errors in Old CSV

- Line 5: got 10 cols, expected 9
- Line 23: got 8 cols, expected 9
- Line 24: got 8 cols, expected 9
- Line 46: got 10 cols, expected 9

## Validation Checks

### Column Count

Expected: 11, Actual: 11 → **PASS**

### Required Headers

Missing: [] → **PASS**

### Numerical Values

All values numeric → **PASS**

### Duplicates

No duplicates → **PASS**

### Missing Fields

Missing fields: 56/308 (18.2%) → **PASS**

## Variables

| # | Variable ID | Value | Unit | Source | Cell | Confidence |
|---|-------------|-------|------|--------|------|------------|
| 1 | flow_gpm | 770.5 | GPM | CAIDA PRESION DE TUBERIA | G5 | HIGH |
| 2 | density_lbm_ft3 | 62.0 | lbm/ft3 | CAIDA PRESION DE TUBERIA | G9 | HIGH |
| 3 | specific_gravity | 0.995 | - | CALCULO DE BOMBA | E11 | HIGH |
| 4 | dynamic_viscosity_cp | 0.52 | cP | CAIDA PRESION DE TUBERIA | G10 | HIGH |
| 5 | temperature_f | 95.0 | degF | VELOCIDADES RECOMENDADAS | AA13 | HIGH |
| 6 | vapor_pressure_value | 0.8 | psia | VELOCIDADES RECOMENDADAS | AA13 | HIGH |
| 7 | suction_target_velocity_fps | 3.12 | ft/s | CAIDA PRESION DE TUBERIA | V6 | MEDIUM |
| 8 | suction_inside_diameter_in | 10.041761045944389 | in | CAIDA PRESION DE TUBERIA | V8 | HIGH |
| 9 | suction_nominal_diameter_in | 10.0 | in | CAIDA PRESION DE TUBERIA | V12 | HIGH |
| 10 | suction_absolute_roughness_ft | 0.00012 | ft | CAIDA PRESION DE TUBERIA | V14 | HIGH |
| 11 | suction_length_ft | 6.95572 | ft | CALCULO DE BOMBA | C12 | UNVERIFIED |
| 12 | suction_static_head_ft | 1.6404199475065617 | ft | CALCULO DE BOMBA | C9 | UNVERIFIED |
| 13 | suction_fitting_losses_ft | 0.01682488888888889 | ft | CALCULO DE BOMBA | C11 | HIGH |
| 14 | discharge_target_velocity_fps | 8.6 | ft/s | CAIDA PRESION DE TUBERIA | G6 | MEDIUM |
| 15 | discharge_inside_diameter_in | 6.048364477182011 | in | CAIDA PRESION DE TUBERIA | G8 | HIGH |
| 16 | discharge_nominal_diameter_in | 6.0 | in | CAIDA PRESION DE TUBERIA | G12 | HIGH |
| 17 | discharge_absolute_roughness_ft | 0.00012 | ft | CAIDA PRESION DE TUBERIA | G14 | HIGH |
| 18 | discharge_length_ft | 36.0 | ft | CALCULO DE BOMBA | C25 | HIGH |
| 19 | discharge_static_head_ft | 6.92 | ft | CALCULO DE BOMBA | C20 | UNVERIFIED |
| 20 | discharge_fitting_losses_ft | 188.5586148 | ft | CALCULO DE BOMBA | C24 | HIGH |
| 21 | atmospheric_pressure_psia | 14.7 | psia | CALCULO DE BOMBA | C8 | MEDIUM |
| 22 | vessel_pressure | 0.0 | psig | CALCULO DE BOMBA | E8 | HIGH |
| 23 | pump_efficiency | 0.72 | - | CALCULO DE BOMBA | C22 | MEDIUM |
| 24 | pump_rpm | 3600.0 | rpm | CALCULO DE BOMBA | C29 | HIGH |
| 25 | legacy_torque_rpm | 1700.0 | rpm | CALCULO DE BOMBA | E23 | LOW |
| 26 | service_factor | 1.0 | - | CALCULO DE BOMBA | C6 | MEDIUM |
| 27 | number_of_stages | 1 | - | - | - | HIGH |
| 28 | number_of_suction_eyes | 1 | - | - | - | MEDIUM |
