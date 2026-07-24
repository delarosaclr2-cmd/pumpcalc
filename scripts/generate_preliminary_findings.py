import json
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path(r"C:\PUMPCALC\reports")

# Compile all findings into a preliminary findings report
findings = [
    {
        "id": "FIND-001",
        "severity": "HIGH",
        "sheet": "VELOCIDADES RECOMENDADAS",
        "cell": "Named Range: LISTA",
        "evidence": "Named range 'LISTA' references '#REF!' - broken reference",
        "possible_impact": "If used in formulas or data validation, would cause #REF! errors",
        "missing_info": "Need to determine what this range originally referenced",
        "status": "CONFIRMED_ERROR",
        "category": "BROKEN_REFERENCE"
    },
    {
        "id": "FIND-002",
        "severity": "MEDIUM",
        "sheet": "CAIDA PRESION DE TUBERIA",
        "cell": "V16",
        "evidence": "Formula '= 64/V11' calculates laminar friction factor (f=64/Re) but G16 uses VLOOKUP from OUTPIPES table for friction factor. Inconsistent approach between discharge (turbulent lookup) and suction (laminar assumption).",
        "possible_impact": "Suction friction factor may be incorrect if flow is turbulent (Re > 2300). Current Re ~462,915 (turbulent) but using laminar formula.",
        "missing_info": "Verify if suction flow regime is actually laminar",
        "status": "PROBABLE_ERROR",
        "category": "INCONSISTENT_METHOD"
    },
    {
        "id": "FIND-003",
        "severity": "HIGH",
        "sheet": "CALCULO DE BOMBA",
        "cell": "E14 (NPSH Available)",
        "evidence": "Formula: =((C8+E8)*(2.31/E11))+C9-C11-C14-E9. C8=14.7 psia (atmospheric), E8=0 psig (vessel pressure). Adding absolute + gauge pressure is dimensionally inconsistent.",
        "possible_impact": "NPSHa calculation may be wrong. If E8 is gauge, should not add directly to absolute C8. If vessel is at atmospheric, E8 should be 0 psig = 14.7 psia absolute.",
        "missing_info": "Clarify if E8 (vessel pressure) is absolute or gauge; clarify reference elevation for C9 (static head)",
        "status": "PROBABLE_ERROR",
        "category": "UNIT_INCONSISTENCY"
    },
    {
        "id": "FIND-004",
        "severity": "MEDIUM",
        "sheet": "CAIDA PRESION DE TUBERIA",
        "cell": "G19, V19 (Friction loss per ft)",
        "evidence": "Formula uses constant 2.3071. This appears to be a combined conversion factor. Need to verify: hf/L = f * (1/D) * (V^2/2g) with imperial units. Standard DW: hf = f*(L/D)*(V^2/2g) where V in ft/s, D in ft, g=32.174 ft/s^2. If using Q in GPM, D in inches, then V = Q*0.4085/D^2. The constant 2.3071 needs dimensional verification.",
        "possible_impact": "If constant is wrong, all friction losses are wrong proportionally",
        "missing_info": "Full derivation of 2.3071 constant from first principles",
        "status": "INSUFFICIENT_INFORMATION",
        "category": "UNVERIFIED_CONSTANT"
    },
    {
        "id": "FIND-005",
        "severity": "MEDIUM",
        "sheet": "CAIDA PRESION DE TUBERIA",
        "cell": "G11, V11 (Reynolds Number)",
        "evidence": "Formula: =50.6*G5*G9/(G8*G10). Constant 50.6 for imperial units (Q=GPM, D=inches, ρ=lb/ft³, μ=cP). Standard formula: Re = 50.6 * Q * SG / (D * μ) where Q=GPM, D=inches, μ=cP. But G9 is density (lb/ft³) not specific gravity. If G9=62.4 (water), then 50.6*62.4 = 3157, but standard is 50.6*SG. Using density directly would give Re 62.4x too high.",
        "possible_impact": "Reynolds number could be off by factor of 62.4 (specific weight of water), leading to wrong flow regime and friction factor",
        "missing_info": "Confirm units of G9/G10 - are they density (lb/ft³) or specific gravity (dimensionless)?",
        "status": "PROBABLE_ERROR",
        "category": "UNIT_INCONSISTENCY"
    },
    {
        "id": "FIND-006",
        "severity": "LOW",
        "sheet": "CALCULO DE BOMBA",
        "cell": "C9 (Static Suction Head)",
        "evidence": "Formula: =500/304.8. Hardcoded 500 mm elevation difference. No reference to where this value comes from.",
        "possible_impact": "If elevation is wrong, NPSHa and TDH are wrong",
        "missing_info": "Source of 500 mm elevation value",
        "status": "UNVERIFIED",
        "category": "HARDCODED_VALUE"
    },
    {
        "id": "FIND-007",
        "severity": "LOW",
        "sheet": "CALCULO DE BOMBA",
        "cell": "C12 (Suction Pipe Length)",
        "evidence": "Formula: =2.12*3.281. Hardcoded 2.12 meters converted to feet. No reference to piping layout.",
        "possible_impact": "If actual length differs, suction friction loss is wrong",
        "missing_info": "Source of 2.12 m suction pipe length",
        "status": "UNVERIFIED",
        "category": "HARDCODED_VALUE"
    },
    {
        "id": "FIND-008",
        "severity": "MEDIUM",
        "sheet": "CALCULO DE BOMBA",
        "cell": "E9 (Vapor Pressure)",
        "evidence": "Formula: =VLOOKUP(A32,presionvapor,4,FALSE). A32=9 (fluid code). The presionvapor table in VELOCIDADES RECOMENDADAS Y4:AB23 needs verification for correct vapor pressure at operating temperature.",
        "possible_impact": "Wrong vapor pressure directly affects NPSHa",
        "missing_info": "Operating temperature (C9 in CALCULO DE BOMBA shows formula referencing G9 from CAIDA sheet, but G9 is density, not temperature)",
        "status": "INSUFFICIENT_INFORMATION",
        "category": "MISSING_DATA"
    },
    {
        "id": "FIND-009",
        "severity": "MEDIUM",
        "sheet": "TABLA DE ACCESORIOS DESCARGA / SUCCION",
        "cell": "Column I (Accessory Loss Calculation)",
        "evidence": "Formula: =((D*F)*($H$2^2)/(32.4*2))*H. This appears to be: Leq = K * V^2 / (2g) * count? But 32.4 ≈ 2g (64.4/2), and there's a factor D (ft from table) * F (K factor). The Crane method uses: h = K * V^2 / (2g). The equivalent length Leq = K * D / f. The current formula seems to mix both methods.",
        "possible_impact": "Accessory losses may be double-counted or incorrectly calculated",
        "missing_info": "Verify if column D is 'Ft' (equivalent length from table) or 'K' factor; verify if column F is K or f; verify method (K-method vs Leq-method)",
        "status": "INSUFFICIENT_INFORMATION",
        "category": "AMBIGUOUS_FORMULA"
    },
    {
        "id": "FIND-010",
        "severity": "LOW",
        "sheet": "CALCULO DE BOMBA",
        "cell": "E27 (Specific Speed)",
        "evidence": "Formula: =(C29*(E4^0.5))/(E24^0.75). C29=3600 (RPM), E4=GPM, E24=TDH in meters. Specific speed Ns = N*sqrt(Q)/H^0.75. But units: Q should be in GPM, H in ft for US Ns. E24 is TDH in METERS (converted from ft). Using meters for H with GPM for Q gives mixed units.",
        "possible_impact": "Specific speed value will be incorrect (unit mismatch)",
        "missing_info": "Confirm intended unit system for specific speed calculation",
        "status": "PROBABLE_ERROR",
        "category": "UNIT_INCONSISTENCY"
    },
    {
        "id": "FIND-011",
        "severity": "LOW",
        "sheet": "RESUMEN PARA PDF",
        "cell": "D13, D15, D16 (GPM to LPM conversion)",
        "evidence": "Formulas use 3.785 (not 3.78541). Similarly D19, D20, D21 use 3.28 (not 3.28084) for ft to m conversion.",
        "possible_impact": "Minor rounding differences in reported values",
        "missing_info": "Acceptable precision for reporting",
        "status": "MINOR_ROUNDING",
        "category": "ROUNDING"
    },
    {
        "id": "FIND-012",
        "severity": "MEDIUM",
        "sheet": "VELOCIDADES RECOMENDADAS",
        "cell": "Column AB (Rows 5-23)",
        "evidence": "Formulas: =(AA5*3.2808)/1.422 etc. Constants 3.2808 (ft/m) and 1.422 (unexplained). Appears to be velocity conversion.",
        "possible_impact": "If 1.422 is wrong, all recommended velocities in table are wrong",
        "missing_info": "Derivation of 1.422 constant",
        "status": "UNVERIFIED_CONSTANT",
        "category": "UNVERIFIED_CONSTANT"
    },
    {
        "id": "FIND-013",
        "severity": "HIGH",
        "sheet": "CALCULO DE BOMBA",
        "cell": "C28 (Total Dynamic Head summation)",
        "evidence": "Formula: =C11+C14+C21+C24+C26. Terms: C11=suction accessory losses, C14=suction pipe friction, C21=static head (C20-C9), C24=discharge accessory losses, C26=discharge pipe friction. But C20 comes from E20/C22 (hydraulic HP / efficiency) which is circular - C20 is discharge pressure head? Need to trace C20.",
        "possible_impact": "If C20 is not static discharge head, TDH summation is wrong",
        "missing_info": "Trace C20 (='CAIDA PRESION DE TUBERIA'!G5? No, E20 is hydraulic HP formula). C20 appears to be a reference to discharge pressure head but formula shows E20 is power calc.",
        "status": "INSUFFICIENT_INFORMATION",
        "category": "CIRCULAR_REFERENCE"
    },
    {
        "id": "FIND-014",
        "severity": "MEDIUM",
        "sheet": "REPORTE GENERAL",
        "cell": "C24, D24 (RAMALES references)",
        "evidence": "C24 references RAMALES!E15, D24 references RAMALES!#REF!. RAMALES sheet only has data up to column F (F18, F19). Column E15 and #REF! suggest deleted columns or incorrect references.",
        "possible_impact": "Report shows #REF! or wrong values for branch losses",
        "missing_info": "What was in RAMALES column E? Was data deleted?",
        "status": "CONFIRMED_ERROR",
        "category": "BROKEN_REFERENCE"
    },
    {
        "id": "FIND-015",
        "severity": "LOW",
        "sheet": "MACROS (Módulo6)",
        "cell": "Macro5 and Macro9 both assigned to CTRL+SHIFT+M",
        "evidence": "Two macros (Macro5 and Macro9) have same keyboard shortcut CTRL+SHIFT+M",
        "possible_impact": "Only one macro will execute; user confusion",
        "missing_info": "Which macro is intended for this shortcut",
        "status": "CONFIRMED_ERROR",
        "category": "MACRO_CONFLICT"
    }
]

