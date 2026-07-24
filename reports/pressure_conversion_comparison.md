# Pressure Conversion Comparison — Hito 5.3B

## Legacy vs Validated pressure-to-head conversion

Constants:
- Legacy factor: 2.31 (psi × 2.31 ≈ ft of water, SG ≈ 1.0)
- Validated factor: 144 / (62.4 × SG) = 144 / (62.4 × 0.995) = 2.319289 ft/psi
- Water density: 62.4 lbm/ft³
- Current case SG: 0.995

| Source | PSI | Legacy (ft) | Formula | Validated (ft) | Formula | Diff (ft) | Diff (%) |
|--------|-----|------------|---------|---------------|---------|----------|---------|
| U39 | 0.36 | 0.8316 | psi × 2.31 | 0.834944 | psi × 144 / (62.4 × SG) | 0.003344 | 0.4021% |
| U40 | 79.77 | 184.2687 | psi × 2.31 | 185.009664 | psi × 144 / (62.4 × SG) | 0.740964 | 0.4021% |

The validated conversion produces a **higher** head because:
- 144 / (62.4 × 0.995) = 2.319289 > 2.31
- The factor 2.31 assumes SG = 144 / (62.4 × 2.31) = 0.9990
- With SG = 0.995 < 1.0, the actual fluid is lighter than water, requiring more head per PSI
