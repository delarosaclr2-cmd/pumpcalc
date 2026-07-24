# Current Case Inputs - Centrifugal Pump Calculation

**Project:** KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C
**Pump Tag:** 005PU001
**Pump Name:** DISPERSION WATER PUMP
**Fluid:** Agua Blanca (Water)
**Revision:** C
**Date:** 2025-01-22

---

## Process & Hydraulic Inputs

| Variable | Value | Unit | Sheet | Cell | Data Type | Origin | Confidence | Observation |
|----------|-------|------|-------|------|-----------|--------|------------|-------------|
| **Caudal Normal (Normal Flow)** | 770.5 | GPM | CAIDA PRESION DE TUBERIA | G5 | USER_INPUT | Process datasheet | HIGH | Base flow for sizing |
| **Caudal de Diseño (Design Flow)** | 770.5 | GPM | CALCULO DE BOMBA / RESUMEN | E4 / B13 | DERIVED_INPUT | =G5 (no depreciation) | HIGH | B15=0% depreciation |
| **Densidad (Density)** | 62 | lbm/ft³ | CAIDA PRESION DE TUBERIA | G9 | LOOKUP | OUTPIPES table (Item 6: Agua Blanca) | HIGH | Mass density, not SG |
| **Gravedad Específica (Specific Gravity)** | 0.995 | - | CALCULO DE BOMBA | E11 | LOOKUP | gravedadespecifica table (Item 9, 95°F) | HIGH | At operating temperature |
| **Viscosidad Dinámica (Dynamic Viscosity)** | 0.52 | cP | CAIDA PRESION DE TUBERIA | G10 | LOOKUP | OUTPIPES table (Item 6) | HIGH | |
| **Temperatura de Operación** | 95 | °F | CALCULO DE BOMBA | (implied) | DESIGN_INPUT | gravedadespecifica/presionvapor Item 9 | HIGH | Matches SG=0.995, Pvap=0.8 psia |
| **Presión de Vapor (Vapor Pressure)** | 0.8 | psia | VELOCIDADES RECOMENDADAS | AA13 (Item 9) | LOOKUP | presionvapor table | HIGH | Absolute pressure |
| **Presión de Vapor (Head)** | 1.846 | ft water | VELOCIDADES RECOMENDADAS | AB13 (Item 9) | DERIVED | =AA13*3.2808/1.422 | HIGH | ft water absolute |
| **Presión Atmosférica** | 14.7 | psia | CALCULO DE BOMBA | C8 | ASSUMPTION | Standard sea level | MEDIUM | No altitude correction |
| **Presión de Recipiente (Vessel Pressure)** | 0 | psig | CALCULO DE BOMBA | E8 | DESIGN_INPUT | Open tank assumption | HIGH | Gauge pressure (0 psig = 14.7 psia) |
| **Elevación Estática Succión (Static Suction Head)** | 1.64 | ft | CALCULO DE BOMBA | C9 | DESIGN_INPUT | =500/304.8 (500 mm) | UNVERIFIED | Hardcoded; needs drawing verification |
| **Nivel Mínimo Operación** | 1.64 | ft | CALCULO DE BOMBA | E10 | DESIGN_INPUT | Hardcoded | UNVERIFIED | Same as static head? |
| **Longitud Tubería Succión** | 6.96 | ft | CALCULO DE BOMBA | C12 | DESIGN_INPUT | =2.12*3.281 (2.12 m) | UNVERIFIED | Hardcoded; needs piping layout |
| **Diámetro Nominal Succión** | 10 | in | CAIDA PRESION DE TUBERIA | V12 | USER_INPUT | Pipe schedule table | HIGH | |
| **Rugosidad Absoluta Succión** | 0.00012 | ft | CAIDA PRESION DE TUBERIA | V14 | LOOKUP | RUGOSIDAD table (Item 1: Acero Inox) | HIGH | Stainless steel |
| **Diámetro Nominal Descarga** | 6 | in | CAIDA PRESION DE TUBERIA | G12 | USER_INPUT | Pipe schedule table | HIGH | |
| **Rugosidad Absoluta Descarga** | 0.00012 | ft | CAIDA PRESION DE TUBERIA | G14 | LOOKUP | RUGOSIDAD table (Item 1: Acero Inox) | HIGH | Stainless steel |

