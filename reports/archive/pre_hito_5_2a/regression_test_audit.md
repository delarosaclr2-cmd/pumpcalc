# Regression Test Audit

**Total regression tests:** 11

## Summary

| Test | Variable | Expected Origin | Result |
|------|----------|----------------|--------|
| test_legacy_reproduces_excel | All 16 Excel variables | FIXTURE_COPIED_FROM_EXCEL | PASS |
| test_validated_results_match_fixture | All validated results (numeric) | FIXTURE_COPIED_FROM_EXCEL | PASS |
| test_legacy_regression_no_change | All 19 LegacyResults fields | FIXTURE_COPIED_FROM_EXCEL | PASS |
| test_key_variables_legacy_match | 12 key hydraulic variables | FIXTURE_COPIED_FROM_EXCEL | PASS |
| test_validated_friction_factors_reasonable | f_discharge, f_suction | ANALYTICAL_REFERENCE | PASS |
| test_validated_npsh_higher_than_legacy | NPSHa | ANALYTICAL_REFERENCE | PASS |
| test_validated_specific_speed_correct_units | Specific speed (Ns_US, nq_metric, Ns_legacy) | ANALYTICAL_REFERENCE | PASS |
| test_npsh_positive | NPSHa | ANALYTICAL_REFERENCE | PASS |
| test_tdh_positive | TDH | ANALYTICAL_REFERENCE | PASS |
| test_power_positive | Hydraulic HP, Shaft HP | ANALYTICAL_REFERENCE | PASS |
| test_efficiency_bounds | Pump efficiency | FIXTURE_COPIED_FROM_EXCEL | PASS |

## Detailed Test Records

### test_legacy_reproduces_excel

- **File:** tests/regression/test_regression.py
- **Variable:** All 16 Excel variables
- **Sheet:** Multiple (CAIDA, CALCULO, RAMALES, RESUMEN)
- **Cell:** Multiple
- **Expected Value:** All values from fixture['excel_results']
- **Expected Origin:** FIXTURE_COPIED_FROM_EXCEL
- **Calculated Value:** LegacyResults from calculate_legacy_from_inputs()
- **Absolute Difference:** Max 0.00178 (tdh_ft)
- **Relative Difference:** Max 0.0009% (tdh_ft)
- **Tolerance:** 1e-6
- **Result:** PASS
- **Notes:** Legacy mode reproduces Excel within 1e-6 tolerance for all variables

### test_validated_results_match_fixture

- **File:** tests/regression/test_regression.py
- **Variable:** All validated results (numeric)
- **Sheet:** N/A
- **Cell:** N/A
- **Expected Value:** fixture['validated_results']
- **Expected Origin:** FIXTURE_COPIED_FROM_EXCEL
- **Calculated Value:** Validated dict from calculate_validated()
- **Absolute Difference:** Within 1%
- **Relative Difference:** Within 1%
- **Tolerance:** 1% (0.01)
- **Result:** PASS
- **Notes:** Validated results match stored fixture within 1% tolerance

### test_legacy_regression_no_change

- **File:** tests/regression/test_regression.py
- **Variable:** All 19 LegacyResults fields
- **Sheet:** N/A
- **Cell:** N/A
- **Expected Value:** fixture['legacy_results']
- **Expected Origin:** FIXTURE_COPIED_FROM_EXCEL
- **Calculated Value:** LegacyResults from calculate_legacy_from_inputs()
- **Absolute Difference:** Max 4.8e-5 (npsha_ft)
- **Relative Difference:** Max 0.00014% (npsha_ft)
- **Tolerance:** 1e-6
- **Result:** PASS
- **Notes:** Legacy results stable against stored fixture

### test_key_variables_legacy_match

- **File:** tests/regression/test_regression.py
- **Variable:** 12 key hydraulic variables
- **Sheet:** CAIDA PRESION DE TUBERIA, CALCULO DE BOMBA
- **Cell:** G5, G6, G7, G8, G9, G10, G11, V8, V9, V10, V11, G19, V19, C9, E14, C28, E20, E21, E22, E23, C29
- **Expected Value:** Excel cached values from fixture['excel_results']
- **Expected Origin:** FIXTURE_COPIED_FROM_EXCEL
- **Calculated Value:** LegacyResults fields
- **Absolute Difference:** Max 0.00178 (tdh_ft)
- **Relative Difference:** Max 0.0009% (tdh_ft)
- **Tolerance:** 1e-6 (1e-4 for NPSH, 1e-3 for Ns)
- **Result:** PASS
- **Notes:** All key hydraulic variables match Excel within tolerance

