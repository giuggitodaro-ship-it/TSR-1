"""TSR-1 master simulation runner.

Reproduces every analysis result of the study from the configuration in
``simulations/configs/run_config.json``:

    PYTHONPATH=src python simulations/run_all.py            # full run
    PYTHONPATH=src python simulations/run_all.py --quick    # reduced Monte Carlo sizes (smoke test)

Outputs (all regenerated):
    simulations/results/*.json, *.csv          analysis results
    simulations/results/design_values.json     values consumed by requirements/build_requirements.py
    engineering/parameter_register.csv         central parameter register
    engineering/mass_budget.csv                bottom-up mass budget
    engineering/power_budget.csv               component × mode power budget
    requirements/*.md, requirements_traceability.csv (regenerated)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tsr1.common.params import REGISTRY as R  # noqa: E402
from tsr1.environment import lunar  # noqa: E402
from tsr1.design.configuration import MODES, Options, build  # noqa: E402
from tsr1.mobility.terramechanics import Wheel, contact_pressure, dp_curve, solve  # noqa: E402
from tsr1.mobility.vehicle import (drive_state, lrv_calibration, max_slope, max_tow_force,  # noqa: E402
                                   wheel_energy_per_m)
import tsr1.reliability.value_model as VM  # noqa: E402
from tsr1.reliability.servicing import LEVELS, TASKS, success_distribution, success_table  # noqa: E402
from tsr1.reliability.tsr_reliability import simulate_tsr  # noqa: E402
from tsr1.budgets import scenarios as SC  # noqa: E402
from tsr1.budgets.closure import check_all, web_dissipation  # noqa: E402
from tsr1.budgets.sensitivity import mass_monte_carlo, override, tornado  # noqa: E402
from tsr1.stability.envelope import case_results, crane_capacity_curve, static_tip_angles  # noqa: E402
from tsr1.recovery import scenarios as RS  # noqa: E402
from tsr1.recovery.towing import helical_anchor_capacity, restraint_capacity, Restraint  # noqa: E402
from tsr1.trades import mobility_trades as TM, manipulator_trades as TMAN, recovery_trades as TR  # noqa: E402
from tsr1.trades import other_trades as TO  # noqa: E402
from tsr1.thermal.lumped import survival as thermal_survival  # noqa: E402

RES = ROOT / "simulations" / "results"
RES.mkdir(parents=True, exist_ok=True)


def jdump(name, obj):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if hasattr(o, "__dataclass_fields__"):
            return {k: conv(v) for k, v in asdict(o).items()}
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(v) for v in o]
        if isinstance(o, float) and (math.isinf(o) or math.isnan(o)):
            return str(o)
        return o
    (RES / name).write_text(json.dumps(conv(obj), indent=1))


def csv_dump(name, rows: list[dict]):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(RES / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (float(v) if isinstance(v, np.floating) else v) for k, v in r.items()})


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main(quick: bool = False):
    cfgfile = json.loads((ROOT / "simulations" / "configs" / "run_config.json").read_text())
    mc = cfgfile["quick" if quick else "full"]
    t0 = time.time()
    # ------------------------------------------------------------------ baseline
    log("building baseline configuration")
    base_opts = Options(**cfgfile["baseline_options"])
    cfg = build(base_opts)
    k_cal = lrv_calibration()
    sn, scn, sw = lunar.soil_nominal(), lunar.soil_conservative(), lunar.soil_weak()
    v = cfg.vehicle
    dv = {}            # design values for requirements

    # ------------------------------------------------------------------ mobility
    log("mobility analysis")
    wl = v.weight / v.n_wheels
    st20 = solve(v.wheel, sn, wl, 0.2)
    slopes = dict(nominal=max_slope(v, sn), conservative=max_slope(v, scn), weak=max_slope(v, sw),
                  one_wheel_out=max_slope(v, sn, failed_wheels=1), two_wheels_out=max_slope(v, sn, failed_wheels=2),
                  nominal_20pct=max_slope(v, sn, slip_limit=0.2))
    slopes = {k: math.degrees(x) for k, x in slopes.items()}
    e_wheel = wheel_energy_per_m(v, sn) / 3.6
    curves = {}
    for nm, s in (("nominal", sn), ("conservative", scn), ("weak", sw)):
        sl, dp = dp_curve(v.wheel, s, wl)
        curves[nm] = dict(slip=sl, dp_over_w=dp / wl)
    slope_power = []
    for d in range(0, 21, 2):
        ds = drive_state(v, sn, math.radians(d))
        p = (k_cal * ds.torque_total * R.v("v_drive_nom") / (v.wheel.r_shear * (1 - ds.slip)) / v.drive_eff
             if ds.feasible else float("nan"))
        slope_power.append(dict(slope_deg=d, slip=ds.slip if ds.feasible else float("nan"), drive_power_W=p))
    tow = [dict(slope_deg=d, nominal_N=max_tow_force(v, sn, math.radians(d)),
                conservative_N=max_tow_force(v, scn, math.radians(d))) for d in range(0, 21, 5)]
    mob = dict(k_cal=k_cal, wheel_load_N=wl, sinkage_m=st20.sinkage, contact_pressure_kPa=contact_pressure(st20, v.wheel) / 1e3,
               slopes_deg=slopes, wheel_energy_Wh_per_km=e_wheel, calibrated_wheel_energy_Wh_per_km=e_wheel * k_cal,
               dp_curves=curves, slope_power=slope_power, tow_capacity=tow,
               drive_rating_Nm=cfg.derived["drive_rating"], drive_torque_soil_Nm=cfg.derived["drive_torque_soil"])
    jdump("mobility.json", mob)
    R.calc("slope_max_nominal", "θ_max,nom", slopes["nominal"], "deg", "mobility.vehicle.max_slope (nominal soil, i<=0.4)", "mobility")
    R.calc("slope_max_conservative", "θ_max,cons", slopes["conservative"], "deg", "mobility.vehicle.max_slope (conservative soil)", "mobility")
    R.calc("contact_pressure", "p", mob["contact_pressure_kPa"] * 1e3, "Pa", "terramechanics.contact_pressure", "mobility")

    # ------------------------------------------------------------------ stability
    log("stability analysis")
    cases = case_results(cfg)
    tip = static_tip_angles(cfg)
    crane_curve = crane_capacity_curve(cfg)
    crane_curve_slope = crane_capacity_curve(cfg, slope_y=math.radians(-15))
    jdump("stability.json", dict(cases=cases, static_tip_angles_deg=tip, crane_capacity_level=crane_curve,
                                 crane_capacity_15deg=crane_curve_slope))

    # ------------------------------------------------------------------ recovery
    log("recovery analysis")
    rng = np.random.default_rng(cfgfile["seeds"]["recovery_cases"])
    rcases = TR.sample_cases(mc["recovery_cases"], rng)
    p_env = {k: dict(mid=TR.envelope_probability(cfg, k, rcases),
                     low=TR.envelope_probability(cfg, k, rcases, bound="low"),
                     high=TR.envelope_probability(cfg, k, rcases, bound="high"),
                     weak_soil=TR.envelope_probability(cfg, k, rcases, strength_factor=0.5))
             for k in TR.RESTRAINTS}
    rcurves = TR.recovery_curves(cfg)
    rscen = RS.analyse(cfg)
    stab_opts = TR.stabilisation_options(cfg)
    winch_sweep = [dict(winch_kN=w, p_env=TR.envelope_probability(cfg, "R4 winch + 2 spades + 2 helical anchors",
                                                                   rcases, winch_kN=w)) for w in (1, 2, 3, 4, 5, 6)]
    jdump("recovery.json", dict(p_env=p_env, curves=rcurves, scenarios=rscen, stabilisation=stab_opts,
                                winch_sweep=winch_sweep, restraint_mass=TR.RESTRAINT_MASS))
    csv_dump("recovery_scenarios.csv", rscen)
    p_env_base = p_env["R4 winch + 2 spades + 2 helical anchors"]["mid"]

    # ------------------------------------------------------------------ power / energy / thermal
    log("power, energy and thermal analysis")
    drms = SC.drm_library(cfg, R.v("service_radius_km"))
    drm_res = [SC.evaluate(cfg, d) for d in drms]
    mode_tab = {m: cfg.mode_power(m) for m in MODES}
    web_q = {m: web_dissipation(cfg, m, R.v("ptm_rating_w") if m == "M8_emergency_power" else 0.0) for m in MODES}
    batt_radius = TO.battery_vs_radius(lambda: cfg)
    surv_w = cfg.mode_power("M10_survival")
    use = cfg.opts.battery_usable_eol_kwh
    res_kwh = R.v("reserve_survival_h") * surv_w / 1000
    # emergency keep-alive duration at the service edge
    d = R.v("service_radius_km")
    e_drive_km = (R.v("drive_duty") * mode_tab["M3_driving"] + (1 - R.v("drive_duty")) * mode_tab["M4_inspection"]) \
        / R.v("tsr_speed_eff") / 1000
    keep = R.v("p_keepalive_w")
    p_m8 = mode_tab["M8_emergency_power"] + keep / R.v("conv_eff")
    t_keep = (use - res_kwh - 2 * d * e_drive_km) * 1000 / p_m8
    t_3kw = (use - res_kwh - 2 * d * e_drive_km) * 1000 / (mode_tab["M8_emergency_power"] + 3000 / R.v("conv_eff"))
    rng_km = (use - res_kwh) / e_drive_km
    th = thermal_survival(cfg.derived["a_mli"], cfg.derived["a_rad"], cfg.derived["p_elec_survival"], use,
                          cfg.derived["battery"].mass * R.v("cp_battery") + 40 * R.v("cp_al"),
                          p_ops_internal=web_q["M5_manipulation"])
    psr_energy_h = (use - res_kwh - 2 * 5.0 * e_drive_km) * 1000 / (mode_tab["M5_manipulation"] + 20.0)
    energy = dict(mode_power_W=mode_tab, web_dissipation_W=web_q, peak_sum_W=cfg.peak_power(),
                  drms=[dict(id=r.drm.id, title=r.drm.title, duration_h=r.duration_h, distance_km=r.distance_km,
                             energy_kwh=r.energy_kwh, energy_with_solar_kwh=r.energy_solar_kwh, peak_W=r.peak_w,
                             tools=r.drm.tools, crew=r.drm.crew_involvement, risks=r.drm.risks,
                             branches=r.drm.branches, phases=r.phase_energy) for r in drm_res],
                  battery=cfg.derived["battery"], reserve_kwh=res_kwh, survival_power_W=surv_w,
                  survival_full_battery_h=use * 1000 / surv_w, keepalive_duration_at_edge_h=t_keep,
                  emergency_3kW_duration_at_edge_h=t_3kw, range_km=rng_km, energy_per_km_kwh=e_drive_km,
                  battery_vs_radius=batt_radius, solar_avg_W=SC.solar_avg_w(cfg), thermal=th,
                  psr_excursion_energy_limited_h=psr_energy_h, tether=cfg.derived["tether"],
                  energy_alternatives=TO.energy_alternatives(cfg))
    jdump("energy_power_thermal.json", energy)

    # ------------------------------------------------------------------ TSR self reliability
    log("TSR self-reliability")
    rel = dict(crew_repair=simulate_tsr(n_runs=mc["tsr_rel_runs"], repair_days=30.0),
               slow_repair=simulate_tsr(n_runs=mc["tsr_rel_runs"], repair_days=120.0),
               peer=simulate_tsr(n_runs=mc["tsr_rel_runs"], peer=True),
               no_repair=simulate_tsr(n_runs=mc["tsr_rel_runs"], p_spare_tsr=0.0))
    jdump("tsr_reliability.json", rel)

    # ------------------------------------------------------------------ servicing success
    log("servicing success distributions")
    srv = {t: {L: dict(zip(("p10", "p50", "p90"),
                           np.percentile(success_distribution(t, L, n=mc["servicing_samples"]), [10, 50, 90])))
               for L in LEVELS} for t in TASKS}
    srv_crew = {t: {L: dict(zip(("p10", "p50", "p90"),
                                np.percentile(success_distribution(t, L, "crew", n=mc["servicing_samples"]),
                                              [10, 50, 90]))) for L in LEVELS} for t in TASKS}
    jdump("servicing_success.json", dict(robot=srv, crew=srv_crew))

    # ------------------------------------------------------------------ value model
    log("value model Monte Carlo")
    vcfg = cfgfile["value_model"]
    sc_base = VM.Scenario(n_assets=vcfg["ref_assets"], keepalive_modules=vcfg["keepalive_modules"],
                          recovery_envelope_p=p_env_base)
    mc_base = VM.monte_carlo(sc_base, n=mc["value_runs"], seed=cfgfile["seeds"]["value"])
    sweep = []
    for N in vcfg["asset_sweep"]:
        r = VM.monte_carlo(replace(sc_base, n_assets=N), n=mc["value_runs_sweep"], seed=cfgfile["seeds"]["value"] + N)
        sweep.append(dict(n_assets=N, **{f"{k}_mean": float(np.mean(r[k])) for k in r},
                          **{f"{k}_p10": float(np.percentile(r[k], 10)) for k in ("dA", "mass0", "mass1")},
                          **{f"{k}_p90": float(np.percentile(r[k], 90)) for k in ("dA", "mass0", "mass1")}))
    level_mixes = {"legacy (L0-heavy)": (0.5, 0.3, 0.15, 0.05), "mixed (baseline)": (0.20, 0.30, 0.35, 0.15),
                   "standardised (L2/L3)": (0.05, 0.10, 0.45, 0.40)}
    mixes = []
    for nm, mix in level_mixes.items():
        r = VM.monte_carlo(replace(sc_base, level_mix=mix), n=mc["value_runs_sweep"], seed=cfgfile["seeds"]["value"] + 7)
        mixes.append(dict(level_mix=nm, **{f"{k}_mean": float(np.mean(r[k])) for k in r}))
    ka = []
    for k in (0, 1, 2, 4):
        r = VM.monte_carlo(replace(sc_base, keepalive_modules=k), n=mc["value_runs_sweep"], seed=cfgfile["seeds"]["value"] + 11)
        ka.append(dict(keepalive_modules=k, **{f"{kk}_mean": float(np.mean(r[kk])) for kk in r}))
    crew = []
    for c in (0.0, 1.0, 2.0):
        r = VM.monte_carlo(replace(sc_base, crew_missions_per_yr=c), n=mc["value_runs_sweep"],
                           seed=cfgfile["seeds"]["value"] + 13, sample=False)
        crew.append(dict(crew_missions_per_yr=c, **{f"{kk}_mean": float(np.mean(r[kk])) for kk in r}))
    two = VM.monte_carlo(replace(sc_base, n_tsr=2, n_assets=60), n=mc["value_runs_sweep"], seed=cfgfile["seeds"]["value"] + 17)
    # TSR life-cycle Earth mass for break-even
    tsr_life_mass = cfg.delivered_mass + vcfg["tsr_spares_kg_per_yr"] * 10 + vcfg["keepalive_modules"] * 23.0
    for s_ in sweep:
        s_["mass_avoided_mean"] = s_["mass0_mean"] - s_["mass1_mean"]
        s_["net_mass_benefit"] = s_["mass_avoided_mean"] - tsr_life_mass
        s_["eva_avoided_mean"] = s_["eva0_mean"] - s_["eva1_mean"]
    # break-even (interpolate)
    xs = [s_["n_assets"] for s_ in sweep]
    ys = [s_["net_mass_benefit"] for s_ in sweep]
    be = None
    for i in range(1, len(xs)):
        if ys[i - 1] < 0 <= ys[i]:
            be = xs[i - 1] + (xs[i] - xs[i - 1]) * (-ys[i - 1]) / (ys[i] - ys[i - 1])
            break
    # correlation-based global sensitivity on baseline MC
    sens = {}
    for k in ("mtbf", "p_spare", "t_survive", "crew", "speed", "tsr_mtbf", "frac_unp"):
        x = mc_base[k]
        for y in ("dA",):
            sens[f"{k}->dA"] = float(np.corrcoef(x, mc_base[y])[0, 1]) if np.std(x) > 0 else 0.0
        sens[f"{k}->mass_avoided"] = float(np.corrcoef(x, mc_base["mass0"] - mc_base["mass1"])[0, 1]) if np.std(x) > 0 else 0.0
    value = dict(base_scenario=sc_base, base=dict({k: dict(mean=float(np.mean(v_)), p10=float(np.percentile(v_, 10)),
                                                          p50=float(np.percentile(v_, 50)),
                                                          p90=float(np.percentile(v_, 90))) for k, v_ in mc_base.items()}),
                 asset_sweep=sweep, level_mix=mixes, keepalive=ka, crew=crew, two_tsr_60_assets={k: float(np.mean(v_)) for k, v_ in two.items()},
                 tsr_lifecycle_mass_kg=tsr_life_mass, break_even_assets=be, sensitivity_corr=sens)
    jdump("value_model.json", value)
    np.savez_compressed(RES / "value_mc_base.npz", **mc_base)
    csv_dump("value_asset_sweep.csv", sweep)

    # ------------------------------------------------------------------ CDR analyses
    log("critical-design-review analyses")
    cdrc = cfgfile["cdr"]
    skill = []
    for kf in cdrc["skill_factors"]:
        with override({"robot_step_factor": kf}):
            r = VM.monte_carlo(sc_base, n=mc["value_runs_sweep"], seed=cfgfile["seeds"]["value"] + 19)
            from tsr1.reliability.servicing import task_success as _ts
            l2 = _ts("oru_replace", "L2", "robot")
        skill.append(dict(robot_step_factor=kf, p_oru_L2=l2, **{f"{k}_mean": float(np.mean(r[k])) for k in r}))
    host = []
    for hc in cdrc["host_cases"]:
        r = VM.monte_carlo(replace(sc_base, host_busy_frac=hc["host_busy_frac"], host_delay_h=hc["host_delay_h"]),
                           n=mc["value_runs_sweep"], seed=cfgfile["seeds"]["value"] + 23)
        host.append(dict(case=hc["label"], **{f"{k}_mean": float(np.mean(r[k])) for k in r}))
    speed_radius = []
    for vk in cdrc["speeds_kmh"]:
        with override({"tsr_speed_eff": vk}):
            dmax = 0.0
            for dd in np.arange(1.0, 40.01, 0.25):
                drm2 = [x for x in SC.drm_library(cfg, float(dd)) if x.id == "DRM-2"][0]
                if SC.evaluate(cfg, drm2).energy_kwh + res_kwh <= use:
                    dmax = float(dd)
            e10 = SC.evaluate(cfg, [x for x in SC.drm_library(cfg, 10.0) if x.id == "DRM-2"][0]).energy_kwh
        speed_radius.append(dict(speed_kmh=vk, max_service_radius_km=dmax, drm2_10km_kwh=e10))
    kit = TO.service_kit(cfg)
    jdump("cdr_analyses.json", dict(skill_factor=skill, host_cases=host, speed_radius=speed_radius, service_kit=kit))

    # ------------------------------------------------------------------ trades
    log("trade studies")
    t_mob = TM.evaluate_mobility(base_opts)
    t_wheel = TM.wheel_sweep(cfg.operational_mass)
    t_man = TMAN.evaluate()
    t_mod = TO.service_module_trade(base_opts.spine_slots)
    t_com = dict(link_10000km=TO.link_budget(), link_3000km=TO.link_budget(d_km=3000.0),
                 ka_band_10000km=TO.link_budget(p_tx_w=10.0, g_tx_dbi=30.0, f_hz=26e9, gt_dbk=10.0),
                 availability=TO.comm_availability())
    t_aut = TO.autonomy_task_time()
    t_arm_mat = TO.arm_material_comparison()
    t_ch_mat = TO.chassis_material_comparison(cfg.operational_mass)
    jdump("trades.json", dict(mobility=t_mob, wheel_types=TM.WHEEL_TYPES, manipulators=t_man, service_modules=t_mod,
                              comms=t_com, autonomy=t_aut, arm_materials=t_arm_mat, chassis_materials=t_ch_mat,
                              energy=TO.energy_alternatives(cfg), battery_vs_radius=batt_radius,
                              stabilisation=stab_opts, recovery_p_env=p_env))
    csv_dump("trade_wheel_sweep.csv", t_wheel)
    csv_dump("trade_mobility.csv", t_mob)
    csv_dump("trade_manipulators.csv", [{k: v_ for k, v_ in r.items() if k != "per_task"} for r in t_man])

    # ------------------------------------------------------------------ sensitivity
    log("sensitivity analysis")
    soil_names = ["soil_phi_deg", "soil_c", "soil_kphi", "soil_kc", "soil_n", "soil_K", "wr_c1", "wr_c2"]
    sens_slope = tornado(lambda: math.degrees(max_slope(v, lunar.soil_nominal())), soil_names, "max slope [deg]")
    mass_names = ["act_torque_density", "batt_spec_energy", "harness_frac", "system_margin", "mga_mechanism",
                  "mga_structure", "mga_harness", "wheel_rim_t", "batt_eol_fade", "batt_dod", "motorisation_factor"]
    sens_mass = tornado(lambda: build(base_opts, iterate=12).delivered_mass, mass_names, "delivered mass [kg]")
    sens_energy = tornado(lambda: SC.evaluate(cfg, [x for x in SC.drm_library(cfg, 10.0) if x.id == "DRM-2"][0]).energy_kwh,
                          ["drive_eff", "drive_duty", "tsr_speed_eff", "conv_eff", "p_keepalive_w"], "DRM-2 energy [kWh]")
    rec_names = ["spade_shape_factor", "helix_Nq", "recovery_fos", "p_brake_release"]
    sens_rec = tornado(lambda: TR.envelope_probability(cfg, "R4 winch + 2 spades + 2 helical anchors", rcases),
                       rec_names, "recovery envelope probability")
    mass_mc = mass_monte_carlo(lambda: build(base_opts, iterate=12), n=mc["mass_mc"],
                               seed=cfgfile["seeds"]["mass_mc"])
    jdump("sensitivity.json", dict(slope=sens_slope, mass=sens_mass, drm2_energy=sens_energy, recovery=sens_rec,
                                   mass_mc=dict(samples=mass_mc, mean=float(mass_mc.mean()),
                                                p10=float(np.percentile(mass_mc, 10)),
                                                p50=float(np.percentile(mass_mc, 50)),
                                                p90=float(np.percentile(mass_mc, 90)),
                                                p_le_1500=float(np.mean(mass_mc <= 1500.0)),
                                                p_le_3000=float(np.mean(mass_mc <= 3000.0))),
                                   value_corr=sens))

    # ------------------------------------------------------------------ design values for requirements
    log("design values, budgets and closure")
    rec_free15 = rcurves["curves"]["R4 winch + 2 spades + 2 helical anchors"]["free_kg"]
    rec_lock15 = rcurves["curves"]["R4 winch + 2 spades + 2 helical anchors"]["locked_kg"]
    i15 = rcurves["curves"]["R4 winch + 2 spades + 2 helical anchors"]["slopes"].index(15.0)
    cap_p50 = restraint_capacity(v.mass, 0.0, Restraint("b", n_spades=2, n_anchors=2), sn, v.wheel, v.n_wheels)
    cap_p10 = restraint_capacity(v.mass, 0.0, Restraint("b", n_spades=2, n_anchors=2), sn, v.wheel, v.n_wheels,
                                 strength_factor=0.5)
    dex = cfg.derived["dex"]
    crane = cfg.derived["crane"]
    dv.update(
        mr01_avail_gain_pp=round(100 * value["base"]["dA"]["p10"], 1), ref_assets=vcfg["ref_assets"],
        oru_max_kg=cfg.opts.heavy_payload, p_emer_cont_kw=R.v("ptm_rating_w") / 1000,
        t_emer_keepalive_h=math.floor(t_keep), p_keepalive_w=R.v("p_keepalive_w"),
        rec_envelope_text=(f"free-rolling vehicles up to {rec_free15[i15]/1000:.1f} t and brake-locked vehicles up to "
                           f"{rec_lock15[i15]/1000:.1f} t on slopes ≤ 15° (anchored winch, FoS {R.v('recovery_fos')}); "
                           f"450 kg-class rovers with wheels embedded ≤ 0.15 m after ramp excavation; direct towing of "
                           f"free-rolling vehicles ≤ {RS.analyse(cfg)[-3]['target_mass_kg']/1000:.1f} t on level ground; "
                           f"P(sampled immobilisation case recoverable) = {p_env_base:.2f}"),
        dust_residual_pct=5, psr_excursion_h=math.floor(min(psr_energy_h * 0.5, 8.0)),
        survival_h=120, service_radius_km=R.v("service_radius_km"),
        response_time_h=math.ceil(R.v("service_radius_km") / R.v("tsr_speed_eff") + 2.0),
        contact_pressure_kpa=round(mob["contact_pressure_kPa"], 2), slope_climb_deg=int(math.floor(slopes["nominal"])),
        slope_climb_cons_deg=int(math.floor(slopes["conservative"])),
        slope_hold_deg=25, obstacle_m=0.45, ditch_m=0.40, v_avg_ms=round(R.v("v_drive_nom") * R.v("drive_duty"), 2),
        v_max_ms=R.v("v_drive_max"), range_km=int(math.floor(rng_km)),
        slope_one_wheel_out_deg=int(math.floor(slopes["one_wheel_out"])), dex_payload_kg=cfg.opts.dex_payload,
        dex_reach_m=round(dex.reach, 2), dex_accuracy_mm=2, heavy_payload_kg=cfg.opts.heavy_payload,
        heavy_reach_m=round(crane.max_reach, 2), tool_change_min=5, spine_payload_kg=cfg.opts.spine_payload,
        spine_slots=cfg.opts.spine_slots, fastener_torque_nm=50, p_charge_kw=R.v("ptm_rating_w") / 1000,
        p_emer_peak_kw=1.5 * R.v("ptm_rating_w") / 1000, tether_m=cfg.opts.tether_m,
        battery_usable_kwh=cfg.opts.battery_usable_eol_kwh, q_reject_max_w=round(max(web_q.values())),
        p_survival_w=round(surv_w), winch_hold_kN=1.0, loc_global_m=1.0, loc_rel_mm=5, loc_rel_deg=0.5,
        winch_line_pull_kN=cfg.opts.winch_pull_kN, winch_line_m=cfg.opts.winch_line_m,
        anchor_capacity_kN=round(cap_p50 / 1000, 1), anchor_capacity_p10_kN=round(cap_p10 / 1000, 1),
        p_mission_10yr=round(rel["crew_repair"].p_capable_10yr, 2), v_crew_ms=0.2, f_crew_n=50,
    )
    claims = dict(survival_h=120, contact_pressure_kpa=dv["contact_pressure_kpa"], slope_climb_deg=dv["slope_climb_deg"],
                  recovery_claimed=("A", "B", "B2", "C-dig", "D", "D2", "D3"))
    closure = check_all(cfg, drm_res, rscen, cases, claims)
    jdump("closure.json", closure)
    (RES / "design_values.json").write_text(json.dumps(dv, indent=1))

    # ------------------------------------------------------------------ budgets CSVs
    with open(ROOT / "engineering" / "mass_budget.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["component", "subsystem", "mga_category", "qty", "cbe_kg", "mga_frac", "predicted_kg",
                    "x_m", "y_m", "z_m", "material", "trl", "basis"])
        for c in cfg.comps:
            w.writerow([c.name, c.subsystem, c.category, c.qty, round(c.cbe, 3), c.mga, round(c.predicted, 3),
                        *[round(p, 3) for p in c.pos], c.material, c.trl, c.basis])
        w.writerow(["TOTAL predicted (CBE + MGA)", "", "", "", round(cfg.cbe(), 2), "", round(cfg.predicted(), 2)])
        w.writerow([f"system margin ({R.v('system_margin'):.0%})", "", "", "", "", "",
                    round(cfg.predicted() * R.v("system_margin"), 2)])
        w.writerow(["DRY MASS ALLOCATION", "", "", "", "", "", round(cfg.dry_mass_allocation, 2)])
        w.writerow(["carried payload (ORUs/modules, nominal)", "", "", "", "", "", round(cfg.opts.payload_carried, 2)])
        w.writerow(["OPERATIONAL MASS", "", "", "", "", "", round(cfg.operational_mass, 2)])
        w.writerow([f"lander accommodation ({R.v('lander_accommodation_frac'):.0%} of dry allocation)", "", "", "", "",
                    "", round(cfg.delivered_mass - cfg.dry_mass_allocation, 2)])
        w.writerow(["DELIVERED MASS (charged to lander)", "", "", "", "", "", round(cfg.delivered_mass, 2)])
    with open(ROOT / "engineering" / "power_budget.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["component", "subsystem", "peak_W"] + list(MODES))
        for c in cfg.comps:
            if c.power or c.peak:
                w.writerow([c.name, c.subsystem, round(c.peak, 1)] + [round(c.power.get(m, 0.0), 1) for m in MODES])
        w.writerow(["TOTAL (bus load)", "", round(cfg.peak_power(), 1)] + [round(mode_tab[m], 1) for m in MODES])
        w.writerow(["WEB dissipation (incl. conversion losses)", "", ""] + [round(web_q[m], 1) for m in MODES])
    jdump("baseline_summary.json", dict(
        options=base_opts, cbe=cfg.cbe(), predicted=cfg.predicted(), dry_allocation=cfg.dry_mass_allocation,
        operational=cfg.operational_mass, delivered=cfg.delivered_mass, subsystems=cfg.subsystem_table(),
        com_stowed=cfg.com(), vehicle=dict(mass=v.mass, h_cg=v.h_cg, x_cg=v.x_cg), derived_keys=list(cfg.derived),
        dex=dex.summary(), crane=dict(mass=crane.mass, reach=crane.max_reach, t_luff=crane.t_luff,
                                     boom_od=crane.boom_od, breakdown=crane.breakdown),
        chassis=cfg.derived["chassis"], a_rad=cfg.derived["a_rad"], a_mli=cfg.derived["a_mli"],
        heater_cold=cfg.derived["heater_cold"], winch=cfg.derived["winch"], battery=cfg.derived["battery"],
        steer_torque=cfg.derived["steer_torque"], anchor_q=helical_anchor_capacity(0.15, 0.6)))
    # ------------------------------------------------------------------ register & requirements
    for k, val in (("mass_delivered", cfg.delivered_mass), ("mass_operational", cfg.operational_mass),
                   ("mass_dry_allocation", cfg.dry_mass_allocation), ("mass_cbe", cfg.cbe())):
        R.calc(k, k, val, "kg", "design.configuration.build (bottom-up roll-up)", "budgets")
    R.calc("battery_nameplate_kwh", "E_bat", cfg.derived["battery"].nameplate_kwh, "kWh", "power.electrical.size_battery", "power")
    R.calc("survival_power", "P_surv", surv_w, "W", "configuration mode M10 (heaters + survival avionics)", "thermal")
    R.calc("radiator_area", "A_rad", cfg.derived["a_rad"], "m^2", "thermal.lumped.radiator_area(q_web_hot)", "thermal")
    R.calc("value_dA_mean", "ΔA", value["base"]["dA"]["mean"], "-", "reliability.value_model.monte_carlo (N=30)", "reliability")
    n_par = R.export_csv(ROOT / "engineering" / "parameter_register.csv")
    subprocess.run([sys.executable, str(ROOT / "requirements" / "build_requirements.py")], check=True)
    n_fail = sum(1 for c in closure if not c["passed"])
    log(f"done in {time.time() - t0:.0f} s; parameters={n_par}; closure checks={len(closure)} failed={n_fail}")
    return n_fail


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    sys.exit(1 if main(a.quick) else 0)
