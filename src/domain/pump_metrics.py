"""
Pump metrics module - Specific speed, suction specific speed, affinity laws.
"""
from dataclasses import dataclass
from typing import Optional
from src.domain.units import Q_, ureg


@dataclass
class PumpMetrics:
    """Pump performance metrics."""
    flow_gpm: float
    head_ft: float
    rpm: float
    efficiency: float = 0.0
    
    @property
    def specific_speed_us(self) -> float:
        """US specific speed: Ns = N * sqrt(Q) / H^0.75"""
        if self.head_ft <= 0:
            return 0.0
        return self.rpm * (self.flow_gpm ** 0.5) / (self.head_ft ** 0.75)
    
    @property
    def suction_specific_speed(self) -> float:
        """Suction specific speed: Nss = N * sqrt(Q) / NPSHr^0.75"""
        # Requires NPSHr which is not provided
        return 0.0
    
    def affinity_laws(self, new_rpm: float) -> 'PumpMetrics':
        """Apply affinity laws to get performance at different speed.
        
        Q2/Q1 = N2/N1
        H2/H1 = (N2/N1)^2
        P2/P1 = (N2/N1)^3
        """
        ratio = new_rpm / self.rpm
        return PumpMetrics(
            flow_gpm=self.flow_gpm * ratio,
            head_ft=self.head_ft * ratio**2,
            rpm=new_rpm,
            efficiency=self.efficiency
        )
    
    def affinity_laws_diameter(self, new_diameter: float, original_diameter: float) -> 'PumpMetrics':
        """Apply affinity laws for impeller diameter change.
        
        Q2/Q1 = D2/D1
        H2/H1 = (D2/D1)^2
        P2/P1 = (D2/D1)^3
        """
        ratio = new_diameter / original_diameter
        return PumpMetrics(
            flow_gpm=self.flow_gpm * ratio,
            head_ft=self.head_ft * ratio**2,
            rpm=self.rpm,
            efficiency=self.efficiency
        )


def specific_speed_us(N_rpm: float, Q_gpm: float, H_ft: float) -> float:
    """US specific speed: Ns = N * sqrt(Q) / H^0.75"""
    if H_ft <= 0:
        return 0.0
    return N_rpm * (Q_gpm ** 0.5) / (H_ft ** 0.75)


def specific_speed_metric(N_rpm: float, Q_m3s: float, H_m: float) -> float:
    """Metric specific speed: nq = N * sqrt(Q) / H^0.75 (Q in m³/s, H in m)"""
    if H_m <= 0:
        return 0.0
    return N_rpm * (Q_m3s ** 0.5) / (H_m ** 0.75)


def suction_specific_speed(N_rpm: float, Q_gpm: float, NPSHr_ft: float) -> float:
    """Suction specific speed: Nss = N * sqrt(Q) / NPSHr^0.75"""
    if NPSHr_ft <= 0:
        return 0.0
    return N_rpm * (Q_gpm ** 0.5) / (NPSHr_ft ** 0.75)


def affinity_flow(Q1: float, N1: float, N2: float) -> float:
    """Q2 = Q1 * (N2/N1)"""
    return Q1 * N2 / N1


def affinity_head(H1: float, N1: float, N2: float) -> float:
    """H2 = H1 * (N2/N1)^2"""
    return H1 * (N2 / N1) ** 2


def affinity_power(P1: float, N1: float, N2: float) -> float:
    """P2 = P1 * (N2/N1)^3"""
    return P1 * (N2 / N1) ** 3


def affinity_diameter_flow(Q1: float, D1: float, D2: float) -> float:
    """Q2 = Q1 * (D2/D1)"""
    return Q1 * D2 / D1


def affinity_diameter_head(H1: float, D1: float, D2: float) -> float:
    """H2 = H1 * (D2/D1)^2"""
    return H1 * (D2 / D1) ** 2


def affinity_diameter_power(P1: float, D1: float, D2: float) -> float:
    """P2 = P1 * (D2/D1)^3"""
    return P1 * (D2 / D1) ** 3


# Impeller type classification by specific speed
def classify_impeller(Ns_us: float) -> str:
    """Classify impeller type by US specific speed."""
    if Ns_us < 500:
        return "Radial (low Ns)"
    elif Ns_us < 4000:
        return "Mixed flow"
    elif Ns_us < 10000:
        return "Axial / Propeller"
    else:
        return "Special / Very high Ns"


def pump_type_from_ns(Ns_us: float) -> str:
    """Determine pump type from specific speed."""
    if Ns_us < 1000:
        return "Radial flow (process, boiler feed)"
    elif Ns_us < 2500:
        return "Mixed flow"
    elif Ns_us < 5000:
        return "Axial flow (propeller)"
    else:
        return "Special"


if __name__ == '__main__':
    # Test with workbook values
    N = 3600  # RPM
    Q = 770.5  # GPM
    H = 195.55  # ft (TDH)
    
    Ns = specific_speed_us(N, Q, H)
    print(f"Specific speed (US): {Ns:.0f}")
    print(f"Impeller type: {classify_impeller(Ns)}")
    print(f"Pump type: {pump_type_from_ns(Ns)}")
    
    # Workbook calculates: (C29*(E4^0.5))/(E24^0.75) = (3600*sqrt(770.5))/(59.6^0.75)
    # E24 = C28*0.3048 = TDH in meters
    # This is WRONG - uses H in meters with Q in GPM
    
    H_m = 195.55 * 0.3048  # 59.6 m
    Ns_wrong = N * (Q ** 0.5) / (H_m ** 0.75)
    print(f"\nWorkbook (wrong units): {Ns_wrong:.0f}")
    print(f"  Uses H in meters with Q in GPM!")
    
    # Correct metric specific speed
    Q_m3s = Q / 448.831 * 0.0283168  # GPM to m3/s
    Ns_metric = specific_speed_metric(N, Q_m3s, H_m)
    print(f"Metric specific speed: {Ns_metric:.1f}")
    
    # Affinity laws test
    pm = PumpMetrics(Q, H, N, 0.72)
    pm_1800 = pm.affinity_laws(1800)
    print(f"\nAt 3600 RPM: Q={pm.flow_gpm} GPM, H={pm.head_ft} ft")
    print(f"At 1800 RPM: Q={pm_1800.flow_gpm:.1f} GPM, H={pm_1800.head_ft:.1f} ft")