---

## Calculated Hydraulic Parameters (from workbook)

| Variable | Value | Unit | Sheet | Cell | Formula | Confidence |
|----------|-------|------|-------|------|---------|------------|
| **Diámetro Interior Calculado Descarga** | 6.048 | in | CAIDA | G8 | =G7*√(G5/G6) | HIGH |
| **Diámetro Interior Calculado Succión** | 10.042 | in | CAIDA | V8 | =V7*√(V5/V6) | HIGH |
| **Número Reynolds Descarga** | 768,553 | - | CAIDA | G11 | =50.6*G5*G9/(G8*G10) | HIGH |
| **Número Reynolds Succión** | 462,915 | - | CAIDA | V11 | =50.6*V5*V9/(V8*V10) | HIGH |
| **Régimen Flujo Descarga** | Turbulent | - | - | - | Re > 4000 | HIGH |
| **Régimen Flujo Succión** | Turbulent | - | - | - | Re > 4000 | HIGH |
| **Factor fricción Descarga (usado)** | 0.0272 | - | CAIDA | G17 | Hardcoded CPL | LOW ⚠️ |
| **Factor fricción Succión (usado)** | 0.000138 | - | CAIDA | V16 | =64/Re (laminar) | **ERROR** ⚠️ |
| **Pérdida fricción/L Descarga** | 0.0445 | ft/ft | CAIDA | G19 | DW hybrid formula | MEDIUM ⚠️ |
| **Pérdida fricción/L Succión** | 0.00375 | ft/ft | CAIDA | V19 | DW hybrid formula | MEDIUM ⚠️ |
| **Pérdidas Accesorios Succión** | 0.0168 | ft | CALCULO | C11 | =TABLA SUCCION!I40 | HIGH |
| **Pérdidas Tubería Succión** | 0.0261 | ft | CALCULO | C14 | =C12*C13 | HIGH |
| **Pérdidas Accesorios Descarga** | 188.56 | ft | CALCULO | C24 | =TABLA DESCARGA!I41 | HIGH |
| **Longitud Ramal Descarga** | 36 | ft | CALCULO / RAMALES | C25 / F18 | =RAMALES!F18 | HIGH |
| **Pérdidas Ramal Descarga** | 1.67 | ft | CALCULO / RAMALES | C26 / F19 | =RAMALES!F19 | HIGH |
| **Carga Estática Total** | 5.28 | ft | CALCULO | C21 | =C20-C9 (6.92-1.64) | HIGH |
| **TDH (Total Dynamic Head)** | 195.55 | ft | CALCULO | C28 | =C11+C14+C21+C24+C26 | HIGH ⚠️* |
| **TDH** | 59.60 | m | CALCULO | E24 | =C28*0.3048 | HIGH |
| **NPSH Disponible** | 33.88 | ft | CALCULO | E14 | =((C8+E8)*2.31/E11)+C9-C11-C14-E9 | HIGH ⚠️** |
| **NPSH Disponible** | 10.33 | m | RESUMEN | G25 | =E14/3.281 | HIGH |
| **Potencia Hidráulica** | 37.86 | HP | CALCULO | E20 | =(E4*C28*E11)/3960 | HIGH |
| **Potencia al Freno** | 52.58 | HP | CALCULO | E21 | =E20/C22 | HIGH |
| **Potencia al Freno** | 39.20 | kW | CALCULO | E22 | =E21*0.7456 | HIGH |
| **Torque** | 162.44 | lb-ft | CALCULO | E23 | =(E21*5252)/1700 | HIGH |
| **Eficiencia Bomba** | 72% | - | CALCULO | C22 | USER_INPUT | MEDIUM |
| **Factor de Servicio** | 1.0 | - | CALCULO | C6 | USER_INPUT | MEDIUM |
| **RPM Bomba** | 3600 | rpm | CALCULO | C29 | USER_INPUT | MEDIUM |
| **Velocidad Específica (Ns)** | 4658 | - | CALCULO | E27 | =(C29*√E4)/E24^0.75 | LOW ⚠️*** |

---

## Accessory Loss Details (from TABLA DE ACCESORIOS)

