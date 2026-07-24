"""
Power module - Hydraulic and shaft power calculations.
"""
from dataclasses import dataclass
from typing import Optional
from src.domain.units import Q_, ureg


@dataclass
class PowerResult:
    """Power calculation results."""
    hydraulic_power_hp: float
    hydraulic_power_kw: float
    shaft_power_hp: float
    shaft_power_kw: float
    shaft_power_kw_legacy: float = 0.0
    torque_lbft: Optional[float] = None
    rpm: Optional[float] = None
    motor_efficiency: Optional[float] = None
    motor_power_kw: Optional[float] = None
    motor_power_hp: Optional[float] = None


def hydraulic_power_hp(Q_gpm: float, TDH_ft: float, SG: float) -> float:
    """Hydraulic horsepower: P_h = Q * TDH * SG / 3960"""
    if Q_gpm < 0:
        raise ValueError("Flow rate must be non-negative")
    if TDH_ft < 0:
        raise ValueError("TDH must be non-negative")
    if SG <= 0:
        raise ValueError("Specific gravity must be positive")
    return Q_gpm * TDH_ft * SG / 3960.0


def hydraulic_power_kw(Q_gpm: float, TDH_ft: float, SG: float) -> float:
    """Hydraulic power in kW (standard 0.7457)."""
    hp = hydraulic_power_hp(Q_gpm, TDH_ft, SG)
    return hp * 0.7457


def shaft_power_hp(hydraulic_hp: float, pump_efficiency: float) -> float:
    """Shaft (brake) horsepower: P_shaft = P_hydraulic / eta_pump"""
    if pump_efficiency <= 0 or pump_efficiency > 1:
        raise ValueError("Pump efficiency must be between 0 and 1")
    return hydraulic_hp / pump_efficiency


def shaft_power_kw(shaft_hp: float) -> float:
    """Convert HP to kW using standard conversion (0.7457)."""
    return shaft_hp * 0.7457


def shaft_power_kw_legacy(shaft_hp: float) -> float:
    """Convert HP to kW using workbook conversion (0.7456)."""
    return shaft_hp * 0.7456


def torque_lbft(shaft_hp: float, rpm: float) -> float:
    """Torque in lb-ft: T = HP * 5252 / RPM"""
    if rpm <= 0:
        raise ValueError("RPM must be > 0")
    return shaft_hp * 5252 / rpm


def motor_power_kw(shaft_kw: float, motor_efficiency: float) -> float:
    """Electrical motor power input."""
    if motor_efficiency <= 0 or motor_efficiency > 1:
        raise ValueError("Motor efficiency must be between 0 and 1")
    return shaft_kw / motor_efficiency


def motor_power_hp(shaft_hp: float, motor_efficiency: float) -> float:
    """Electrical motor power input in HP."""
    if motor_efficiency <= 0 or motor_efficiency > 1:
        raise ValueError("Motor efficiency must be between 0 and 1")
    return shaft_hp / motor_efficiency


def power_legacy(
    Q_gpm: float,
    TDH_ft: float,
    SG: float,
    pump_efficiency: float,
    rpm: float,
    motor_efficiency: float = None
) -> PowerResult:
    """Legacy workbook power calculation.
    
    Workbook formulas:
    E20 = (E4*C28*E11)/3960        # Hydraulic HP
    E21 = E20/C22                  # Shaft HP
    E22 = E21*0.7456               # Shaft kW (workbook conversion)
    E23 = (E21*5252)/1700          # Torque (hardcoded 1700 rpm)
    """
    ph_hp = hydraulic_power_hp(Q_gpm, TDH_ft, SG)
    pb_hp = shaft_power_hp(ph_hp, pump_efficiency)
    pb_kw = shaft_power_kw_legacy(pb_hp)  # workbook 0.7456
    tq = torque_lbft(pb_hp, rpm) if rpm > 0 else None

    result = PowerResult(
        hydraulic_power_hp=ph_hp,
        hydraulic_power_kw=hydraulic_power_kw(Q_gpm, TDH_ft, SG),
        shaft_power_hp=pb_hp,
        shaft_power_kw=pb_kw,
        shaft_power_kw_legacy=pb_kw,
        torque_lbft=tq,
        rpm=rpm
    )

    if motor_efficiency is not None:
        result.motor_efficiency = motor_efficiency
        result.motor_power_hp = motor_power_hp(pb_hp, motor_efficiency)
        result.motor_power_kw = motor_power_kw(pb_kw, motor_efficiency)

    return result


