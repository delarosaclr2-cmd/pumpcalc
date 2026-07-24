import hashlib
import json
from pathlib import Path
from datetime import datetime

FILES = {
    "source": Path(r"C:\PUMPCALC\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm"),
    "original": Path(r"C:\PUMPCALC\original\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm"),
    "working": Path(r"C:\PUMPCALC\working\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm"),
}

REPORTS_DIR = Path(r"C:\PUMPCALC\reports")

def compute_hashes(filepath):
    hashes = {}
    for algo in ['md5', 'sha256', 'sha1']:
        h = hashlib.new(algo)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        hashes[algo] = h.hexdigest()
    return hashes

def get_file_info(filepath):
    stat = filepath.stat()
    return {
        "path": str(filepath),
        "name": filepath.name,
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "hashes": compute_hashes(filepath)
    }

def main():
    results = {}
    for key, path in FILES.items():
        if path.exists():
            results[key] = get_file_info(path)
            print(f"{key}: {path.name} - {results[key]['size_bytes']:,} bytes - SHA256: {results[key]['hashes']['sha256']}")
        else:
            results[key] = {"error": "FILE_NOT_FOUND", "path": str(path)}
            print(f"{key}: NOT FOUND at {path}")
    
    # Check if all three exist and have same SHA256
    all_exist = all("error" not in results[k] for k in FILES)
    identical = False
    if all_exist:
        hashes = [results[k]["hashes"]["sha256"] for k in FILES]
        identical = len(set(hashes)) == 1
    
    conclusion = "IDENTICAL" if identical else ("NOT_IDENTICAL" if all_exist else "MISSING_FILE")
    
    report = {
        "inspection_time": datetime.now().isoformat(),
        "files": results,
        "all_files_exist": all_exist,
        "hashes_identical": identical,
        "conclusion": conclusion
    }
    
    # Save JSON
    json_path = REPORTS_DIR / "file_integrity_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nJSON saved to: {json_path}")
    
    # Generate Markdown
    md_path = REPORTS_DIR / "file_integrity_report.md"
    lines = []
    lines.append("# File Integrity Report")
    lines.append(f"\n**Inspection time:** {report['inspection_time']}")
    lines.append(f"\n**Conclusion:** `{conclusion}`")
    lines.append(f"\n**All files exist:** {all_exist}")
    lines.append(f"**Hashes identical:** {identical}")
    
    lines.append("\n## File Details")
    for key, info in results.items():
        lines.append(f"\n### {key.upper()}")
        if "error" in info:
            lines.append(f"- **Error:** {info['error']}")
            lines.append(f"- **Path:** {info['path']}")
        else:
            lines.append(f"- **Path:** {info['path']}")
            lines.append(f"- **Name:** {info['name']}")
            lines.append(f"- **Size:** {info['size_bytes']:,} bytes")
            lines.append(f"- **Created:** {info['created']}")
            lines.append(f"- **Modified:** {info['modified']}")
            lines.append(f"- **MD5:** {info['hashes']['md5']}")
            lines.append(f"- **SHA1:** {info['hashes']['sha1']}")
            lines.append(f"- **SHA256:** {info['hashes']['sha256']}")
    
    if all_exist:
        lines.append("\n## Hash Comparison")
        lines.append("| File | MD5 | SHA1 | SHA256 |")
        lines.append("|------|-----|------|--------|")
        for key, info in results.items():
            lines.append(f"| {key} | {info['hashes']['md5']} | {info['hashes']['sha1']} | {info['hashes']['sha256']} |")
        
        if identical:
            lines.append("\n✅ **All three files are bit-for-bit identical.**")
        else:
            lines.append("\n❌ **Files differ!**")
            for key in FILES:
                h = results[key]["hashes"]["sha256"]
                if h != results["source"]["hashes"]["sha256"]:
                    lines.append(f"- **{key}** differs from source")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Markdown saved to: {md_path}")
    
    if conclusion != "IDENTICAL":
        print(f"\n⚠️  CONCLUSION: {conclusion} - STOP, do not continue")
        exit(1)
    else:
        print(f"\n✅ CONCLUSION: {conclusion} - Safe to continue")

if __name__ == "__main__":
    main()