"""
Sensitivity Analysis - Impact of key parameter variations on results.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

from src.application.legacy_calculator import calculate_legacy_from_inputs
from src.application.validated_calculator import calculate_validated
from src.infrastructure.input_loader import create_workbook_inputs

# Base case
base = create_workbook_inputs()

# Sensitivity parameters
sensitivities = {
    'roughness_ft': [0.00006, 0.00012, 0.00018, 0.00024, 0.0003],  # 0.5x to 2.5x
    'suction_length_ft': [3.0, 5.0, 7.0, 10.0, 15.0],
    'discharge_length_ft': [18, 27, 36, 54, 72],
    'sg': [0.95, 0.995, 1.0, 1.05, 1.1],
    'viscosity_cP': [0.3, 0.52, 0.8, 1.2, 2.0],
    'atm_psi': [13.0, 14.0, 14.7, 15.5, 16.0],
    'vapor_psi': [0.4, 0.6, 0.8, 1.0, 1.5],
    'efficiency': [0.60, 0.66, 0.72, 0.78, 0.85],
    'rpm': [1750, 2950, 3550, 3600, 5000],
}

results = []

for param, values in sensitivities.items():
    for val in values:
        # Create modified inputs
        inputs = create_workbook_inputs()
        
        if param == 'roughness_ft':
            inputs.suction_pipe.roughness_ft = val
            inputs.discharge_pipe.roughness_ft = val
        elif param == 'suction_length_ft':
            inputs.suction_pipe.length_ft = val
        elif param == 'discharge_length_ft':
            inputs.discharge_pipe.length_ft = val
        elif param == 'sg':
            inputs.fluid.specific_gravity = val
        elif param == 'viscosity_cP':
            inputs.fluid.viscosity_cP = val
        elif param == 'atm_psi':
            inputs.atmospheric_pressure_psi = val
        elif param == 'vapor_psi':
            inputs.fluid.vapor_pressure_psi = val
        elif param == 'efficiency':
            inputs.pump.efficiency = val
        elif param == 'rpm':
            inputs.pump.rpm = val
        
        # Calculate both
        legacy = calculate_legacy_from_inputs(inputs)
        validated = calculate_validated(inputs)
        
        results.append({
            'parameter': param,
            'value': val,
            'legacy_tdh_ft': legacy.tdh_ft,
            'validated_tdh_ft': validated['tdh_ft'],
            'legacy_npsha_ft': legacy.npsha_ft,
            'validated_npsha_ft': validated['npsha_ft'],
            'legacy_shaft_hp': legacy.shaft_hp,
            'validated_shaft_hp': validated['shaft_hp'],
            'legacy_f_discharge': legacy.f_discharge,
            'validated_f_discharge': validated['f_discharge'],
            'legacy_f_suction': legacy.f_suction,
            'validated_f_suction': validated['f_suction'],
        })

# Print summary
print(f"{'Parameter':<20} {'Value':>10} {'Legacy TDH':>12} {'Valid TDH':>12} {'Legacy NPSH':>12} {'Valid NPSH':>12} {'Legacy HP':>10} {'Valid HP':>10} {'Legacy fD':>10} {'Valid fD':>10} {'Legacy fS':>10} {'Valid fS':>10}")
print('-' * 150)
for r in results:
    print(f"{r['parameter']:<20} {r['value']:>10.4f} {r['legacy_tdh_ft']:>12.2f} {r['validated_tdh_ft']:>12.2f} {r['legacy_npsha_ft']:>12.2f} {r['validated_npsha_ft']:>12.2f} {r['legacy_shaft_hp']:>10.2f} {r['validated_shaft_hp']:>10.2f} {r['legacy_f_discharge']:>10.6f} {r['validated_f_discharge']:>10.6f} {r['legacy_f_suction']:>10.6f} {r['validated_f_suction']:>10.6f}")

# Save CSV
import csv
with open(r'C:\PUMPCALC\reports\sensitivity_analysis.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("\nSaved to reports/sensitivity_analysis.csv")