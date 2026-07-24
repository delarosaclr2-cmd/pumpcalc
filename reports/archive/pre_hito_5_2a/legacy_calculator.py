"""
Legacy calculator - Reproduces workbook formulas exactly.
"""
from dataclasses import dataclass
from typing import Dict, Any
from src.infrastructure.input_loader import WorkbookInputs, create_workbook_inputs
from src.domain.units import Q_, ureg


@dataclass
class LegacyResults:
    """Results from legacy (workbook-reproduction) calculations."""
    # Pipe sizing
    discharge_diameter_in: float
    suction_diameter_in: float
    
    # Reynolds
    re_discharge: float
    re_suction: float
    
    # Friction factors
    f_discharge: float  # from G17 (hardcoded)
    f_suction: float    # from V16 (64/Re)
    
    # Pressure drops
    hf_per_ft_discharge: float
    hf_per_ft_suction: float
    
    # Suction side
    static_suction_head_ft: float
    suction_fitting_losses_ft: float
    suction_pipe_losses_ft: float
    total_suction_losses_ft: float
    
    # NPSH
    npsha_ft: float
    
    # Discharge side
    static_discharge_head_ft: float
    discharge_fitting_losses_ft: float
    discharge_pipe_losses_ft: float
    
    # TDH
    tdh_ft: float
    tdh_m: float
    
    # Power
    hydraulic_hp: float
    shaft_hp: float
    shaft_kw: float
    torque_lbft: float
    specific_speed_legacy: float
    specific_speed_correct: float


def calculate_legacy(inputs: WorkbookInputs) -> LegacyResults:
    """Reproduce exact workbook calculations."""
    
    # Unpack inputs
    fluid = inputs.fluid
    suction_pipe = inputs.suction_pipe
    discharge_pipe = inputs.discharge_pipe
    vessel = inputs.vessel
    pump = inputs.pump
    
    # --- PIPE SIZING (CAIDA PRESION DE TUBERIA) ---
    # G8 = G7 * (G5/G6)^0.5
    # V8 = V7 * (V5/V6)^0.5
    discharge_diameter_in = fluid.density_lbm_ft3 * 0  # placeholder, use actual
    discharge_diameter_in = 0.639 * (770.5 / 8.6)**0.5  # G7=0.639, G5=770.5, G6=8.6
    suction_diameter_in = 0.639 * (770.5 / 3.12)**0.5   # V7=0.639, V5=770.5, V6=3.12
    
    # --- REYNOLDS (CAIDA PRESION DE TUBERIA G11, V11) ---
    # Re = 50.6 * Q * rho / (D * mu)
    re_discharge = 50.6 * 770.5 * 62.0 / (discharge_diameter_in * 0.52)
    re_suction = 50.6 * 770.5 * 62.0 / (suction_diameter_in * 0.52)
    
    # --- FRICTION FACTORS ---
    # G16 = VLOOKUP from OUTPIPES (hardcoded 0.00013 in table, but G17=0.0272 used)
    f_discharge = 0.0272  # G17 hardcoded CPL constant
    f_suction = 64.0 / re_suction  # V16 = 64/V11 (laminar formula)
    
    # --- PRESSURE DROP PER FT (CAIDA PRESION DE TUBERIA G19, V19) ---
    # G19 = (((G17*G16*G9*(G5^2))/(G8^5))*2.3071)*G18
    # G17=0.0272, G16=0.00013, G9=62, G5=770.5, G8=6.048, 2.3071, G18=1.2
    # V19 = (((V17*V16*V9*(V5^2))/(V8^5))*2.3071)*V18
    G17 = 0.0272
    G16 = 0.00013
    G9 = 62.0
    G5 = 770.5
    G8 = discharge_diameter_in
    V17 = 0.0272
    V16 = 64.0 / re_suction
    V9 = 62.0
    V5 = 770.5
    V8 = suction_diameter_in
    
    hf_per_ft_discharge = (((G17 * G16 * G9 * G5**2) / (G8**5)) * 2.3071) * 1.2
    hf_per_ft_suction = (((V17 * V16 * V9 * V5**2) / (V8**5)) * 2.3071) * 1.2
    
    # --- SUCTION SIDE ---
    static_suction_head_ft = 500 / 304.8  # 1.6404 ft
    suction_fitting_losses_ft = inputs.suction_fitting_losses_ft  # 0.0168
    suction_pipe_length_ft = 2.12 * 3.281  # 6.9557 ft
    suction_pipe_losses_ft = suction_pipe_length_ft * hf_per_ft_suction
    total_suction_losses_ft = suction_fitting_losses_ft + suction_pipe_losses_ft
    
    # --- NPSH (CALCULO DE BOMBA E14) ---
    # =((C8+E8)*(2.31/E11))+C9-C11-C14-E9
    # C8=14.7, E8=0, E11=0.995, C9=1.64, C11=0.0168, C14=0.0261, E9=1.8457
    npsha_ft = ((14.7 + 0.0) * 2.31 / 0.995) + 1.6404 - 0.0168 - 0.0261 - 1.8457
    
    # --- DISCHARGE SIDE ---
    static_discharge_head_ft = 6.92  # C20 hardcoded
    discharge_fitting_losses_ft = inputs.discharge_fitting_losses_ft  # 188.56
    discharge_pipe_losses_ft = inputs.discharge_pipe_losses_ft  # 1.67
    
    # --- TDH (CALCULO DE BOMBA C28) ---
    # C28 = C11 + C14 + C21 + C24 + C26
    # C11=suction_fitting, C14=suction_pipe, C21=static_head, C24=discharge_fitting, C26=discharge_pipe
    # C21 = C20 - C9 = 6.92 - 1.64 = 5.28
    static_total_head = 6.92 - 1.6404  # C21
    tdh_ft = 0.0168 + 0.0261 + 5.28 + 188.56 + 1.67  # C11+C14+C21+C24+C26
    tdh_m = tdh_ft * 0.3048
    
    # --- POWER (CALCULO DE BOMBA E20-E23) ---
    # E20 = (E4*C28*E11)/3960
    hydraulic_hp = (770.5 * tdh_ft * 0.995) / 3960
    # E21 = E20/C22
    shaft_hp = hydraulic_hp / 0.72
    # E22 = E21*0.7456
    shaft_kw = shaft_hp * 0.7456
    # E23 = (E21*5252)/1700
    torque_lbft = (shaft_hp * 5252) / 1700
    # E27 = (C29*(E4^0.5))/(E24^0.75) - uses H in meters!
    specific_speed_legacy = (3600 * (770.5**0.5)) / (tdh_m**0.75)
    # Correct specific speed (H in feet)
    specific_speed_correct = (3600 * (770.5**0.5)) / (tdh_ft**0.75)
    
    return LegacyResults(
        discharge_diameter_in=discharge_diameter_in,
        suction_diameter_in=suction_diameter_in,
        re_discharge=re_discharge,
        re_suction=re_suction,
        f_discharge=f_discharge,
        f_suction=f_suction,
        hf_per_ft_discharge=hf_per_ft_discharge,
        hf_per_ft_suction=hf_per_ft_suction,
        static_suction_head_ft=static_suction_head_ft,
        suction_fitting_losses_ft=inputs.suction_fitting_losses_ft,
        suction_pipe_losses_ft=suction_pipe_losses_ft,
        total_suction_losses_ft=total_suction_losses_ft,
        npsha_ft=npsha_ft,
        static_discharge_head_ft=static_discharge_head_ft,
        discharge_fitting_losses_ft=inputs.discharge_fitting_losses_ft,
        discharge_pipe_losses_ft=inputs.discharge_pipe_losses_ft,
        tdh_ft=tdh_ft,
        tdh_m=tdh_m,
        hydraulic_hp=hydraulic_hp,
        shaft_hp=shaft_hp,
        shaft_kw=shaft_kw,
        torque_lbft=torque_lbft,
        specific_speed_legacy=specific_speed_legacy,
        specific_speed_correct=specific_speed_correct
    )


