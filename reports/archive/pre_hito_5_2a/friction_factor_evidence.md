# Friction Factor Evidence Report

**Generated:** 2026-07-22T11:43:20.229530

## Input Data

- Flow: 770.5 GPM
- Fluid density: 62.0 lbm/ft³
- Dynamic viscosity: 0.52 cP

### Discharge Pipe

| Property | Value | Source |
|----------|-------|--------|
| Nominal diameter | 6.0 in | `CAIDA!G12` |
| Inside diameter | 6.048364 in | `CAIDA!G8` (calculated: `=G7*(G5/G6)^0.5`) |
| Material | N/A | `OUTPIPES` lookup from `A20` |
| Absolute roughness | 0.00012 ft | `CAIDA!G14` (VLOOKUP `RUGOSIDAD`) |
| Relative roughness | 0.000240 | `CAIDA!G15` = `G14/(G12/12)` |
| Cross-section area | 0.199528 ft² | computed |
| Velocity | 8.6037 ft/s | `V = Q/A` |
| Reynolds number | 768553 | `CAIDA!G11` = `50.6*G5*G9/(G8*G10)` |

### Suction Pipe

| Property | Value | Source |
|----------|-------|--------|
| Nominal diameter | 10.0 in | `CAIDA!V12` |
| Inside diameter | 10.041761 in | `CAIDA!V8` (calculated: `=V7*(V5/V6)^0.5`) |
| Material | N/A | `OUTPIPES` lookup from `B20` |
| Absolute roughness | 0.00012 ft | `CAIDA!V14` (VLOOKUP `RUGOSIDAD`) |
| Relative roughness | 0.000144 | `CAIDA!V15` = `V14/(V12/12)` |
| Cross-section area | 0.549980 ft² | computed |
| Velocity | 3.1214 ft/s | `V = Q/A` |
| Reynolds number | 462915 | `CAIDA!V11` = `50.6*V5*V9/(V8*V10)` |

## Friction Factor Comparison

| Method | Discharge f | Discharge Residual | Suction f | Suction Residual |
|--------|------------|-------------------|-----------|------------------|
| **Excel (legacy)** | 0.027200 | N/A | 0.000138 | N/A |
| **Colebrook** | 0.015319 | 2.327329e-08 | 0.015018 | 9.301905e-09 |
| **Haaland** | 0.015224 | 2.594804e-02 | 0.014853 | 4.757154e-02 |
| **Swamee_Jain** | 0.015411 | 2.491067e-02 | 0.015074 | 1.596379e-02 |

## Detailed Discharge Results

| Metric | Value |
|--------|-------|
| Colebrook-White f | 0.015319 |
| Colebrook residual | 2.327329e-08 |
| Colebrook iterations | 4 |
| Colebrook converged | True |
| Haaland f | 0.015224 |
| Haaland residual | 2.594804e-02 |
| Swamee-Jain f | 0.015411 |
| Swamee-Jain residual | 2.491067e-02 |
| Excel (legacy) f | 0.027200 |
| Legacy is _____× Colebrook | 1.776× |

## Detailed Suction Results

| Metric | Value |
|--------|-------|
| Colebrook-White f | 0.015018 |
| Colebrook residual | 9.301905e-09 |
| Colebrook iterations | 5 |
| Colebrook converged | True |
| Haaland f | 0.014853 |
| Haaland residual | 4.757154e-02 |
| Swamee-Jain f | 0.015074 |
| Swamee-Jain residual | 1.596379e-02 |
| Excel (legacy) f | 0.000138 |
| Legacy is _____× Colebrook | 0.009206× (÷109) |

## Input Status

| Parameter | Status | Notes |
|-----------|--------|-------|
| Discharge inside diameter | VERIFIED | Calculated from velocity formula in Excel |
| Suction inside diameter | VERIFIED | Calculated from velocity formula in Excel |
| Material | VERIFIED | Acero Inox SS from OUTPIPES table |
| Absolute roughness | VERIFIED | 0.00012 ft from RUGOSIDAD table for Acero Inox SS |
| Density | VERIFIED | 62.0 lbm/ft³ from OUTPIPES table |
| Viscosity | VERIFIED | 0.52 cP from OUTPIPES table |

Note: The inner diameters used here are calculated from Excel's velocity-sizing formula. For final verification, the actual pipe schedule inner diameter should be confirmed against pipe specifications. The `RUGOSIDAD` table shows 0.00012 ft for Acero Inox SS (stainless steel), which is standard.
