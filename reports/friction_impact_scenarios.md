# Friction Impact Scenarios

**Generated:** 2026-07-22T11:46:09.473659

## Scenarios

| Scenario | Suction f | Discharge f | Description |
|----------|-----------|-------------|-------------|
| **A** | 64/Re (laminar) | 0.0272 (hardcoded) | Current Excel behavior |
| **B** | Colebrook-White | 0.0272 (hardcoded) | Fix suction only |
| **C** | 64/Re (laminar) | Colebrook-White | Fix discharge only |
| **D** | Colebrook-White | Colebrook-White | Fully validated |

## Results Summary

| Metric | Scenario A | Scenario B | Scenario C | Scenario D | A→D Change |
|--------|-----------|-----------|-----------|-----------|-----------|
| Suction f | 0.000138 | 0.015012 | 0.000138 | 0.015012 | +0.0149 (+10758.19%) |
| Discharge f | 0.027200 | 0.027200 | 0.015301 | 0.015301 | -0.0119 (-43.75%) |
| hf/ft Suction (ft/ft) | 0.000025 | 0.002716 | 0.000025 | 0.002716 | +0.0027 (+10758.19%) |
| hf/ft Discharge (ft/ft) | 0.062080 | 0.062080 | 0.034922 | 0.034922 | -0.0272 (-43.75%) |
| Suction Pipe Loss (ft) | 0.000174 | 0.018893 | 0.000174 | 0.018893 | +0.0187 (+10758.19%) |
| Discharge Pipe Loss (ft) | 2.234872 | 2.234872 | 1.257178 | 1.257178 | -0.9777 (-43.75%) |
| TDH (ft) | 196.0901 | 196.1088 | 195.1124 | 195.1311 | -0.9590 (-0.49%) |
| NPSHa (ft) | 33.9053 | 33.8866 | 33.9053 | 33.8866 | -0.0187 (-0.06%) |
| Hydraulic HP | 37.9626 | 37.9662 | 37.7733 | 37.7770 | -0.1857 (-0.49%) |
| Shaft HP | 52.7259 | 52.7309 | 52.4630 | 52.4680 | -0.2579 (-0.49%) |
| Shaft kW | 39.3124 | 39.3162 | 39.1164 | 39.1201 | -0.1923 (-0.49%) |
| Torque (lb-ft) | 162.8919 | 162.9074 | 162.0797 | 162.0953 | -0.7966 (-0.49%) |

## Detailed Scenario Results

### Scenario A

**A: Both Legacy (current Excel)**

| Metric | Value |
|--------|-------|
| Suction friction factor | 0.000138 |
| Discharge friction factor | 0.027200 |
| hf/ft Suction | 0.000025 ft/ft |
| hf/ft Discharge | 0.062080 ft/ft |
| Suction pipe loss | 0.000174 ft |
| Discharge pipe loss | 2.234872 ft |
| TDH | 196.0901 ft |
| NPSHa | 33.9053 ft |
| Hydraulic HP | 37.9626 |
| Shaft HP | 52.7259 |
| Shaft kW | 39.3124 |
| Torque | 162.8919 lb-ft |

### Scenario B

**B: Colebrook Suction Only**

| Metric | Value |
|--------|-------|
| Suction friction factor | 0.015012 |
| Discharge friction factor | 0.027200 |
| hf/ft Suction | 0.002716 ft/ft |
| hf/ft Discharge | 0.062080 ft/ft |
| Suction pipe loss | 0.018893 ft |
| Discharge pipe loss | 2.234872 ft |
| TDH | 196.1088 ft |
| NPSHa | 33.8866 ft |
| Hydraulic HP | 37.9662 |
| Shaft HP | 52.7309 |
| Shaft kW | 39.3162 |
| Torque | 162.9074 lb-ft |

### Scenario C

**C: Colebrook Discharge Only**

| Metric | Value |
|--------|-------|
| Suction friction factor | 0.000138 |
| Discharge friction factor | 0.015301 |
| hf/ft Suction | 0.000025 ft/ft |
| hf/ft Discharge | 0.034922 ft/ft |
| Suction pipe loss | 0.000174 ft |
| Discharge pipe loss | 1.257178 ft |
| TDH | 195.1124 ft |
| NPSHa | 33.9053 ft |
| Hydraulic HP | 37.7733 |
| Shaft HP | 52.4630 |
| Shaft kW | 39.1164 |
| Torque | 162.0797 lb-ft |

### Scenario D

**D: Both Colebrook (Validated)**

| Metric | Value |
|--------|-------|
| Suction friction factor | 0.015012 |
| Discharge friction factor | 0.015301 |
| hf/ft Suction | 0.002716 ft/ft |
| hf/ft Discharge | 0.034922 ft/ft |
| Suction pipe loss | 0.018893 ft |
| Discharge pipe loss | 1.257178 ft |
| TDH | 195.1311 ft |
| NPSHa | 33.8866 ft |
| Hydraulic HP | 37.7770 |
| Shaft HP | 52.4680 |
| Shaft kW | 39.1201 |
| Torque | 162.0953 lb-ft |

## Key Insights

1. **TDH changes by -0.9590 ft (-0.49%)** from Scenario A to D.
   - Suction pipe loss drops from 0.0002 to 0.0189 ft.
   - Discharge pipe loss drops from 2.2349 to 1.2572 ft.

2. **NPSHa change is negligible** for friction corrections alone:
   - NPSHa goes from 33.91 ft (A) to 33.89 ft (B) when correcting suction f.
   - The larger NPSH discrepancy (33.88 → 34.80 ft) is driven by the vapor pressure SG correction, not friction.

3. **The compensating error is evident:**
   - Scenario C (fixing discharge only) OVER-estimates friction on both sides
   - Scenario B (fixing suction only) UNDER-estimates friction on discharge
   - Only Scenario D (both Colebrook) is physically correct

4. **Power impact:** Shaft HP changes by -0.2579 HP.

## Conclusion

The compensating errors in the legacy workbook make the TDH appear correct for this single operating point, but individual components are wrong. Any change in flow rate, pipe geometry, or fluid properties will break this compensation. The validated Colebrook-White friction factors must be used for all operating conditions.