def power_validated(
    Q_gpm: float,
    TDH_ft: float,
    SG: float,
    pump_efficiency: float,
    rpm: float,
    motor_efficiency: float = None,
    legacy_rpm: float = None,
) -> PowerResult:
    """Validated power calculation with proper units (not delegating to legacy)."""
    if Q_gpm < 0:
        raise ValueError("Flow rate must be non-negative")
    if TDH_ft < 0:
        raise ValueError("TDH must be non-negative")
    if SG <= 0:
        raise ValueError("Specific gravity must be positive")
    if pump_efficiency <= 0 or pump_efficiency > 1:
        raise ValueError("Pump efficiency must be between 0 and 1")

    ph_hp = hydraulic_power_hp(Q_gpm, TDH_ft, SG)
    pb_hp = shaft_power_hp(ph_hp, pump_efficiency)
    pb_kw = shaft_power_kw(pb_hp)          # standard 0.7457
    pb_kw_legacy = shaft_power_kw_legacy(pb_hp)  # workbook 0.7456
    tq = torque_lbft(pb_hp, rpm) if rpm > 0 else None

    result = PowerResult(
        hydraulic_power_hp=ph_hp,
        hydraulic_power_kw=hydraulic_power_kw(Q_gpm, TDH_ft, SG),
        shaft_power_hp=pb_hp,
        shaft_power_kw=pb_kw,
        shaft_power_kw_legacy=pb_kw_legacy,
        torque_lbft=tq,
        rpm=rpm,
    )

    if motor_efficiency is not None:
        result.motor_efficiency = motor_efficiency
        result.motor_power_hp = motor_power_hp(pb_hp, motor_efficiency)
        result.motor_power_kw = motor_power_kw(pb_kw, motor_efficiency)

    return result


def specific_speed_us(N_rpm: float, Q_gpm: float, H_ft: float) -> float:
    """US specific speed: Ns = N * sqrt(Q) / H^0.75"""
    if H_ft <= 0:
        return 0
    return N_rpm * (Q_gpm ** 0.5) / (H_ft ** 0.75)


def specific_speed_metric(N_rpm: float, Q_m3s: float, H_m: float) -> float:
    """Metric specific speed: nq = N * sqrt(Q) / H^0.75 (Q in m³/s, H in m)"""
    if H_m <= 0:
        return 0
    return N_rpm * (Q_m3s ** 0.5) / (H_m ** 0.75)


def specific_speed_legacy(N_rpm: float, Q_gpm: float, H_m: float) -> float:
    """Legacy workbook formula: =(C29*(E4^0.5))/(E24^0.75)
    Workbook uses Q in GPM and H in meters - MIXED UNITS!
    """
    if H_m <= 0:
        return 0
    return N_rpm * (Q_gpm ** 0.5) / (H_m ** 0.75)


if __name__ == '__main__':
    Q = 770.5
    TDH = 195.55
    SG = 0.995
    eta = 0.72
    rpm = 3600
    leg_rpm = 1700

    print("Power Calculations:")
    print("=" * 50)

    ph = hydraulic_power_hp(Q, TDH, SG)
    pb = shaft_power_hp(ph, eta)
    pk = shaft_power_kw(pb)
    pk_leg = shaft_power_kw_legacy(pb)
    tq = torque_lbft(pb, rpm)
    tq_leg = torque_lbft(pb, leg_rpm)

    print(f"Q = {Q} GPM, TDH = {TDH:.2f} ft, SG = {SG}")
    print(f"Hydraulic HP: {ph:.4f}")
    print(f"Shaft HP: {pb:.4f}")
    print(f"Shaft kW (standard 0.7457): {pk:.4f}")
    print(f"Shaft kW (workbook 0.7456): {pk_leg:.4f}")
    print(f"Torque @ {rpm} rpm: {tq:.2f} lb-ft")
    print(f"Torque @ {leg_rpm} rpm: {tq_leg:.2f} lb-ft")
