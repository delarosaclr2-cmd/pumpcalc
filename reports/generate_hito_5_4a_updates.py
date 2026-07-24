"""
Update 8 existing reports for Hito 5.4A changes.
"""
import sys; sys.path.insert(0, r'C:\PUMPCALC')
from src.domain.accessory_losses import build_semantic_tdh_balances
import os; os.makedirs('reports', exist_ok=True)

SG = 0.995
balances = build_semantic_tdh_balances(sg=SG)
keys = list(balances.keys())

def scenario_desc(key):
    return balances[key]['description'].split(':')[0].strip()

# ========== 1. pressure_term_scenarios.md ==========
md = [
    '# Pressure Term Scenarios — Hito 5.4A',
    '',
    f'## {len(keys)} parallel scenarios (A–F)',
    '',
]
for key in keys:
    b = balances[key]
    desc = b['description']
    md.append(f'### {key}: {desc}')
    md.append('')
    tdh = b['total_dynamic_head_ft']
    tdh_str = f'{tdh:.6f}' if isinstance(tdh, float) else str(tdh)
    md.append(f'- **Total TDH**: {tdh_str} ft')
    for field in ['static_elevation_head_ft', 'surface_pressure_difference_ft',
                  'pipe_major_losses_ft', 'accessory_minor_losses_ft',
                  'instrument_pressure_drop_ft', 'equipment_pressure_drop_ft',
                  'equipment_internal_pressure_drop_ft', 'required_residual_pressure_head_ft',
                  'unclassified_required_pressure_head_ft',
                  'minimum_required_equipment_inlet_pressure_head_ft',
                  'receiving_vessel_operating_pressure_head_ft',
                  'discharge_fitting_losses_legacy_ft']:
        val = b.get(field)
        if val is not None and abs(val) > 1e-10:
            md.append(f'- {field}: {val}')
    md.append('')

# Add new boundary fields for D
b = balances['VALIDATED_U40_AS_ABSOLUTE']
md.append('### Boundary metadata for ABSOLUTE scenario')
md.append(f'- source_boundary_absolute_pressure_psia: {b.get("source_boundary_absolute_pressure_psia")}')
md.append(f'- destination_required_absolute_pressure_psia: {b.get("destination_required_absolute_pressure_psia")}')
md.append(f'- pressure_difference_psi: {b.get("pressure_difference_psi")}')
md.append(f'- pressure_head_difference_ft: {b.get("pressure_head_difference_ft")}')
md.append('')

