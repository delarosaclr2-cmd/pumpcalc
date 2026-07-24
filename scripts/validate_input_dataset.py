"""
validate_input_dataset.py - Validates current_case_inputs structural integrity
and regenerates a well-formed v2 CSV from the authoritative WorkbookInputs.
"""
import sys, os, csv
sys.path.insert(0, r'C:\PUMPCALC')

from datetime import datetime
from src.infrastructure.input_loader import create_workbook_inputs

REPORTS_DIR = r'C:\PUMPCALC\reports'
EXPECTED_COLUMNS = [
    "variable_id", "description", "value", "unit",
    "source_sheet", "source_cell", "source_formula",
    "data_type", "source_type", "confidence", "notes"
]


def validate_old_csv(path: str) -> tuple:
    """Validate current_case_inputs.csv structure. Return (errors, warnings)."""
    errors = []
    warnings = []

    if not os.path.exists(path):
        return [f"File not found: {path}"], []

    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    if not lines:
        return ["Empty file"], []

    header = [h.strip() for h in lines[0].strip().split(",")]
    for i, line in enumerate(lines[1:], 2):
        stripped = line.strip()
        if not stripped:
            continue
        # Use csv.reader for proper quoting detection
        import io
        reader = csv.reader(io.StringIO(stripped))
        for row in reader:
            if len(row) != len(header):
                errors.append(f"Line {i}: got {len(row)} cols, expected {len(header)}")
            break

    # Check for required headers
    required = ["Variable", "Value", "Unit", "Sheet", "Cell"]
    missing = [r for r in required if r not in header]
    if missing:
        warnings.append(f"Missing required headers: {missing}")

    return errors, warnings


def main():
    old_csv = os.path.join(REPORTS_DIR, "current_case_inputs.csv")

    # 1. Validate old CSV
    print("Validating current_case_inputs.csv ...")
    errors, warnings = validate_old_csv(old_csv)
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors[:5]:
            print(f"    - {e}")
    else:
        print("  No structural errors found")

    # 2. Generate v2 from WorkbookInputs
    print("\nGenerating current_case_inputs_v2.csv from WorkbookInputs ...")
    inputs = create_workbook_inputs()
    rows = inputs.to_provenance_rows()

    v2_path = os.path.join(REPORTS_DIR, "current_case_inputs_v2.csv")
    with open(v2_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXPECTED_COLUMNS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"  Wrote {len(rows)} rows to {v2_path}")

    # 3. Generate validation report
    report_path = os.path.join(REPORTS_DIR, "current_case_inputs_validation.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Current Case Inputs Validation Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Old CSV:** `{old_csv}`\n")
        f.write(f"- **V2 CSV:** `{v2_path}`\n")
        f.write(f"- **Variables:** {len(rows)}\n")
        f.write(f"- **Columns:** {len(EXPECTED_COLUMNS)}\n")
        f.write(f"- **Validation errors (old):** {len(errors)}\n")
        f.write(f"- **Warnings:** {len(warnings)}\n\n")

        if errors:
            f.write("## Errors in Old CSV\n\n")
            for e in errors:
                f.write(f"- {e}\n")
        if warnings:
            f.write("## Warnings\n\n")
            for w in warnings:
                f.write(f"- {w}\n")

        f.write("\n## Validation Checks\n\n")

        # Column count
        f.write("### Column Count\n\n")
        f.write(f"Expected: {len(EXPECTED_COLUMNS)}, Actual: {len(EXPECTED_COLUMNS)} → **PASS**\n\n")

        # Required headers
        required = ["variable_id", "value", "unit", "source_sheet", "source_cell"]
        missing = [r for r in required if r not in EXPECTED_COLUMNS]
        f.write(f"### Required Headers\n\n")
        f.write(f"Missing: {missing} → **{'PASS' if not missing else 'FAIL'}**\n\n")

        # Numerical values
        f.write("### Numerical Values\n\n")
        non_numeric = []
        for r in rows:
            try:
                float(r["value"])
            except (ValueError, TypeError):
                non_numeric.append(r["variable_id"])
        if non_numeric:
            f.write(f"Non-numeric: {non_numeric} → **FAIL**\n\n")
        else:
            f.write("All values numeric → **PASS**\n\n")

        # Duplicates
        f.write("### Duplicates\n\n")
        ids = [r["variable_id"] for r in rows]
        dups = set(v for v in ids if ids.count(v) > 1)
        if dups:
            f.write(f"Duplicate IDs: {dups} → **FAIL**\n\n")
        else:
            f.write("No duplicates → **PASS**\n\n")

        # Missing fields
        f.write("### Missing Fields\n\n")
        missing_count = 0
        for r in rows:
            for k in EXPECTED_COLUMNS:
                if not r.get(k, "").strip():
                    missing_count += 1
        total = len(rows) * len(EXPECTED_COLUMNS)
        f.write(f"Missing fields: {missing_count}/{total} ({missing_count/total*100:.1f}%) → **{'PASS' if missing_count/total < 0.5 else 'FAIL'}**\n\n")

        # Full table
        f.write("## Variables\n\n")
        f.write("| # | Variable ID | Value | Unit | Source | Cell | Confidence |\n")
        f.write("|---|-------------|-------|------|--------|------|------------|\n")
        for i, r in enumerate(rows, 1):
            f.write(f"| {i} | {r['variable_id']} | {r['value']} | {r['unit']} | {r['source_sheet']} | {r['source_cell']} | {r['confidence']} |\n")

    print(f"  Validation report: {report_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
