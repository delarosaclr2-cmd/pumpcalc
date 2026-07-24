"""
Generate all Hito 5.4A reports.
"""
import sys; sys.path.insert(0, r'C:\PUMPCALC')
from src.domain.accessory_losses import (
    build_semantic_tdh_balances, required_boundary_pressure_head,
    compute_source_boundary_absolute_pressure, BoundaryType,
    PressureBoundaryWarning,
)
import os; os.makedirs('reports', exist_ok=True)

SG = 0.995

# ========== 1. absolute_pressure_boundary_model ==========
md = [
    '# Absolute Pressure Boundary Model',
    '',
    '## Source Boundary Definition',
    '',
    '| Parameter | Value |',
    '|-----------|-------|',
    '| Atmospheric pressure (psia) | 14.7 |',
    '| Vessel pressure | 0.0 |',
    '| Vessel pressure type | GAUGE |',
    '| Source boundary absolute pressure (psia) | 14.7 |',
    '',
    '## Required Boundary Pressure Head',
    '',
    '| Required Pressure Reference | Value (psia) | Source (psia) | Difference (psi) | Head (ft) | Status |',
    '|---|---|---|---|---|---|',
]
csv = ['reference,required_value,source_abs,difference_psi,head_ft,status']
for ref, val in [('GAUGE', 79.77), ('ABSOLUTE', 79.77), ('DIFFERENTIAL', 10.0), ('UNKNOWN', 79.77)]:
    res = required_boundary_pressure_head(val, ref, 14.7, SG)
    if res.calculation_status != 'PRESSURE_REFERENCE_REQUIRED':
        head_fmt = f'{res.pressure_head_difference_ft:.4f}'
        diff_fmt = f'{res.pressure_difference_psi:.4f}'
    else:
        head_fmt = 'N/A'
        diff_fmt = 'N/A'
    md.append(f'| {ref} | {val} | {res.source_boundary_abs_psia} | {diff_fmt} | {head_fmt} | {res.calculation_status} |')
    csv.append(f'{ref},{val},{res.source_boundary_abs_psia},{diff_fmt},{head_fmt},{res.calculation_status}')
