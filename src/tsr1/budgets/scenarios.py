"""Design-reference-mission (DRM) timelines and energy closure (directive §28, §44).

Each DRM is a sequence of phases (mode, duration, distance, extra load). Phase power is the
configuration's mode power plus extras (client power delivered through the PTM, winch, slope driving).
Driving phases use a 70 % motion duty cycle: P = 0.7·P(M3) + 0.3·P(M4) (perception/planning stops).
Energy is compared with the battery's usable end-of-life energy, keeping a survival reserve, both
without solar input (conservative) and with the vertical arrays' average output in sunlit fractions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from tsr1.common.params import REGISTRY as R
from tsr1.environment.lunar import SOLAR_CONST

SUB = "budgets"
R.define("drive_duty", "δ_drv", 0.70, "-", "ASSUMPTION", "A: autonomy stop-and-go (perceive/plan) duty cycle", SUB,
         "fraction of traverse time in motion", low=0.5, high=0.9)
R.define("reserve_survival_h", "t_res", 50.0, "h", "DESIGN", "TS-06: VIPER-class 50 h darkness survival (S035)", SUB,
         "survival reserve retained at end of any DRM (no solar)")
R.define("solar_cell_eff", "η_PV", 0.30, "-", "SOURCE", "L007 (IMM/triple-junction BOL ~30 %, LITERATURE-RECALL)", SUB,
         "solar cell efficiency BOL", low=0.28, high=0.33)
R.define("solar_eol_factor", "f_PV,EOL", 0.85, "-", "ESTIMATE", "A: radiation, UV, thermal cycling, residual dust", SUB,
         "end-of-life array output factor", low=0.75, high=0.92)
R.define("solar_geom_factor", "f_geom", 2.0 / math.pi, "-", "CALCULATED",
         "mean |cos(azimuth)| for fixed vertical side panels with sun on the horizon", SUB,
         "projection factor of fixed vertical arrays")
R.define("sortie_sunlit_frac", "f_sun", 0.5, "-", "ASSUMPTION", "A: routes partly in terrain shadow (ridge 92 % S030)", SUB,
         "fraction of sortie time with arrays illuminated", low=0.0, high=0.9)


@dataclass
class Phase:
    name: str
    mode: str
    hours: float
    km: float = 0.0
    extra_w: float = 0.0
    note: str = ""


@dataclass
class DRM:
    id: str
    title: str
    phases: list
    tools: list
    crew_involvement: str
    risks: list
    branches: list
    client_energy_kwh: float = 0.0


@dataclass
class DRMResult:
    drm: DRM
    duration_h: float
    distance_km: float
    energy_kwh: float
    energy_solar_kwh: float
    peak_w: float
    phase_energy: list = field(default_factory=list)


def _phase_power(cfg, ph: Phase) -> float:
    if ph.mode == "drive":
        d = R.v("drive_duty")
        return d * cfg.mode_power("M3_driving") + (1 - d) * cfg.mode_power("M4_inspection") + ph.extra_w
    return cfg.mode_power(ph.mode) + ph.extra_w


def solar_avg_w(cfg) -> float:
    a = cfg.opts.solar_area / 2.0          # one side panel faces the sun at a time
    return (R.v("solar_cell_eff") * SOLAR_CONST * a * R.v("solar_geom_factor") * R.v("solar_eol_factor"))


def evaluate(cfg, drm: DRM) -> DRMResult:
    E, t, km, pk, rows = 0.0, 0.0, 0.0, 0.0, []
    for ph in drm.phases:
        p = _phase_power(cfg, ph)
        E += p * ph.hours
        t += ph.hours
        km += ph.km
        pk = max(pk, p)
        rows.append((ph.name, ph.mode, ph.hours, ph.km, p, p * ph.hours / 1000))
    e_sol = solar_avg_w(cfg) * R.v("sortie_sunlit_frac") * t
    return DRMResult(drm, t, km, E / 1000, max(E - e_sol, 0) / 1000, pk, rows)


def drm_library(cfg, dist_km: float | None = None) -> list[DRM]:
    """Representative DRMs. Distance defaults to the service radius (worst case asset at the edge)."""
    d = R.v("service_radius_km") if dist_km is None and "service_radius_km" in R else (dist_km or 10.0)
    v = R.v("tsr_speed_eff") if "tsr_speed_eff" in R else 1.26
    eta = R.v("conv_eff")
    drive = lambda km, name: Phase(name, "drive", km / v, km)
    keep = R.v("p_keepalive_w") if "p_keepalive_w" in R else 300.0
    winch_w = cfg.derived["winch"].power_elec if "winch" in cfg.derived else 0.0
    return [
        DRM("DRM-1", "Routine inspection patrol",
            [drive(2 * d, "patrol loop (2·R_s)")] + [Phase(f"stand-off inspection stop {k+1}", "M4_inspection", 0.5)
                                                     for k in range(8)] +
            [Phase("report via relay", "M11_safe", 0.5)],
            ["mast cameras", "thermal IR", "LiDAR", "macro camera on arm"], "none",
            ["terrain hazard", "lighting (long shadows)"],
            ["anomaly found → schedule DRM-2/3/5", "comm outage → store-and-forward"]),
        DRM("DRM-2", "Electrical failure: emergency power + ORU replacement",
            [drive(d, "traverse to asset"), Phase("stand-off inspection", "M4_inspection", 0.5),
             Phase("close inspection + diagnosis", "M5_manipulation", 1.0),
             Phase("deploy tether, connect ISPSIS port", "M5_manipulation", 0.5),
             Phase("keep-alive + bus diagnosis", "M8_emergency_power", 1.0, extra_w=keep / eta),
             Phase("ORU swap (keep-alive on)", "M5_manipulation", 3.0, extra_w=keep / eta),
             Phase("functional test", "M8_emergency_power", 0.5, extra_w=keep / eta),
             Phase("disconnect, stow", "M5_manipulation", 0.5), drive(d, "return to home node")],
            ["electrical probe", "connector tool", "socket driver", "OTCM/androgynous adapter", "power tether"],
            "none (task-level approvals from MOC)",
            ["connector damage", "wrong diagnosis", "ORU fastener seized"],
            ["no spare → leave keep-alive module, request spare", "unpowered > t_survive → loss",
             "fastener seized → abort, report"],
            client_energy_kwh=keep * 5.0 / 1000),
        DRM("DRM-3", "Dust contamination of solar array / radiator",
            [drive(0.5 * d, "traverse to array"), Phase("inspect (IR, imaging, I-V telemetry)", "M4_inspection", 0.5),
             Phase("clean 30 m² (brush + EDS wand, 10 m²/h)", "M5_manipulation", 3.0),
             Phase("verify recovery", "M4_inspection", 0.5), drive(0.5 * d, "return")],
            ["dust brush", "EDS wand", "thermal IR"], "none", ["re-contamination by own wheels", "abrasion of coating"],
            ["insufficient recovery → schedule crew / coating replacement"]),
        DRM("DRM-4", "Immobilized rover recovery (450 kg, 10° slope)",
            [drive(0.8 * d, "traverse to target"), Phase("stand-off assessment", "M4_inspection", 1.0),
             Phase("keep-alive power to target", "M8_emergency_power", 2.0, extra_w=150 / eta),
             Phase("deploy spades, install 2 helical anchors", "M5_manipulation", 1.5),
             Phase("rig line to tow point", "M5_manipulation", 1.0),
             Phase("winch 30 m (0.05 m/s) + monitoring", "M7_recovery_winch", 0.5, extra_w=winch_w * 0.6),
             Phase("stow anchors/line", "M5_manipulation", 1.0),
             Phase("tow 200 m to flat service zone", "drive", 0.2 / 0.5 * 1.5, 0.2, extra_w=200.0),
             drive(0.8 * d, "return")],
            ["anchor driver", "helical anchors", "spades", "shackle/hitch", "winch"], "none",
            ["anchor pull-out", "line snag", "target structural damage"],
            ["anchor creep → add anchor / reduce load", "target beyond envelope → keep-alive + crew/LTV assist"],
            client_energy_kwh=0.3),
        DRM("DRM-5", "Communication node electronics replacement",
            [drive(d, "traverse to comm tower"), Phase("inspect", "M4_inspection", 0.5),
             Phase("temporary power to node", "M8_emergency_power", 0.5, extra_w=200 / eta),
             Phase("ORU swap at 2.5 m height (crane-assisted)", "M6_heavy_manip", 2.5, extra_w=200 / eta),
             Phase("link test", "M8_emergency_power", 0.5, extra_w=200 / eta), drive(d, "return")],
            ["crane", "socket driver", "connector tool", "lifting fixture"], "none",
            ["ORU drop", "mast access geometry"], ["access infeasible → lower mast if designed (L3)"],
            client_energy_kwh=0.7),
        DRM("DRM-6", "Heavy ORU exchange (100 kg battery module of a power node)",
            [drive(0.3 * d, "traverse"), Phase("inspect", "M4_inspection", 0.5),
             Phase("lower body, lock differential", "M6_heavy_manip", 0.3),
             Phase("crane lift-out / lift-in with arm guidance", "M6_heavy_manip", 3.0),
             Phase("test", "M5_manipulation", 0.5), drive(0.3 * d, "return")],
            ["crane", "lifting fixture", "socket driver"], "none", ["load swing", "tip-over"],
            ["outside stability envelope → reposition / crew"]),
    ]
