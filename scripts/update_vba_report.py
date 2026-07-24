import json
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path(r"C:\PUMPCALC\reports")

# Update the VBA inventory with the olevba findings
vba_data = {
    "file": r"C:\PUMPCALC\original\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm",
    "inspection_time": datetime.now().isoformat(),
    "vba_classification": "VBA_CODE_FOUND",
    "vba_modules": [
        {"name": "Hoja1.cls", "type": "Worksheet", "sheet": "PAGINA PRINCIPAL", "code": "Private Sub BOMBA_Click()\n\nEnd Sub"},
        {"name": "Hoja2.cls", "type": "Worksheet", "sheet": "CAIDA PRESION DE TUBERIA", "code": "(empty)"},
        {"name": "Hoja3.cls", "type": "Worksheet", "sheet": "CALCULO DE BOMBA", "code": "(empty)"},
        {"name": "Hoja4.cls", "type": "Worksheet", "sheet": "TABLA DE ACCESORIOS DESCARGA", "code": "(empty)"},
        {"name": "Hoja12.cls", "type": "Worksheet", "sheet": "005PU001", "code": "(empty)"},
        {"name": "Hoja11.cls", "type": "Worksheet", "sheet": "RESUMEN PARA PDF", "code": "(empty)"},
        {"name": "Módulo1.bas", "type": "Standard Module", "procedures": [
            {"name": "presiontub", "shortcut": "CTRL+w", "description": "Selects 'CAIDA PRESION DE TUBERIA' sheet"},
            {"name": "paginaprincipal", "shortcut": "CTRL+q", "description": "Selects 'PAGINA PRINCIPAL' sheet"},
            {"name": "ESPECTUBERIAS", "shortcut": "CTRL+e", "description": "Selects 'ESPECIFICACIÓN DE TUBERIA' sheet"}
        ]},
        {"name": "ThisWorkbook.cls", "type": "ThisWorkbook", "code": "(empty)"},
        {"name": "Hoja13.cls", "type": "Worksheet", "sheet": "REGISTROS", "code": "(empty)"},
        {"name": "Módulo2.bas", "type": "Standard Module", "procedures": [
            {"name": "TABLACC", "shortcut": " ", "description": "Selects 'TABLA DE ACCESORIOS' sheet"},
            {"name": "bomba", "shortcut": " ", "description": "Selects 'CALCULO DE BOMBA' sheet"},
            {"name": "imprimir", "shortcut": "CTRL+i", "description": "Complex print setup and print macro"},
            {"name": "eliminarultimoreg", "shortcut": " ", "description": "Deletes row 2 (last record)"}
        ]},
        {"name": "Módulo3.bas", "type": "Standard Module", "code": "(empty)"},
        {"name": "Módulo4.bas", "type": "Standard Module", "procedures": [
            {"name": "RAMAL", "shortcut": " ", "description": "Copies calculation data from CALCULO DE BOMBA and CAIDA PRESION DE TUBERIA to RAMALES sheet, inserts columns, sets formulas"}
        ]},
        {"name": "Hoja5.cls", "type": "Worksheet", "sheet": "TABLA DE ACCESORIOS SUCCION", "code": "(empty)"},
        {"name": "Módulo5.bas", "type": "Standard Module", "procedures": [
            {"name": "nuevoregistro", "shortcut": " ", "description": "Clears input cells across multiple sheets (CAIDA PRESION DE TUBERIA, CALCULO DE BOMBA, REPORTE GENERAL, RAMALES)"},
            {"name": "generareporte", "shortcut": " ", "description": "Generates report by copying data from CAIDA PRESION DE TUBERIA and CALCULO DE BOMBA to REPORTE GENERAL"}
        ]},
        {"name": "Hoja6.cls", "type": "Worksheet", "sheet": "VELOCIDADES RECOMENDADAS", "code": "(empty)"},
        {"name": "Hoja14.cls", "type": "Worksheet", "sheet": "REPORTE GENERAL", "code": "(empty)"},
        {"name": "Módulo6.bas", "type": "Standard Module", "procedures": [
            {"name": "Macro5", "shortcut": "Ctrl+Shift+M", "description": "Copies H6:I40 to N6 as values"},
            {"name": "Macro6", "shortcut": "Ctrl+Shift+V", "description": "Copies H6:I40 to R6 as values"},
            {"name": "Macro7", "shortcut": "Ctrl+Shift+B", "description": "Copies H6:I40 to X6 as values"},
            {"name": "Macro8", "shortcut": "Ctrl+Shift+N", "description": "Copies H6:I40 to AB6 as values"},
            {"name": "Macro9", "shortcut": "Ctrl+Shift+M", "description": "Copies H6:I40 to AF6 as values"}
        ]},
        {"name": "Hoja7.cls", "type": "Worksheet", "sheet": "ESPECIFICACIÓN DE TUBERIA", "code": "(empty)"},
        {"name": "Hoja8.cls", "type": "Worksheet", "sheet": "PAGINA PRINCIPAL (2?)", "code": "(empty)"}
    ],
    "warnings": [
        "AutoExec: BOMBA_Click runs when file opened and ActiveX objects trigger events",
        "Suspicious: Hex Strings detected (possible obfuscation)",
        "Suspicious: Base64 Strings detected (possible obfuscation)"
    ],
    "vba_project_size": 78336
}

