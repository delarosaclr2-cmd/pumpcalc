# Hydraulic Discrepancies Report

## Overview

This report details all discrepancies found between the Excel workbook (legacy) calculations and the validated independent hydraulic engine.

## Discrepancy Classification

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 2 | Errors that affect safety or pump selection |
| **HIGH** | 3 | Significant engineering errors |
| **MEDIUM** | 3 | Notable differences requiring review |
| **LOW** | 4 | Minor differences, rounding, or documentation |
| **INFO** | 1 | Hito 5.4A boundary model completions |

## Discrepancies

### DISCREP-001: Suction Friction Factor Uses Laminar Formula for Turbulent Flow
**Severity: CRITICAL**
- **Location:** `CAIDA PRESION DE TUBERIA!V16`
- **Excel Formula:** `=64/V11` (laminar: f = 64/Re)
- **Actual Reynolds:** 462,915 (turbulent)
- **Validated f:** 0.0150 (Colebrook-White)
- **Excel f:** 0.000138
- **Error:** -99% (100x underestimation)
- **Impact:** Suction pipe friction loss underestimated by ~100x
- **Recommendation:** Replace with Colebrook-White or Swamee-Jain for all regimes

### DISCREP-002: Discharge Friction Factor Hardcoded
**Severity: HIGH**
- **Location:** `CAIDA PRESION DE TUBERIA!G17`
- **Excel Value:** 0.0272 (hardcoded constant)
- **Validated f:** 0.0153 (Colebrook-White at Re=768,553)
- **Error:** +78% overestimation
- **Impact:** Discharge pipe friction loss overestimated by ~2x
- **Recommendation:** Calculate friction factor from Reynolds and relative roughness

### DISCREP-003: NPSH Vapor Pressure Not Corrected for Specific Gravity
**Severity: HIGH**
- **Location:** `CALCULO DE BOMBA!E14`
- **Excel Formula:** `((C8+E8)*(2.31/E11))+C9-C11-C14-E9`
- **Issue:** Vapor pressure term `E9` in ft water not divided by SG
- **Excel NPSHa:** 33.88 ft
- **Validated NPSHa:** 34.80 ft
- **Difference:** +0.92 ft (2.7%)
- **Root Cause:** `E9` = 1.846 ft water (absolute), should be `E9/E11` = 1.855 ft fluid
- **Recommendation:** Divide vapor pressure head by specific gravity

### DISCREP-004: Specific Speed Uses Mixed Units
**Severity: MEDIUM**
- **Location:** `CALCULO DE BOMBA!E27`
- **Excel Formula:** `=(C29*(E4^0.5))/(E24^0.75)`
- **Units:** Q in GPM, H in **meters** (E24 = C28*0.3048)
- **Excel Ns:** 4,658 (mixed units - WRONG)
- **Correct US Ns:** 1,911 (Q in GPM, H in ft)
- **Correct Metric nq:** 88.5 (Q in m³/s, H in m)
- **Impact:** Specific speed value meaningless for pump selection
- **Recommendation:** Use consistent units: H in ft for US Ns, or convert Q to m³/s and H to m for metric nq

### DISCREP-005: Velocity Head Constant Approximation
**Severity: LOW**
- **Location:** Multiple accessory loss formulas (32.4*2)
- **Excel Value:** 32.4 (≈ g = 32.174 ft/s²)
- **Actual 2g:** 64.348 ft/s²
- **Excel 2g:** 64.8
- **Error:** +0.7%
- **Impact:** Minor overestimation of velocity head
- **Recommendation:** Use exact 32.174 or 64.348

### DISCREP-006: Atmospheric Pressure Fixed at Sea Level
**Severity: LOW**
- **Location:** `CALCULO DE BOMBA!C8`
- **Excel Value:** 14.7 psia (hardcoded)
- **Issue:** No altitude correction
- **Impact:** NPSHa error ~0.5 ft per 1000 ft elevation
- **Recommendation:** Add site altitude input

