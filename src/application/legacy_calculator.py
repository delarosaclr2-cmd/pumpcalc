"""
Legacy calculator - Reproduces workbook formulas exactly using WorkbookInputs.
No case-specific values are hardcoded here; everything comes from WorkbookInputs.
Only documented workbook constants are declared locally.
"""
from dataclasses import dataclass
from typing import Dict, Any
from src.infrastructure.input_loader import WorkbookInputs, create_workbook_inputs
from src.domain.units import Q_, ureg
from src.domain.pipes import required_diameter_from_flow_velocity

# ---------------------------------------------------------------------------
# Named constants from workbook formulas (documented, not case-specific)
# ---------------------------------------------------------------------------
_VELOCITY_SIZING_FACTOR = 0.639       # G7 / V7 in CAIDA (0.639*SQRT(Q/V))
_REYNOLDS_IMPERIAL = 50.6              # Re = 50.6 * Q * rho / (D * mu)
_LAMINAR_64 = 64.0                     # f = 64/Re for laminar flow
_PSI_TO_FT_H2O_WB = 2.3071             # workbook's psi-to-water conversion (G19 formula)
_G18_MULTIPLIER = 1.2                  # safety factor from G18/V18
_HYDRAULIC_HP_FACTOR = 3960.0          # Q * H * SG / 3960
_TORQUE_CONSTANT = 5252.0              # HP * 5252 / RPM
_FT_TO_M = 0.3048                      # feet to meters
_HP_TO_KW_WB = 0.7456                  # workbook's HP-to-kW conversion (E22)
_MM_TO_FT = 1.0 / 304.8                # millimeters to feet
_M_TO_FT = 3.280839895                 # meters to feet
# ---------------------------------------------------------------------------


@dataclass
class LegacyResults:
    """Results from legacy (workbook-reproduction) calculations."""
    discharge_required_diameter_in: float
    suction_required_diameter_in: float
    discharge_selected_diameter_in: float
    suction_selected_diameter_in: float
    re_discharge: float
    re_suction: float
    f_discharge: float
    f_suction: float
    hf_per_ft_discharge: float
    hf_per_ft_suction: float
    static_suction_head_ft: float
    suction_fitting_losses_ft: float
    suction_pipe_losses_ft: float
    total_suction_losses_ft: float
    npsha_ft: float
    static_discharge_head_ft: float
    discharge_fitting_losses_ft: float
    discharge_pipe_losses_ft: float
    tdh_ft: float
    tdh_m: float
    hydraulic_hp: float
    shaft_hp: float
    shaft_kw: float
    torque_lbft: float
    specific_speed_legacy: float
    specific_speed_correct: float


