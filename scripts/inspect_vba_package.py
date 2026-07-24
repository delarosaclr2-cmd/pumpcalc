import zipfile
import json
from pathlib import Path
from datetime import datetime

FILE_PATH = Path(r"C:\PUMPCALC\original\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm")
REPORTS_DIR = Path(r"C:\PUMPCALC\reports")

def inspect_vba_and_package(filepath):
    """Inspect VBA modules and XLSM package contents"""
    inventory = {
        "file": str(filepath),
        "inspection_time": datetime.now().isoformat(),
        "vba_modules": [],
        "vba_code": {},
        "package_contents": [],
        "package_details": {}
    }
    
    with zipfile.ZipFile(filepath, 'r') as z:
        # List all files in package
        for info in z.infolist():
            inventory["package_contents"].append({
                "name": info.filename,
                "size": info.file_size,
                "compressed_size": info.compress_size,
                "date_time": info.date_time,
                "crc": info.CRC
            })
        
        # Look for VBA project
        vba_files = [f for f in z.namelist() if 'vba' in f.lower() or f.endswith('.bin')]
        
        if 'xl/vbaProject.bin' in z.namelist():
            # Read VBA project binary
            vba_data = z.read('xl/vbaProject.bin')
            inventory["package_details"]["vbaProject.bin_size"] = len(vba_data)
            
            # Try to extract module names from VBA project
            # VBA project is a compound document - we can try to find module names
            try:
                # Search for module names in the binary
                vba_text = vba_data.decode('latin-1', errors='ignore')
                import re
                # Find module names (Attribute VB_Name = "ModuleName")
                module_names = re.findall(r'Attribute VB_Name\s*=\s*"([^"]+)"', vba_text)
                inventory["vba_modules"] = module_names
                
                # Find all code modules
                # Look for module streams
                for name in ['ThisWorkbook', 'Sheet1', 'Sheet2', 'Sheet3', 'Sheet4', 'Sheet5', 
                            'Sheet6', 'Sheet7', 'Sheet8', 'Sheet9', 'Sheet10', 'Sheet11', 'Sheet12',
                            'Module1', 'Module2', 'Module3', 'Module4', 'Module5']:
                    pass
            except:
                pass
        
        # Read workbook.xml for sheet info
        if 'xl/workbook.xml' in z.namelist():
            wb_xml = z.read('xl/workbook.xml').decode('utf-8', errors='ignore')
            inventory["package_details"]["workbook_xml"] = wb_xml[:5000]
        
        # Read content types
        if '[Content_Types].xml' in z.namelist():
            ct_xml = z.read('[Content_Types].xml').decode('utf-8', errors='ignore')
            inventory["package_details"]["content_types_xml"] = ct_xml[:5000]
        
        # Read app.xml for properties
        if 'docProps/app.xml' in z.namelist():
            app_xml = z.read('docProps/app.xml').decode('utf-8', errors='ignore')
            inventory["package_details"]["app_xml"] = app_xml
        
        # Read core.xml
        if 'docProps/core.xml' in z.namelist():
            core_xml = z.read('docProps/core.xml').decode('utf-8', errors='ignore')
            inventory["package_details"]["core_xml"] = core_xml
        
        # Check for custom XML parts
        custom_xml = [f for f in z.namelist() if f.startswith('customXml/')]
        inventory["package_details"]["custom_xml_parts"] = custom_xml
        
        # Check for drawings, charts, images
        drawings = [f for f in z.namelist() if f.startswith('xl/drawings/')]
        charts = [f for f in z.namelist() if f.startswith('xl/charts/')]
        images = [f for f in z.namelist() if f.startswith('xl/media/')]
        inventory["package_details"]["drawings"] = drawings
        inventory["package_details"]["charts"] = charts
        inventory["package_details"]["images"] = images
        
        # Check for external links
        ext_links = [f for f in z.namelist() if f.startswith('xl/externalLinks/')]
        inventory["package_details"]["external_links"] = ext_links
        
        # Check for macros in sheet XMLs (macro sheets)
        sheet_files = [f for f in z.namelist() if f.startswith('xl/worksheets/sheet') and f.endswith('.xml')]
        macro_sheets = []
        for sf in sheet_files:
            try:
                content = z.read(sf).decode('utf-8', errors='ignore')
                if 'macro' in content.lower() or 'vba' in content.lower():
                    macro_sheets.append(sf)
            except:
                pass
        inventory["package_details"]["potential_macro_sheets"] = macro_sheets
    
    return inventory