### DISCREP-007: Specific Speed RPM Hardcoded at 1700 for Torque
**Severity: LOW**
- **Location:** `CALCULO DE BOMBA!E23`
- **Excel Formula:** `=(E21*5252)/1700`
- **Actual Pump RPM:** 3600 (C29)
- **Impact:** Torque calculated at wrong speed
- **Recommendation:** Use C29 (actual RPM) instead of 1700

### DISCREP-008: Suction/Discharge Static Heads Hardcoded
**Severity: MEDIUM**
- **Locations:** `CALCULO DE BOMBA!C9` (=500/304.8), `C20` (=6.92), `C12` (=2.12*3.281)
- **Issue:** No traceability to piping drawings
- **Impact:** Geometry changes not reflected in calculations
- **Recommendation:** Link to piping layout inputs

### DISCREP-009: Accessory Loss Method Mixing K and Leq
**Severity: MEDIUM**
- **Location:** `TABLA DE ACCESORIOS` sheets
- **Formula:** `=((D*F)*($H$2^2)/(32.4*2))*H`
- **Issue:** D = ft (equivalent length), F = K factor, mixes methods
- **Impact:** Potential double-counting or unit confusion
- **Recommendation:** Standardize on K-method or Leq-method

### DISCREP-010: Velocity Conversion Constant 1.422 Unexplained
**Severity: MEDIUM**
- **Location:** `VELOCIDADES RECOMENDADAS!AB` column
- **Formula:** `=(AA*3.2808)/1.422`
- **Issue:** Constant 1.422 not documented
- **Derivation:** 3.2808/1.422 = 2.307 ≈ 2.31 (psi→ft water)
- **Impact:** Velocity recommendations in table may be incorrect
- **Recommendation:** Document or replace with explicit conversion

### DISCREP-011: Minimum Required Equipment Inlet Pressure Entry Dominates Discharge Fitting Losses
**Severity: HIGH**
- **Location:** `TABLA DE ACCESORIOS DESCARGA!U40`
- **Excel Value:** 79.77 PSI (hardcoded, no formula)
- **Cell Comment:** "PRESION DE OPERACION DEL EQUIPO"
- **Column Header (U3:U6):** "ESPESADOR DISCOS CARA" — does not match pressure data
- **User Confirmed Semantics:** MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE — manually added to guarantee minimum inlet pressure
- **Legacy Head:** 184.27 ft (×2.31)
- **Validated Head:** 185.01 ft (×144/(62.4×0.995), assuming gauge)
- **Classification:** MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE (user confirmed)
- **Pressure Reference:** UNKNOWN (pending — must confirm gauge or absolute)
- **Impact:** 98.2% of discharge fitting loss (188.56 ft) comes from this single entry. As a boundary condition (not a loss), it must be separated from accessory_minor_losses.
- **Hito 5.4A Resolution:** Absolute boundary model implemented. Source boundary computed as 14.7 psia (atm + 0 psig gauge).  
  - GAUGE: difference = 79.77 psi, head = 185.01 ft  
  - ABSOLUTE: difference = 79.77 - 14.7 = 65.07 psi, head = 150.92 ft  
  - UNKNOWN: returns PRESSURE_REFERENCE_REQUIRED — user must specify reference  
- **Recommendation:** Confirm pressure reference (GAUGE/ABSOLUTE), obtain equipment datasheet, verify minimum inlet pressure requirement. See `reports/hito_5_4a_summary.md`.

