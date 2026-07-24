"""
Friction factor module - Darcy friction factor calculations.
"""
import math
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class FrictionResult:
    """Result of friction factor calculation."""
    reynolds: float
    relative_roughness: float
    friction_factor: float
    flow_regime: str  # "laminar", "transitional", "turbulent"
    method: str  # "laminar", "colebrook", "swamee-jain", "haaland"
    iterations: int = 0
    converged: bool = True


def colebrook_white(reynolds: float, rel_roughness: float, 
                    initial_guess: Optional[float] = None,
                    tolerance: float = 1e-8, max_iter: int = 100) -> FrictionResult:
    """
    Solve Colebrook-White equation for Darcy friction factor.
    
    1/sqrt(f) = -2.0 * log10(rel_roughness/3.7 + 2.51/(Re*sqrt(f)))
    
    Args:
        reynolds: Reynolds number
        rel_roughness: epsilon/D (relative roughness)
        initial_guess: initial guess for f (default: Haaland approximation)
        tolerance: convergence tolerance
        max_iter: maximum iterations
    
    Returns:
        FrictionResult with friction factor and metadata
    """
    if reynolds < 2300:
        return FrictionResult(
            reynolds=reynolds,
            relative_roughness=rel_roughness,
            friction_factor=64.0 / reynolds,
            flow_regime="laminar",
            method="laminar"
        )
    
    # Initial guess using Swamee-Jain
    if initial_guess is None:
        if rel_roughness > 0:
            initial_guess = 0.25 / (math.log10(rel_roughness/3.7 + 5.74/reynolds**0.9))**2
        else:
            initial_guess = 0.005
    
    f = max(initial_guess, 1e-6)
    converged = False
    
    for i in range(max_iter):
        sqrt_f = math.sqrt(f)
        lhs = 1.0 / sqrt_f
        rhs = -2.0 * math.log10(rel_roughness/3.7 + 2.51/(reynolds * sqrt_f))
        f_new = 1.0 / (rhs * rhs)
        
        if abs(f_new - f) < tolerance:
            f = f_new
            converged = True
            break
        f = f_new
    
    flow_regime = "turbulent"
    if reynolds < 4000:
        flow_regime = "transitional"
    
    return FrictionResult(
        reynolds=reynolds,
        relative_roughness=rel_roughness,
        friction_factor=f,
        flow_regime=flow_regime,
        method="colebrook-white",
        iterations=i+1,
        converged=converged
    )


def swamee_jain(reynolds: float, rel_roughness: float) -> FrictionResult:
    """
    Swamee-Jain explicit approximation to Colebrook-White.
    
    Valid for: 4000 < Re < 1e8, 1e-6 < eps/D < 1e-2
    """
    if reynolds < 2300:
        return FrictionResult(
            reynolds=reynolds,
            relative_roughness=rel_roughness,
            friction_factor=64.0 / reynolds,
            flow_regime="laminar",
            method="laminar"
        )
    
    if reynolds < 4000:
        flow_regime = "transitional"
    else:
        flow_regime = "turbulent"
    
    if rel_roughness <= 0:
        f = 0.25 / (math.log10(5.74/reynolds**0.9))**2
    else:
        f = 0.25 / (math.log10(rel_roughness/3.7 + 5.74/reynolds**0.9))**2
    
    return FrictionResult(
        reynolds=reynolds,
        relative_roughness=rel_roughness,
        friction_factor=f,
        flow_regime=flow_regime,
        method="swamee-jain"
    )


def haaland(reynolds: float, rel_roughness: float) -> FrictionResult:
    """
    Haaland explicit approximation to Colebrook-White.
    
    Valid for: 4000 < Re < 1e8, 1e-6 < eps/D < 1e-2
    """
    if reynolds < 2300:
        return FrictionResult(
            reynolds=reynolds,
            relative_roughness=rel_roughness,
            friction_factor=64.0 / reynolds,
            flow_regime="laminar",
            method="laminar"
        )
    
    if reynolds < 4000:
        flow_regime = "transitional"
    else:
        flow_regime = "turbulent"
    
    if rel_roughness <= 0:
        # Smooth pipe: use Prandtl's smooth pipe formula approximation
        f = 0.25 / (math.log10(5.74 / reynolds**0.9))**2
    else:
        f = 1.0 / (-1.8 * math.log10((rel_roughness/3.7)**1.11 + 6.9/reynolds))**2
    
    return FrictionResult(
        reynolds=reynolds,
        relative_roughness=rel_roughness,
        friction_factor=f,
        flow_regime=flow_regime,
        method="haaland"
    )


def get_friction_factor(reynolds: float, rel_roughness: float,
                        method: str = "colebrook") -> FrictionResult:
    """
    Get friction factor using specified method.
    
    Args:
        reynolds: Reynolds number
        rel_roughness: epsilon/D (relative roughness)
        method: "laminar", "colebrook", "swamee-jain", "haaland"
    
    Returns:
        FrictionResult
    """
    if method == "laminar":
        return FrictionResult(
            reynolds=reynolds,
            relative_roughness=rel_roughness,
            friction_factor=64.0 / reynolds if reynolds > 0 else 0.0,
            flow_regime="laminar",
            method="laminar"
        )
    elif method == "colebrook":
        return colebrook_white(reynolds, rel_roughness)
    elif method == "swamee-jain":
        return swamee_jain(reynolds, rel_roughness)
    elif method == "haaland":
        return haaland(reynolds, rel_roughness)
    else:
        raise ValueError(f"Unknown method: {method}")


def get_all_methods(reynolds: float, rel_roughness: float) -> dict:
    """Get friction factor from all methods for comparison."""
    results = {}
    for method in ["laminar", "colebrook", "swamee-jain", "haaland"]:
        try:
            results[method] = get_friction_factor(reynolds, rel_roughness, method)
        except Exception as e:
            results[method] = f"Error: {e}"
    return results


if __name__ == '__main__':
    # Test with current case values
    reynolds_suction = 462915
    reynolds_discharge = 768553
    roughness = 0.00012  # ft
    D_suction = 10.02  # in
    D_discharge = 6.065  # in
    
    rel_rough_suction = roughness / (D_suction / 12)
    rel_rough_discharge = roughness / (D_discharge / 12)
    
    print(f"Suction: Re={reynolds_suction}, D={D_suction} in, eps/D={rel_rough_suction:.6f}")
    print(f"Discharge: Re={reynolds_discharge}, D={D_discharge} in, eps/D={rel_rough_discharge:.6f}")
    print()
    
    for method in ["colebrook", "swamee-jain", "haaland"]:
        r1 = get_friction_factor(reynolds_suction, rel_rough_suction, method)
        r2 = get_friction_factor(reynolds_discharge, rel_rough_discharge, method)
        print(f"{method}: f_suction={r1.friction_factor:.6f}, f_discharge={r2.friction_factor:.6f}")
    
    print()
    print("Legacy workbook values:")
    print(f"  Suction (V16=64/Re): f=0.000138 (WRONG - laminar formula for turbulent flow)")
    print(f"  Discharge (G17 hardcoded): f=0.0272 (may be 2x actual)")
    print()
    
    # Show all methods comparison
    print("All methods comparison (suction):")
    for method, result in get_all_methods(reynolds_suction, rel_rough_suction).items():
        if hasattr(result, 'friction_factor'):
            print(f"  {method}: f={result.friction_factor:.6f} ({result.flow_regime})")