### Succión (Total: 0.0168 ft)
| Item | Accesorio | Cantidad | K factor | Leq/D | Pérdida (ft) |
|------|-----------|----------|----------|-------|--------------|
| 1 | Válvula Compuerta 100% | 1 | 0.19 (f) | 8/D | 0.0002 |
| 2 | Válvula Compuerta 1/2 | 1 | 0.34 (f) | 12/D | 0.0004 |
| 3 | Válvula Compuerta 3/4 | 1 | 0.44 (f) | 17/D | 0.0005 |
| 4 | Válvula Globo 100% | 1 | 10.0 (f) | 340/D | 0.0097 |
| ... | ... | ... | ... | ... | ... |

### Descarga (Total: 188.56 ft)
| Item | Accesorio | Cantidad | K factor | Leq/D | Pérdida (ft) |
|------|-----------|----------|----------|-------|--------------|
| 1 | Válvula Compuerta 100% | 2 | 0.19 (f) | 8/D | ~0.5 |
| ... | ... (34 items total) | ... | ... | ... | ... |

---

## Pump Specification Outputs (005PU001 / RESUMEN PARA PDF)

| Parameter | Value | Unit | Source |
|-----------|-------|------|--------|
| Flujo Nominal | 770.5 | GPM | RESUMEN!B13 |
| Flujo de Diseño | 770.5 | GPM | RESUMEN!B16 |
| TDH Requerido | 195.55 | ft | RESUMEN!B28 |
| TDH Requerido | 84.65 | psi | RESUMEN!D28 |
| TDH Requerido | 59.60 | m | CALCULO!E24 |
| NPSH Disponible | 33.88 | ft | RESUMEN!G25 |
| NPSH Disponible | 10.33 | m | 005PU001!H10 |
| Potencia al Freno | 52.58 | HP | RESUMEN!G29 |
| Potencia al Freno | 39.20 | kW | CALCULO!E22 |
| Tipo de Impulsor | FLUJO MIXTO | - | CALCULO!E29 |
| Eficiencia | 72% | - | CALCULO!C22 |

---

## Critical Issues Requiring Resolution

| Issue | Severity | Impact | Resolution Needed |
|-------|----------|--------|-------------------|
| Friction factor suction uses laminar (64/Re) at Re=462,915 | **CRITICAL** | Suction head loss underestimated ~100x | Implement Colebrook-White/Swamee-Jain |
| Friction factor discharge hardcoded (0.0272) | **HIGH** | Discharge head loss may be 2x off | Use Moody chart or correlation |
| Vapor pressure head not divided by SG in NPSH | **MEDIUM** | NPSH error ~0.5% for water, higher for other fluids | Use E9/E11 in independent engine |
| Specific speed uses TDH in meters with GPM | **LOW** | Ns units wrong for pump selection | Use TDH in feet |
| Static suction head (500 mm) and suction length (2.12 m) hardcoded | **MEDIUM** | Geometry not traceable | Link to piping drawings |
| Atmospheric pressure fixed at 14.7 psia | **LOW** | No altitude correction | Add site altitude input |
| TDH discharge static head (C20=6.92) hardcoded | **MEDIUM** | Not derived from layout | Link to discharge elevation |

---

## Data Quality Flags

| Flag | Meaning |
|------|---------|
| HIGH | Verified from source data or fundamental equations |
| MEDIUM | Derived from lookup tables with known source |
| LOW | Engineering judgment, approximation, or hardcoded |
| UNVERIFIED | No traceability to source documents |
| MISSING | Data not present in workbook |
| AMBIGUOUS | Conflicting or unclear definitions |
| ERROR | Mathematically or dimensionally incorrect |

---

## Missing Data for Complete Independent Calculation

1. **Piping isometric drawings** for elevations and lengths
2. **Pump performance curves** (H-Q, η-Q, NPSHr-Q) from manufacturer
3. **Site altitude** for atmospheric pressure correction
4. **Complete accessory schedule** with K factors (not just Leq/D)
5. **Motor efficiency** for electrical power estimation
6. **Impeller diameter range** for affinity law calculations
7. **Minimum continuous flow (MCSF)** from manufacturer
8. **Allowable operating region (AOR)** and **preferred operating region (POR)**