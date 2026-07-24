import json
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path(r"C:\PUMPCALC\reports")

# Load updated findings
with open(REPORTS_DIR / "preliminary_findings.json", encoding='utf-8') as f:
    findings = json.load(f)

# Create technical_review_corrections
corrections = []
for ff in findings:
    if 'supersedes' in ff or 'correction' in ff:
        corrections.append({
            "previous_id": ff.get('supersedes', ff['id']),
            "previous_conclusion": ff.get('status', ''),
            "previous_evidence": ff.get('evidence', ''),
            "new_derivation": ff.get('correction', '') or ff.get('evidence', ''),
            "corrected_conclusion": ff.get('status', ''),
            "correction_reason": ff.get('correction', ''),
            "project_impact": ff.get('possible_impact', ''),
            "timestamp": datetime.now().isoformat()
        })

# Add explicit corrections for major changes
major_corrections = [
    {
        "previous_id": "FIND-005",
        "previous_conclusion": "PROBABLE_ERROR - 50.6 factor assumes specific gravity, not density",
        "previous_evidence": "Re = 50.6 × Q × SG / (D × μ) standard formula; workbook uses density ρ",
        "new_derivation": "Re = ρVD/μ with Q=GPM, ρ=lbm/ft³, D=in, μ=cP. Derived constant = 50.66. Workbook uses ρ=62 lbm/ft³ from OUTPIPES, not SG.",
        "corrected_conclusion": "FORMULA_CORRECT_WITH_DENSITY",
        "correction_reason": "Standard formula Re=50.6×Q×SG/(D×μ) assumes SG relative to water (ρ=62.4×SG). Workbook fluid tables provide mass density directly in lbm/ft³. Formula is correct for given units.",
        "project_impact": "Hydraulic engine can use workbook Re formula directly; no correction needed",
        "timestamp": datetime.now().isoformat()
    },
    {
        "previous_id": "FIND-003",
        "previous_conclusion": "PROBABLE_ERROR - Patm(psia)+Pvessel(psig) sums absolute + gauge",
        "previous_evidence": "C8=14.7 psia, E8=0 psig; formula (C8+E8)*2.31/SG",
        "new_derivation": "Standard NPSH: P_abs = Patm_abs + Pvessel_gauge. For open tank Pvessel=0 psig → 14.7 psia. Formula correct IF E8 is gauge pressure (standard convention). Vapor pressure E9 in ft water needs /SG correction.",
        "corrected_conclusion": "CORRECT_FOR_GAUGE_VESSEL_PRESSURE",
        "correction_reason": "Vessel pressure is conventionally given in gauge. Sum Patm_abs + Pvessel_gauge = absolute pressure at liquid surface. Formula dimensionally consistent.",
        "project_impact": "Independent engine should follow same convention; add SG correction for vapor pressure term",
        "timestamp": datetime.now().isoformat()
    },
    {
        "previous_id": "FIND-002",
        "previous_conclusion": "PROBABLE_ERROR - inconsistent friction factor method",
        "previous_evidence": "Discharge uses table lookup (0.00013), suction uses 64/Re",
        "new_derivation": "OUTPIPES col 8 = 0.00013 is PIPE ROUGHNESS (ε in ft), NOT friction factor. Discharge friction factor f=0.0272 (G17) hardcoded. Suction uses laminar f=64/Re for Re=462,915 (turbulent). Both sides WRONG.",
        "corrected_conclusion": "CONFIRMED_ERROR - MAJOR",
        "correction_reason": "Discharge uses wrong value (roughness as friction factor) but hardcoded f=0.0272 in formula. Suction uses laminar formula for turbulent flow. Neither uses proper Moody/Colebrook.",
        "project_impact": "Independent engine MUST implement proper friction factor calculation (Colebrook-White or Swamee-Jain)",
        "timestamp": datetime.now().isoformat()
    },
    {
        "previous_id": "FIND-013",
        "previous_conclusion": "INSUFFICIENT_INFORMATION - possible circular reference C28←C21←C20←E20",
        "previous_evidence": "C20=E20/C22, C21=C20-C9, C28=C28=C11+C14+C21+C24+C26",
        "new_derivation": "C20=6.92 (HARDCODED constant), NOT formula. C21=C20-C9 (static head). C28=sum of losses + C21. E20=(E4*C28*E11)/3960 uses C28. NO CIRCULARITY.",
        "corrected_conclusion": "NO_CIRCULAR_REFERENCE",
        "correction_reason": "Previous analysis misread column C (head) as column E (power). C20 is user input 6.92 ft static discharge head.",
        "project_impact": "TDH calculation is linear; independent engine can replicate directly",
        "timestamp": datetime.now().isoformat()
    },
    {
        "previous_id": "FIND-004",
        "previous_conclusion": "INSUFFICIENT_INFORMATION - 2.3071 unverified",
        "previous_evidence": "Used in G19, V19, RAMALES!D12, VELOCIDADES!V27-V30",
        "new_derivation": "2.3071 = 144/62.395 ≈ 2.3077 = psi to ft water conversion (144 in²/ft² ÷ 62.4 lb/ft³). Used to convert pressure drop (psi/ft) to head (ft liquid/ft).",
        "corrected_conclusion": "VALID_PRESSURE_HEAD_CONVERSION",
        "correction_reason": "Constant is standard conversion; slight precision difference (2.3071 vs 2.3077) from using γ=62.428 or rounding",
        "project_impact": "Acceptable; independent engine can use exact 2.3077 or 144/62.4",
        "timestamp": datetime.now().isoformat()
    },
    {
        "previous_id": "FIND-009",
        "previous_conclusion": "INSUFFICIENT_INFORMATION - accessory formula ambiguous",
        "previous_evidence": "Formula =((D*F)*V²/(32.4*2))*H; unclear if K-method or Leq-method",
        "new_derivation": "Standard equivalent length: h = f × (Leq/D) × V²/(2g). Workbook: D=f (friction factor), F=Leq/D, 32.4*2=64.8≈2g (g=32.174). Method is Leq-method with g≈32.4.",
        "corrected_conclusion": "VALID_LEQ_METHOD",
        "correction_reason": "Formula matches standard Leq method; 32.4 is g approximation (32.174). Error 0.7% on velocity head.",
        "project_impact": "Acceptable; independent engine should use exact g=32.174",
        "timestamp": datetime.now().isoformat()
    },
    {
        "previous_id": "FIND-012",
        "previous_conclusion": "UNVERIFIED_CONSTANT - 1.422 unexplained",
        "previous_evidence": "AB = (AA*3.2808)/1.422 in VELOCIDADES RECOMENDADAS",
        "new_derivation": "AA=psia, AB=ft water. 3.2808=ft/m. 1.422 = 3.2808/2.3071 = (ft/m) / (ft water/psi) = psi·m/ft². Formula: ft water = psia × 2.3071. In metric: ft water = (psia × 2.3071) = (AA × 2.3071) = AA × 3.2808 / 1.422.",
        "corrected_conclusion": "EXPLAINED",
        "correction_reason": "1.422 = 3.2808 / 2.3071 derived from pressure-head conversion and metric conversion",
        "project_impact": "Table can be regenerated from fundamentals",
        "timestamp": datetime.now().isoformat()
    }
]

