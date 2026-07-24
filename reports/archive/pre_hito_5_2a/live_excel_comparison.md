# Live Excel Comparison Report

**Generated:** 2026-07-22T11:40:34.774512

## Conditions

- Workbook: `working/KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm`
- Macros: Disabled
- Events: Disabled
- Alerts: Disabled
- External links: Not updated
- Calculation: `CalculateFullRebuild`
- Mode: Read-only, no changes saved

## Summary

| Metric | Value |
|--------|-------|
| Total variables compared | 28 |
| Exact matches | 15 |
| Within tolerance | 0 |
| Formula reproduction error | 13 |
| Outside tolerance | 0 |
| Not comparable | 0 |
| Exact match rate | 53.57% |
| Structure match rate (exact + formula reproduction) | 100.00% |

## Detailed Comparison

| Variable | Sheet | Cell | Formula | Excel (live) | Legacy Python | Abs Diff | Rel Diff | Tolerance | Status |
|----------|-------|------|---------|-------------|--------------|---------|---------|-----------|--------|
| discharge_diameter_in | CAIDA PRESION DE TUBERIA | G8 | `=G7*(G5/G6)^0.5` | 6.048364477 | 6.048364477 | 0.000000e+00 | 0.000000e+00 | 1e-06 abs / 1e-06 rel | EXACT_MATCH |
| suction_diameter_in | CAIDA PRESION DE TUBERIA | V8 | `=V7*(V5/V6)^0.5` | 10.04176105 | 10.04176105 | 0.000000e+00 | 0.000000e+00 | 1e-06 abs / 1e-06 rel | EXACT_MATCH |
| re_discharge | CAIDA PRESION DE TUBERIA | G11 | `=50.6*G5*G9/(G8*G10)` | 768552.5214 | 768552.5214 | 0.000000e+00 | 0.000000e+00 | 0.001 abs / 1e-06 rel | EXACT_MATCH |
| re_suction | CAIDA PRESION DE TUBERIA | V11 | `=50.6*V5*V9/(V8*V10)` | 462915.3938 | 462915.3938 | 0.000000e+00 | 0.000000e+00 | 0.001 abs / 1e-06 rel | EXACT_MATCH |
| f_discharge | CAIDA PRESION DE TUBERIA | G17 | `0.0272` | 0.0272 | 0.0272 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| f_suction | CAIDA PRESION DE TUBERIA | V16 | `=64/V11` | 0.0001382542055 | 0.0001382542055 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| hf_per_ft_discharge | CAIDA PRESION DE TUBERIA | G19 | `=(((G17*G16*G9*(G5^2))/(G8^5))*2.3071)*G18` | 0.04451507679 | 0.04451507679 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| hf_per_ft_suction | CAIDA PRESION DE TUBERIA | V19 | `=(((V17*V16*V9*(V5^2))/(V8^5))*2.3071)*V18` | 0.003753033858 | 0.003753033858 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| static_suction_head_ft | CALCULO DE BOMBA | C9 | `=500/304.8` | 1.640419948 | 1.640419948 | 0.000000e+00 | 0.000000e+00 | 1e-06 abs / 1e-06 rel | EXACT_MATCH |
| suction_fitting_losses_ft | CALCULO DE BOMBA | C11 | `='TABLA DE ACCESORIOS SUCCION'!I40` | 0.01682488889 | 0.0168 | -2.488889e-05 | -1.479290e-03 | 0.0001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |
| suction_pipe_losses_ft | CALCULO DE BOMBA | C14 | `=C12*C13` | 0.02610505267 | 0.02610505267 | 0.000000e+00 | 0.000000e+00 | 0.0001 abs / 0.001 rel | EXACT_MATCH |
| static_head_diff_ft | CALCULO DE BOMBA | C21 | `=C20-C9` | 5.279580052 | 5.279580052 | 0.000000e+00 | 0.000000e+00 | 0.0001 abs / 0.001 rel | EXACT_MATCH |
| pump_efficiency | CALCULO DE BOMBA | C22 | `0.72` | 0.72 | 0.72 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| discharge_fitting_losses_ft | CALCULO DE BOMBA | C24 | `='TABLA DE ACCESORIOS DESCARGA'!I41` | 188.5586148 | 188.56 | 1.385185e-03 | 7.346178e-06 | 0.001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |
| discharge_pipe_losses_ft | CALCULO DE BOMBA | C26 | `=RAMALES!F19` | 1.669988617 | 1.67 | 1.138348e-05 | 6.816501e-06 | 0.0001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |
| tdh_ft | CALCULO DE BOMBA | C28 | `=C11+C14+C21+C24+C26` | 195.5511134 | 195.5529 | 1.786575e-03 | 9.136100e-06 | 0.005 abs / 1e-05 rel | FORMULA_REPRODUCTION_ERROR |
| tdh_m | CALCULO DE BOMBA | E24 | `=C28*0.3048` | 59.60397937 | 59.60452392 | 5.445479e-04 | 9.136100e-06 | 0.002 abs / 1e-05 rel | FORMULA_REPRODUCTION_ERROR |
| rpm | CALCULO DE BOMBA | C29 | `3600` | 3600 | 3600 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| flow_gpm | CALCULO DE BOMBA | E4 | `='CAIDA PRESION DE TUBERIA'!G5` | 770.5 | 770.5 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| specific_gravity | CALCULO DE BOMBA | E11 | `=BUSCARV(A32,gravedadespecifica,5,FALSE)` | 0.995 | 0.995 | 0.000000e+00 | 0.000000e+00 | 1e-09 abs / 1e-08 rel | EXACT_MATCH |
| vapor_pressure_head_ft | CALCULO DE BOMBA | E9 | `=BUSCARV(A32,presionvapor,4,FALSE)` | 1.845738397 | 1.8457 | -3.839662e-05 | -2.080285e-05 | 0.001 abs / 0.0001 rel | FORMULA_REPRODUCTION_ERROR |
| npsha_ft | CALCULO DE BOMBA | E14 | `=((C8+E8)*(2.31/E11))+C9-C11-C14-E9` | 33.8793898 | 33.87943819 | 4.839067e-05 | 1.428322e-06 | 0.001 abs / 1e-05 rel | FORMULA_REPRODUCTION_ERROR |
| hydraulic_hp | CALCULO DE BOMBA | E20 | `=(E4*C28*E11)/3960` | 37.85827582 | 37.85862169 | 3.458770e-04 | 9.136100e-06 | 0.0001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |
| shaft_hp | CALCULO DE BOMBA | E21 | `=E20/C22` | 52.58093863 | 52.58141902 | 4.803847e-04 | 9.136100e-06 | 0.0001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |
| shaft_kw | CALCULO DE BOMBA | E22 | `=E21*0.7456` | 39.20434784 | 39.20470602 | 3.581749e-04 | 9.136100e-06 | 0.0001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |
| torque_lbft | CALCULO DE BOMBA | E23 | `=(E21*5252)/1700` | 162.4441704 | 162.4456545 | 1.484106e-03 | 9.136100e-06 | 0.001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |
| specific_speed_legacy | CALCULO DE BOMBA | E27 | `=(C29*(E4^0.5))/(E24^0.75)` | 4658.352841 | 4658.320921 | -3.191913e-02 | -6.852021e-06 | 0.01 abs / 1e-05 rel | FORMULA_REPRODUCTION_ERROR |
| minor_losses_total_ft | CALCULO DE BOMBA | C11+C24 | `C11: ='TABLA DE ACCESORIOS SUCCION'!I40 + C24: ='TABLA DE ACCESORIOS DESCARGA'!I41` | 188.5754397 | 188.5768 | 1.360296e-03 | 7.213539e-06 | 0.001 abs / 0.001 rel | FORMULA_REPRODUCTION_ERROR |