# Save JSON
json_path = REPORTS_DIR / "vba_inventory.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(vba_data, f, indent=2, ensure_ascii=False)

# Generate markdown
md_path = REPORTS_DIR / "vba_inventory.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# VBA Inventory Report (Complete)\n\n")
    f.write(f"**File:** {vba_data['file']}\n")
    f.write(f"**Inspection time:** {vba_data['inspection_time']}\n")
    f.write(f"**VBA Project Size:** {vba_data['vba_project_size']:,} bytes\n")
    f.write(f"**Classification:** {vba_data['vba_classification']}\n\n")
    
    f.write("## VBA Modules Summary\n\n")
    f.write("| Module | Type | Sheet/Description | Procedures |\n")
    f.write("|--------|------|-------------------|------------|\n")
    for m in vba_data['vba_modules']:
        if 'procedures' in m:
            proc_names = [p['name'] for p in m['procedures']]
            f.write(f"| {m['name']} | {m['type']} | {m.get('sheet', '')} | {', '.join(proc_names)} |\n")
        else:
            f.write(f"| {m['name']} | {m['type']} | {m.get('sheet', '')} | {m.get('code', '(empty)')} |\n")
    
    f.write("\n## Detailed Procedures\n\n")
    for m in vba_data['vba_modules']:
        if 'procedures' in m:
            f.write(f"### {m['name']} ({m['type']})\n")
            for p in m['procedures']:
                f.write(f"- **{p['name']}** (Shortcut: {p['shortcut']}): {p['description']}\n")
            f.write("\n")
    
    f.write("## Sheet Module Code\n\n")
    for m in vba_data['vba_modules']:
        if m['type'] == 'Worksheet' and m.get('code') and m['code'] != '(empty)':
            f.write(f"### {m['name']} - Sheet: {m['sheet']}\n")
            f.write("```vba\n")
            f.write(m['code'])
            f.write("\n```\n\n")
    
    f.write("## Warnings from olevba\n\n")
    for w in vba_data['warnings']:
        f.write(f"- ⚠️ {w}\n")
    
    f.write("\n## Keyboard Shortcuts Summary\n\n")
    f.write("| Shortcut | Macro | Module | Action |\n")
    f.write("|----------|-------|--------|--------|\n")
    shortcuts = [
        ("CTRL+w", "presiontub", "Módulo1", "Go to CAIDA PRESION DE TUBERIA"),
        ("CTRL+q", "paginaprincipal", "Módulo1", "Go to PAGINA PRINCIPAL"),
        ("CTRL+e", "ESPECTUBERIAS", "Módulo1", "Go to ESPECIFICACIÓN DE TUBERIA"),
        ("CTRL+i", "imprimir", "Módulo2", "Print with custom setup"),
        ("CTRL+SHIFT+M", "Macro5", "Módulo6", "Copy H6:I40 to N6 (values)"),
        ("CTRL+SHIFT+V", "Macro6", "Módulo6", "Copy H6:I40 to R6 (values)"),
        ("CTRL+SHIFT+B", "Macro7", "Módulo6", "Copy H6:I40 to X6 (values)"),
        ("CTRL+SHIFT+N", "Macro8", "Módulo6", "Copy H6:I40 to AB6 (values)"),
        ("CTRL+SHIFT+M", "Macro9", "Módulo6", "Copy H6:I40 to AF6 (values) - CONFLICT"),
    ]
    for sc, macro, mod, action in shortcuts:
        f.write(f"| {sc} | {macro} | {mod} | {action} |\n")
    
    f.write("\n⚠️ **Conflict:** CTRL+SHIFT+M assigned to both Macro5 and Macro9\n")

print(f"Updated VBA inventory saved to {json_path} and {md_path}")