def main():
    print(f"Inspecting VBA and package: {FILE_PATH}")
    inventory = inspect_vba_and_package(FILE_PATH)
    
    # Save JSON
    json_path = REPORTS_DIR / "vba_package_inventory.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False, default=str)
    print(f"JSON saved to: {json_path}")
    
    # Generate markdown
    md_path = REPORTS_DIR / "vba_inventory.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(generate_vba_report(inventory))
    print(f"Markdown saved to: {md_path}")
    
    # Generate XLSM package inventory
    xlsm_md_path = REPORTS_DIR / "xlsm_package_inventory.md"
    with open(xlsm_md_path, 'w', encoding='utf-8') as f:
        f.write(generate_xlsm_package_report(inventory))
    print(f"XLSM package report saved to: {xlsm_md_path}")

def generate_vba_report(inv):
    lines = []
    lines.append("# VBA Inventory Report")
    lines.append(f"\n**File:** {inv['file']}")
    lines.append(f"**Inspection time:** {inv['inspection_time']}")
    
    lines.append(f"\n## VBA Modules Found")
    if inv['vba_modules']:
        for m in inv['vba_modules']:
            lines.append(f"- `{m}`")
    else:
        lines.append("*No VBA modules detected via simple binary scan*")
    
    lines.append(f"\n## VBA Project Binary")
    if 'vbaProject.bin_size' in inv['package_details']:
        lines.append(f"- **Size:** {inv['package_details']['vbaProject.bin_size']:,} bytes")
    else:
        lines.append("- **vbaProject.bin not found**")
    
    lines.append(f"\n## Potential Macro Sheets")
    if inv['package_details'].get('potential_macro_sheets'):
        for s in inv['package_details']['potential_macro_sheets']:
            lines.append(f"- `{s}`")
    else:
        lines.append("*None detected*")
    
    return "\n".join(lines)

def generate_xlsm_package_report(inv):
    lines = []
    lines.append("# XLSM Package Inventory")
    lines.append(f"\n**File:** {inv['file']}")
    lines.append(f"**Inspection time:** {inv['inspection_time']}")
    
    lines.append(f"\n## Package Contents ({len(inv['package_contents'])} files)")
    lines.append("| File | Size | Compressed | Ratio |")
    lines.append("|------|------|------------|-------|")
    for item in sorted(inv['package_contents'], key=lambda x: x['name']):
        ratio = item['compressed_size'] / item['size'] if item['size'] > 0 else 0
        lines.append(f"| `{item['name']}` | {item['size']:,} | {item['compressed_size']:,} | {ratio:.2f} |")
    
    lines.append(f"\n## Key Package Details")
    
    pd = inv['package_details']
    
    if pd.get('vbaProject.bin_size'):
        lines.append(f"\n### VBA Project")
        lines.append(f"- **vbaProject.bin:** {pd['vbaProject.bin_size']:,} bytes")
    
    if pd.get('external_links'):
        lines.append(f"\n### External Links ({len(pd['external_links'])})")
        for el in pd['external_links']:
            lines.append(f"- `{el}`")
    else:
        lines.append(f"\n### External Links: None")
    
    if pd.get('drawings'):
        lines.append(f"\n### Drawings ({len(pd['drawings'])})")
        for d in pd['drawings']:
            lines.append(f"- `{d}`")
    
    if pd.get('charts'):
        lines.append(f"\n### Charts ({len(pd['charts'])})")
        for c in pd['charts']:
            lines.append(f"- `{c}`")
    
    if pd.get('images'):
        lines.append(f"\n### Images/Media ({len(pd['images'])})")
        for i in pd['images']:
            lines.append(f"- `{i}`")
    
    if pd.get('custom_xml_parts'):
        lines.append(f"\n### Custom XML Parts ({len(pd['custom_xml_parts'])})")
        for c in pd['custom_xml_parts']:
            lines.append(f"- `{c}`")
    
    if pd.get('potential_macro_sheets'):
        lines.append(f"\n### Potential Macro Sheets ({len(pd['potential_macro_sheets'])})")
        for s in pd['potential_macro_sheets']:
            lines.append(f"- `{s}`")
    
    # Core properties
    if pd.get('core_xml'):
        lines.append(f"\n### Core Properties (docProps/core.xml)")
        lines.append("```xml")
        lines.append(pd['core_xml'][:3000])
        lines.append("```")
    
    if pd.get('app_xml'):
        lines.append(f"\n### App Properties (docProps/app.xml)")
        lines.append("```xml")
        lines.append(pd['app_xml'][:3000])
        lines.append("```")
    
    return "\n".join(lines)

if __name__ == "__main__":
    main()