## Context Cells

| Variable | Sheet | Cell | Value | Formula | Description |
|----------|-------|------|-------|---------|-------------|
| Q_GPM | CAIDA PRESION DE TUBERIA | G5 | 770.5 | `770.5` | Flow (discharge) |
| f_discharge | CAIDA PRESION DE TUBERIA | G17 | 0.0272 | `0.0272` | Friction factor discharge |
| f_suction | CAIDA PRESION DE TUBERIA | V16 | 0.0001382542055 | `=64/V11` | Friction factor suction (64/Re) |
| f_factor_v17 | CAIDA PRESION DE TUBERIA | V17 | 0.0272 | `0.0272` | V17 constant |
| D_nom_discharge_in | CAIDA PRESION DE TUBERIA | G12 | 6 | `6` | Nominal D discharge |
| D_nom_suction_in | CAIDA PRESION DE TUBERIA | V12 | 10 | `10` | Nominal D suction |
| roughness_disch_ft | CAIDA PRESION DE TUBERIA | G14 | 0.00012 | `=BUSCARV(A21,RUGOSIDAD,3)` | Abs roughness discharge |
| roughness_suct_ft | CAIDA PRESION DE TUBERIA | V14 | 0.00012 | `=BUSCARV(B21,RUGOSIDAD,3)` | Abs roughness suction |
| eps_rel_discharge | CAIDA PRESION DE TUBERIA | G15 | 0.00024 | `=G14/(G12/12)` | Relative roughness discharge |
| eps_rel_suction | CAIDA PRESION DE TUBERIA | V15 | 0.000144 | `=V14/(V12/12)` | Relative roughness suction |
| f_lookup_cpl | CAIDA PRESION DE TUBERIA | G16 | 0.00013 | `=BUSCARV(A20,OUTPIPES,8,FALSE)` | f lookup from OUTPIPES |
| G18_factor | CAIDA PRESION DE TUBERIA | G18 | 1.2 | `1.2` | G18 multiplier |
| V18_factor | CAIDA PRESION DE TUBERIA | V18 | 1.2 | `1.2` | V18 multiplier |
| P_atm_psi | CALCULO DE BOMBA | C8 | 14.7 | `=14.7` | Atmospheric pressure |
| P_vessel_psi | CALCULO DE BOMBA | E8 | 0 | `0` | Vessel pressure |
| vapor_press_ft | CALCULO DE BOMBA | E9 | 1.845738397 | `=BUSCARV(A32,presionvapor,4,FALSE)` | Vapor pressure head |
| SG | CALCULO DE BOMBA | E11 | 0.995 | `=BUSCARV(A32,gravedadespecifica,5,FALSE)` | Specific gravity |
| static_disch_ft | CALCULO DE BOMBA | C20 | 6.92 | `6.92` | Static discharge head |

