"""
Comparison service - Compare legacy (workbook) vs validated calculations.
"""
from dataclasses import dataclass
from typing import Dict, Any, List
from src.domain.units import Q_, ureg


@dataclass
class ComparisonResult:
    """Result of comparing legacy vs validated vs Excel."""
    variable: str
    sheet: str
    cell: str
    excel_value: float
    legacy_value: float
    validated_value: float
    unit: str
    legacy_diff: float
    validated_diff: float
    legacy_rel_diff: float
    validated_rel_diff: float
    tolerance: float
    status: str  # LEGACY_MATCH, LEGACY_MISMATCH, VALIDATED_MATCH, etc.
    explanation: str


class ResultClassifier:
    """Classify comparison results."""
    
    STATUSES = {
        'LEGACY_MATCH': 'Legacy reproduces Excel exactly',
        'LEGACY_MISMATCH': 'Legacy does not match Excel',
        'VALIDATED_MATCH': 'Validated matches Excel within tolerance',
        'VALIDATED_DIFFERENCE': 'Validated differs from Excel',
        'ROUNDING_ONLY': 'Difference within rounding tolerance',
        'UNIT_CONVERSION_DIFFERENCE': 'Difference due to unit conversion',
        'FORMULA_DIFFERENCE': 'Different formula used',
        'INPUT_DIFFERENCE': 'Different input values used',
        'MISSING_INPUT': 'Required input not available',
        'ENGINEERING_REVIEW_REQUIRED': 'Significant discrepancy requiring review'
    }
    
    @classmethod
    def classify(cls, legacy_diff: float, validated_diff: float, 
                 legacy_rel: float, validated_rel: float,
                 tolerance: float) -> str:
        """Classify the comparison result."""
        
        # Legacy exact match
        if abs(legacy_diff) <= tolerance:
            if abs(validated_diff) <= tolerance:
                return 'LEGACY_MATCH'
            else:
                return 'LEGACY_MATCH'  # Legacy matches, validated differs
        
        # Legacy mismatch
        if abs(validated_diff) <= tolerance:
            return 'VALIDATED_MATCH'
        
        # Both differ significantly
        if abs(validated_rel) < abs(legacy_rel):
            return 'VALIDATED_DIFFERENCE'
        else:
            return 'LEGACY_MISMATCH'


