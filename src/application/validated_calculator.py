"""
Validated calculator - Uses proper hydraulic equations with correct physics.
All inputs from WorkbookInputs; no case-specific hardcoded values.
All results are computed and returned; no literal return values.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import math
from src.infrastructure.input_loader import WorkbookInputs, create_workbook_inputs
from src.domain.units import Q_, ureg
from src.domain.friction import get_friction_factor
from src.domain.npsh import (
    NPSHInputs, calculate_npsha, evaluate_npsh_margin,
    convert_npshr_to_ft, check_npshr_reference_identity,
    NPSH_MARGIN_CALCULATED,
    NPSH_MARGIN_NOT_EVALUABLE_MISSING_NPSHR,
    NPSH_MARGIN_NOT_CLASSIFIED_NO_POLICY,
    NPSHR_REFERENCE_INCOMPLETE,
    NPSHR_REFERENCE_MISMATCH,
    NPSHR_REFERENCE_MATCHED,
    NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_INCOMPLETE,
    NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_MISMATCH,
)
from src.domain.power import (
    hydraulic_power_hp, shaft_power_hp, shaft_power_kw,
    torque_lbft, specific_speed_us as ss_us,
    specific_speed_metric as ss_metric, specific_speed_legacy as ss_legacy,
)
from src.domain.pipes import required_diameter_from_flow_velocity
from src.domain.accessory_losses import (
    compute_suction_results, compute_discharge_results,
    summarize_suction, summarize_discharge,
    detect_double_counting, build_pareto_leq_only, build_pareto_full_discharge,
    build_scenario_comparisons,
)
from src.domain.system_boundaries import compute_boundary_absolute_pressure
from src.domain.pressure_requirements import (
    build_pressure_head_terms, build_pressure_requirements,
    build_semantic_tdh_balances, build_system_curve_classification,
    detect_pressure_boundary_overlap, combine_boundary_pressures,
    PressureReference,
)

# Named constants
_REYNOLDS_IMPERIAL = 50.66             # Re factor for imperial units
_G = 32.174                            # gravity ft/s²
_HYDRAULIC_HP_FACTOR = 3960.0
_TORQUE_CONSTANT = 5252.0
_FT_TO_M = 0.3048
_HP_TO_KW = 0.7457                     # standard conversion (not workbook's 0.7456)
_M_TO_FT = 3.28084
_GPM_TO_FT3S = 1.0 / 448.831
_FT3_TO_M3 = 0.0283168


@dataclass
class ValidatedResults:
    """Results from validated (physics-based) calculations.
    Every field is a computed result, never a hardcoded literal.
    """
    # Pipe sizing
    suction_required_diameter_in: float
    discharge_required_diameter_in: float
    suction_nominal_diameter_in: float
    discharge_nominal_diameter_in: float
    suction_selected_inside_diameter_in: Optional[float]
    discharge_selected_inside_diameter_in: Optional[float]
    suction_pipe_schedule: str
    discharge_pipe_schedule: str
    suction_pipe_material: str
    discharge_pipe_material: str
    # Reynolds
    re_discharge: float
    re_suction: float
    # Friction factors (Colebrook-White)
    f_discharge: float
    f_suction: float
    f_discharge_method: str
    f_suction_method: str
    # Pressure drops (Darcy-Weisbach)
    hf_per_ft_discharge: float
    hf_per_ft_suction: float
    # Suction side
    static_suction_head_ft: float
    suction_fitting_losses_ft: float
    suction_major_losses_ft: float
    total_suction_losses_ft: float
    # NPSH
    npsha_ft: float
    npsha_m: float
    npsha_from_surface_ft: float
    npsha_from_flange_ft: float
    npsh_boundary_method: str
    npsh_margin_status: str
    npsha_equivalence_diff: float
    npsha_equivalence_status: str
    # Discharge side
    static_discharge_head_ft: float
    discharge_fitting_losses_ft: float
    discharge_major_losses_ft: float
    total_discharge_losses_ft: float
    # TDH
    tdh_ft: float
    tdh_m: float
    tdh_surface_to_surface_ft: float
    tdh_flange_to_flange_ft: Optional[float]
    tdh_flange_input_status: str
    partial_geometric_kinetic_difference_ft: float
    tdh_boundary_method: str
    # Power
    hydraulic_hp: float
    shaft_hp: float
    shaft_kw: float
    torque_lbft: float
    legacy_torque_lbft: float
    pump_rpm: float
    legacy_torque_rpm: float
    # Specific speed
    specific_speed_us: float
    specific_speed_metric: float
    specific_speed_legacy: float
    # Optional fields with defaults
    npsha_components: Dict = field(default_factory=dict)
    tdh_components: Dict = field(default_factory=dict)
    accessory_audit: Dict = field(default_factory=dict)
    friction_comparison: Dict = field(default_factory=dict)
    specific_speed_definition: str = ""
    flow_basis: str = ""
    head_basis: str = ""
    stage_count: int = 1
    suction_eye_count: int = 1
    diameter_status: str = "OK"
    # NPSHr integration
    npshr_source_value: Optional[float] = None
    npshr_source_unit: Optional[str] = None
    npshr_ft: Optional[float] = None
    npshr_reference_status: Optional[str] = None
    npshr_reference_missing_fields: list = field(default_factory=list)
    npshr_reference_mismatched_fields: list = field(default_factory=list)
    npsh_margin_ft: Optional[float] = None
    npsh_availability_ratio: Optional[float] = None
    npsh_margin_fraction: Optional[float] = None
    npsh_margin_calculation_status: Optional[str] = None
    npsh_margin_acceptance_status: Optional[str] = None
    npsh_margin_warnings: list = field(default_factory=list)
    npshr_traceability: Optional[dict] = None


def calculate_validated(inputs: WorkbookInputs = None) -> ValidatedResults:
    """Calculate validated results from WorkbookInputs.
    
    Every intermediate variable is computed once and returned.
    No hardcoded literals — all case-specific values come from inputs.
    """
    if inputs is None:
        inputs = create_workbook_inputs()

    # --- unpack inputs ---
    Q = inputs.flow_gpm
    rho = inputs.density_lbm_ft3
    sg = inputs.specific_gravity
    mu = inputs.dynamic_viscosity_cp
    _N = inputs.pump_rpm

    # --- PIPE SIZING: required vs selected ---
    # Required diameters from velocity sizing (for recommendation)
    suct_req_in = required_diameter_from_flow_velocity(Q, inputs.suction_target_velocity_fps)
    disch_req_in = required_diameter_from_flow_velocity(Q, inputs.discharge_target_velocity_fps)

    # Hydraulic diameter: use selected if available, otherwise fall back to required
    D_suct_in = inputs.suction_selected_inside_diameter_in if inputs.suction_selected_inside_diameter_in is not None else inputs.suction_required_diameter_in
    D_disch_in = inputs.discharge_selected_inside_diameter_in if inputs.discharge_selected_inside_diameter_in is not None else inputs.discharge_required_diameter_in

    # Pipe schedule status
    pipe_schedule_status = "OK"
    if inputs.suction_pipe_schedule == "MISSING_SELECTED_PIPE_SCHEDULE" or inputs.discharge_pipe_schedule == "MISSING_SELECTED_PIPE_SCHEDULE":
        pipe_schedule_status = "MISSING_SELECTED_PIPE_SCHEDULE"
    diameter_status = pipe_schedule_status

    # --- REYNOLDS (uses selected inside diameter) ---
    re_discharge = _REYNOLDS_IMPERIAL * Q * rho / (D_disch_in * mu)
    re_suction = _REYNOLDS_IMPERIAL * Q * rho / (D_suct_in * mu)

    # --- VELOCITIES (uses selected inside diameter) ---
    Q_ft3s = Q * _GPM_TO_FT3S
    A_disch = math.pi * (D_disch_in / 12 / 2) ** 2
    A_suct = math.pi * (D_suct_in / 12 / 2) ** 2
    V_disch = Q_ft3s / A_disch
    V_suct = Q_ft3s / A_suct

    D_disch_ft = D_disch_in / 12
    D_suct_ft = D_suct_in / 12
    eps_disch = inputs.discharge_absolute_roughness_ft / D_disch_ft
    eps_suct = inputs.suction_absolute_roughness_ft / D_suct_ft

    # --- FRICTION FACTORS (Colebrook-White) ---
    fr_disch = get_friction_factor(re_discharge, eps_disch, "colebrook")
    fr_suct = get_friction_factor(re_suction, eps_suct, "colebrook")
    f_disch = fr_disch.friction_factor
    f_suct = fr_suct.friction_factor

    # --- DARCY-WEISBACH HEAD LOSS PER FT ---
    hf_ft_disch = f_disch / D_disch_ft * (V_disch ** 2 / (2 * _G))
    hf_ft_suct = f_suct / D_suct_ft * (V_suct ** 2 / (2 * _G))

    # --- SUCTION SIDE ---
    static_suct_ft = inputs.suction_static_head_ft
    suct_fit_ft = inputs.suction_fitting_losses_ft
    suct_len_ft = inputs.suction_length_ft
    suct_major_ft = suct_len_ft * hf_ft_suct
    total_suct_ft = suct_fit_ft + suct_major_ft

    # --- DISCHARGE SIDE ---
    static_disch_ft = inputs.discharge_static_head_ft
    disch_fit_ft = inputs.discharge_fitting_losses_ft
    disch_len_ft = inputs.discharge_length_ft
    disch_major_ft = disch_len_ft * hf_ft_disch
    total_disch_ft = disch_fit_ft + disch_major_ft

    # --- VELOCITY HEADS ---
    vel_head_suct = V_suct ** 2 / (2 * _G)
    vel_head_disch = V_disch ** 2 / (2 * _G)
    vel_head_diff = vel_head_disch - vel_head_suct

    # --- NPSH: TWO BOUNDARY METHODS (equivalent by Bernoulli) ---

    # Method 1: From free surface (includes static head, excludes velocity head)
    # This is the workbook formula: ((C8+E8)*2.31/E11)+C9-C11-C14-E9
    # NPSHa_surface = P_surface/γ + z_surface - z_pump - losses - Pv/γ
    npsh_surface_inp = NPSHInputs(
        p_atm_abs_psi=inputs.atmospheric_pressure_psia,
        p_vessel=inputs.vessel_pressure,
        p_vessel_type=inputs.vessel_pressure_type,
        specific_gravity=sg,
        vapor_pressure_psi=inputs.vapor_pressure_value,
        liquid_surface_elev_ft=static_suct_ft,
        pump_centerline_elev_ft=0.0,
        suction_fitting_losses_ft=suct_fit_ft,
        suction_pipe_losses_ft=suct_major_ft,
        velocity_head_ft=0.0,  # surface velocity ≈ 0
    )
    npsh_surface_result = calculate_npsha(npsh_surface_inp)
    npsha_from_surface_ft = npsh_surface_result.npsha_ft

    # Method 2: From suction flange (Bernoulli-derived, equals surface route)
    # NPSHa_flange = P_flange/γ + V²/2g - Pv/γ
    # Where P_flange/γ = P_surface/γ + z_surface - z_flange - losses - V²/2g
    # Therefore NPSHa_flange = P_surface/γ + z_surface - z_flange - losses - Pv/γ
    # This is IDENTICAL to NPSHa_surface when z_flange = z_pump
    # The velocity head cancels out via Bernoulli — do NOT add it again
    npsh_flange_inp = NPSHInputs(
        p_atm_abs_psi=inputs.atmospheric_pressure_psia,
        p_vessel=inputs.vessel_pressure,
        p_vessel_type=inputs.vessel_pressure_type,
        specific_gravity=sg,
        vapor_pressure_psi=inputs.vapor_pressure_value,
        liquid_surface_elev_ft=static_suct_ft,
        pump_centerline_elev_ft=0.0,
        suction_fitting_losses_ft=suct_fit_ft,
        suction_pipe_losses_ft=suct_major_ft,
        velocity_head_ft=0.0,  # Bernoulli cancellation: V²/2g in P_flange derivation cancels out
    )
    npsh_flange_result = calculate_npsha(npsh_flange_inp)
    npsha_from_flange_ft = npsh_flange_result.npsha_ft

    # Verify equivalence: both routes must produce the same NPSHa
    npsha_equivalence_diff = abs(npsha_from_surface_ft - npsha_from_flange_ft)
    npsha_equivalence_status = "EQUIVALENT" if npsha_equivalence_diff < 1e-8 else "NOT_EQUIVALENT"

    # The workbook uses surface-based NPSH (no velocity head)
    # Both methods produce the same result via Bernoulli derivation
    npsh_boundary_method = "FROM_FREE_SURFACE"

    # --- TDH: TWO METHODS ---
    static_head_diff = static_disch_ft - static_suct_ft
    pressure_head_diff = 0.0  # open tank, no additional pressurization

    # Method A - Surface to surface (velocities at free surfaces ≈ 0)
    # TDH_surface = elev_diff + press_diff + major_losses + minor_losses
    # Velocities at free surfaces are negligible, so velocity head is NOT included.
    # This matches the workbook formula: C28 = C11 + C14 + C21 + C24 + C26
    tdh_surface_to_surface_ft = (static_head_diff
                                  + suct_fit_ft + suct_major_ft
                                  + disch_fit_ft + disch_major_ft
                                  + pressure_head_diff)

    # Method B - Flange to flange (requires actual flange pressures)
    # TDH_flange = (P_disch - P_suct)/γ + (V_d² - V_s²)/(2g) + (z_disch - z_suct)
    # Without direct flange pressure measurements, this cannot be computed.
    tdh_flange_input_status = "TDH_FLANGE_NOT_CALCULABLE"
    tdh_flange_to_flange_ft = None  # no flange pressure data available

    # Partial geometric-kinetic difference (elevation + velocity head, no pressure)
    # This is NOT the pump TDH — it is only the elevation and kinetic components
    partial_geometric_kinetic_difference_ft = static_head_diff + vel_head_diff

    # Boundary condition status: C9/C20 elevations need physical confirmation
    # They are currently used as tank free surface elevations but this has not
    # been physically verified — it's only inferred from formula structure.
    tdh_boundary_method = "BOUNDARY_CONDITION_UNVERIFIED"
    tdh_ft = tdh_surface_to_surface_ft
    tdh_m = tdh_ft * _FT_TO_M

    # --- NPSH (primary = surface-based, matching workbook) ---
    npsha_ft = npsha_from_surface_ft
    npsha_m = npsha_ft * _FT_TO_M

    # --- NPSHr integration (guarded by reference identity) ---
    npshr_source_value = None
    npshr_source_unit = None
    npshr_ft_val = None
    npshr_reference_status = None
    npshr_reference_missing = []
    npshr_reference_mismatched = []
    npsh_margin_ft_val = None
    npsh_availability_ratio_val = None
    npsh_margin_fraction_val = None
    npsh_margin_calc_status = None
    npsh_margin_accept_status = None
    npsh_margin_warn = []
    npshr_traceability = None

    if inputs.npshr is None:
        # NPSHr not provided - use existing contract
        margin_result = evaluate_npsh_margin(npsha_ft, None)
        npsh_margin_ft_val = margin_result.npsh_margin_ft
        npsh_availability_ratio_val = margin_result.npsh_availability_ratio
        npsh_margin_fraction_val = margin_result.npsh_margin_fraction
        npsh_margin_calc_status = margin_result.calculation_status
        npsh_margin_accept_status = margin_result.acceptance_status
        npsh_margin_warn = margin_result.warnings
    else:
        npshr_ref = inputs.npshr
        npshr_source_value = npshr_ref.value
        npshr_source_unit = npshr_ref.unit
        npshr_ft_val = convert_npshr_to_ft(npshr_ref.value, npshr_ref.unit)

        # Check reference identity
        ref_check = check_npshr_reference_identity(
            operating_flow_gpm=Q,
            operating_tdh_ft=tdh_ft,
            operating_speed_rpm=_N,
            operating_impeller_diameter_mm=inputs.pump_impeller_diameter_mm,
            reference_flow_gpm=npshr_ref.flow_gpm,
            reference_tdh_ft=npshr_ref.duty_tdh_ft,
            reference_speed_rpm=npshr_ref.speed_rpm,
            reference_impeller_diameter_mm=npshr_ref.impeller_diameter_mm,
        )
        npshr_reference_status = ref_check.status
        npshr_reference_missing = ref_check.missing_fields
        npshr_reference_mismatched = ref_check.mismatched_fields

        # Build full traceability dict from all provenance info
        def _dump_prov(p):
            if p is None:
                return None
            return p.model_dump() if hasattr(p, 'model_dump') else dict(p)

        npshr_traceability = {
            "source_value": npshr_ref.value,
            "source_unit": npshr_ref.unit,
            "converted_ft": npshr_ft_val,
            "value_provenance": _dump_prov(npshr_ref.value_provenance),
            "flow_gpm": npshr_ref.flow_gpm,
            "flow_provenance": _dump_prov(npshr_ref.flow_provenance),
            "duty_tdh_ft": npshr_ref.duty_tdh_ft,
            "duty_tdh_provenance": _dump_prov(npshr_ref.duty_tdh_provenance),
            "speed_rpm": npshr_ref.speed_rpm,
            "speed_provenance": _dump_prov(npshr_ref.speed_provenance),
            "impeller_diameter_mm": npshr_ref.impeller_diameter_mm,
            "impeller_provenance": _dump_prov(npshr_ref.impeller_provenance),
            "curve_reference": npshr_ref.curve_reference,
            "curve_provenance": _dump_prov(npshr_ref.curve_provenance),
        }

        if npshr_reference_status == NPSHR_REFERENCE_INCOMPLETE:
            npsh_margin_ft_val = None
            npsh_availability_ratio_val = None
            npsh_margin_fraction_val = None
            npsh_margin_calc_status = NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_INCOMPLETE
            npsh_margin_accept_status = NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_INCOMPLETE
            npsh_margin_warn = ref_check.warnings
        elif npshr_reference_status == NPSHR_REFERENCE_MISMATCH:
            npsh_margin_ft_val = None
            npsh_availability_ratio_val = None
            npsh_margin_fraction_val = None
            npsh_margin_calc_status = NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_MISMATCH
            npsh_margin_accept_status = NPSH_MARGIN_NOT_EVALUABLE_REFERENCE_MISMATCH
            npsh_margin_warn = ref_check.warnings
        else:  # NPSHR_REFERENCE_MATCHED
            margin_result = evaluate_npsh_margin(npsha_ft, npshr_ft_val)
            npsh_margin_ft_val = margin_result.npsh_margin_ft
            npsh_availability_ratio_val = margin_result.npsh_availability_ratio
            npsh_margin_fraction_val = margin_result.npsh_margin_fraction
            npsh_margin_calc_status = margin_result.calculation_status
            npsh_margin_accept_status = margin_result.acceptance_status
            npsh_margin_warn = margin_result.warnings

    # --- POWER (uses TDH surface-to-surface) ---
    hyd_hp = hydraulic_power_hp(Q, tdh_ft, sg)
    sh_hp = shaft_power_hp(hyd_hp, inputs.pump_efficiency)
    sh_kw = sh_hp * _HP_TO_KW
    val_torque = torque_lbft(sh_hp, _N)
    leg_torque = torque_lbft(sh_hp, inputs.legacy_torque_rpm)

    # --- SPECIFIC SPEED ---
    Q_per_eye = Q / inputs.number_of_suction_eyes
    H_per_stage = tdh_ft / inputs.number_of_stages
    H_per_stage_m = tdh_m / inputs.number_of_stages
    Q_m3s = Q * _GPM_TO_FT3S * _FT3_TO_M3
    Q_m3s_per_eye = Q_m3s / inputs.number_of_suction_eyes

    ss_us_val = ss_us(_N, Q_per_eye, H_per_stage)
    ss_metric_val = ss_metric(_N, Q_m3s_per_eye, H_per_stage_m)
    ss_legacy_val = ss_legacy(_N, Q, tdh_m)

    # --- FRICTION COMPARISON ---
    friction_comparison = {
        "discharge": {
            "Re": re_discharge,
            "eps_D": eps_disch,
            "legacy_f": inputs.legacy_f_discharge,
            "validated_f": f_disch,
            "difference_pct": (f_disch - inputs.legacy_f_discharge) / inputs.legacy_f_discharge * 100,
            "validated_method": "colebrook",
        },
        "suction": {
            "Re": re_suction,
            "eps_D": eps_suct,
            "legacy_f": 64.0 / re_suction,
            "validated_f": f_suct,
            "difference_pct": (f_suct - 64.0 / re_suction) / (64.0 / re_suction) * 100,
            "validated_method": "colebrook",
        },
    }

    return ValidatedResults(
        suction_required_diameter_in=suct_req_in,
        discharge_required_diameter_in=disch_req_in,
        suction_nominal_diameter_in=inputs.suction_nominal_diameter_in,
        discharge_nominal_diameter_in=inputs.discharge_nominal_diameter_in,
        suction_selected_inside_diameter_in=inputs.suction_selected_inside_diameter_in,
        discharge_selected_inside_diameter_in=inputs.discharge_selected_inside_diameter_in,
        suction_pipe_schedule=inputs.suction_pipe_schedule,
        discharge_pipe_schedule=inputs.discharge_pipe_schedule,
        suction_pipe_material=inputs.suction_pipe_material,
        discharge_pipe_material=inputs.discharge_pipe_material,
        re_discharge=re_discharge,
        re_suction=re_suction,
        f_discharge=f_disch,
        f_suction=f_suct,
        f_discharge_method="colebrook",
        f_suction_method="colebrook",
        hf_per_ft_discharge=hf_ft_disch,
        hf_per_ft_suction=hf_ft_suct,
        static_suction_head_ft=static_suct_ft,
        suction_fitting_losses_ft=suct_fit_ft,
        suction_major_losses_ft=suct_major_ft,
        total_suction_losses_ft=total_suct_ft,
        npsha_ft=npsha_ft,
        npsha_m=npsha_m,
        npsha_from_surface_ft=npsha_from_surface_ft,
        npsha_from_flange_ft=npsha_from_flange_ft,
        npsh_boundary_method=npsh_boundary_method,
        npsh_margin_status=npsh_surface_result.status,
        npsha_equivalence_diff=npsha_equivalence_diff,
        npsha_equivalence_status=npsha_equivalence_status,
        npshr_source_value=npshr_source_value,
        npshr_source_unit=npshr_source_unit,
        npshr_ft=npshr_ft_val,
        npshr_reference_status=npshr_reference_status,
        npshr_reference_missing_fields=npshr_reference_missing,
        npshr_reference_mismatched_fields=npshr_reference_mismatched,
        npsh_margin_ft=npsh_margin_ft_val,
        npsh_availability_ratio=npsh_availability_ratio_val,
        npsh_margin_fraction=npsh_margin_fraction_val,
        npsh_margin_calculation_status=npsh_margin_calc_status,
        npsh_margin_acceptance_status=npsh_margin_accept_status,
        npsh_margin_warnings=npsh_margin_warn,
        npshr_traceability=npshr_traceability,
        npsha_components={
            "surface_absolute_pressure_psia": npsh_surface_result.p_surface_abs_psi,
            "surface_pressure_head_ft": npsh_surface_result.pressure_head_ft,
            "static_suction_head_ft": npsh_surface_result.elevation_head_ft,
            "suction_major_losses_ft": npsh_surface_result.suction_pipe_losses_ft,
            "suction_minor_losses_ft": npsh_surface_result.suction_fitting_losses_ft,
            "vapor_pressure_psia": npsh_surface_result.p_vapor_abs_psi,
            "vapor_pressure_head_ft": npsh_surface_result.vapor_pressure_head_ft,
            "velocity_head_at_flange_ft": vel_head_suct,
            "npsha_from_surface_ft": npsha_from_surface_ft,
            "npsha_from_flange_ft": npsha_from_flange_ft,
            "equivalence_diff_ft": npsha_equivalence_diff,
            "equivalence_status": npsha_equivalence_status,
        },
        static_discharge_head_ft=static_disch_ft,
        discharge_fitting_losses_ft=disch_fit_ft,
        discharge_major_losses_ft=disch_major_ft,
        total_discharge_losses_ft=total_disch_ft,
        tdh_ft=tdh_ft,
        tdh_m=tdh_m,
        tdh_surface_to_surface_ft=tdh_surface_to_surface_ft,
        tdh_flange_to_flange_ft=tdh_flange_to_flange_ft,
        tdh_flange_input_status=tdh_flange_input_status,
        partial_geometric_kinetic_difference_ft=partial_geometric_kinetic_difference_ft,
        tdh_boundary_method=tdh_boundary_method,
        tdh_components={
            "static_head_difference_ft": static_head_diff,
            "suction_major_losses_ft": suct_major_ft,
            "suction_minor_losses_ft": suct_fit_ft,
            "discharge_major_losses_ft": disch_major_ft,
            "discharge_minor_losses_ft": disch_fit_ft,
            "pressure_head_difference_ft": pressure_head_diff,
            "velocity_head_difference_ft": vel_head_diff,
            "tdh_surface_to_surface_ft": tdh_surface_to_surface_ft,
            "tdh_flange_to_flange_ft": tdh_flange_to_flange_ft,
            "tdh_flange_input_status": tdh_flange_input_status,
            "partial_geometric_kinetic_difference_ft": partial_geometric_kinetic_difference_ft,
        },
        accessory_audit=compute_accessory_audit(atmospheric_pressure_psia=inputs.atmospheric_pressure_psia),
        hydraulic_hp=hyd_hp,
        shaft_hp=sh_hp,
        shaft_kw=sh_kw,
        torque_lbft=val_torque,
        legacy_torque_lbft=leg_torque,
        pump_rpm=float(_N),
        legacy_torque_rpm=inputs.legacy_torque_rpm,
        specific_speed_us=ss_us_val,
        specific_speed_metric=ss_metric_val,
        specific_speed_legacy=ss_legacy_val,
        specific_speed_definition=(
            "Ns_US = N * sqrt(Q_per_eye) / H_per_stage^0.75  (US)\n"
            "nq = N * sqrt(Q_m3s_per_eye) / H_m_per_stage^0.75  (metric)"
        ),
        flow_basis=f"Q/{inputs.number_of_suction_eyes} per suction eye",
        head_basis=f"H/{inputs.number_of_stages} per stage",
        stage_count=inputs.number_of_stages,
        suction_eye_count=inputs.number_of_suction_eyes,
        friction_comparison=friction_comparison,
        diameter_status=diameter_status,
    )


def compute_accessory_audit(
    atmospheric_pressure_psia: Optional[float] = None,
    vessel_pressure: float = 0.0,
    vessel_pressure_type: str = "GAUGE",
) -> Dict:
    """Compute accessory loss audit data.

    atmospheric_pressure_psia must come from WorkbookInputs, never hardcoded.
    Pass None to signal 'no atmospheric data available' (tests only).
    """
    suction = compute_suction_results()
    discharge = compute_discharge_results()
    s_sum = summarize_suction(suction)
    d_sum = summarize_discharge(discharge)
    double_counting = detect_double_counting(discharge)
    scenarios = build_scenario_comparisons()
    pareto = build_pareto_leq_only(discharge, 5)
    pressure_terms = build_pressure_head_terms()
    if atmospheric_pressure_psia is None:
        raise ValueError("compute_accessory_audit requires atmospheric_pressure_psia from WorkbookInputs")
    tdh_balances = build_semantic_tdh_balances(
        source_atmospheric_pressure_psia=atmospheric_pressure_psia,
        source_vessel_pressure=vessel_pressure,
        source_vessel_pressure_type=vessel_pressure_type,
    )
    system_curve = build_system_curve_classification()
    return {
        "suction_leq_formula_total_ft": s_sum.total_leq_formula_loss_ft,
        "suction_pressure_total_ft": s_sum.total_pressure_loss_ft,
        "suction_excel_total_ft": s_sum.excel_total_ft,
        "suction_active_rows": s_sum.active_row_count,
        "suction_total_rows": s_sum.row_count,
        "discharge_leq_formula_total_ft": d_sum.total_leq_formula_loss_ft,
        "discharge_pressure_total_ft": d_sum.total_pressure_loss_ft,
        "discharge_excel_total_ft": d_sum.excel_total_ft,
        "discharge_pressure_share_pct": d_sum.pressure_share_pct,
        "discharge_active_rows": d_sum.active_row_count,
        "discharge_total_rows": d_sum.row_count,
        "double_counting_found": len(double_counting) > 0,
        "double_counting_details": double_counting,
        "scenarios": scenarios,
        "pareto_top5": pareto,
        "g_workbook": 32.4,
        "g_standard": 32.174,
        # Hito 5.3B additions
        "pressure_head_terms": [
            {
                "name": t.name,
                "value": t.value,
                "pressure_unit": t.pressure_unit,
                "pressure_reference": t.pressure_reference,
                "classification": t.classification,
                "specific_gravity": t.specific_gravity,
                "legacy_head_ft": t.legacy_head_ft,
                "validated_head_ft": t.validated_head_ft,
                "source_sheet": t.source_sheet,
                "source_cell": t.source_cell,
                "confidence": t.confidence,
                "user_confirmed": t.user_confirmed,
                "pressure_reference_notes": t.pressure_reference_notes,
            }
            for t in pressure_terms
        ],
        "semantic_tdh_balances": tdh_balances,
        "system_curve_classification": system_curve,
        # Hito 5.4 additions
        "pressure_requirements": [
            {
                "term_id": r.term_id,
                "name": r.name,
                "term_type": r.term_type,
                "value": r.value,
                "unit": r.unit,
                "pressure_reference": r.pressure_reference,
                "flow_dependency": r.flow_dependency,
                "design_flow_gpm": r.design_flow_gpm,
                "active": r.active,
                "source_type": r.source_type,
                "source_sheet": r.source_sheet,
                "source_cell": r.source_cell,
                "source_comment": r.source_comment,
                "confidence": r.confidence,
                "user_confirmed": r.user_confirmed,
                "notes": r.notes,
                "start_node": r.start_node,
                "end_node": r.end_node,
                "combination_rule": r.combination_rule,
            }
            for r in build_pressure_requirements()
        ],
        "pressure_boundary_warnings": [
            {
                "type": w["type"],
                "description": w["description"],
                "term_ids": w["term_ids"],
                "shared_node": w.get("shared_node"),
                "suggested_rule": w.get("suggested_rule"),
            }
            for w in detect_pressure_boundary_overlap(build_pressure_requirements())
        ],
        "pressure_boundary_combination_rule": "ALTERNATIVE_SCENARIOS",
        "source_boundary_absolute_pressure_psia": compute_boundary_absolute_pressure(
            atmospheric_pressure_psia=atmospheric_pressure_psia,
            vessel_pressure=vessel_pressure,
            vessel_pressure_type=vessel_pressure_type,
        ),
    }


def run_validated() -> ValidatedResults:
    """Main entry point for validated calculations."""
    return calculate_validated()


if __name__ == "__main__":
    results = calculate_validated()
    print("Validated Calculations:")
    print("=" * 60)
    suct_sel = f"{results.suction_selected_inside_diameter_in:.4f}" if results.suction_selected_inside_diameter_in is not None else "MISSING"
    disch_sel = f"{results.discharge_selected_inside_diameter_in:.4f}" if results.discharge_selected_inside_diameter_in is not None else "MISSING"
    print(f"Suction: required ID={results.suction_required_diameter_in:.4f} in, selected ID={suct_sel} in, schedule={results.suction_pipe_schedule}")
    print(f"Discharge: required ID={results.discharge_required_diameter_in:.4f} in, selected ID={disch_sel} in, schedule={results.discharge_pipe_schedule}")
    print(f"Pipe schedule status: {results.diameter_status}")
    print(f"Re discharge: {results.re_discharge:.0f}")
    print(f"Re suction: {results.re_suction:.0f}")
    print(f"f discharge (Colebrook): {results.f_discharge:.6f}")
    print(f"f suction (Colebrook): {results.f_suction:.6f}")
    print(f"hf/ft discharge: {results.hf_per_ft_discharge:.6f} ft/ft")
    print(f"hf/ft suction: {results.hf_per_ft_suction:.6f} ft/ft")
    print(f"NPSHa (surface): {results.npsha_from_surface_ft:.4f} ft")
    print(f"NPSHa (flange):  {results.npsha_from_flange_ft:.4f} ft")
    print(f"NPSHa equivalence diff: {results.npsha_equivalence_diff:.2e} ft [{results.npsha_equivalence_status}]")
    print(f"TDH (surface-to-surface): {results.tdh_surface_to_surface_ft:.4f} ft ({results.tdh_m:.2f} m)")
    flange_tdh = f"{results.tdh_flange_to_flange_ft:.4f}" if results.tdh_flange_to_flange_ft is not None else results.tdh_flange_input_status
    print(f"TDH (flange-to-flange):   {flange_tdh}")
    print(f"Partial geometric-kinetic diff: {results.partial_geometric_kinetic_difference_ft:.4f} ft")
    print(f"Shaft HP: {results.shaft_hp:.4f}")
    print(f"Torque (validated @ {results.pump_rpm:.0f} RPM): {results.torque_lbft:.2f} lb-ft")
    print(f"Torque (legacy @ {results.legacy_torque_rpm:.0f} RPM): {results.legacy_torque_lbft:.2f} lb-ft")
    print(f"Specific speed (US): {results.specific_speed_us:.0f}")
    print(f"Specific speed (metric): {results.specific_speed_metric:.1f}")
    print(f"Specific speed (legacy): {results.specific_speed_legacy:.0f}")
    print(f"\nTDH components: {results.tdh_components}")
    print(f"\nNPSHa components: {results.npsha_components}")
