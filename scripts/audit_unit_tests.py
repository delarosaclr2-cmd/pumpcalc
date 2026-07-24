"""
Audit of unit tests - documents all unit tests for hydraulic calculations.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import unittest
import inspect
import json

# Discover unit tests
loader = unittest.TestLoader()
suite = loader.discover(r'C:\PUMPCALC\tests\unit', pattern='test_*.py')

unit_tests = []
for test_group in suite:
    for test_case in test_group:
        if hasattr(test_case, '__iter__'):
            for test in test_case:
                if isinstance(test, unittest.TestCase):
                    method_name = test._testMethodName
                    class_name = test.__class__.__name__
                    
                    # Get the test method
                    method = getattr(test, method_name)
                    doc = method.__doc__ or ""
                    source = inspect.getsource(method) if hasattr(inspect, 'getsource') else ""
                    
                    # Determine what's being tested
                    test_name = f"{class_name}.{method_name}"
                    
                    unit_tests.append({
                        "test_file": f"tests/unit/{class_name}.py" if "Test" in class_name else "tests/unit/unknown.py",
                        "test_class": class_name,
                        "test_method": method_name,
                        "docstring": doc.strip(),
                        "source_lines": len(source.split('\n')),
                        "status": "DISCOVERED"
                    })

print(f"Found {len(unit_tests)} unit tests")

# Save
import csv
csv_path = r"C:\PUMPCALC\reports\unit_test_audit.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=unit_tests[0].keys())
    writer.writeheader()
    writer.writerows(unit_tests)

md_path = r"C:\PUMPCALC\reports\unit_test_audit.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# Unit Test Audit\n\n")
    f.write(f"**Total unit tests discovered:** {len(unit_tests)}\n\n")
    f.write("## Tests by Class\n\n")
    classes = {}
    for t in unit_tests:
        c = t['test_class']
        if c not in classes:
            classes[c] = 0
        classes[c] += 1
    for c, count in sorted(classes.items()):
        f.write(f"- {c}: {count} tests\n")
    
    f.write("\n## Test Details\n\n")
    for t in unit_tests:
        f.write(f"### {t['test_class']}.{t['test_method']}\n\n")
        f.write(f"- **Docstring:** {t['docstring']}\n")
        f.write(f"- **Source lines:** {t['source_lines']}\n")
        f.write(f"- **Status:** {t['status']}\n\n")

print(f"Unit test audit saved to {csv_path} and {md_path}")