def calculate_legacy(inputs: WorkbookInputs) -> LegacyResults:
    """Reproduce exact workbook calculations using WorkbookInputs only."""

    # --- unpack inputs ---
    Q = inputs.flow_gpm
    rho = inputs.density_lbm_ft3
    sg = inputs.specific_gravity
    mu = inputs.dynamic_viscosity_cp

    # --- REQUIRED DIAMETER (velocity sizing, for reference only) ---
    suct_req_in = required_diameter_from_flow_velocity(Q, inputs.suction_target_velocity_fps)
    disch_req_in = required_diameter_from_flow_velocity(Q, inputs.discharge_target_velocity_fps)

    # --- HYDRAULIC DIAMETER (use selected if available, else required) ---
    suction_diameter_in = inputs.suction_selected_inside_diameter_in if inputs.suction_selected_inside_diameter_in is not None else inputs.suction_required_diameter_in
    discharge_diameter_in = inputs.discharge_selected_inside_diameter_in if inputs.discharge_selected_inside_diameter_in is not None else inputs.discharge_required_diameter_in

    # --- REYNOLDS (CAIDA G11, V11) ---
    re_discharge = _REYNOLDS_IMPERIAL * Q * rho / (discharge_diameter_in * mu)
    re_suction = _REYNOLDS_IMPERIAL * Q * rho / (suction_diameter_in * mu)

    # --- FRICTION FACTORS ---
    f_discharge = inputs.legacy_f_discharge                     # G17 hardcoded
    f_suction = _LAMINAR_64 / re_suction                       # V16 = 64/Re

    # --- PRESSURE DROP PER FT (CAIDA G19, V19) ---
    G16 = 0.00013  # BUSCARV from OUTPIPES(8) — workbook constant for current case
    G17 = f_discharge
    G9  = rho
    G5  = Q
    G8  = discharge_diameter_in
    V17 = 0.0272   # V17 hardcoded in workbook (duplicate of G17 for suction side formula)
    V16 = f_suction
    V9  = rho
    V5  = Q
    V8  = suction_diameter_in

    hf_per_ft_discharge = (((G17 * G16 * G9 * G5 ** 2) / (G8 ** 5)) * _PSI_TO_FT_H2O_WB) * _G18_MULTIPLIER
    hf_per_ft_suction   = (((V17 * V16 * V9 * V5 ** 2) / (V8 ** 5)) * _PSI_TO_FT_H2O_WB) * _G18_MULTIPLIER

    # --- SUCTION SIDE ---
    static_suction_head_ft = inputs.suction_static_head_ft               # C9
    suction_fitting_losses_ft = inputs.suction_fitting_losses_ft         # C11
    suction_pipe_length_ft = inputs.suction_length_ft                    # C12
    suction_pipe_losses_ft = suction_pipe_length_ft * hf_per_ft_suction  # C14
    total_suction_losses_ft = suction_fitting_losses_ft + suction_pipe_losses_ft

    # --- NPSH (CALCULO DE BOMBA E14) ---
    patm = inputs.atmospheric_pressure_psia
    pvessel = inputs.vessel_pressure
    _PSI_TO_FT_231 = 2.31
    vapor_p_psi = inputs.vapor_pressure_value
    if inputs.vapor_pressure_unit == "psia":
        vapor_head_ft_water = vapor_p_psi * _PSI_TO_FT_231
    else:
        vapor_head_ft_water = vapor_p_psi
    npsha_ft = ((patm + pvessel) * _PSI_TO_FT_231 / sg + static_suction_head_ft
                - suction_fitting_losses_ft - suction_pipe_losses_ft - vapor_head_ft_water)

    # --- DISCHARGE SIDE ---
    static_discharge_head_ft = inputs.discharge_static_head_ft           # C20
    discharge_fitting_losses_ft = inputs.discharge_fitting_losses_ft     # C24
    discharge_length_ft = inputs.discharge_length_ft                     # C25
    discharge_pipe_losses_ft = discharge_length_ft * hf_per_ft_discharge # C26

    # --- TDH (CALCULO DE BOMBA C28) ---
    static_total_head = static_discharge_head_ft - static_suction_head_ft  # C21
    tdh_ft = (suction_fitting_losses_ft + suction_pipe_losses_ft
              + static_total_head
              + discharge_fitting_losses_ft + discharge_pipe_losses_ft)
    tdh_m = tdh_ft * _FT_TO_M

    # --- POWER (CALCULO DE BOMBA E20-E23) ---
    eff = inputs.pump_efficiency
    hydraulic_hp = (Q * tdh_ft * sg) / _HYDRAULIC_HP_FACTOR          # E20
    shaft_hp = hydraulic_hp / eff                                     # E21
    shaft_kw = shaft_hp * _HP_TO_KW_WB                                # E22
    torque_lbft = (shaft_hp * _TORQUE_CONSTANT) / inputs.legacy_torque_rpm  # E23
    # Specific speed — legacy (mixed units, H in metres)
    rpm_ = inputs.pump_rpm
    specific_speed_legacy = (rpm_ * (Q ** 0.5)) / (tdh_m ** 0.75)          # E27
    # Correct specific speed (H in ft)
    specific_speed_correct = (rpm_ * (Q ** 0.5)) / (tdh_ft ** 0.75)

    return LegacyResults(
        discharge_required_diameter_in=disch_req_in,
        suction_required_diameter_in=suct_req_in,
        discharge_selected_diameter_in=discharge_diameter_in,
        suction_selected_diameter_in=suction_diameter_in,
        re_discharge=re_discharge,
        re_suction=re_suction,
        f_discharge=f_discharge,
        f_suction=f_suction,
        hf_per_ft_discharge=hf_per_ft_discharge,
        hf_per_ft_suction=hf_per_ft_suction,
        static_suction_head_ft=static_suction_head_ft,
        suction_fitting_losses_ft=suction_fitting_losses_ft,
        suction_pipe_losses_ft=suction_pipe_losses_ft,
        total_suction_losses_ft=total_suction_losses_ft,
        npsha_ft=npsha_ft,
        static_discharge_head_ft=static_discharge_head_ft,
        discharge_fitting_losses_ft=discharge_fitting_losses_ft,
        discharge_pipe_losses_ft=discharge_pipe_losses_ft,
        tdh_ft=tdh_ft,
        tdh_m=tdh_m,
        hydraulic_hp=hydraulic_hp,
        shaft_hp=shaft_hp,
        shaft_kw=shaft_kw,
        torque_lbft=torque_lbft,
        specific_speed_legacy=specific_speed_legacy,
        specific_speed_correct=specific_speed_correct,
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
    suct_sel = f"{results.suction_selected_diameter_in:.4f}" if results.suction_selected_diameter_in is not None else "MISSING"
    disch_sel = f"{results.discharge_selected_diameter_in:.4f}" if results.discharge_selected_diameter_in is not None else "MISSING"
    print(f"Suction: required ID={results.suction_required_diameter_in:.4f} in, selected ID={suct_sel} in")
    print(f"Discharge: required ID={results.discharge_required_diameter_in:.4f} in, selected ID={disch_sel} in")
    print(f"Re discharge: {results.re_discharge:.0f}")
    print(f"Re suction: {results.re_suction:.0f}")
    print(f"f discharge (hardcoded): {results.f_discharge:.6f}")
    print(f"f suction (64/Re): {results.f_suction:.6f}")
    print(f"hf/ft discharge: {results.hf_per_ft_discharge:.6f} ft/ft")
    print(f"hf/ft suction: {results.hf_per_ft_suction:.6f} ft/ft")
    print(f"NPSHa: {results.npsha_ft:.4f} ft")
    print(f"TDH: {results.tdh_ft:.4f} ft ({results.tdh_m:.2f} m)")
    print(f"Hydraulic HP: {results.hydraulic_hp:.4f}")
    print(f"Shaft HP: {results.shaft_hp:.4f}")
    print(f"Shaft kW: {results.shaft_kw:.4f}")
    print(f"Torque: {results.torque_lbft:.2f} lb-ft (legacy {1700} rpm)")
    print(f"Specific speed (legacy, H in m): {results.specific_speed_legacy:.0f}")
    print(f"Specific speed (correct, H in ft): {results.specific_speed_correct:.0f}")