md.extend([
    '## Key observations',
    '',
    '1. **A == B**: WORKBOOK_LEGACY and SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION have the same TDH but different composition.',
    '2. **C (Gauge)**: TDH increases slightly when SG-based conversion is applied.',
    f'3. **D (Absolute)**: Now calculable with source boundary (14.7 psia). Difference = {b.get("pressure_difference_psi")} psi, Head = {b.get("pressure_head_difference_ft")} ft.',
    '4. **E (Unknown)**: Returns PRESSURE_REFERENCE_REQUIRED -- user must specify pressure reference.',
    '5. **F (Excluded)**: TDH collapses to ~11.28 ft -- sensitivity only, NOT a recommended correction.',
])
with open('reports/pressure_term_scenarios.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
print('1/8 pressure_term_scenarios.md')

# ========== 2. pressure_term_scenarios.csv ==========
# Use the same fields as before plus boundary fields
fields = ['scenario', 'description', 'static_elevation_head_ft', 'surface_pressure_difference_ft',
          'pipe_major_losses_ft', 'accessory_minor_losses_ft', 'instrument_pressure_drop_ft',
          'equipment_internal_pressure_drop_ft', 'minimum_required_equipment_inlet_pressure_head_ft',
          'receiving_vessel_operating_pressure_head_ft', 'discharge_fitting_losses_legacy_ft',
          'total_dynamic_head_ft']
blines = [','.join(fields)]
for key in keys:
    b = balances[key]
    vals = [key, b['description']]
    for f in fields[2:-1]:
        vals.append(f'{b.get(f, 0.0):.6f}' if abs(b.get(f, 0.0)) > 1e-10 else '0.0')
    tdh = b['total_dynamic_head_ft']
    vals.append(f'{tdh:.6f}' if isinstance(tdh, float) else str(tdh))
    blines.append(','.join(vals))
with open('reports/pressure_term_scenarios.csv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(blines))
print('2/8 pressure_term_scenarios.csv')

# ========== 3. semantic_head_balance.md ==========
md = [
    '# Semantic Head Balance — Hito 5.4A',
    '',
    f'## {len(keys)} TDH scenarios (A–F)',
    '',
    '### Common components',
    '- Static elevation head: 5.27958 ft',
    '- Surface pressure difference: 0.0 ft',
    '- Pipe major losses: 1.696094 ft',
    '',
]
for key in keys:
    b = balances[key]
    tdh = b['total_dynamic_head_ft']
    tdh_str = f'{tdh:.6f}' if isinstance(tdh, float) else str(tdh)
    md.append(f'**{key}**: TDH = {tdh_str} ft — {b["description"]}')
    md.append('')
    for field in ['static_elevation_head_ft', 'surface_pressure_difference_ft',
                  'pipe_major_losses_ft', 'accessory_minor_losses_ft',
                  'instrument_pressure_drop_ft', 'equipment_pressure_drop_ft',
                  'equipment_internal_pressure_drop_ft', 'required_residual_pressure_head_ft',
                  'unclassified_required_pressure_head_ft',
                  'minimum_required_equipment_inlet_pressure_head_ft',
                  'receiving_vessel_operating_pressure_head_ft',
                  'discharge_fitting_losses_legacy_ft']:
        val = b.get(field)
        if val is not None and abs(val) > 1e-10:
            md.append(f'- {field}: {val}')
    md.append('')
md.extend([
    '### Key observations',
    '1. WORKBOOK_LEGACY == SEMANTIC_RECLASSIFICATION_LEGACY_CONVERSION (same TDH, different composition)',
    '2. VALIDATED_U40_AS_GAUGE adjusts for SG correction',
    '3. VALIDATED_U40_AS_ABSOLUTE now calculable with source boundary (14.7 psia)',
    '4. U40_REFERENCE_UNKNOWN requires pressure reference specification',
    '5. U40_EXCLUDED is sensitivity only — not a recommended correction',
])
with open('reports/semantic_head_balance.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
print('3/8 semantic_head_balance.md')

# ========== 4. semantic_head_balance.csv ==========
with open('reports/semantic_head_balance.csv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(blines))  # same format as pressure_term_scenarios
print('4/8 semantic_head_balance.csv')

# ========== 5. equipment_pressure_requirement_model.md ==========
md = [
    '# Equipment Pressure Requirement Model — Hito 5.4A',
    '',
    '## PressureRequirement data model',
    '',
    '| Field | Type | Description |',
    '|-------|------|-------------|',
    '| term_id | str | Unique identifier |',
    '| name | str | Human-readable name |',
    '| term_type | PressureTermType | INSTRUMENT_PRESSURE_DROP, EQUIPMENT_INTERNAL_PRESSURE_DROP, MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE, RECEIVING_VESSEL_OPERATING_PRESSURE |',
    '| value | float | Numerical value |',
    '| unit | str | psi, psig, psia, bar(g), etc. |',
    '| pressure_reference | PressureReference | GAUGE, ABSOLUTE, DIFFERENTIAL, VACUUM, UNKNOWN |',
    '| flow_dependency | FlowDependency | FLOW_INDEPENDENT, QUADRATIC_WITH_FLOW, MANUFACTURER_CURVE, USER_DEFINED, UNKNOWN |',
    '| design_flow_gpm | float or None | Associated design flow rate |',
    '| active | bool | Whether term contributes to balance |',
    '| source_type | str | WORKBOOK_MANUAL_INPUT, etc. |',
    '| source_sheet | str or None | Source workbook sheet |',
    '| source_cell | str or None | Source cell reference |',
    '| source_comment | str or None | Cell comment text |',
    '| confidence | str | PROVISIONAL, HIGH, USER_CONFIRMED_SEMANTICS |',
    '| user_confirmed | bool | Whether confirmed by user |',
    '| notes | str or None | Free-text notes |',
    '| start_node | str or None | Hydraulic node (start) |',
    '| end_node | str or None | Hydraulic node (end) |',
    '| combination_rule | str | MAXIMUM_REQUIREMENT, ADDITIVE, ALTERNATIVE_SCENARIOS, USER_DEFINED |',
    '',
    '## Current case terms',
    '',
    '| ID | Name | Type | Value | Ref | Flow Dep | SG | Legacy (ft) | Validated (ft) | Confirmed |',
    '|----|------|------|-------|-----|----------|----|------------|---------------|-----------|',
    '| DISCHARGE_INSTRUMENT_FT_001 | Perdida del transmisor de flujo | INSTRUMENT_PRESSURE_DROP | 0.36 psi | DIFFERENTIAL | UNKNOWN | 0.995 | 0.8316 | 0.8349 | True |',
    '| EQUIPMENT_MINIMUM_INLET_PRESSURE_001 | Presion minima requerida en la entrada del equipo | MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE | 79.77 psi | UNKNOWN | FLOW_INDEPENDENT | 0.995 | 184.2687 | 185.0097 | True |',
    '',
    '## Confirmed classifications',
    '',
    '### U39 — INSTRUMENT_PRESSURE_DROP',
    '- Cell: TABLA DE ACCESORIOS DESCARGA!U39',
    '- Value: 0.36 psi (differential)',
    '- Comment: "PERDIDAS POR TRANSMISOR DE FLUJO"',
    '- Reference: DIFFERENTIAL (confirmed)',
    '- Flow dependency: UNKNOWN (do not assume Q^2 without curve)',
    '- Confidence: HIGH (user confirmed)',
    '',
    '### U40 — MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE',
    '- Cell: TABLA DE ACCESORIOS DESCARGA!U40',
    '- Value: 79.77 psi',
    '- Comment: "PRESION DE OPERACION DEL EQUIPO"',
    '- Reference: UNKNOWN (pending user confirmation)',
    '- Flow dependency: FLOW_INDEPENDENT (does not vary with flow)',
    '- Confidence: USER_CONFIRMED_SEMANTICS (semantics confirmed, reference pending)',
    '',
    '## Hito 5.4A additions',
    '',
    '### Source boundary definition',
    '- Boundary type: FREE_SURFACE (open tank)',
    '- Atmospheric pressure: 14.7 psia',
    '- Vessel pressure: 0.0 psig',
    '- Computed source_abs: 14.7 psia',
    '',
    '### Boundary pressure rules',
    '- **GAUGE**: pressure_difference = required_value; dest_abs = source_abs + value',
    '- **ABSOLUTE**: pressure_difference = required_abs - source_abs; dest_abs = required_value',
    '- **DIFFERENTIAL**: same as GAUGE (pressure_difference = value)',
    '- **UNKNOWN**: returns PRESSURE_REFERENCE_REQUIRED',
    '',
    '### Current absolute result',
    '- Required: 79.77 psia (ABSOLUTE)',
    '- Source: 14.7 psia',
    '- Difference: 65.07 psi',
    '- Head: ~150.92 ft',
]
with open('reports/equipment_pressure_requirement_model.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
print('5/8 equipment_pressure_requirement_model.md')

# ========== 6. equipment_pressure_requirement_model.csv ==========
csv_lines = [
    'term_id,name,type,value,unit,reference,flow_dependency,sg,legacy_ft,validated_ft,confirmed,notes',
    'DISCHARGE_INSTRUMENT_FT_001,"Perdida del transmisor de flujo",INSTRUMENT_PRESSURE_DROP,0.36,psi,DIFFERENTIAL,UNKNOWN,0.995,0.8316,0.834944,True,"U39 - differential pressure drop across flow transmitter"',
    'EQUIPMENT_MINIMUM_INLET_PRESSURE_001,"Presion minima requerida en la entrada del equipo",MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE,79.77,psi,UNKNOWN,FLOW_INDEPENDENT,0.995,184.2687,185.009664,True,"U40 - minimum required equipment inlet pressure"',
]
with open('reports/equipment_pressure_requirement_model.csv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(csv_lines))
print('6/8 equipment_pressure_requirement_model.csv')

# ========== 7. pressure_boundary_combination_rules.md ==========
md = [
    '# Pressure Boundary Combination Rules — Hito 5.4A',
    '',
    '## Combination rules',
    '',
    '| Rule | Description | When to use |',
    '|------|-------------|-------------|',
    '| MAXIMUM_REQUIREMENT | The higher of two overlapping requirements dominates | Opposite ends of same pipe, safety margin |',
    '| ADDITIVE | Both requirements must be met in series | Sequential equipment, series configuration |',
    '| ALTERNATIVE_SCENARIOS | Each term generates a separate TDH scenario | GAUGE vs ABSOLUTE pressure reference alternatives |',
    '| USER_DEFINED | Custom rule set by user | Site-specific rules |',
    '',
    '## Current application',
    '',
    '- U39 (INSTRUMENT_PRESSURE_DROP) and U40 (MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE) are treated as ALTERNATIVE_SCENARIOS.',
    '- They do not share a common node (no overlap detected).',
    '- U39 is located at the discharge pipe (flow transmitter).',
    '- U40 is at the equipment inlet (operating pressure requirement).',
    '',
    '## Hito 5.4A Boundary hierarchy',
    '',
    '| Boundary type | Used for |',
    '|--------------|----------|',
    '| FREE_SURFACE | Open tank, vented vessel |',
    '| VESSEL_GAS_SPACE | Pressurized vessel gas space |',
    '| PUMP_SUCTION_FLANGE | NPSHa calculation node |',
    '| PIPE_NODE | Intermediate pipe analysis |',
    '| EQUIPMENT_INLET | Equipment pressure requirement |',
    '| EQUIPMENT_OUTLET | Equipment discharge boundary |',
    '',
    '## Scenario combination',
    '',
    f'Current 6 scenarios:',
    '',
]
for key in keys:
    md.append(f'- {key}: {balances[key]["description"]}')
md.extend([
    '',
    '## Absolute scenario requires boundary reference',
    '',
    '- D (ABSOLUTE): uses source_boundary_absolute_pressure_psia = 14.7 (computed from atm + vessel gauge)',
    '- E (UNKNOWN): PRESSURE_REFERENCE_REQUIRED until user specifies reference',
    '- The absolute vs gauge combination follows ALTERNATIVE_SCENARIOS (each produces a separate TDH)',
])
with open('reports/pressure_boundary_combination_rules.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))
print('7/8 pressure_boundary_combination_rules.md')

# ========== 8. data_lineage.csv (append) ==========
import csv
from datetime import datetime
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
new_rows = [
    [now, 'Hito 5.4A', 'BoundaryType', 'Enum', 'Created', '6 boundary types (FREE_SURFACE through EQUIPMENT_OUTLET)'],
    [now, 'Hito 5.4A', 'SystemBoundary', 'Dataclass', 'Created', 'Typed boundary node with pressure, elevation, confidence'],
    [now, 'Hito 5.4A', 'PressureBoundaryResult', 'Dataclass', 'Created', 'Result container for boundary pressure computations'],
    [now, 'Hito 5.4A', 'compute_source_boundary_absolute_pressure', 'Function', 'Created', 'GAUGE/ABSOLUTE/VACUUM variants for source boundary'],
    [now, 'Hito 5.4A', 'required_boundary_pressure_head', 'Function', 'Created', '4-reference rule engine (GAUGE/ABSOLUTE/DIFFERENTIAL/UNKNOWN)'],
    [now, 'Hito 5.4A', 'DESTINATION_PRESSURE_BELOW_SOURCE_PRESSURE', 'Warning', 'Added', 'Negative pressure differences are allowed, not clamped to zero'],
    [now, 'Hito 5.4A', 'build_semantic_tdh_balances', 'Function', 'Updated', 'D (ABSOLUTE) now calculable with source boundary; new E (UNKNOWN) scenario; 6 total scenarios'],
    [now, 'Hito 5.4A', 'U40_REFERENCE_UNKNOWN', 'Scenario', 'Added', 'New E scenario returning PRESSURE_REFERENCE_REQUIRED'],
]
# Read existing
existing = []
try:
    with open('reports/data_lineage.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        existing = list(reader)
except FileNotFoundError:
    existing = [['Timestamp', 'Milestone', 'Component', 'Type', 'Action', 'Description']]

# Append new rows
if len(existing) <= 1:
    # Only header, just add new
    existing.extend(new_rows)
else:
    existing.extend(new_rows)

with open('reports/data_lineage.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(existing)
print('8/8 data_lineage.csv updated with 8 new entries')

print('\nAll 8 existing reports updated.')
