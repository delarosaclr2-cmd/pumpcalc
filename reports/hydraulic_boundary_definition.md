# Hydraulic Boundary Definition (Hito 5.2C — Corrections)

## 1. TDH — Two Methods

### Method A: Surface-to-Surface (Primary)
```text
TDH_surface_to_surface = (z_disch_surface - z_suct_surface)
                        + suction_minor_losses
                        + suction_major_losses
                        + discharge_minor_losses
                        + discharge_major_losses
                        + (P_disch_surface - P_suct_surface)/γ
```
- Velocities at free surfaces ≈ 0, so velocity head is NOT included.
- This matches the workbook formula: C28 = C11 + C14 + C21 + C24 + C26.
- **Primary TDH result** (`tdh_ft` = 195.13 ft).

### Method B: Flange-to-Flange (Requires Pressure Data)
```text
TDH_flange_to_flange = (P_disch_flange - P_suct_flange)/γ
                      + (V_d² - V_s²)/2g
                      + (z_disch_flange - z_suct_flange)
```
- **Currently NOT CALCULABLE** because no flange pressure data exists.
- `tdh_flange_to_flange_ft` = None
- `tdh_flange_input_status` = `"TDH_FLANGE_NOT_CALCULABLE"`

### Partial Geometric-Kinetic Difference (NOT TDH)
```text
partial_geometric_kinetic_difference = (z_disch - z_suct) + (V_d² - V_s²)/2g
```
- Value: 6.28 ft (elevation diff 5.28 ft + velocity head diff 1.00 ft).
- **This is NOT the pump TDH.** It omits the pressure difference term entirely.
- Renamed from the incorrect `tdh_flange_to_flange_ft` (Hito 5.2B error).

### Workbook Classification (UNVERIFIED)
- `CALCULO DE BOMBA!C9` (suction_static_head_ft) = **TANK_FREE_SURFACE_ELEVATION**  
  Formula: `=500/304.8` → 1.6404 ft (500 mm converted to ft).  
  Assumed to represent elevation of liquid free surface relative to pump centerline.
- `CALCULO DE BOMBA!C20` (discharge_static_head_ft) = **TANK_FREE_SURFACE_ELEVATION**  
  Value: 6.92 ft (hardcoded).  
  Assumed to represent elevation of discharge liquid free surface.

> **Status:** `BOUNDARY_CONDITION_UNVERIFIED` — C9 and C20 are treated as tank free surface elevations based on formula structure, but this has NOT been physically confirmed (see Section 3).

## 2. NPSHa — Two Methods (Equivalent via Bernoulli)

### Method A: From Free Surface
```text
NPSHa_surface = P_surface_abs/γ
               + (z_surface - z_pump)
               - suction_major_losses
               - suction_minor_losses
               - P_vapor_abs/γ
```
- No velocity head (free surface velocity ≈ 0).
- Matches workbook formula: `((C8+E8)*(2.31/E11))+C9-C11-C14-E9`.
- Value: 33.88 ft.

### Method B: From Suction Flange (Bernoulli-Derived)
```text
NPSHa_flange = P_flange_abs/γ + V_s²/2g - P_vapor_abs/γ
```
Where `P_flange_abs/γ` is derived via Bernoulli from the free surface:
```text
P_flange/γ = P_surface/γ + z_surface - z_flange - losses - V_s²/2g
```
Substituting:
```text
NPSHa_flange = P_surface/γ + z_surface - z_flange - losses - V_s²/2g + V_s²/2g - Pv/γ
             = P_surface/γ + z_surface - z_flange - losses - Pv/γ
             = NPSHa_surface  (when z_flange = z_pump)
```

> **Key insight:** The velocity head term cancels out. Both routes produce the **same value** (33.88 ft) — `npsha_equivalence_diff < 1e-8 ft`. The previous implementation (Hito 5.2B) INCORRECTLY added velocity head to surface NPSH, producing 34.03 ft (double counting).

### Correction (Hito 5.2C)
- Old (wrong): `NPSHa_flange = NPSHa_surface + velocity_head`
- New (correct): `NPSHa_flange == NPSHa_surface` (Bernoulli equivalence)
- `npsha_equivalence_status`: `"EQUIVALENT"` (diff = 0.0 ft)

## 3. Boundary Classification Status

| Method               | Field                   | Value                        | Status          |
|----------------------|------------------------|------------------------------|-----------------|
| TDH surface-to-surface | `tdh_boundary_method`  | BOUNDARY_CONDITION_UNVERIFIED | ⚠️ Unconfirmed  |
| NPSH from free surface  | `npsh_boundary_method` | FROM_FREE_SURFACE            | ✅ Confirmed    |
| TDH flange-to-flange    | `tdh_flange_input_status` | TDH_FLANGE_NOT_CALCULABLE  | ❌ No flange data |

> **Why BOUNDARY_CONDITION_UNVERIFIED for TDH?** C9 and C20 are identified as tank free surface elevations based on formula structure (C9 = 500/304.8 = 1.64 ft, C20 = 6.92 ft hardcoded). However, this classification relies solely on formula analysis — physical confirmation (P&ID review, site verification) is required before marking as verified.

## 4. Code Changes (Hito 5.2C)

- `src/application/validated_calculator.py`:
  - NPSH: Both routes use `velocity_head_ft=0.0` (Bernoulli cancellation documented)
  - NPSH: Added `npsha_equivalence_diff` and `npsha_equivalence_status`
  - TDH: `tdh_flange_to_flange_ft` = None (no pressure data)
  - TDH: Added `tdh_flange_input_status` = "TDH_FLANGE_NOT_CALCULABLE"
  - TDH: Added `partial_geometric_kinetic_difference_ft` for elevation + vel diff
  - TDH: `tdh_boundary_method` = "BOUNDARY_CONDITION_UNVERIFIED"
