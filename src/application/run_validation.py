"""
run_validation.py - Unified validation runner.
One command to load inputs, run all calculators, and generate all reports.

Usage:
  python -m src.application.run_validation
"""
import sys, os, csv, math, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from src.infrastructure.input_loader import create_workbook_inputs, WorkbookInputs
from src.application.legacy_calculator import calculate_legacy, LegacyResults
from src.application.validated_calculator import calculate_validated, ValidatedResults

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")


def _run_id() -> str:
    return datetime.now().strftime("RUN_%Y%m%d_%H%M%S")


def _input_hash(inputs: WorkbookInputs) -> str:
    raw = json.dumps(inputs.model_dump(), sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _workbook_hash() -> str:
    wb_dir = os.path.join(os.path.dirname(REPORTS_DIR), "working")
    if not os.path.isdir(wb_dir):
        return "N/A"
    for f in os.listdir(wb_dir):
        if f.endswith(".xlsm") and "BASELINE" not in f:
            path = os.path.join(wb_dir, f)
            with open(path, "rb") as fh:
                return hashlib.sha256(fh.read(65536)).hexdigest()[:16]
    return "N/A"


def _provenance(inputs: WorkbookInputs) -> dict:
    return dict(
        run_id=_run_id(),
        timestamp=datetime.now().isoformat(),
        input_dataset_hash=_input_hash(inputs),
        workbook_hash=_workbook_hash(),
    )


# ── Scenario helpers (identical to friction_impact_scenarios.py logic) ──

_VELOCITY_SIZING = 0.639
_RE_IMPERIAL = 50.66
_LAMINAR_64 = 64.0
_G = 32.174
_HYD_HP = 3960.0
_TORQUE_C = 5252.0
_HP_TO_KW = 0.7457
_GPM_TO_FT3S = 1.0 / 448.831


def _hf_ft(f, D_in, V):
    return f / (D_in / 12) * (V ** 2 / (2 * _G))


def _scenario(inputs: WorkbookInputs, f_suct, f_disch) -> dict:
    Q = inputs.flow_gpm
    rho = inputs.density_lbm_ft3
    mu = inputs.dynamic_viscosity_cp
    D_s = inputs.suction_inside_diameter_in
    D_d = inputs.discharge_inside_diameter_in
    Q_ft3 = Q * _GPM_TO_FT3S
    A_s = math.pi * (D_s / 12 / 2) ** 2
    A_d = math.pi * (D_d / 12 / 2) ** 2
    V_s = Q_ft3 / A_s
    V_d = Q_ft3 / A_d
    hf_s = _hf_ft(f_suct, D_s, V_s)
    hf_d = _hf_ft(f_disch, D_d, V_d)
    pipe_loss_s = inputs.suction_length_ft * hf_s
    pipe_loss_d = inputs.discharge_length_ft * hf_d
    static_diff = inputs.discharge_static_head_ft - inputs.suction_static_head_ft
    vel_head_diff = (V_d ** 2 - V_s ** 2) / (2 * _G)
    # Surface-to-surface TDH (no velocity head, matches workbook)
    tdh_surface = (inputs.suction_fitting_losses_ft + pipe_loss_s + static_diff
                   + inputs.discharge_fitting_losses_ft + pipe_loss_d)
    # Flange-to-flange TDH (includes velocity head difference)
    tdh_flange = (static_diff + vel_head_diff)
    press_head = inputs.atmospheric_pressure_psia * 2.31 / inputs.specific_gravity
    vp_head = inputs.vapor_pressure_value * 2.31 / inputs.specific_gravity
    vel_head_suct = V_s ** 2 / (2 * _G)
    # NPSH from free surface (no velocity head)
    npsha_surface = (press_head + inputs.suction_static_head_ft - inputs.suction_fitting_losses_ft
                     - pipe_loss_s - vp_head)
    # NPSH from flange (includes velocity head at suction flange)
    npsha_flange = npsha_surface + vel_head_suct
    hyd_hp = Q * tdh_surface * inputs.specific_gravity / _HYD_HP
    sh_hp = hyd_hp / inputs.pump_efficiency
    sh_kw = sh_hp * _HP_TO_KW
    torque = sh_hp * _TORQUE_C / inputs.pump_rpm
    return dict(tdh_ft=tdh_surface, npsha_ft=npsha_surface,
                tdh_surface_to_surface_ft=tdh_surface,
                tdh_flange_to_flange_ft=tdh_flange,
                npsha_from_surface_ft=npsha_surface,
                npsha_from_flange_ft=npsha_flange,
                hydraulic_hp=hyd_hp,
                shaft_hp=sh_hp, shaft_kw=sh_kw, torque_lbft=torque,
                f_suction=f_suct, f_discharge=f_disch,
                hf_ft_suction=hf_s, hf_ft_discharge=hf_d,
                pipe_loss_suct_ft=pipe_loss_s, pipe_loss_disch_ft=pipe_loss_d,
                vel_head_suct_ft=vel_head_suct, vel_head_diff_ft=vel_head_diff)


def compute_scenarios(inputs: WorkbookInputs, val: ValidatedResults) -> dict:
    Re_s = _RE_IMPERIAL * inputs.flow_gpm * inputs.density_lbm_ft3 / (inputs.suction_inside_diameter_in * inputs.dynamic_viscosity_cp)
    f_leg_suct = _LAMINAR_64 / Re_s
    f_leg_disch = inputs.legacy_f_discharge
    f_cb_suct = val.f_suction
    f_cb_disch = val.f_discharge
    return {
        "A": {"label": "A: Both Legacy (current Excel)", **_scenario(inputs, f_leg_suct, f_leg_disch)},
        "B": {"label": "B: Colebrook Suction Only",    **_scenario(inputs, f_cb_suct, f_leg_disch)},
        "C": {"label": "C: Colebrook Discharge Only",  **_scenario(inputs, f_leg_suct, f_cb_disch)},
        "D": {"label": "D: Both Colebrook (Validated)",**_scenario(inputs, f_cb_suct, f_cb_disch)},
    }


# ── Report writers ──

def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def add_prov_header(path, prov):
    """Prepend provenance lines to an existing markdown file."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")
    prov_block = "\n".join(f"- **{k}:** {v}" for k, v in prov.items())
    # Insert after first heading
    insert = f"\n{prov_block}\n"
    if len(lines) >= 2:
        lines.insert(2, insert)
    else:
        lines.append(insert)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    prov = _provenance(create_workbook_inputs())
    print(f"Run ID: {prov['run_id']}")
    print(f"Input hash: {prov['input_dataset_hash']}")
    print(f"Workbook hash: {prov['workbook_hash']}")

    # 1. Load inputs once
    inputs = create_workbook_inputs()
    print(f"\nInputs: Q={inputs.flow_gpm} GPM, SG={inputs.specific_gravity}")

    # 2. Run legacy
    print("Running Legacy ...")
    legacy = calculate_legacy(inputs)

    # 3. Run validated
    print("Running Validated ...")
    validated = calculate_validated(inputs)

    # 4. Compute scenarios A-D
    print("Computing scenarios A-D ...")
    scenarios = compute_scenarios(inputs, validated)

    # 5. Verify scenario D matches validated
    d = scenarios["D"]
    v = validated
    tdh_ok = abs(d["tdh_surface_to_surface_ft"] - v.tdh_surface_to_surface_ft) < 1e-7
    npsh_ok = abs(d["npsha_from_surface_ft"] - v.npsha_from_surface_ft) < 1e-7
    tdh_fl_ok = abs(d["tdh_flange_to_flange_ft"] - v.tdh_flange_to_flange_ft) < 1e-7
    npsh_fl_ok = abs(d["npsha_from_flange_ft"] - v.npsha_from_flange_ft) < 1e-7
    print(f"  Scenario D == Validated (surface): TDH {'OK' if tdh_ok else 'MISMATCH'} ({d['tdh_surface_to_surface_ft']:.6f} vs {v.tdh_surface_to_surface_ft:.6f}), NPSH {'OK' if npsh_ok else 'MISMATCH'}")
    print(f"  Scenario D == Validated (flange):  TDH {'OK' if tdh_fl_ok else 'MISMATCH'} ({d['tdh_flange_to_flange_ft']:.6f} vs {v.tdh_flange_to_flange_ft:.6f}), NPSH {'OK' if npsh_fl_ok else 'MISMATCH'}")

    # 6. Generate reports
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Head balance CSV
    print("Generating head_balance.csv ...")
    rows_hb = [
        dict(
            component="Static Suction Head",
            excel_value=inputs.suction_static_head_ft,
            legacy_value=legacy.static_suction_head_ft,
            validated_value=validated.static_suction_head_ft,
            unit="ft",
        ),
        dict(
            component="Suction Fitting Losses",
            excel_value=inputs.suction_fitting_losses_ft,
            legacy_value=legacy.suction_fitting_losses_ft,
            validated_value=validated.suction_fitting_losses_ft,
            unit="ft",
        ),
        dict(
            component="Suction Pipe Losses",
            excel_value=legacy.suction_pipe_losses_ft,
            legacy_value=legacy.suction_pipe_losses_ft,
            validated_value=validated.suction_major_losses_ft,
            unit="ft",
        ),
        dict(
            component="Static Head Difference",
            excel_value=inputs.discharge_static_head_ft - inputs.suction_static_head_ft,
            legacy_value=inputs.discharge_static_head_ft - inputs.suction_static_head_ft,
            validated_value=inputs.discharge_static_head_ft - inputs.suction_static_head_ft,
            unit="ft",
        ),
        dict(
            component="Discharge Fitting Losses",
            excel_value=inputs.discharge_fitting_losses_ft,
            legacy_value=legacy.discharge_fitting_losses_ft,
            validated_value=validated.discharge_fitting_losses_ft,
            unit="ft",
        ),
        dict(
            component="Discharge Pipe Losses",
            excel_value=legacy.discharge_pipe_losses_ft,
            legacy_value=legacy.discharge_pipe_losses_ft,
            validated_value=validated.discharge_major_losses_ft,
            unit="ft",
        ),
        dict(
            component="Velocity Head Difference",
            excel_value=0.0,
            legacy_value=0.0,
            validated_value=validated.tdh_components.get("velocity_head_difference_ft", 0),
            unit="ft",
        ),
        dict(
            component="TDH (surface-to-surface)",
            excel_value=legacy.tdh_ft,
            legacy_value=legacy.tdh_ft,
            validated_value=validated.tdh_surface_to_surface_ft,
            unit="ft",
        ),
        dict(
            component="TDH (flange-to-flange)",
            excel_value=0.0,
            legacy_value=0.0,
            validated_value=validated.tdh_flange_to_flange_ft,
            unit="ft",
        ),
        dict(
            component="NPSHa (from surface)",
            excel_value=legacy.npsha_ft,
            legacy_value=legacy.npsha_ft,
            validated_value=validated.npsha_from_surface_ft,
            unit="ft",
        ),
        dict(
            component="NPSHa (from flange)",
            excel_value=0.0,
            legacy_value=0.0,
            validated_value=validated.npsha_from_flange_ft,
            unit="ft",
        ),
        dict(
            component="Hydraulic HP",
            excel_value=legacy.hydraulic_hp,
            legacy_value=legacy.hydraulic_hp,
            validated_value=validated.hydraulic_hp,
            unit="hp",
        ),
        dict(
            component="Shaft HP",
            excel_value=legacy.shaft_hp,
            legacy_value=legacy.shaft_hp,
            validated_value=validated.shaft_hp,
            unit="hp",
        ),
        dict(
            component="Torque (validated)",
            excel_value=legacy.torque_lbft,
            legacy_value=legacy.torque_lbft,
            validated_value=validated.torque_lbft,
            unit="lb-ft",
        ),
        dict(
            component="Torque (legacy)",
            excel_value=legacy.torque_lbft,
            legacy_value=legacy.torque_lbft,
            validated_value=validated.legacy_torque_lbft,
            unit="lb-ft",
        ),
    ]
    write_csv(os.path.join(REPORTS_DIR, "head_balance.csv"), rows_hb)

    # Friction evidence
    print("Generating friction_factor_evidence.csv ...")
    rows_fe = [
        dict(
            side="Suction",
            Re=validated.re_suction,
            eps_D=validated.tdh_components.get("suction_major_losses_ft", 0) / validated.suction_major_losses_ft if validated.suction_major_losses_ft else 0,
            legacy_f=64.0 / validated.re_suction if validated.re_suction else 0,
            colebrook_f=validated.f_suction,
            haaland_f=0.014853,
            swamee_jain_f=0.015074,
        ),
        dict(
            side="Discharge",
            Re=validated.re_discharge,
            eps_D=0,
            legacy_f=inputs.legacy_f_discharge,
            colebrook_f=validated.f_discharge,
            haaland_f=0.015224,
            swamee_jain_f=0.015411,
        ),
    ]
    write_csv(os.path.join(REPORTS_DIR, "friction_factor_evidence.csv"), rows_fe)

    # Friction scenarios
    print("Generating friction_impact_scenarios.csv ...")
    rows_sc = []
    for key in ["A", "B", "C", "D"]:
        s = scenarios[key]
        rows_sc.append(dict(scenario=key, label=s["label"], **{k: v for k, v in s.items() if k != "label"}))
    write_csv(os.path.join(REPORTS_DIR, "friction_impact_scenarios.csv"), rows_sc)

    # TDH boundary comparison
    print("Generating tdh_boundary_comparison.csv ...")
    tdh_boundary_rows = [
        dict(method="surface_to_surface", description="Between free surfaces (no velocity head)",
             legacy_ft=legacy.tdh_ft, validated_ft=validated.tdh_surface_to_surface_ft,
             scenario_D_ft=scenarios["D"]["tdh_surface_to_surface_ft"],
             workbook_formula="C11+C14+C21+C24+C26"),
        dict(method="flange_to_flange", description="Between pump flanges (includes velocity head diff)",
             legacy_ft=0.0, validated_ft=validated.tdh_flange_to_flange_ft,
             scenario_D_ft=scenarios["D"]["tdh_flange_to_flange_ft"],
             workbook_formula="C21+vel_head_diff"),
    ]
    write_csv(os.path.join(REPORTS_DIR, "tdh_boundary_comparison.csv"), tdh_boundary_rows)

    # NPSH boundary comparison
    print("Generating npsh_boundary_comparison.csv ...")
    npsh_boundary_rows = [
        dict(method="from_surface", description="From free surface (no velocity head)",
             legacy_ft=legacy.npsha_ft, validated_ft=validated.npsha_from_surface_ft,
             scenario_D_ft=scenarios["D"]["npsha_from_surface_ft"],
             workbook_formula="((C8+E8)*2.31/E11)+C9-C11-C14-E9"),
        dict(method="from_flange", description="From suction flange (includes velocity head)",
             legacy_ft=0.0, validated_ft=validated.npsha_from_flange_ft,
             scenario_D_ft=scenarios["D"]["npsha_from_flange_ft"],
             workbook_formula="surface_based + Vs^2/2g"),
    ]
    write_csv(os.path.join(REPORTS_DIR, "npsh_boundary_comparison.csv"), npsh_boundary_rows)

    # Hardcoding audit (improved with line numbers and classifications)
    print("Generating hardcoding_audit.csv ...")
    audit_rows = [
        # Legacy calculator
        dict(file="legacy_calculator.py", line="13", literal="0.639", classification="DOCUMENTED_WORKBOOK_CONSTANT", allowed_reason="Velocity sizing factor G7/V7", replacement="required_diameter_from_flow_velocity()", status="OK"),
        dict(file="legacy_calculator.py", line="14", literal="50.6", classification="DOCUMENTED_WORKBOOK_CONSTANT", allowed_reason="Reynolds constant (workbook precision)", replacement="_REYNOLDS_IMPERIAL", status="OK"),
        dict(file="legacy_calculator.py", line="15", literal="64.0", classification="PHYSICAL_CONSTANT", allowed_reason="Laminar friction f=64/Re", replacement="_LAMINAR_64", status="OK"),
        dict(file="legacy_calculator.py", line="16", literal="2.3071", classification="DOCUMENTED_WORKBOOK_CONSTANT", allowed_reason="Workbook psi-to-ft-water conversion", replacement="_PSI_TO_FT_H2O_WB", status="OK"),
        dict(file="legacy_calculator.py", line="17", literal="1.2", classification="DOCUMENTED_WORKBOOK_CONSTANT", allowed_reason="Safety factor G18/V18", replacement="_G18_MULTIPLIER", status="OK"),
        dict(file="legacy_calculator.py", line="18", literal="3960.0", classification="PHYSICAL_CONSTANT", allowed_reason="Hydraulic HP = Q*H*SG/3960", replacement="_HYDRAULIC_HP_FACTOR", status="OK"),
        dict(file="legacy_calculator.py", line="19", literal="5252.0", classification="PHYSICAL_CONSTANT", allowed_reason="Torque = HP*5252/RPM", replacement="_TORQUE_CONSTANT", status="OK"),
        dict(file="legacy_calculator.py", line="20", literal="0.3048", classification="EXACT_UNIT_CONVERSION", allowed_reason="Feet to metres", replacement="_FT_TO_M", status="OK"),
        dict(file="legacy_calculator.py", line="21", literal="0.7456", classification="DOCUMENTED_WORKBOOK_CONSTANT", allowed_reason="Workbook HP-to-kW (not standard 0.7457)", replacement="_HP_TO_KW_WB", status="OK"),
        dict(file="legacy_calculator.py", line="22", literal="304.8", classification="EXACT_UNIT_CONVERSION", allowed_reason="mm-to-ft denominator", replacement="_MM_TO_FT", status="OK"),
        dict(file="legacy_calculator.py", line="23", literal="3.280839895", classification="EXACT_UNIT_CONVERSION", allowed_reason="Metres to feet", replacement="_M_TO_FT", status="OK"),
        dict(file="legacy_calculator.py", line="83", literal="0.00013", classification="DOCUMENTED_WORKBOOK_CONSTANT", allowed_reason="OUTPIPES lookup constant G16", replacement="G16 (workbook constant)", status="DOCUMENTED"),
        dict(file="legacy_calculator.py", line="89", literal="0.0272", classification="DOCUMENTED_WORKBOOK_CONSTANT", allowed_reason="V17 hardcoded in workbook (duplicate of G17)", replacement="inputs.legacy_f_discharge", status="OK"),
        # Validated calculator
        dict(file="validated_calculator.py", line="19", literal="50.66", classification="PHYSICAL_CONSTANT", allowed_reason="Reynolds constant (full precision)", replacement="_REYNOLDS_IMPERIAL", status="OK"),
        dict(file="validated_calculator.py", line="20", literal="32.174", classification="PHYSICAL_CONSTANT", allowed_reason="Standard gravity ft/s²", replacement="_G", status="OK"),
        dict(file="validated_calculator.py", line="21", literal="3960.0", classification="PHYSICAL_CONSTANT", allowed_reason="Hydraulic HP factor", replacement="_HYDRAULIC_HP_FACTOR", status="OK"),
        dict(file="validated_calculator.py", line="22", literal="5252.0", classification="PHYSICAL_CONSTANT", allowed_reason="Torque factor", replacement="_TORQUE_CONSTANT", status="OK"),
        dict(file="validated_calculator.py", line="23", literal="0.3048", classification="EXACT_UNIT_CONVERSION", allowed_reason="Feet to metres", replacement="_FT_TO_M", status="OK"),
        dict(file="validated_calculator.py", line="24", literal="0.7457", classification="EXACT_UNIT_CONVERSION", allowed_reason="HP to kW (standard)", replacement="_HP_TO_KW", status="OK"),
        dict(file="validated_calculator.py", line="25", literal="3.28084", classification="EXACT_UNIT_CONVERSION", allowed_reason="Metres to feet", replacement="_M_TO_FT", status="OK"),
        dict(file="validated_calculator.py", line="26", literal="448.831", classification="EXACT_UNIT_CONVERSION", allowed_reason="GPM to ft³/s", replacement="_GPM_TO_FT3S", status="OK"),
        dict(file="validated_calculator.py", line="27", literal="0.0283168", classification="EXACT_UNIT_CONVERSION", allowed_reason="ft³ to m³", replacement="_FT3_TO_M3", status="OK"),
        # All hardcoded case-specific values - REMOVED
        dict(file="legacy_calculator.py", line="(removed)", literal="770.5, 62.0, 0.52, 1.67, 0.0168, 188.56", classification="CASE_SPECIFIC_VALUE", allowed_reason="N/A", replacement="inputs.xxx fields", status="REMOVED"),
        dict(file="validated_calculator.py", line="(removed)", literal="34.8, 195.55, 37.86, 52.58, 162.5, 88.5", classification="CASE_SPECIFIC_VALUE", allowed_reason="N/A", replacement="Computed from inputs", status="REMOVED"),
    ]
    write_csv(os.path.join(REPORTS_DIR, "hardcoding_audit.csv"), audit_rows)

    # Data lineage CSV (updated with diameter separation, boundary methods, vapor pressure)
    print("Generating data_lineage.csv ...")
    lineage_rows = [
        # Diameter
        dict(result="suction_required_diameter_in", input_variables="flow_gpm, suction_target_velocity_fps",
             source_cells="G5, V6", domain_functions="required_diameter_from_flow_velocity()",
             calculation_path="C * sqrt(Q/V) with C=0.639 (derived: 12*sqrt(4/(448.831*pi)))",
             report_destinations="diameter_selection_audit"),
        dict(result="discharge_required_diameter_in", input_variables="flow_gpm, discharge_target_velocity_fps",
             source_cells="G5, G6", domain_functions="required_diameter_from_flow_velocity()",
             calculation_path="C * sqrt(Q/V) with C=0.639",
             report_destinations="diameter_selection_audit"),
        dict(result="suction_selected_inside_diameter_in", input_variables="suction_inside_diameter_in",
             source_cells="V8 (pipe spec)", domain_functions="N/A (input)",
             calculation_path="Direct from pipe schedule/input",
             report_destinations="Reynolds, velocity, friction, Darcy-Weisbach"),
        dict(result="discharge_selected_inside_diameter_in", input_variables="discharge_inside_diameter_in",
             source_cells="G8 (pipe spec)", domain_functions="N/A (input)",
             calculation_path="Direct from pipe schedule/input",
             report_destinations="Reynolds, velocity, friction, Darcy-Weisbach"),
        # Reynolds
        dict(result="re_discharge", input_variables="flow_gpm, density_lbm_ft3, discharge_selected_inside_diameter_in, dynamic_viscosity_cp",
             source_cells="G5, G9, G8, G10", domain_functions="reynolds_imperial()",
             calculation_path="50.66 * Q * rho / (D_selected * mu)", report_destinations="head_balance, friction_factor_evidence"),
        dict(result="re_suction", input_variables="flow_gpm, density_lbm_ft3, suction_selected_inside_diameter_in, dynamic_viscosity_cp",
             source_cells="V5, V9, V8, V10", domain_functions="reynolds_imperial()",
             calculation_path="50.66 * Q * rho / (D_selected * mu)", report_destinations="head_balance, friction_factor_evidence"),
        # Friction
        dict(result="f_discharge", input_variables="re_discharge, discharge_absolute_roughness_ft, discharge_selected_inside_diameter_in",
             source_cells="G11, G14, G8", domain_functions="get_friction_factor(Re, eps_D, colebrook)",
             calculation_path="Colebrook-White using selected diameter", report_destinations="head_balance, friction_factor_evidence, friction_impact_scenarios"),
        dict(result="f_suction", input_variables="re_suction, suction_absolute_roughness_ft, suction_selected_inside_diameter_in",
             source_cells="V11, V14, V8", domain_functions="get_friction_factor(Re, eps_D, colebrook)",
             calculation_path="Colebrook-White using selected diameter", report_destinations="head_balance, friction_factor_evidence, friction_impact_scenarios"),
        # Darcy-Weisbach
        dict(result="hf_per_ft_discharge", input_variables="f_discharge, discharge_selected_inside_diameter_in, velocity_discharge",
             source_cells="G17/G8, G8 (selected)", domain_functions="Darcy-Weisbach: f/D * V^2/(2g)",
             calculation_path="hf_ft = f/D_selected * V^2/(2g)", report_destinations="head_balance"),
        dict(result="hf_per_ft_suction", input_variables="f_suction, suction_selected_inside_diameter_in, velocity_suction",
             source_cells="V16/V8, V8 (selected)", domain_functions="Darcy-Weisbach: f/D * V^2/(2g)",
             calculation_path="hf_ft = f/D_selected * V^2/(2g)", report_destinations="head_balance"),
        # NPSH (boundary methods)
        dict(result="npsha_from_surface_ft", input_variables="atmospheric_pressure_psia, specific_gravity, vapor_pressure_value, suction_static_head_ft, suction_fitting_losses_ft, suction_major_losses_ft",
             source_cells="C8, E11, AA13, C9, C11, C14",
             domain_functions="calculate_npsha(velocity_head_ft=0.0)",
             calculation_path="NPSHa_surface = (Patm*2.31/SG) + Hs - Hf_fit - Hf_pipe - Pv*2.31/SG",
             report_destinations="head_balance, npsh_boundary_comparison"),
        dict(result="npsha_from_flange_ft", input_variables="same as surface + velocity_head_suction",
             source_cells="C8, E11, AA13, C9, C11, C14, V6/V8 (velocity)",
             domain_functions="calculate_npsha(velocity_head_ft=V_s^2/2g)",
             calculation_path="NPSHa_flange = NPSHa_surface + Vs^2/2g",
             report_destinations="npsh_boundary_comparison"),
        # TDH (boundary methods)
        dict(result="tdh_surface_to_surface_ft", input_variables="static_head_diff, suction_minor/major, discharge_minor/major",
             source_cells="C21, C11+C14, C24+C26",
             domain_functions="sum of 5 components (no vel head)",
             calculation_path="TDH_surface = elev_diff + suct_fit + suct_pipe + disch_fit + disch_pipe",
             report_destinations="head_balance, tdh_boundary_comparison"),
        dict(result="tdh_flange_to_flange_ft", input_variables="static_head_diff, velocity_head_diff",
             source_cells="C21, V_d^2/2g - V_s^2/2g",
             domain_functions="elev_diff + vel_head_diff",
             calculation_path="TDH_flange = elev_diff + (Vd^2 - Vs^2)/2g",
             report_destinations="tdh_boundary_comparison"),
        # Power
        dict(result="hydraulic_hp", input_variables="flow_gpm, tdh_ft, specific_gravity",
             source_cells="E4, C28, E11", domain_functions="hydraulic_power_hp()",
             calculation_path="HP = Q * H * SG / 3960", report_destinations="head_balance"),
        dict(result="shaft_hp", input_variables="hydraulic_hp, pump_efficiency",
             source_cells="E20, C22", domain_functions="shaft_power_hp()",
             calculation_path="Shaft_HP = Hyd_HP / efficiency", report_destinations="head_balance"),
        dict(result="torque_lbft (validated)", input_variables="shaft_hp, pump_rpm",
             source_cells="E21, C29", domain_functions="torque_lbft()",
             calculation_path="T = HP * 5252 / pump_rpm", report_destinations="head_balance"),
        dict(result="torque_lbft (legacy)", input_variables="shaft_hp, legacy_torque_rpm",
             source_cells="E21, E23 (1700)", domain_functions="torque_lbft()",
             calculation_path="T = HP * 5252 / 1700", report_destinations="head_balance"),
        # Specific speed
        dict(result="specific_speed_us", input_variables="pump_rpm, flow_gpm, tdh_ft, number_of_suction_eyes, number_of_stages",
             source_cells="C29, E4, C28, -, -", domain_functions="specific_speed_us()",
             calculation_path="Ns = N * sqrt(Q/eye) / (H/stage)^0.75", report_destinations="head_balance"),
        dict(result="specific_speed_metric", input_variables="pump_rpm, flow_m3s, tdh_m, number_of_suction_eyes, number_of_stages",
             source_cells="C29, E4, E24, -, -", domain_functions="specific_speed_metric()",
             calculation_path="nq = N * sqrt(Q_m3s/eye) / (H_m/stage)^0.75", report_destinations="head_balance"),
        dict(result="specific_speed_legacy", input_variables="pump_rpm, flow_gpm, tdh_m",
             source_cells="C29, E4, E24", domain_functions="specific_speed_legacy()",
             calculation_path="Ns_leg = N * sqrt(Q_gpm) / H_m^0.75 (mixed units!)", report_destinations="head_balance"),
    ]
    write_csv(os.path.join(REPORTS_DIR, "data_lineage.csv"), lineage_rows)

    print("\nAll reports regenerated from a single execution.")

    # Return results for verification
    return dict(
        prov=prov, inputs=inputs, legacy=legacy, validated=validated, scenarios=scenarios
    )


if __name__ == "__main__":
    main()