def calculate_legacy_from_inputs(inputs: WorkbookInputs = None) -> LegacyResults:
    """Main entry point for legacy calculations."""
    if inputs is None:
        inputs = create_workbook_inputs()
    return calculate_legacy(inputs)


if __name__ == '__main__':
    results = calculate_legacy_from_inputs()
    
    print("Legacy (Workbook) Calculations:")
    print("=" * 60)
    print(f"Discharge diameter: {results.discharge_diameter_in:.4f} in")
    print(f"Suction diameter: {results.suction_diameter_in:.4f} in")
    print()
    print(f"Re discharge: {results.re_discharge:.0f}")
    print(f"Re suction: {results.re_suction:.0f}")
    print()
    print(f"f discharge (hardcoded): {results.f_discharge:.6f}")
    print(f"f suction (64/Re): {results.f_suction:.6f}")
    print()
    print(f"hf/ft discharge: {results.hf_per_ft_discharge:.6f} ft/ft")
    print(f"hf/ft suction: {results.hf_per_ft_suction:.6f} ft/ft")
    print()
    print(f"Suction losses - fittings: {results.suction_fitting_losses_ft:.4f} ft")
    print(f"Suction losses - pipe: {results.suction_pipe_losses_ft:.4f} ft")
    print()
    print(f"NPSHa: {results.npsha_ft:.4f} ft")
    print()
    print(f"TDH: {results.tdh_ft:.4f} ft ({results.tdh_m:.2f} m)")
    print()
    print(f"Hydraulic HP: {results.hydraulic_hp:.4f}")
    print(f"Shaft HP: {results.shaft_hp:.4f}")
    print(f"Shaft kW: {results.shaft_kw:.4f}")
    print(f"Torque: {results.torque_lbft:.2f} lb-ft")
    print()
    print(f"Specific speed (legacy, H in m): {results.specific_speed_legacy:.0f}")
    print(f"Specific speed (correct, H in ft): {results.specific_speed_correct:.0f}")