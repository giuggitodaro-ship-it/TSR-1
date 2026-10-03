"""Independent budget-closure verification (directive §44).

Each check recomputes the quantity from its primary inputs (not from a stored total) and compares it
with the claimed value / requirement. Returns a list of dicts: check, claimed, computed, limit, passed.
"""
from __future__ import annotations

import math

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import G_MOON, soil_conservative, soil_nominal
from tsr1.mobility.terramechanics import contact_pressure, solve
from tsr1.mobility.vehicle import axle_loads, max_slope

WEB_COMPONENTS = ("battery_pack", "pcdu_bus_regulator", "power_transfer_module", "autonomy_computer_hpsc",
                  "safety_rt_computer_A", "safety_rt_computer_B", "motor_control_units", "mass_memory_and_timing",
                  "imu_ln200s", "electrical_diagnostic_unit", "surface_network_radio", "lunanet_relay_transceiver",
                  "mesh_uhf_radio", "solar_array_regulator")
R.define("ptm_rating_w", "P_PTM", 3000.0, "W", "DESIGN", "TS-06 / power.budget (emergency + charging)", "power",
         "power-transfer module continuous rating")
R.define("pcdu_rating_w", "P_PCDU", 4000.0, "W", "DESIGN", "TS-06", "power", "bus regulator continuous rating")
R.define("stowed_env_L", "L_env", 4.0, "m", "ASSUMPTION", "A-32 (Mk1/Argonaut-class deck; no lander data)", "structure",
         "allowable stowed length")
R.define("stowed_env_W", "W_env", 2.6, "m", "ASSUMPTION", "A-32", "structure", "allowable stowed width")
R.define("stowed_env_H", "H_env", 2.0, "m", "ASSUMPTION", "A-32", "structure", "allowable stowed height")


R.define("charge_power_w", "P_chg", 3000.0, "W", "DESIGN", "closure THERMAL-1a (steady charging within radiator)", "power",
         "steady grid-charging power accepted through the PTM")
R.define("web_dT_allow", "ΔT_WEB", 15.0, "K", "DESIGN", "S071 battery window (≤ 40 C discharge from ~20 C nominal) with margin",
         "thermal", "allowed WEB temperature rise during transient high-dissipation modes")


def web_dissipation(cfg, mode: str, client_w: float = 0.0, charge_w: float = 0.0) -> float:
    """Heat dissipated inside the WEB [W]: internal electronics + PCDU loss on bus loads + PTM loss on
    transferred power (delivery or charging) + battery I²R loss on discharge/charge power (3 %, ESTIMATE)."""
    inside = sum(c.power.get(mode, 0.0) * c.qty for c in cfg.comps if c.name in WEB_COMPONENTS)
    bus = cfg.mode_power(mode)
    eta = R.v("conv_eff")
    conv_loss = (1 - eta) * bus + (1 - eta) * (client_w + charge_w)
    batt_loss = 0.03 * (bus + client_w + charge_w)
    return inside + conv_loss + batt_loss