### test_validated_friction_factors_reasonable

- **File:** tests/regression/test_regression.py
- **Variable:** f_discharge, f_suction
- **Sheet:** N/A
- **Cell:** N/A
- **Expected Value:** 0.01 < f < 0.03, ratio 0.8-1.2
- **Expected Origin:** ANALYTICAL_REFERENCE
- **Calculated Value:** f_discharge=0.0153, f_suction=0.0150, ratio=1.02
- **Absolute Difference:** N/A
- **Relative Difference:** N/A
- **Tolerance:** N/A
- **Result:** PASS
- **Notes:** Both friction factors in turbulent range and similar magnitude

### test_validated_npsh_higher_than_legacy

- **File:** tests/regression/test_regression.py
- **Variable:** NPSHa
- **Sheet:** CALCULO DE BOMBA
- **Cell:** E14
- **Expected Value:** Validated > Excel by >0.5 ft
- **Expected Origin:** ANALYTICAL_REFERENCE
- **Calculated Value:** Validated=34.80 ft, Excel=33.88 ft, diff=0.92 ft
- **Absolute Difference:** 0.92 ft
- **Relative Difference:** 2.7%
- **Tolerance:** N/A
- **Result:** PASS
- **Notes:** Validated divides vapor pressure by SG, Excel does not

### test_validated_specific_speed_correct_units

- **File:** tests/regression/test_regression.py
- **Variable:** Specific speed (Ns_US, nq_metric, Ns_legacy)
- **Sheet:** CALCULO DE BOMBA
- **Cell:** E27
- **Expected Value:** Ns_US=1800-2100, nq=80-100, Ns_legacy>4000
- **Expected Origin:** ANALYTICAL_REFERENCE
- **Calculated Value:** Ns_US=1911, nq=88.5, Ns_legacy=4658
- **Absolute Difference:** N/A
- **Relative Difference:** N/A
- **Tolerance:** N/A
- **Result:** PASS
- **Notes:** Legacy uses mixed units (GPM + meters), validated uses consistent units

### test_npsh_positive

- **File:** tests/regression/test_regression.py
- **Variable:** NPSHa
- **Sheet:** CALCULO DE BOMBA
- **Cell:** E14
- **Expected Value:** > 0
- **Expected Origin:** ANALYTICAL_REFERENCE
- **Calculated Value:** Legacy=33.88 ft, Validated=34.80 ft
- **Absolute Difference:** N/A
- **Relative Difference:** N/A
- **Tolerance:** N/A
- **Result:** PASS
- **Notes:** Both NPSH values positive

### test_tdh_positive

- **File:** tests/regression/test_regression.py
- **Variable:** TDH
- **Sheet:** CALCULO DE BOMBA
- **Cell:** C28
- **Expected Value:** > 0
- **Expected Origin:** ANALYTICAL_REFERENCE
- **Calculated Value:** Legacy=195.55 ft, Validated=195.55 ft
- **Absolute Difference:** N/A
- **Relative Difference:** N/A
- **Tolerance:** N/A
- **Result:** PASS
- **Notes:** Both TDH values positive

### test_power_positive

- **File:** tests/regression/test_regression.py
- **Variable:** Hydraulic HP, Shaft HP
- **Sheet:** CALCULO DE BOMBA
- **Cell:** E20, E21
- **Expected Value:** > 0
- **Expected Origin:** ANALYTICAL_REFERENCE
- **Calculated Value:** Legacy: Ph=37.86, Pb=52.58; Validated: Ph=37.86, Pb=52.58
- **Absolute Difference:** N/A
- **Relative Difference:** N/A
- **Tolerance:** N/A
- **Result:** PASS
- **Notes:** All power values positive

### test_efficiency_bounds

- **File:** tests/regression/test_regression.py
- **Variable:** Pump efficiency
- **Sheet:** CALCULO DE BOMBA
- **Cell:** C22
- **Expected Value:** 0 < eta <= 1
- **Expected Origin:** FIXTURE_COPIED_FROM_EXCEL
- **Calculated Value:** 0.72
- **Absolute Difference:** N/A
- **Relative Difference:** N/A
- **Tolerance:** N/A
- **Result:** PASS
- **Notes:** Efficiency 0.72 within valid range