### DISCREP-012: U40 Pressure Reference Unknown — Absolute vs Gauge Ambiguity
**Severity: INFO**
- **Location:** `TABLA DE ACCESORIOS DESCARGA!U40`
- **Issue:** U40 pressure reference not confirmed (GAUGE, ABSOLUTE, or other)
- **Hito 5.4A Resolution:** Boundary model differentiates GAUGE vs ABSOLUTE via source boundary (14.7 psia)
  - **GAUGE scenario:** TDH = 196.30 ft (validated SG conversion)
  - **ABSOLUTE scenario:** TDH = 162.20 ft (79.77 psia - 14.7 psia → 65.07 psi difference)
  - **UNKNOWN scenario:** PRESSURE_REFERENCE_REQUIRED (user input pending)
- **Recommendation:** Confirm U40 pressure reference with equipment datasheet or process engineer

## Summary Table

| ID | Variable | Excel (workbook) | Legacy Python | Validated | Unit | Diff | Severity |
|----|----------|-------|--------|-----------|------|------|----------|
| 001 | f_suction | 0.000138 | 0.000138 | 0.0150 | - | +10,768% | CRITICAL |
| 002 | f_discharge | 0.0272 | 0.0272 | 0.0153 | - | -44% | HIGH |
| 003 | NPSHa | 33.88 | 33.88 | 34.80 | ft | +0.92 | HIGH |
| 004 | Ns (US) | 4,658 | 4,658 | 1,911 | - | -59% | MEDIUM |
| 005 | f (velocity head) | 32.4 | 32.4 | 32.174 | ft/s² | 0.7% | LOW |
| 006 | P_atm | 14.7 | 14.7 | site-specific | psia | varies | LOW |
| 007 | Torque RPM | 1700 | 1700 | 3600 | rpm | -53% | LOW |
| 008 | Static heads | hardcoded | hardcoded | from drawings | ft | varies | MEDIUM |
| 009 | Accessory method | mixed | mixed | K-method | - | - | MEDIUM |
| 010 | Velocity const | 1.422 | 1.422 | 2.31 | - | - | MEDIUM |
| 011 | Minimum inlet pressure | 79.77 (as psi) | 184.27 (legacy ft) | 185.01 (validated ft) | psi/ft | U40 as boundary, not loss | HIGH |
| 012 | U40 pressure reference | GAUGE: 185.01 ft | ABSOLUTE: 150.92 ft | UNKNOWN: not calculable | ft | GAUGE/ABSOLUTE/UNKNOWN | INFO |

Note: Hito 5.4A resolved the DISCREP-011 calculation path. If U40 is ABSOLUTE, TDH = 162.20 ft (150.92 ft above accessory+pipe+static). If GAUGE, TDH = 196.30 ft. The 34.1 ft difference underscores the need for reference confirmation (DISCREP-012).

## Recommendations Priority

1. **Immediate:** Fix suction friction factor (DISCREP-001)
2. **Immediate:** Fix discharge friction factor (DISCREP-002)
3. **Immediate:** Correct NPSH vapor pressure division by SG (DISCREP-003)
4. **High:** Fix specific speed units (DISCREP-004)
5. **High:** Link static heads to piping drawings (DISCREP-008)
6. **Medium:** Standardize accessory loss method (DISCREP-009)
7. **Medium:** Document velocity conversion constant (DISCREP-010)
8. **Low:** Use exact g = 32.174 (DISCREP-005)
9. **Low:** Add altitude input for atmospheric pressure (DISCREP-006)
10. **Low:** Fix torque RPM reference (DISCREP-007)
11. **Info:** Confirm U40 pressure reference (DISCREP-012)

## Validation Status

| Test | Status |
|------|--------|
| Unit tests (accessory audit, conversions, friction, NPSH, power, units) | 150 passed |
| Integration tests (legacy vs Excel, pipeline, torque, NPSH) | 22 passed |
| Hito 5.4 (semantic model, combination rules, boundary overlap) | 27 passed |
| Hito 5.4A (absolute boundary model, source boundary) | 16 passed |
| Sensitivity analysis | Completed |
| Independent validation | Completed |

---
*Generated: 2026-07-22 (updated for Hito 5.4A)*
*Project: KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C*