def compare_legacy_vs_excel() -> List[ComparisonResult]:
    """Compare legacy calculator outputs with Excel values."""
    
    # Excel cached values (from recalculation report)
    excel_values = {
        'discharge_diameter_in': 6.048364477182011,
        'suction_diameter_in': 10.041761045944389,
        're_discharge': 768552.5213911285,
        're_suction': 462915.39382010826,
        'f_discharge': 0.0272,  # G17 hardcoded
        'f_suction': 0.0001382542055295547,  # V16 = 64/Re
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
    
    # Legacy calculator values
    from src.application.legacy_calculator import calculate_legacy_from_inputs
    legacy = calculate_legacy_from_inputs()
    
    legacy_values = {
        'discharge_diameter_in': legacy.discharge_diameter_in,
        'suction_diameter_in': legacy.suction_diameter_in,
        're_discharge': legacy.re_discharge,
        're_suction': legacy.re_suction,
        'f_discharge': legacy.f_discharge,
        'f_suction': legacy.f_suction,
        'hf_per_ft_discharge': legacy.hf_per_ft_discharge,
        'hf_per_ft_suction': legacy.hf_per_ft_suction,
        'npsha_ft': legacy.npsha_ft,
        'tdh_ft': legacy.tdh_ft,
        'tdh_m': legacy.tdh_m,
        'hydraulic_hp': legacy.hydraulic_hp,
        'shaft_hp': legacy.shaft_hp,
        'shaft_kw': legacy.shaft_kw,
        'torque_lbft': legacy.torque_lbft,
        'specific_speed_legacy': legacy.specific_speed_legacy,
    }
    
    # Validated calculator values
    from src.application.validated_calculator import run_validated
    validated = run_validated()
    
    validated_values = {
        'discharge_diameter_in': validated.discharge_diameter_in,
        'suction_diameter_in': validated.suction_diameter_in,
        're_discharge': validated.re_discharge,
        're_suction': validated.re_suction,
        'f_discharge': validated.f_discharge,
        'f_suction': validated.f_suction,
        'hf_per_ft_discharge': validated.hf_per_ft_discharge,
        'hf_per_ft_suction': validated.hf_per_ft_suction,
        'npsha_ft': validated.npsha_ft,
        'tdh_ft': validated.tdh_ft,
        'tdh_m': validated.tdh_m,
        'hydraulic_hp': validated.hydraulic_hp,
        'shaft_hp': validated.shaft_hp,
        'shaft_kw': validated.shaft_kw,
        'torque_lbft': validated.torque_lbft,
        'specific_speed_legacy': validated.specific_speed_legacy,
        'specific_speed_us': validated.specific_speed_us,
    }
    
    # Tolerances
    tolerances = {
        'discharge_diameter_in': 1e-6,
        'suction_diameter_in': 1e-6,
        're_discharge': 0.001,  # 0.1%
        're_suction': 0.001,
        'f_discharge': 0.01,  # 1%
        'f_suction': 0.01,
        'hf_per_ft_discharge': 0.01,
        'hf_per_ft_suction': 0.01,
        'npsha_ft': 0.01,
        'tdh_ft': 0.01,
        'tdh_m': 0.01,
        'hydraulic_hp': 0.01,
        'shaft_hp': 0.01,
        'shaft_kw': 0.01,
        'torque_lbft': 0.01,
        'specific_speed_legacy': 0.01,
    }
    
    results = []
    for var in excel_values:
        if var in legacy_values:
            excel = excel_values[var]
            legacy = legacy_values[var]
            validated = validated_values.get(var, None)
            
            legacy_diff = legacy - excel
            legacy_rel = abs(legacy_diff / excel) if excel != 0 else float('inf')
            
            validated_diff = None
            validated_rel = None
            if validated is not None:
                validated_diff = validated - excel
                validated_rel = abs(validated_diff / excel) if excel != 0 else float('inf')
            
            tol = tolerances.get(var, 0.01)
            
            if validated is not None:
                status = ResultClassifier.classify(
                    legacy_diff, validated_diff, legacy_rel, 
                    abs(validated_diff / excel) if excel != 0 else float('inf'), tol
                )
            else:
                status = 'LEGACY_MATCH' if abs(legacy_diff) <= tol else 'LEGACY_MISMATCH'
            
            results.append(ComparisonResult(
                variable=var,
                sheet='Various',
                cell='Various',
                excel_value=excel,
                legacy_value=legacy,
                validated_value=validated if validated is not None else float('nan'),
                unit='Various',
                legacy_diff=legacy_diff,
                validated_diff=validated_diff if validated_diff is not None else float('nan'),
                legacy_rel_diff=legacy_rel,
                validated_rel_diff=validated_rel if validated_rel is not None else float('nan'),
                tolerance=tol,
                status=status,
                explanation=''
            ))
    
    return results


if __name__ == '__main__':
    results = compare_legacy_vs_excel()
    
    print("Comparison: Legacy vs Excel")
    print("=" * 80)
    print(f"{'Variable':<30} {'Excel':>12} {'Legacy':>12} {'Diff':>10} {'Rel%':>8} {'Status':<20}")
    print("-" * 80)
    
    for r in results:
        if r.legacy_value is not None:
            print(f"{r.variable:<30} {r.excel_value:>12.6f} {r.legacy_value:>12.6f} {r.legacy_diff:>10.6f} {r.legacy_rel_diff*100:>7.3f}% {r.status:<20}")
    
    print("\n\nValidated vs Excel:")
    for r in results:
        if r.validated_value is not None and not (isinstance(r.validated_value, float) and r.validated_value != r.validated_value):
            print(f"{r.variable:<30} {r.excel_value:>12.6f} {r.validated_value:>12.6f} {r.validated_diff:>10.6f} {r.validated_rel_diff*100:>7.3f}% {r.status:<20}")