import win32com.client
import os
import time
from pathlib import Path

WORKING_FILE = Path(r"C:\PUMPCALC\working\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm")
RECALC_FILE = Path(r"C:\PUMPCALC\working\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1)_BASELINE_RECALCULATED.xlsm")
REPORTS_DIR = Path(r"C:\PUMPCALC\reports")

def recalculate_and_capture():
    """Open workbook with Excel COM, recalculate, capture before/after values"""
    
    # Check if Excel is running
    try:
        excel = win32com.client.Dispatch('Excel.Application')
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.EnableEvents = False
        excel.AskToUpdateLinks = False
        excel.AutomationSecurity = 3  # msoAutomationSecurityForceDisable = disable macros
        
        print("Excel started, opening workbook...")
        
        # Open workbook
        wb = excel.Workbooks.Open(
            str(WORKING_FILE),
            UpdateLinks=0,  # Don't update external links
            ReadOnly=False,
            IgnoreReadOnlyRecommended=True
        )
        
        print(f"Workbook opened: {wb.Name}")
        print(f"Calculation mode before: {excel.Calculation}")
        
        # Set to manual calculation first
        excel.Calculation = -4135  # xlCalculationManual
        
        # Capture values BEFORE recalculation (key cells)
        key_cells = [
            # CAIDA PRESION DE TUBERIA
            ("CAIDA PRESION DE TUBERIA", "G5"), ("CAIDA PRESION DE TUBERIA", "V5"),
            ("CAIDA PRESION DE TUBERIA", "G8"), ("CAIDA PRESION DE TUBERIA", "V8"),
            ("CAIDA PRESION DE TUBERIA", "G11"), ("CAIDA PRESION DE TUBERIA", "V11"),
            ("CAIDA PRESION DE TUBERIA", "G19"), ("CAIDA PRESION DE TUBERIA", "V19"),
            # CALCULO DE BOMBA
            ("CALCULO DE BOMBA", "C9"), ("CALCULO DE BOMBA", "C14"),
            ("CALCULO DE BOMBA", "E14"), ("CALCULO DE BOMBA", "C28"),
            ("CALCULO DE BOMBA", "E20"), ("CALCULO DE BOMBA", "E21"),
            ("CALCULO DE BOMBA", "E22"), ("CALCULO DE BOMBA", "E23"),
            ("CALCULO DE BOMBA", "E24"), ("CALCULO DE BOMBA", "E27"),
            # RESUMEN PARA PDF
            ("RESUMEN PARA PDF", "B13"), ("RESUMEN PARA PDF", "B28"),
            ("RESUMEN PARA PDF", "D28"), ("RESUMEN PARA PDF", "G25"),
            ("RESUMEN PARA PDF", "G29"),
        ]
        
        before_values = {}
        for sheet_name, cell_ref in key_cells:
            try:
                ws = wb.Worksheets(sheet_name)
                cell = ws.Range(cell_ref)
                before_values[f"{sheet_name}!{cell_ref}"] = cell.Value
            except:
                before_values[f"{sheet_name}!{cell_ref}"] = "ERROR_READING"
        
        print("Captured before values")
        
        # Force full recalculation
        print("Starting CalculateFullRebuild...")
        start_time = time.time()
        wb.ForceFullCalculation = True
        excel.CalculateFullRebuild()
        elapsed = time.time() - start_time
        print(f"Recalculation completed in {elapsed:.2f} seconds")
        
        # Capture values AFTER recalculation
        after_values = {}
        for sheet_name, cell_ref in key_cells:
            try:
                ws = wb.Worksheets(sheet_name)
                cell = ws.Range(cell_ref)
                after_values[f"{sheet_name}!{cell_ref}"] = cell.Value
            except:
                after_values[f"{sheet_name}!{cell_ref}"] = "ERROR_READING"
        
        print("Captured after values")
        
        # Save as new file
        wb.SaveAs(str(RECALC_FILE))
        print(f"Saved recalculated workbook to: {RECALC_FILE}")
        
        # Close workbook
        wb.Close(SaveChanges=False)
        excel.Quit()
        
        # Generate comparison report
        changes = []
        for key in before_values:
            before = before_values[key]
            after = after_values.get(key, "MISSING")
            if before != after:
                changes.append({
                    "cell": key,
                    "before": before,
                    "after": after,
                    "changed": True
                })
            else:
                changes.append({
                    "cell": key,
                    "before": before,
                    "after": after,
                    "changed": False
                })
        
        # Save CSV
        import csv
        csv_path = REPORTS_DIR / "recalculation_changes.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["cell", "before", "after", "changed"])
            writer.writeheader()
            writer.writerows(changes)
        
        # Save Markdown
        md_path = REPORTS_DIR / "recalculation_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Recalculation Report\n\n")
            f.write(f"**Source file:** {WORKING_FILE}\n")
            f.write(f"**Recalculated file:** {RECALC_FILE}\n")
            f.write(f"**Recalculation time:** {elapsed:.2f} seconds\n")
            f.write(f"**Cells monitored:** {len(key_cells)}\n")
            f.write(f"**Cells changed:** {sum(1 for c in changes if c['changed'])}\n\n")
            
            f.write("## Value Changes\n\n")
            f.write("| Cell | Before | After | Changed |\n")
            f.write("|------|--------|-------|---------|\n")
            for c in changes:
                before_str = str(c['before'])[:50]
                after_str = str(c['after'])[:50]
                changed = "✅" if c['changed'] else "❌"
                f.write(f"| {c['cell']} | {before_str} | {after_str} | {changed} |\n")
        
        print(f"Report saved to {md_path}")
        
    except Exception as e:
        print(f"Error during recalculation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    recalculate_and_capture()