# Save JSON
json_path = REPORTS_DIR / "preliminary_findings.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(findings, f, indent=2, ensure_ascii=False)

# Save Markdown
md_path = REPORTS_DIR / "preliminary_findings.md"
with open(md_path, 'w', encoding='utf-8') as md_file:
    md_file.write("# Preliminary Findings Report\n\n")
    md_file.write(f"**Generated:** {datetime.now().isoformat()}\n")
    md_file.write(f"**Total Findings:** {len(findings)}\n\n")
    
    # Summary by severity
    by_severity = {}
    for find in findings:
        sev = find['severity']
        if sev not in by_severity:
            by_severity[sev] = []
        by_severity[sev].append(find)
    
    md_file.write("## Summary by Severity\n\n")
    for sev in ["HIGH", "MEDIUM", "LOW"]:
        if sev in by_severity:
            md_file.write(f"- **{sev}:** {len(by_severity[sev])} findings\n")
    
    md_file.write("\n## Summary by Category\n\n")
    by_category = {}
    for find in findings:
        cat = find['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(find)
    
    for cat in sorted(by_category.keys()):
        md_file.write(f"- **{cat}:** {len(by_category[cat])} findings\n")
    
    md_file.write("\n---\n\n## Detailed Findings\n\n")
    for finding in findings:
        md_file.write(f"### {finding['id']}: {finding['severity']} - {finding['category']}\n\n")
        md_file.write(f"- **Sheet:** {finding['sheet']}\n")
        md_file.write(f"- **Cell/Reference:** {finding['cell']}\n")
        md_file.write(f"- **Evidence:** {finding['evidence']}\n")
        md_file.write(f"- **Possible Impact:** {finding['possible_impact']}\n")
        md_file.write(f"- **Missing Information:** {finding['missing_info']}\n")
        md_file.write(f"- **Status:** {finding['status']}\n\n")
        md_file.write("---\n\n")

print(f"Preliminary findings saved to {json_path} and {md_path}")