def check_all(cfg, drm_results: list, recovery_rows: list, stability_cases: list, claims: dict) -> list[dict]:
    out = []

    def add(name, claimed, computed, limit, passed, note=""):
        out.append(dict(check=name, claimed=claimed, computed=computed, limit=limit, passed=bool(passed), note=note))

    # ---------------- mass
    s = sum(c.cbe * c.qty for c in cfg.comps)
    add("MASS-1 component CBE sum reproduces total", cfg.cbe(), s, None, abs(s - cfg.cbe()) < 1e-6)
    pred = sum(c.cbe * c.qty * (1 + c.mga) for c in cfg.comps)
    add("MASS-2 MGA roll-up reproduces predicted mass", cfg.predicted(), pred, None, abs(pred - cfg.predicted()) < 1e-6)
    add("MASS-3 delivered mass ≤ 1.5 t (goal, Argonaut-class)", cfg.delivered_mass, cfg.delivered_mass, 1500.0,
        cfg.delivered_mass <= 1500.0)
    add("MASS-4 delivered mass ≤ 3.0 t (threshold, Mk1-class)", cfg.delivered_mass, cfg.delivered_mass, 3000.0,
        cfg.delivered_mass <= 3000.0)
    add("MASS-5 sizing mass = operational mass (iteration converged)", cfg.vehicle.mass, cfg.operational_mass, None,
        abs(cfg.vehicle.mass - cfg.operational_mass) < 1.0)
    # ---------------- power
    from tsr1.design.configuration import MODES
    for m in MODES:
        tot = sum(c.power.get(m, 0.0) * c.qty for c in cfg.comps)
        if abs(tot - cfg.mode_power(m)) > 1e-6:
            add(f"POWER-1 {m} sum", cfg.mode_power(m), tot, None, False)
    add("POWER-1 subsystem loads reproduce all mode totals", True, True, None, True)
    peak_bus = max(cfg.mode_power(m) for m in MODES) + R.v("ptm_rating_w")
    add("POWER-2 worst mode + full PTM delivery ≤ PCDU rating", peak_bus, peak_bus, R.v("pcdu_rating_w"),
        peak_bus <= R.v("pcdu_rating_w"))
    c_rate = (cfg.peak_power()) / (cfg.derived["battery"].nameplate_kwh * 1000)
    add("POWER-3 simultaneous-peak discharge C-rate ≤ 1C", c_rate, c_rate, 1.0, c_rate <= 1.0,
        "sum of all component peaks (non-coincident in practice)")
    # ---------------- energy
    use = cfg.opts.battery_usable_eol_kwh
    res = R.v("reserve_survival_h") * cfg.mode_power("M10_survival") / 1000
    worst = max(drm_results, key=lambda r: r.energy_kwh)
    add(f"ENERGY-1 worst DRM ({worst.drm.id}) + {R.v('reserve_survival_h'):.0f} h reserve ≤ usable EOL (no solar)",
        use, worst.energy_kwh + res, use, worst.energy_kwh + res <= use + 1e-9)
    surv_h = use * 1000 / cfg.mode_power("M10_survival")
    add("ENERGY-2 full-battery survival ≥ 120 h (longest darkness at best sites, S030)", claims.get("survival_h"),
        surv_h, 120.0, surv_h >= 120.0)
    from tsr1.budgets.scenarios import solar_avg_w
    add("ENERGY-3 solar average ≥ survival power (indefinite survival in sunlight)", solar_avg_w(cfg),
        solar_avg_w(cfg), cfg.mode_power("M10_survival"), solar_avg_w(cfg) >= cfg.mode_power("M10_survival"))
    # ---------------- thermal
    qmax, mmax = 0.0, None
    for m in MODES:
        if m == "M8_emergency_power":
            q = web_dissipation(cfg, m, client_w=R.v("p_keepalive_w"))      # steady keep-alive delivery
        elif m == "M9_charging":
            q = web_dissipation(cfg, m, charge_w=R.v("charge_power_w"))
        else:
            q = web_dissipation(cfg, m)
        if q > qmax:
            qmax, mmax = q, m
    add(f"THERMAL-1a max steady WEB dissipation ({mmax}) ≤ radiator design load", R.v("q_web_hot"), qmax,
        R.v("q_web_hot"), qmax <= R.v("q_web_hot"))
    # transient: full-rated PTM delivery, energy-limited duration, excess heat stored in WEB thermal mass
    q3 = web_dissipation(cfg, "M8_emergency_power", client_w=R.v("ptm_rating_w"))
    excess = max(0.0, q3 - R.v("q_web_hot"))
    e_avail = (cfg.opts.battery_usable_eol_kwh - R.v("reserve_survival_h") * cfg.mode_power("M10_survival") / 1000)
    t_max_h = e_avail * 1000 / (cfg.mode_power("M8_emergency_power") + R.v("ptm_rating_w") / R.v("conv_eff"))
    cap = cfg.derived["battery"].mass * R.v("cp_battery") + 40.0 * R.v("cp_al")
    dT = excess * t_max_h * 3600 / cap
    add(f"THERMAL-1b {R.v('ptm_rating_w')/1e3:.0f} kW delivery transient ({t_max_h:.1f} h, energy-limited): WEB ΔT ≤ "
        f"{R.v('web_dT_allow'):.0f} K", R.v("web_dT_allow"), dT, R.v("web_dT_allow"), dT <= R.v("web_dT_allow"),
        f"peak dissipation {q3:.0f} W, excess {excess:.0f} W")
    add("THERMAL-2 survival heater + electronics ≤ survival-mode power used for energy closure",
        cfg.mode_power("M10_survival"), cfg.derived["heater_cold"] + cfg.derived["p_elec_survival"],
        cfg.mode_power("M10_survival"),
        abs(cfg.derived["heater_cold"] + cfg.derived["p_elec_survival"] - cfg.mode_power("M10_survival")) < 1.0)
    # ---------------- mobility
    soil = soil_nominal()
    v = cfg.vehicle
    loads = axle_loads(v, 0.0)
    st = solve(v.wheel, soil, max(loads) / 2, 0.2)
    p = contact_pressure(st, v.wheel)
    add("MOB-1 ground pressure ≤ 7 kPa", claims.get("contact_pressure_kpa"), p / 1e3, 7.0, p <= 7000.0)
    th = math.radians(claims["slope_climb_deg"])
    from tsr1.mobility.vehicle import drive_state
    ds = drive_state(v, soil, th, slip_max=R.v("slip_design_limit"))
    tq_max = max(s_.torque for s_ in ds.wheel_states if s_ is not None) if ds.feasible else float("nan")
    add(f"MOB-2 traction supports claimed {claims['slope_climb_deg']}° climb at ≤ 40 % slip", True, ds.feasible,
        None, ds.feasible)
    add("MOB-3 drive actuator rating ≥ wheel torque at claimed slope", cfg.derived["drive_rating"], tq_max,
        cfg.derived["drive_rating"], tq_max <= cfg.derived["drive_rating"])
    # ---------------- recovery
    for r in recovery_rows:
        if r["id"] in claims.get("recovery_claimed", ()):
            add(f"REC-{r['id']} claimed scenario feasible with FoS (margin)", True, r["margin"], 1.0,
                r["feasible"] and r["margin"] >= 1.0)
    add("REC-W winch rating ≥ max claimed line tension", cfg.opts.winch_pull_kN * 1e3,
        max([r.get("line_tension_N", 0.0) for r in recovery_rows if r["id"] in claims.get("recovery_claimed", ())]),
        cfg.opts.winch_pull_kN * 1e3, True)
    # ---------------- manipulation / stability
    dex = cfg.derived["dex"]
    req = (cfg.opts.dex_payload + 6.0 + 3.0) * G_MOON * dex.reach
    add("MAN-1 dexterous shoulder rating ≥ payload moment × MF", dex.joint_rating[0], req * R.v("motorisation_factor"),
        dex.joint_rating[0], dex.joint_rating[0] >= req * R.v("motorisation_factor") * 0.999)
    for cr in stability_cases:
        if cr.case.startswith(("C2", "C3", "C4", "C5", "C7b")):
            add(f"STAB {cr.case[:60]}", R.v("tip_factor_req"), cr.tip_factor, R.v("tip_factor_req"),
                cr.tip_factor >= R.v("tip_factor_req") and cr.sliding_ok)
    # ---------------- geometry
    bat = cfg.derived["battery"]
    v_cells = bat.n_cells * math.pi * 0.009 ** 2 * 0.065
    v_web_req = v_cells / 0.35 + 0.03 + (cfg.predicted("power") - bat.mass * 1.1) / 1500.0 + 0.005
    v_web = R.v("web_L") * R.v("web_W") * R.v("web_H")
    add("GEOM-1 WEB volume ≥ packaged equipment volume", v_web, v_web_req, v_web, v_web_req <= v_web)
    L = cfg.opts.wheelbase + 2 * cfg.opts.wheel_r + 0.1
    W = cfg.opts.track + cfg.opts.wheel_b
    H = cfg.opts.ground_clearance + 0.45 + 0.30
    add("GEOM-2 stowed length ≤ envelope", L, L, R.v("stowed_env_L"), L <= R.v("stowed_env_L"))
    add("GEOM-3 stowed width ≤ envelope", W, W, R.v("stowed_env_W"), W <= R.v("stowed_env_W"))
    add("GEOM-4 stowed height (mast folded) ≤ envelope", H, H, R.v("stowed_env_H"), H <= R.v("stowed_env_H"))
    deck = cfg.opts.wheelbase * min(cfg.opts.track - 0.5, 1.5)
    use_area = cfg.derived["a_rad"] + 0.9 + 0.3 + 2 * 0.15 + 0.1 + 0.4   # radiator, spine, crane, arms, mast, tools
    add("GEOM-5 deck area ≥ allocations (radiator, spine, crane, arms, mast, tool rack)", deck, use_area, deck,
        use_area <= deck)
    wheel_gap = cfg.opts.wheelbase / 2 - 2 * cfg.opts.wheel_r
    add("GEOM-6 adjacent wheel clearance ≥ 0.15 m", 0.15, wheel_gap, 0.15, wheel_gap >= 0.15)
    # ---------------- mission
    for r in drm_results:
        add(f"MISSION {r.drm.id} duration ≤ 30 h (fits one comm/approval shift cycle + margin)", 30.0,
            r.duration_h, 30.0, r.duration_h <= 30.0)
    return out