md.extend([
    '',
    '## Formulas',
    '',
    '- **GAUGE**: `pressure_difference = required_value`',
    '- **ABSOLUTE**: `pressure_difference = required_abs - source_abs`',
    '- **DIFFERENTIAL**: `pressure_difference = required_value` (same as GAUGE)',
    '- **UNKNOWN**: `status = PRESSURE_REFERENCE_REQUIRED`',
    '- **Head**: `pressure_difference * 144 / (62.4 * SG)`',
])
with open('reports/absolute_pressure_boundary_model.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
with open('reports/absolute_pressure_boundary_model.csv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(csv))
print('1/4 absolute_pressure_boundary_model')

# ========== 2. gauge_vs_absolute_pressure_scenarios ==========
md = [
    '# Gauge vs Absolute Pressure Scenarios',
    '',
    '| Scenario | U40 Reference | Source Boundary (psia) | Difference (psi) | Head (ft) |',
    '|---|---|---|---|---|',
]
csv = ['scenario,reference,source_abs,difference_psi,head_ft']
for ref, lbl in [
    ('GAUGE', 'GAUGE'),
    ('ABSOLUTE', 'ABSOLUTE'),
]:
    res = required_boundary_pressure_head(79.77, ref, 14.7, SG)
    md.append(f'| {lbl} | {ref} | {res.source_boundary_abs_psia} | {res.pressure_difference_psi:.4f} | {res.pressure_head_difference_ft:.4f} |')
    csv.append(f'{ref},{ref},{res.source_boundary_abs_psia},{res.pressure_difference_psi:.6f},{res.pressure_head_difference_ft:.6f}')
md.extend([
    '',
    '## Key Difference',
    '',
    '- **GAUGE**: difference = 79.77 psi, head = 185.01 ft',
    '- **ABSOLUTE**: difference = 79.77 - 14.7 = 65.07 psi, head = 150.92 ft',
    '- Absolute subtraction reduces TDH by ~34.1 ft vs gauge scenario',
])
with open('reports/gauge_vs_absolute_pressure_scenarios.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
with open('reports/gauge_vs_absolute_pressure_scenarios.csv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(csv))
print('2/4 gauge_vs_absolute_pressure_scenarios')

# ========== 3. source_boundary_definition ==========
md = [
    '# Source Boundary Definition',
    '',
    '## System Boundary Node',
    '',
    'The source boundary is the physical location where pressure is referenced.',
    '',
    '| Field | Value |',
    '|-------|-------|',
    '| boundary_type | FREE_SURFACE (tank/vented) |',
    '| atmospheric_pressure_psia | 14.7 (sea level) |',
    '| vessel_pressure | 0.0 psig |',
    '| vessel_pressure_type | GAUGE |',
    '| computed_source_abs_psia | 14.7 |',
    '',
    '## BoundaryType Enum',
    '',
    '| Value | Description |',
    '|-------|-------------|',
]
for bt in BoundaryType:
    desc = bt.name.replace('_', ' ').title()
    md.append(f'| {bt.value} | {desc} |')
md.extend([
    '',
    '## GAUGE vs ABSOLUTE vs VACUUM',
    '',
    '- **GAUGE**: source_abs = atm + vessel_pressure',
    '- **ABSOLUTE**: source_abs = vessel_pressure (already absolute)',
    '- **VACUUM**: source_abs = atm - vessel_pressure',
    '',
    '## Current Case: Open Tank at Atmospheric Pressure',
    '',
    '`source_abs = 14.7 + 0.0 = 14.7 psia`',
])
with open('reports/source_boundary_definition.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
print('3/4 source_boundary_definition')

# ========== 4. hito_5_4a_summary ==========
md = [
    '# Hito 5.4A — Absolute Pressure Boundary Model',
    '',
    '## Summary',
    '',
    'This milestone implements a complete absolute pressure boundary model for the TDH calculation pipeline.',
    '',
    '## What Changed',
    '',
    '1. **BoundaryType enum** — 6 boundary types (FREE_SURFACE through EQUIPMENT_OUTLET)',
    '',
    '2. **SystemBoundary dataclass** — Typed boundary node with pressure, elevation, confidence',
    '',
    '3. **PressureBoundaryResult dataclass** — Result container for boundary pressure computations',
    '',
    '4. **compute_source_boundary_absolute_pressure()** — Three reference variants (GAUGE, ABSOLUTE, VACUUM)',
    '',
    '5. **required_boundary_pressure_head()** — Core function with 4 reference rules',
    '',
    '6. **build_semantic_tdh_balances() updated** —',
    '   - D (ABSOLUTE): now calculable using source boundary (14.7 psia)',
    '   - E (UNKNOWN): new scenario returning PRESSURE_REFERENCE_REQUIRED',
    '   - F (U40_EXCLUDED): sensitivity scenario',
    '',
    '7. **DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE warning** — Negative differences allowed',
    '',
    '## Current Case Results',
    '',
    '| Scenario | TDH (ft) | Notes |',
    '|---|---|---|',
]
balances = build_semantic_tdh_balances(sg=SG)
for key in balances:
    tdh = balances[key]['total_dynamic_head_ft']
    desc = balances[key]['description']
    tdh_str = f'{tdh:.6f}' if isinstance(tdh, float) else str(tdh)
    md.append(f'| {key} | {tdh_str} | {desc.split(":")[0]} |')
md.extend([
    '',
    '## Negative Difference Handling',
    '',
    '- DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE is a WARNING, not an error',
    '',
    '## Next Steps (Hito 5.5)',
    '',
    '- Full integration with pump selection and NPSH calculations',
    '- Source boundary pressure from workbook inputs',
])
with open('reports/hito_5_4a_summary.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
print('4/4 hito_5_4a_summary')

print('\nAll 4 new reports generated.')
