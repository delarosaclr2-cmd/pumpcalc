# Diameter Selection Audit (Hito 5.2C)

## 1. Required Diameter (Velocity Sizing) — G8/V8

The required diameter is computed via:
```python
required_diameter_from_flow_velocity(flow_gpm, target_velocity_fps)
```

**Derivation:**
```
Q (GPM) → ft³/s:  Q_ft3s = Q / 448.831
A (ft²) = Q_ft3s / V_fps = π × D_ft² / 4
D_ft = sqrt(4 × Q_ft3s / (π × V_fps))
D_in = D_ft × 12
D_in = 12 × sqrt(4 × Q_gpm / (448.831 × π × V_fps))
     = [12 × sqrt(4 / (448.831 × π))] × sqrt(Q_gpm / V_fps)
     = 0.639 × sqrt(Q_gpm / V_fps)
```

The constant `C = 12 × sqrt(4 / (448.831 × π)) ≈ 0.639`.

**Current case values:**
| Side      | Target V (ft/s) | Required ID (in) | Source cell | Formula                |
|-----------|----------------|------------------|-------------|------------------------|
| Suction   | 3.12 (V6)      | 10.044 (V8)      | V8          | V7 × sqrt(V5/V6)       |
| Discharge | 8.6 (G6)       | 6.050 (G8)       | G8          | G7 × sqrt(G5/G6)       |

> **Correction (Hito 5.2C):** G8 and V8 are **required diameters from velocity sizing**, not selected inside diameters from pipe schedules. They were incorrectly labeled as `selected_inside_diameter_in` in Hito 5.2B.

## 2. Selected Diameter (Actual Pipe Spec)

| Variable              | Suction                       | Discharge                     |
|-----------------------|-------------------------------|-------------------------------|
| Nominal NPS (G12/V12) | 10 in                         | 6 in                          |
| Required ID (G8/V8)   | 10.042 in (velocity-based)    | 6.048 in (velocity-based)     |
| Selected NPS          | 10 in (from V12)              | 6 in (from G12)               |
| Selected schedule     | **MISSING_SELECTED_PIPE_SCHEDULE** | **MISSING_SELECTED_PIPE_SCHEDULE** |
| Selected ID           | **None** (cannot compute without schedule) | **None** (cannot compute without schedule) |
| Material              | Acero Inox SS (OUTPIPES)      | Acero Inox SS (OUTPIPES)      |
| Wall thickness        | **None** (not in workbook)    | **None** (not in workbook)    |
| Outside diameter      | **None** (not in workbook)    | **None** (not in workbook)    |

> The workbook has nominal diameters V12/G12 from OUTPIPES table but **no explicit pipe schedule, wall thickness, or outside diameter data**. The ESPECIFICACIÓN DE TUBERIA sheet exists but is empty. The OUTPIPES table references STD for steel pipe but this was inferred from the codebase, not directly from the workbook.

## 3. Hydraulic Diameter Used

Since no confirmed selected ID is available, hydraulic calculations fall back to the **required diameter** (velocity-based). This is labeled transparently:

- `inputs.suction_required_diameter_in` → used for Reynolds, velocity, friction factor
- `inputs.discharge_required_diameter_in` → used for Reynolds, velocity, friction factor
- `inputs.suction_selected_inside_diameter_in` = None
- `inputs.discharge_selected_inside_diameter_in` = None

**Status:** `MISSING_SELECTED_PIPE_SCHEDULE`

## 4. Scenario Analysis (When Schedule Becomes Available)

Once a schedule is confirmed, compute:
```text
ID = OD - 2 × wall_thickness
```

For ANSI standard pipes:

| NPS | Schedule | OD (in) | Wall (in) | ID (in) | ID vs Required (10.042/6.048) |
|-----|----------|---------|-----------|---------|-------------------------------|
| 10" | STD/40   | 10.750  | 0.365     | 10.020  | -0.022 in (0.2%)              |
| 10" | XS/80    | 10.750  | 0.500     | 9.750   | -0.292 in (2.9%)              |
| 6"  | STD/40   | 6.625   | 0.280     | 6.065   | +0.017 in (0.3%)              |
| 6"  | XS/80    | 6.625   | 0.432     | 5.761   | -0.287 in (4.7%)              |

**STD schedule (most common for water/petroleum)** produces IDs within 0.3% of the required diameters, suggesting the velocity-based sizing approximates a standard schedule selection.

## 5. Impact of Schedule on Hydraulics

For the same flow rate, smaller ID → higher velocity → higher Re → higher friction factor → higher head loss:
- Re ∝ 1/D
- hf ∝ 1/D⁵ (Darcy-Weisbach)

The impact of switching from STD to XS would be significant (2.9-4.7% diameter change → 15-26% hf change).

## 6. Code Changes (Hito 5.2C)

- `src/infrastructure/input_loader.py`:
  - Renamed `suction_inside_diameter_in` → `suction_required_diameter_in`
  - Renamed `discharge_inside_diameter_in` → `discharge_required_diameter_in`
  - Added `suction_selected_inside_diameter_in` (Optional[float], default None)
  - Added `discharge_selected_inside_diameter_in` (Optional[float], default None)
  - Added `suction_pipe_schedule`, `discharge_pipe_schedule` (default: MISSING_SELECTED_PIPE_SCHEDULE)
  - Added `suction_wall_thickness_in`, `discharge_wall_thickness_in` (Optional[float])
  - Added `suction_outside_diameter_in`, `discharge_outside_diameter_in` (Optional[float])
  - Added `suction_pipe_material`, `discharge_pipe_material`
- `src/application/validated_calculator.py`: Uses required diameter as fallback for hydraulics when selected unavailable
- `src/application/legacy_calculator.py`: Same pattern

## 7. Status

- [x] G8/V8 reclassified as required diameters (not selected IDs)
- [x] Selected ID fields added (Optional, default None)
- [x] Pipe schedule fields added (MISSING_SELECTED_PIPE_SCHEDULE)
- [x] Hydraulics use required diameter as fallback (transparent)
- [x] Material tracked (Acero Inox SS from OUTPIPES)
- [x] Scenario analysis for STD/XS schedules
- [x] All tests updated for new classification
