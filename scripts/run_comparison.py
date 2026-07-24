"""
Run comparison between legacy and validated calculations.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

from src.application.legacy_calculator import calculate_legacy_from_inputs
from src.application.validated_calculator import calculate_validated

# Run both calculators
legacy = calculate_legacy_from_inputs()
validated = calculate_validated()

# Excel reference values (from data_only workbook)
excel_values = {
    'discharge_diameter_in': 6.048364477182011,
    'suction_diameter_in': 10.041761045944389,
    're_discharge': 768552.5213911285,
    're_suction': 462915.39382010826,
    'f_discharge': 0.0272,
    'f_suction': 0.0001382542055295547,
    'hf_per_ft_discharge': 0.04451507678789271,
    'hf_per_ft_suction': 0.0037530338578161656,
    'npsha_ft': 33.87938980028249,
    'tdh_ft': 195.55111342538294,
    'tdh_m': 59.60397937205672,
    'hydraulic_hp': 37.85827581560259,
    'shaft_hp': 52.580938632781375,
    'shaft_kw': 39.2043478446018,
    'torque_lbft': 162.4441704113928,
    'specific_speed_legacy': 4658.352840595163,
}

legacy_attrs = {
    'discharge_diameter_in': 'discharge_diameter_in',
    'suction_diameter_in': 'suction_diameter_in',
    're_discharge': 're_discharge',
    're_suction': 're_suction',
    'f_discharge': 'f_discharge',
    'f_suction': 'f_suction',
    'hf_per_ft_discharge': 'hf_per_ft_discharge',
    'hf_per_ft_suction': 'hf_per_ft_suction',
    'npsha_ft': 'npsha_ft',
    'tdh_ft': 'tdh_ft',
    'tdh_m': 'tdh_m',
    'hydraulic_hp': 'hydraulic_hp',
    'shaft_hp': 'shaft_hp',
    'shaft_kw': 'shaft_kw',
    'torque_lbft': 'torque_lbft',
    'specific_speed_legacy': 'specific_speed_legacy',
}

validated_keys = {
    'discharge_diameter_in': 'discharge_diameter_in',
    'suction_diameter_in': 'suction_diameter_in',
    're_discharge': 're_discharge',
    're_suction': 're_suction',
    'f_discharge': 'f_discharge',
    'f_suction': 'f_suction',
    'hf_per_ft_discharge': 'hf_per_ft_discharge',
    'hf_per_ft_suction': 'hf_per_ft_suction',
    'npsha_ft': 'npsha_ft',
    'tdh_ft': 'tdh_ft',
    'tdh_m': 'tdh_m',
    'hydraulic_hp': 'hydraulic_hp',
    'shaft_hp': 'shaft_hp',
    'shaft_kw': 'shaft_kw',
    'torque_lbft': 'torque_lbft',
    'specific_speed_legacy': 'specific_speed_legacy',
}

print(f"{'Variable':<35} {'Excel':>12} {'Legacy':>12} {'Validated':>12} {'Leg-Diff':>10} {'Val-Diff':>10} {'Leg-Rel%':>8} {'Val-Rel%':>8} {'Status':<15}")
print('-' * 120)

for key, excel_val in excel_values.items():
    legacy_val = getattr(legacy, legacy_attrs.get(key, ''))
    validated_val = validated[validated_keys.get(key, key)]
    
    legacy_diff = legacy_val - excel_val
    val_diff = validated[key] - excel_val
    legacy_rel = (legacy_diff / excel_val * 100) if excel_val != 0 else 0
    val_rel = ((validated[key] - excel_val) / excel_val * 100) if excel_val != 0 else 0
    
    if abs(legacy_diff) < 1e-9:
        status = "LEGACY_MATCH"
    elif abs(validated[key] - excel_val) < abs(legacy_val - excel_val):
        status = "VALIDATED_BETTER"
    elif abs(legacy_diff) < abs(excel_val) * 0.001:
        status = "ROUNDING"
    else:
        status = "FORMULA_DIFF"
    
    print(f"{key:<35} {excel_val:>12.6f} {legacy_val:>12.6f} {validated[key]:>12.6f} {legacy_diff:>10.6f} {val_diff:>10.6f} {legacy_rel:>8.3f} {val_rel:>8.3f} {status:<15}")

print()
print("=" * 120)
print("KEY FINDINGS:")
print("=" * 120)

# Friction factor comparison
print("\n1. FRICTION FACTOR COMPARISON:")
print(f"  Discharge: Legacy f={legacy.f_discharge:.6f} (hardcoded) vs Validated={validated['f_discharge']:.6f} (Colebrook)")
print(f"  Suction:   Legacy f={legacy.f_suction:.6f} (64/Re laminar) vs Validated={validated['f_suction']:.6f} (Colebrook)")
print(f"  Discharge: Legacy overestimates f by {((legacy.f_discharge/validated['f_discharge'])-1)*100:.0f}%")
print(f"  Suction:   Legacy underestimates f by {((legacy.f_suction/validated['f_suction'])-1)*100:.0f}% (uses laminar for turbulent)")

# NPSH comparison
print(f"\n2. NPSH AVAILABLE:")
print(f"  Excel:     {excel_values['npsha_ft']:.4f} ft")
print(f"  Legacy:    {legacy.npsha_ft:.4f} ft")
print(f"  Validated: {validated['npsha_ft']:.2f} ft")
print(f"  Difference (Validated - Excel): {validated['npsha_ft'] - excel_values['npsha_ft']:.4f} ft")
print(f"  Note: Validated divides vapor pressure by SG; Excel does not")

# TDH comparison
print(f"\n3. TDH:")
print(f"  Excel:     {excel_values['tdh_ft']:.4f} ft")
print(f"  Legacy:    {legacy.tdh_ft:.4f} ft")
print(f"  Validated: {validated['tdh_ft']:.2f} ft")

# Power comparison
print(f"\n4. POWER:")
print(f"  Shaft HP - Excel: {excel_values['shaft_hp']:.4f}, Legacy: {legacy.shaft_hp:.4f}, Validated: {validated['shaft_hp']:.2f}")
print(f"  Shaft kW - Excel: {excel_values['shaft_kw']:.4f}, Legacy: {legacy.shaft_kw:.4f}, Validated: {validated['shaft_kw']:.2f}")

# Specific speed
print(f"\n5. SPECIFIC SPEED:")
print(f"  Legacy (H in m): {legacy.specific_speed_legacy:.0f} (WRONG - mixed units)")
print(f"  Correct US:      {validated['specific_speed_us']:.0f}")
print(f"  Metric:          {validated['specific_speed_metric']:.1f}")

print("\n" + "=" * 120)
print("SUMMARY:")
print("- Legacy mode reproduces Excel exactly (LEGACY_MATCH for all direct calculations)")
print("- Validated mode uses correct physics (Colebrook-White, proper NPSH, correct Ns)")
print("- Major discrepancies: Friction factors (suction 100x low, discharge 1.8x high)")
print("- NPSH difference: ~1 ft (vapor pressure SG correction)")
print("- Specific speed: Legacy uses mixed units (GPM + meters), correct uses ft")