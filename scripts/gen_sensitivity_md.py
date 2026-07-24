"""
Generate sensitivity analysis markdown report.
"""
import csv
from pathlib import Path

csv_path = Path(r"C:\PUMPCALC\reports\sensitivity_analysis.csv")
md_path = Path(r"C:\PUMPCALC\reports\sensitivity_analysis.md")

rows = []
with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Group by parameter
params = {}
for r in rows:
    p = r['parameter']
    if p not in params:
        params[p] = []
    params[p].append(r)

with open(md_path, 'w') as f:
    f.write("# Sensitivity Analysis Report\n\n")
    f.write(f"**Generated:** {__import__('datetime').datetime.now().isoformat()}\n\n")
    f.write("## Summary\n\n")
    f.write("This analysis evaluates the sensitivity of key hydraulic outputs to variations in input parameters.\n\n")
    f.write("**Key Observations:**\n")
    f.write("- **TDH is insensitive** to all parameters in legacy mode (constant 195.55 ft) - this is because the legacy calculator uses hardcoded accessory losses and pipe lengths that don't scale with flow\n")
    f.write("- **NPSHa is insensitive** to most parameters except atmospheric pressure and vapor pressure\n")
    f.write("- **Friction factors are constant** in legacy mode (hardcoded), but vary with Reynolds number in validated mode\n")
    f.write("- **Power is insensitive** to most parameters in legacy mode\n\n")
    
    f.write("## Detailed Results by Parameter\n\n")
    
    for param, values in sorted(params.items()):
        f.write(f"### {param}\n\n")
        f.write("| Value | Legacy TDH (ft) | Validated TDH (ft) | Legacy NPSH (ft) | Validated NPSH (ft) | Legacy HP | Validated HP | Legacy fD | Validated fD | Legacy fS | Validated fS |\n")
        f.write("|-------|----------------|-------------------|-----------------|---------------------|-----------|--------------|-----------|--------------|-----------|--------------|\n")
        for v in values:
            f.write(f"| {float(v['value']):.4f} | {float(v['legacy_tdh_ft']):.2f} | {float(v['validated_tdh_ft']):.2f} | {float(v['legacy_npsha_ft']):.2f} | {float(v['validated_npsha_ft']):.2f} | {float(v['legacy_shaft_hp']):.2f} | {float(v['validated_shaft_hp']):.2f} | {float(v['legacy_f_discharge']):.6f} | {float(v['validated_f_discharge']):.6f} | {float(v['legacy_f_suction']):.6f} | {float(v['validated_f_suction']):.6f} |\n")
        f.write("\n")
    
    f.write("## Sensitivity Summary\n\n")
    f.write("| Parameter | Legacy TDH Range | Validated TDH Range | Legacy NPSH Range | Validated NPSH Range | Notes |\n")
    f.write("|-----------|-----------------|--------------------|------------------|---------------------|-------|\n")
    
    for param, values in sorted(params.items()):
        v_list = [float(v['value']) for v in values]
        legacy_tdh = [float(v['legacy_tdh_ft']) for v in values]
        valid_tdh = [float(v['validated_tdh_ft']) for v in values]
        legacy_npsh = [float(v['legacy_npsha_ft']) for v in values]
        valid_npsh = [float(v['validated_npsha_ft']) for v in values]
        
        td_range = f"{min(legacy_tdh):.2f}-{max(legacy_tdh):.2f}"
        vtd_range = f"{min(valid_tdh):.2f}-{max(valid_tdh):.2f}"
        np_range = f"{min(legacy_npsh):.2f}-{max(legacy_npsh):.2f}"
        vnp_range = f"{min(valid_npsh):.2f}-{max(valid_npsh):.2f}"
        
        notes = ""
        if max(legacy_tdh) - min(legacy_tdh) < 0.01:
            notes = "Legacy TDH constant (hardcoded losses)"
        
        f.write(f"| {param} | {td_range} | {vtd_range} | {np_range} | {vnp_range} | {notes} |\n")

print("Markdown report generated at:", md_path)