## Formula Reproduction Errors

The following variables have correct formula structure but use **hardcoded inputs** in the Python LEGACY calculator instead of dynamic cell references:

| Variable | Sheet | Cell | Excel (live) | Legacy | Abs Diff | Rel Diff |
|----------|-------|------|-------------|--------|---------|--------|
| suction_fitting_losses_ft | CALCULO DE BOMBA | C11 | 0.01682488889 | 0.0168 | -2.488889e-05 | -1.479290e-03 |
| discharge_fitting_losses_ft | CALCULO DE BOMBA | C24 | 188.5586148 | 188.56 | 1.385185e-03 | 7.346178e-06 |
| discharge_pipe_losses_ft | CALCULO DE BOMBA | C26 | 1.669988617 | 1.67 | 1.138348e-05 | 6.816501e-06 |
| tdh_ft | CALCULO DE BOMBA | C28 | 195.5511134 | 195.5529 | 1.786575e-03 | 9.136100e-06 |
| tdh_m | CALCULO DE BOMBA | E24 | 59.60397937 | 59.60452392 | 5.445479e-04 | 9.136100e-06 |
| vapor_pressure_head_ft | CALCULO DE BOMBA | E9 | 1.845738397 | 1.8457 | -3.839662e-05 | -2.080285e-05 |
| npsha_ft | CALCULO DE BOMBA | E14 | 33.8793898 | 33.87943819 | 4.839067e-05 | 1.428322e-06 |
| hydraulic_hp | CALCULO DE BOMBA | E20 | 37.85827582 | 37.85862169 | 3.458770e-04 | 9.136100e-06 |
| shaft_hp | CALCULO DE BOMBA | E21 | 52.58093863 | 52.58141902 | 4.803847e-04 | 9.136100e-06 |
| shaft_kw | CALCULO DE BOMBA | E22 | 39.20434784 | 39.20470602 | 3.581749e-04 | 9.136100e-06 |
| torque_lbft | CALCULO DE BOMBA | E23 | 162.4441704 | 162.4456545 | 1.484106e-03 | 9.136100e-06 |
| specific_speed_legacy | CALCULO DE BOMBA | E27 | 4658.352841 | 4658.320921 | -3.191913e-02 | -6.852021e-06 |
| minor_losses_total_ft | CALCULO DE BOMBA | C11+C24 | 188.5754397 | 188.5768 | 1.360296e-03 | 7.213539e-06 |

### Root Cause

The Excel workbook computes these values from dynamic cell references (e.g., `C11='TABLA DE ACCESORIOS SUCCION'!I40`, `C24='TABLA DE ACCESORIOS DESCARGA'!I41`, `C26=RAMALES!F19`). The Python LEGACY calculator instead stores **hardcoded approximations** of these values (e.g., 0.0168 instead of 0.0168249, 188.56 instead of 188.5586, 1.67 instead of 1.66999).

These small rounding errors propagate through TDH, power, and specific speed calculations. The formula **structure** is identical between Excel and LEGACY Python; only the input precision differs.

**Fix:** Replace hardcoded input values with dynamic calculations that reproduce the Excel cell references.

## Variables Outside Tolerance

All variables are within defined tolerance.

## Status Definitions

| Status | Description |
|--------|-------------|
| EXACT_MATCH | No numerical difference (`abs_diff == 0.0`) |
| WITHIN_TOLERANCE | Difference within allowed tolerance, formula structure correct |
| FORMULA_REPRODUCTION_ERROR | Formula structure correct, but legacy uses hardcoded inputs instead of dynamic cell references |
| OUTSIDE_TOLERANCE | Difference exceeds allowed tolerance |
| NOT_COMPARABLE | One or both values unavailable |
| MAPPING_ERROR | Cell reference could not be resolved |