# Save technical_review_corrections
import csv
json_path = REPORTS_DIR / "technical_review_corrections.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(major_corrections, f, indent=2, ensure_ascii=False)

csv_path = REPORTS_DIR / "technical_review_corrections.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    if major_corrections:
        writer = csv.DictWriter(f, fieldnames=major_corrections[0].keys())
        writer.writeheader()
        writer.writerows(major_corrections)

# Generate Markdown
md_path = REPORTS_DIR / "technical_review_corrections.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# Technical Review Corrections\n\n")
    f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
    f.write("This document records all corrections to preliminary findings after critical re-review.\n\n")
    
    for corr in major_corrections:
        f.write(f"## {corr['previous_id']}\n\n")
        f.write(f"**Previous Conclusion:** {corr['previous_conclusion']}\n\n")
        f.write(f"**Previous Evidence:** {corr['previous_evidence']}\n\n")
        f.write(f"**New Derivation:**\n```\n{corr['new_derivation']}\n```\n\n")
        f.write(f"**Corrected Conclusion:** {corr['corrected_conclusion']}\n\n")
        f.write(f"**Correction Reason:** {corr['correction_reason']}\n\n")
        f.write(f"**Project Impact:** {corr['project_impact']}\n\n")
        f.write("---\n\n")

print("technical_review_corrections saved")