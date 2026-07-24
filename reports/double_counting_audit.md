# Double Counting Audit

## Structural Anomalies

| Side | Row | Item | Accessory | Issue |
|---|---|---|---|---|
| discharge | 39 | 19 | Codo  Soldado 90 (Radio Largo) | DUAL_ENTRY: row has both Leq formula loss and pressure entry |
| discharge | 40 | 20 | Codo Soldado 45 ( Radio Largo) | ZERO_QUANTITY_PRESSURE: pressure entry with zero quantity count |

## Notes

1. **Row 39** (Codo Soldado 90-deg Radio Largo): Has both a Leq formula loss (0.62 ft) and a pressure entry (0.36 PSI -> 0.83 ft). These may represent two independent estimates of the same physical loss or distinct adjacent losses.
2. **Row 40** (Codo Soldado 45-deg Radio Largo): Has 79.77 PSI pressure entry with zero quantity (H40=0). This is consistent with it being a system-level equipment pressure requirement rather than a per-fitting minor loss.
