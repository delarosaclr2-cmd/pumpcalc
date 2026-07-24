# Technical Review Corrections

**Generated:** 2026-07-20T15:40:28.243707

This document records all corrections to preliminary findings after critical re-review.

## FIND-005

**Previous Conclusion:** PROBABLE_ERROR - 50.6 factor assumes specific gravity, not density

**Previous Evidence:** Re = 50.6 × Q × SG / (D × μ) standard formula; workbook uses density ρ

**New Derivation:**
```
Re = ρVD/μ with Q=GPM, ρ=lbm/ft³, D=in, μ=cP. Derived constant = 50.66. Workbook uses ρ=62 lbm/ft³ from OUTPIPES, not SG.
```

**Corrected Conclusion:** FORMULA_CORRECT_WITH_DENSITY

**Correction Reason:** Standard formula Re=50.6×Q×SG/(D×μ) assumes SG relative to water (ρ=62.4×SG). Workbook fluid tables provide mass density directly in lbm/ft³. Formula is correct for given units.

**Project Impact:** Hydraulic engine can use workbook Re formula directly; no correction needed

---

## FIND-003

**Previous Conclusion:** PROBABLE_ERROR - Patm(psia)+Pvessel(psig) sums absolute + gauge

**Previous Evidence:** C8=14.7 psia, E8=0 psig; formula (C8+E8)*2.31/SG

**New Derivation:**
```
Standard NPSH: P_abs = Patm_abs + Pvessel_gauge. For open tank Pvessel=0 psig → 14.7 psia. Formula correct IF E8 is gauge pressure (standard convention). Vapor pressure E9 in ft water needs /SG correction.
```

**Corrected Conclusion:** CORRECT_FOR_GAUGE_VESSEL_PRESSURE

**Correction Reason:** Vessel pressure is conventionally given in gauge. Sum Patm_abs + Pvessel_gauge = absolute pressure at liquid surface. Formula dimensionally consistent.

**Project Impact:** Independent engine should follow same convention; add SG correction for vapor pressure term

---

## FIND-002

**Previous Conclusion:** PROBABLE_ERROR - inconsistent friction factor method

**Previous Evidence:** Discharge uses table lookup (0.00013), suction uses 64/Re

**New Derivation:**
```
OUTPIPES col 8 = 0.00013 is PIPE ROUGHNESS (ε in ft), NOT friction factor. Discharge friction factor f=0.0272 (G17) hardcoded. Suction uses laminar f=64/Re for Re=462,915 (turbulent). Both sides WRONG.
```

**Corrected Conclusion:** CONFIRMED_ERROR - MAJOR

**Correction Reason:** Discharge uses wrong value (roughness as friction factor) but hardcoded f=0.0272 in formula. Suction uses laminar formula for turbulent flow. Neither uses proper Moody/Colebrook.

**Project Impact:** Independent engine MUST implement proper friction factor calculation (Colebrook-White or Swamee-Jain)

---

## FIND-013

**Previous Conclusion:** INSUFFICIENT_INFORMATION - possible circular reference C28←C21←C20←E20

**Previous Evidence:** C20=E20/C22, C21=C20-C9, C28=C28=C11+C14+C21+C24+C26

**New Derivation:**
```
C20=6.92 (HARDCODED constant), NOT formula. C21=C20-C9 (static head). C28=sum of losses + C21. E20=(E4*C28*E11)/3960 uses C28. NO CIRCULARITY.
```

**Corrected Conclusion:** NO_CIRCULAR_REFERENCE

**Correction Reason:** Previous analysis misread column C (head) as column E (power). C20 is user input 6.92 ft static discharge head.

**Project Impact:** TDH calculation is linear; independent engine can replicate directly

---

## FIND-004

**Previous Conclusion:** INSUFFICIENT_INFORMATION - 2.3071 unverified

**Previous Evidence:** Used in G19, V19, RAMALES!D12, VELOCIDADES!V27-V30

**New Derivation:**
```
2.3071 = 144/62.395 ≈ 2.3077 = psi to ft water conversion (144 in²/ft² ÷ 62.4 lb/ft³). Used to convert pressure drop (psi/ft) to head (ft liquid/ft).
```

**Corrected Conclusion:** VALID_PRESSURE_HEAD_CONVERSION

**Correction Reason:** Constant is standard conversion; slight precision difference (2.3071 vs 2.3077) from using γ=62.428 or rounding

**Project Impact:** Acceptable; independent engine can use exact 2.3077 or 144/62.4

---

## FIND-009

**Previous Conclusion:** INSUFFICIENT_INFORMATION - accessory formula ambiguous

**Previous Evidence:** Formula =((D*F)*V²/(32.4*2))*H; unclear if K-method or Leq-method

**New Derivation:**
```
Standard equivalent length: h = f × (Leq/D) × V²/(2g). Workbook: D=f (friction factor), F=Leq/D, 32.4*2=64.8≈2g (g=32.174). Method is Leq-method with g≈32.4.
```

**Corrected Conclusion:** VALID_LEQ_METHOD

**Correction Reason:** Formula matches standard Leq method; 32.4 is g approximation (32.174). Error 0.7% on velocity head.

**Project Impact:** Acceptable; independent engine should use exact g=32.174

---

## FIND-012

**Previous Conclusion:** UNVERIFIED_CONSTANT - 1.422 unexplained

**Previous Evidence:** AB = (AA*3.2808)/1.422 in VELOCIDADES RECOMENDADAS

**New Derivation:**
```
AA=psia, AB=ft water. 3.2808=ft/m. 1.422 = 3.2808/2.3071 = (ft/m) / (ft water/psi) = psi·m/ft². Formula: ft water = psia × 2.3071. In metric: ft water = (psia × 2.3071) = (AA × 2.3071) = AA × 3.2808 / 1.422.
```

**Corrected Conclusion:** EXPLAINED

**Correction Reason:** 1.422 = 3.2808 / 2.3071 derived from pressure-head conversion and metric conversion

**Project Impact:** Table can be regenerated from fundamentals

---

