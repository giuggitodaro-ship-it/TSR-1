"""System-level value model: distributed lunar infrastructure WITH vs WITHOUT TSR-1 (directive §29).

Discrete-event Monte Carlo over a 10-year horizon. Each asset alternates between operating periods
(exponential time-to-failure, MTBF A-08) and fault periods. Fault types (A-09) and their handling:

  electrical / comm   asset down; fraction ``frac_unpowered`` loses keep-alive power and is
                      destroyed (thermal death) unless power is restored within t_survive (A-14).
  dust                asset degraded (performance loss ``dust_loss``) until cleaned.
  immobilization      mobile assets only: down; lost unless recovered (TSR envelope probability
                      from the recovery model) or recovered by crew (low probability).
  catastrophic        not serviceable; lost.

Repairs: TSR-1 (if present) serves a priority queue (unpowered first); task time = travel out/back at
the effective speed + service time + recharge. Success probabilities per task and compatibility level
come from ``servicing.py``; ORU repairs need a spare (probability p_spare) or wait for an Earth spare.
Crew (A-07) are present in windows; during a window they work the backlog within an EVA crew-hour
budget, with crew success probabilities. Lost assets are replaced from Earth after a lead time.

Common random numbers: identical failure sequences are used for both cases of a replicate.
Outputs: availability, downtime, assets lost, EVA crew-hours, Earth-supplied mass, response time,
TSR utilisation.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field, replace

import numpy as np

from tsr1.common.params import REGISTRY as R
from tsr1.reliability.servicing import task_success

SUB = "reliability"
YEAR_H = 8766.0

R.define("asset_mtbf_yr", "MTBF_a", 4.0, "yr", "ASSUMPTION", "A-08", SUB, "per-asset serviceable-fault MTBF (log-uniform)",
         low=1.0, high=10.0)
R.define("p_spare", "p_sp", 0.75, "-", "ASSUMPTION", "A-10", SUB, "ORU spare available on base when needed", low=0.5, high=0.9)
R.define("t_survive_h", "t_surv,a", 50.0, "h", "ASSUMPTION", "A-14 (S035 VIPER ~50 h)", SUB,
         "time to irreversible thermal damage of an unpowered asset", low=24.0, high=120.0)
R.define("replace_lead_yr", "t_repl", 1.5, "yr", "ASSUMPTION", "A-11", SUB, "Earth replacement lead time", low=1.0, high=2.0)
R.define("spare_lead_yr", "t_spare", 0.5, "yr", "ASSUMPTION", "A-11 (next-lander ORU delivery)", SUB,
         "Earth ORU spare lead time", low=0.25, high=1.0)
R.define("frac_unpowered", "f_unp", 0.5, "-", "ASSUMPTION", "A-14", SUB,
         "fraction of electrical/comm faults that remove keep-alive power", low=0.3, high=0.7)
R.define("dust_loss", "d_dust", 0.3, "-", "ASSUMPTION", "A-09; S062 (sub-monolayer degrades surfaces)", SUB,
         "performance loss of dust-degraded asset", low=0.1, high=0.5)
from tsr1.trades.other_trades import KA_OPTIONS, KA_SELECTED, keepalive_module_sizing  # noqa: E402

_KA = keepalive_module_sizing(*KA_OPTIONS[KA_SELECTED])
R.calc("ka_sustain_p", "p_KA", _KA["p_sustain"], "-",
       f"trades.other_trades.keepalive_module_sizing({KA_SELECTED}); range = asset survival power x1.5 / x0.67 (CDR-20)",
       SUB, low=_KA["p_sustain_low"], high=_KA["p_sustain_high"],
       note="probability a MOD-KA module can sustain a parked asset (power and dark-period bridging)")
R.define("crew_missions_per_yr", "n_crew", 1.0, "1/yr", "ASSUMPTION", "A-07", SUB, "surface crew missions per year",
         low=0.0, high=2.0)
R.define("crew_mission_days", "t_crew", 30.0, "d", "ASSUMPTION", "A-07", SUB, "surface stay per mission")
R.define("crew_maint_hours", "H_crew", 120.0, "crew-h", "ASSUMPTION", "A-07, S049 (ISS ~1.9 h/workday)", SUB,
         "crew-hours available for external maintenance per mission", low=60.0, high=240.0)
R.define("tsr_speed_eff", "v_eff", 1.26, "km/h", "CALCULATED", "0.5 m/s nominal × 0.7 driving duty (autonomy stops)",
         SUB, "effective TSR traverse speed incl. perception/planning stops", low=0.7, high=2.5)
from tsr1.reliability.tsr_reliability import critical_fault_rate  # noqa: E402

R.define("tsr_mtbf_yr", "MTBF_T", 1.0 / critical_fault_rate("nominal"), "yr", "CALCULATED",
         "reliability.tsr_reliability.critical_fault_rate (single-string servicing-critical ORUs)", SUB,
         "TSR-1 mean time between faults that remove a servicing function",
         low=1.0 / critical_fault_rate("high"), high=1.0 / critical_fault_rate("low"))
R.define("tsr_repair_days", "t_rep,T", 30.0, "d", "ASSUMPTION", "A: ORU swap by crew/peer with on-base spares", SUB,
         "mean TSR-1 outage per fault", low=7.0, high=120.0)


@dataclass
class Scenario:
    n_assets: int = 30
    years: float = 10.0
    frac_mobile: float = 0.25
    level_mix: tuple = (0.20, 0.30, 0.35, 0.15)          # L0..L3
    fault_mix: tuple = (0.35, 0.20, 0.15, 0.15, 0.15)    # electrical, dust, comm, immobilization, catastrophic
    service_radius_km: float = 10.0
    asset_mass_mean: float = 400.0                       # kg (replacement mass, A)
    oru_mass_frac: float = 0.06
    mtbf_yr: float = field(default_factory=lambda: R.v("asset_mtbf_yr"))
    p_spare: float = field(default_factory=lambda: R.v("p_spare"))
    t_survive_h: float = field(default_factory=lambda: R.v("t_survive_h"))
    replace_lead_yr: float = field(default_factory=lambda: R.v("replace_lead_yr"))
    spare_lead_yr: float = field(default_factory=lambda: R.v("spare_lead_yr"))
    frac_unpowered: float = field(default_factory=lambda: R.v("frac_unpowered"))
    dust_loss: float = field(default_factory=lambda: R.v("dust_loss"))
    crew_missions_per_yr: float = field(default_factory=lambda: R.v("crew_missions_per_yr"))
    crew_mission_days: float = field(default_factory=lambda: R.v("crew_mission_days"))
    crew_maint_hours: float = field(default_factory=lambda: R.v("crew_maint_hours"))
    # TSR parameters
    n_tsr: int = 1
    tsr_speed_kmh: float = field(default_factory=lambda: R.v("tsr_speed_eff"))
    tsr_mtbf_yr: float = field(default_factory=lambda: R.v("tsr_mtbf_yr"))
    tsr_repair_days: float = field(default_factory=lambda: R.v("tsr_repair_days"))
    recovery_envelope_p: float = 0.75      # from recovery model (overwritten by run_all)
    service_h: tuple = (8.0, 4.0, 6.0, 16.0)   # electrical, dust, comm, recovery on-site hours
    recharge_h: float = 3.0
    crew_hours_task: tuple = (20.0, 8.0, 20.0, 30.0)   # A-21
    crew_recovery_p: float = 0.3
    immob_abandon_days: float = 30.0
    keepalive_modules: int = 0           # deployable keep-alive power modules (service-spine module, TS-07)
    ka_sustain_p: float = field(default_factory=lambda: R.v("ka_sustain_p"))
    host_busy_frac: float = 0.0          # CDR-01: probability the (shared) host vehicle is busy when a task arrives
    host_delay_h: float = 0.0            # mean extra delay before a busy host can start the task     # immobilised asset declared lost if not recovered (A-14 analogue)


FAULTS = ("electrical", "dust", "comm", "immobilization", "catastrophic")


@dataclass
class Asset:
    idx: int
    level: str
    mobile: bool
    dist_km: float
    mass: float
    ttf: list            # pre-sampled operating times to failure [h]
    ftypes: list
    unpowered: list
    k: int = 0


@dataclass
class Metrics:
    availability: float
    downtime_h: float
    lost: int
    eva_crew_h: float
    earth_mass_kg: float
    mean_response_h: float
    tsr_utilisation: float
    tasks_tsr: int
    tasks_tsr_success: int
    faults: int = 0              # fault events (all types) during the run
    lost_catastrophic: int = 0   # losses from non-serviceable faults (scale with operating exposure)
    ka_demand: int = 0           # events where a stabilised asset needed a keep-alive module to wait for a spare
    ka_denied: int = 0           # ... and none was free (asset lost unless crew present)
    ka_used: int = 0             # keep-alive deployments that sustained the asset
    ka_hours: float = 0.0        # module-hours deployed (for the inventory rule, Little's law)


def make_assets(sc: Scenario, rng: np.random.Generator) -> list[Asset]:
    assets = []
    lv = ("L0", "L1", "L2", "L3")
    for i in range(sc.n_assets):
        mobile = rng.random() < sc.frac_mobile
        level = lv[rng.choice(4, p=np.asarray(sc.level_mix) / sum(sc.level_mix))]
        dist = sc.service_radius_km * math.sqrt(rng.random())
        mass = rng.lognormal(math.log(sc.asset_mass_mean) - 0.5 * 0.6 ** 2, 0.6)
        n = 60
        ttf = list(rng.exponential(sc.mtbf_yr * YEAR_H, n))
        fm = np.asarray(sc.fault_mix, float)
        if not mobile:   # fixed assets cannot be immobilised: reassign to electrical
            fm = fm.copy(); fm[0] += fm[3]; fm[3] = 0.0
        ft = [FAULTS[j] for j in rng.choice(5, size=n, p=fm / fm.sum())]
        unp = list(rng.random(n) < sc.frac_unpowered)
        assets.append(Asset(i, level, mobile, dist, mass, ttf, ft, unp))
    return assets


def _crew_windows(sc: Scenario, rng: np.random.Generator) -> list[tuple[float, float]]:
    wins = []
    for y in range(int(math.ceil(sc.years))):
        n = int(sc.crew_missions_per_yr) + (1 if rng.random() < sc.crew_missions_per_yr % 1 else 0)
        for _ in range(n):
            t0 = (y + rng.random()) * YEAR_H
            wins.append((t0, t0 + sc.crew_mission_days * 24))
    return sorted(wins)


def simulate(sc: Scenario, assets: list[Asset], with_tsr: bool, rng: np.random.Generator,
             crew_windows: list[tuple[float, float]]) -> Metrics:
    T = sc.years * YEAR_H
    # per-asset state
    state = {a.idx: "up" for a in assets}
    perf = {a.idx: 1.0 for a in assets}
    last_t = {a.idx: 0.0 for a in assets}
    up_int = {a.idx: 0.0 for a in assets}
    fault_info: dict[int, dict] = {}
    ev: list = []
    seq = 0

    def push(t, kind, data):
        nonlocal seq
        heapq.heappush(ev, (t, seq, kind, data))
        seq += 1

    def set_state(i, t, st, p):
        up_int[i] += perf[i] * (min(t, T) - last_t[i])
        last_t[i] = min(t, T)
        state[i], perf[i] = st, p

    for a in assets:
        push(a.ttf[0], "fail", a.idx)
        a.k = 0
    lost = 0
    lost_cat = 0
    n_faults = 0
    earth_mass = 0.0
    eva_h = 0.0
    responses = []
    n_units = max(1, sc.n_tsr) if with_tsr else 0
    busy_until = [0.0] * n_units
    down_until = [0.0] * n_units
    tsr_busy_total = 0.0
    tasks_tsr = 0
    tasks_ok = 0
    ka_free = sc.keepalive_modules if with_tsr else 0
    ka_used = 0
    ka_demand = 0
    ka_denied = 0
    ka_hours = 0.0
    backlog: list[int] = []      # assets awaiting crew
    crew_used: dict = {}         # crew-hours used per window
    queue: list = []             # TSR priority queue (prio, t_fault, idx)
    amap = {a.idx: a for a in assets}
    # TSR self-fault process
    for u in range(n_units):
        t = rng.exponential(sc.tsr_mtbf_yr * YEAR_H)
        while t < T:
            push(t, "tsr_fault", u)
            t += sc.tsr_repair_days * 24 + rng.exponential(sc.tsr_mtbf_yr * YEAR_H)
    for (w0, w1) in crew_windows:
        push(w0, "crew_start", (w0, w1))

    def release_ka(info, t):
        nonlocal ka_free, ka_hours
        if info is not None and info.get("keepalive"):
            ka_free += 1
            ka_hours += min(t, T) - info["ka_t"]
            info["keepalive"] = False

    def resolve_repair(i, t, success):
        a = amap[i]
        info = fault_info.pop(i, None)
        release_ka(info, t)
        if success:
            set_state(i, t, "up", 1.0)
            a.k += 1
            if a.k < len(a.ttf):
                push(t + a.ttf[a.k], "fail", i)
        return info

    def lose(i, t):
        nonlocal lost, earth_mass
        release_ka(fault_info.get(i), t)
        if state[i] == "lost":
            return
        set_state(i, t, "lost", 0.0)
        fault_info.pop(i, None)
        lost += 1
        earth_mass += amap[i].mass
        push(t + sc.replace_lead_yr * YEAR_H, "replaced", i)

    def try_start_tsr(t):
        nonlocal tsr_busy_total, tasks_tsr, tasks_ok, earth_mass
        if not with_tsr:
            return
        free = [u for u in range(n_units) if t >= busy_until[u] and t >= down_until[u]]
        for u in free:
            _start_one(t, u)

    def _start_one(t, u):
        nonlocal tsr_busy_total, tasks_tsr, tasks_ok, earth_mass
        while queue:
            prio, tf, i = heapq.heappop(queue)
            if i not in fault_info or state[i] == "lost":
                continue
            info = fault_info[i]
            a = amap[i]
            ft = info["type"]
            j = {"electrical": 0, "dust": 1, "comm": 2, "immobilization": 3}[ft]
            travel = a.dist_km / sc.tsr_speed_kmh
            if sc.host_busy_frac > 0 and rng.random() < sc.host_busy_frac:
                travel += rng.exponential(sc.host_delay_h)   # shared host must finish/abort its current job
            t_arrive = t + travel
            responses.append(t_arrive - info["t"])
            dur = 2 * travel + sc.service_h[j] + sc.recharge_h
            tasks_tsr += 1
            ok = False
            if info.get("unpowered") and t_arrive > info["t"] + sc.t_survive_h:
                # too late: thermal death occurs at its scheduled time (already handled by event)
                pass
            if ft in ("electrical", "comm"):
                powered_ok = True
                if info.get("unpowered"):
                    powered_ok = (t_arrive <= info["t"] + sc.t_survive_h and
                                  rng.random() < task_success("emergency_power", a.level, "robot", rng))
                    if powered_ok:
                        info["stabilised"] = True
                if powered_ok or not info.get("unpowered"):
                    spare = rng.random() < sc.p_spare
                    if spare and rng.random() < task_success("oru_replace", a.level, "robot", rng):
                        ok = True
                        earth_mass += max(5.0, sc.oru_mass_frac * a.mass)
            elif ft == "dust":
                ok = rng.random() < task_success("dust_clean", a.level, "robot", rng)
            elif ft == "immobilization":
                ok = (rng.random() < task_success("recovery_rig", a.level, "robot", rng) and
                      rng.random() < sc.recovery_envelope_p)
            t_done = t + dur
            busy_until[u] = t_done
            tsr_busy_total += dur
            push(t_done, "tsr_done", (i, ok))
            return

    while ev:
        t, _, kind, data = heapq.heappop(ev)
        if t > T:
            break
        if kind == "fail":
            i = data
            a = amap[i]
            if state[i] != "up":
                continue
            ft = a.ftypes[a.k]
            unp = a.unpowered[a.k] and ft in ("electrical", "comm")
            n_faults += 1
            if ft == "catastrophic":
                lost_cat += 1
                lose(i, t)
                continue
            set_state(i, t, "degraded" if ft == "dust" else "down", 1 - sc.dust_loss if ft == "dust" else 0.0)
            # triage (ConOps §7): with TSR-1 present, crew are tasked only with faults TSR-1 cannot repair
            # (ORU work on L0/L1 assets) or after a failed TSR-1 attempt; TSR-1 still provides power/keep-alive.
            crew_needed = (not with_tsr) or (ft in ("electrical", "comm") and a.level in ("L0", "L1"))
            fault_info[i] = {"type": ft, "t": t, "unpowered": unp, "stabilised": False, "crew_needed": crew_needed}
            if unp:
                push(t + sc.t_survive_h, "thermal_check", (i, t))
            if ft == "immobilization":
                push(t + sc.immob_abandon_days * 24, "abandon_check", (i, t))
            prio = 0 if unp else (1 if ft == "immobilization" else (2 if ft in ("electrical", "comm") else 3))
            if with_tsr:
                heapq.heappush(queue, (prio, t, i))
                try_start_tsr(t)
            backlog.append(i)
            # crew present now? respond immediately within window (only if crew are needed for this fault)
            if crew_needed:
                for (w0, w1) in crew_windows:
                    if w0 <= t <= w1:
                        push(t + 2.0, "crew_task", i)
                        break
        elif kind == "thermal_check":
            i, tf = data
            info = fault_info.get(i)
            if info is not None and info["t"] == tf and not info.get("stabilised") and state[i] == "down":
                lose(i, t)
        elif kind == "abandon_check":
            i, tf = data
            info = fault_info.get(i)
            if info is not None and info["t"] == tf and state[i] == "down":
                lose(i, t)
        elif kind == "tsr_done":
            i, ok = data
            if i in fault_info and state[i] != "lost":
                if ok:
                    tasks_ok += 1
                    resolve_repair(i, t, True)
                    if i in backlog:
                        backlog.remove(i)
                else:
                    info = fault_info[i]
                    info["crew_needed"] = True        # TSR attempt failed -> eligible for crew
                    crew_now = any(w0 <= t <= w1 for (w0, w1) in crew_windows)
                    if info["type"] == "immobilization":
                        # failed TSR recovery: crew may still try within the abandonment time (same rule as baseline)
                        if crew_now:
                            push(t + 2.0, "crew_task", i)
                    elif info.get("unpowered") and info.get("stabilised"):
                        # TSR restored power but repair failed: asset dies when TSR leaves unless a keep-alive module
                        # is left connected (then it waits for a spare / crew) or crew repair it within t_survive
                        ka_demand += 1
                        if ka_free <= 0:
                            ka_denied += 1
                        if ka_free > 0 and rng.random() < sc.ka_sustain_p:
                            ka_free -= 1
                            ka_used += 1
                            info["keepalive"] = True
                            info["ka_t"] = t
                            info["unpowered"] = False
                            push(t + sc.spare_lead_yr * YEAR_H, "spare_arrival", i)
                        elif crew_now:
                            info["stabilised"] = False
                            info["t"] = t
                            push(t + sc.t_survive_h, "thermal_check", (i, t))
                            push(t + 2.0, "crew_task", i)
                        else:
                            lose(i, t)
                    elif info["type"] in ("electrical", "comm") and not info.get("unpowered"):
                        # no spare or failed: wait for Earth spare, then one more TSR attempt
                        push(t + sc.spare_lead_yr * YEAR_H, "spare_arrival", i)
            try_start_tsr(t)
        elif kind == "spare_arrival":
            i = data
            if i in fault_info and state[i] != "lost":
                a = amap[i]
                if with_tsr and rng.random() < task_success("oru_replace", a.level, "robot", rng):
                    earth_mass += max(5.0, sc.oru_mass_frac * a.mass)
                    resolve_repair(i, t + 24.0, True)
                    if i in backlog:
                        backlog.remove(i)
        elif kind == "tsr_fault":
            down_until[data] = max(t, busy_until[data]) + sc.tsr_repair_days * 24
            push(down_until[data], "tsr_up", data)
        elif kind == "tsr_up":
            try_start_tsr(t)
        elif kind == "crew_start":
            w0, w1 = data
            hours = sc.crew_maint_hours
            for i in sorted(list(backlog), key=lambda k: fault_info.get(k, {}).get("t", 0)):
                if i not in fault_info or state[i] == "lost":
                    continue
                push(t + 24.0, "crew_task", i)
        elif kind == "crew_task":
            i = data
            if i not in fault_info or state[i] == "lost":
                continue
            info = fault_info[i]
            if not info.get("crew_needed", True):
                continue
            a = amap[i]
            j = {"electrical": 0, "dust": 1, "comm": 2, "immobilization": 3}[info["type"]]
            # crew-hour budget per window
            win = next(((w0, w1) for (w0, w1) in crew_windows if w0 <= t <= w1 + 48), None)
            if win is None:
                continue
            used = crew_used.get(win, 0.0)
            if used + sc.crew_hours_task[j] > sc.crew_maint_hours:
                continue
            crew_used[win] = used + sc.crew_hours_task[j]
            eva_h += sc.crew_hours_task[j]
            ft = info["type"]
            if ft in ("electrical", "comm"):
                ok = rng.random() < sc.p_spare and rng.random() < task_success("oru_replace", a.level, "crew", rng)
                if ok:
                    earth_mass += max(5.0, sc.oru_mass_frac * a.mass)
                elif not info.get("unpowered"):
                    push(t + sc.spare_lead_yr * YEAR_H, "spare_arrival_crew", i)
            elif ft == "dust":
                ok = rng.random() < task_success("dust_clean", a.level, "crew", rng)
            else:
                ok = rng.random() < sc.crew_recovery_p * task_success("recovery_rig", a.level, "crew", rng)
            if ok:
                resolve_repair(i, t, True)
                if i in backlog:
                    backlog.remove(i)
            elif ft == "immobilization":
                lose(i, t)
        elif kind == "spare_arrival_crew":
            # spare arrives; repaired at next crew window (handled via backlog) — nothing to do here
            pass
        elif kind == "replaced":
            i = data
            a = amap[i]
            set_state(i, t, "up", 1.0)
            a.k += 1
            if a.k < len(a.ttf):
                push(t + a.ttf[a.k], "fail", i)
    for i in state:
        set_state(i, T, state[i], perf[i])
    for info in fault_info.values():
        release_ka(info, T)
    avail = sum(up_int.values()) / (len(assets) * T)
    down = len(assets) * T - sum(up_int.values())
    util = tsr_busy_total / (T * n_units) if with_tsr else 0.0
    return Metrics(avail, down, lost, eva_h, earth_mass, float(np.mean(responses)) if responses else float("nan"),
                   util, tasks_tsr, tasks_ok, n_faults, lost_cat, ka_demand, ka_denied, ka_used, ka_hours)


def run_pair(sc: Scenario, seed: int) -> tuple[Metrics, Metrics]:
    """Simulate one replicate without and with TSR-1 using common random numbers."""
    rng_a = np.random.default_rng(seed)
    assets = make_assets(sc, rng_a)
    wins = _crew_windows(sc, rng_a)
    import copy
    a1, a2 = copy.deepcopy(assets), copy.deepcopy(assets)
    m0 = simulate(sc, a1, False, np.random.default_rng(seed + 1), wins)
    m1 = simulate(sc, a2, True, np.random.default_rng(seed + 1), wins)
    return m0, m1


def sample_scenario(base: Scenario, rng: np.random.Generator) -> Scenario:
    """Draw uncertain parameters from their registered ranges (Monte Carlo over epistemic uncertainty)."""
    lo, hi = R.rng("asset_mtbf_yr")
    return replace(base,
                   mtbf_yr=float(math.exp(rng.uniform(math.log(lo), math.log(hi)))),
                   p_spare=float(rng.uniform(*R.rng("p_spare"))),
                   t_survive_h=float(rng.uniform(*R.rng("t_survive_h"))),
                   replace_lead_yr=float(rng.uniform(*R.rng("replace_lead_yr"))),
                   spare_lead_yr=float(rng.uniform(*R.rng("spare_lead_yr"))),
                   frac_unpowered=float(rng.uniform(*R.rng("frac_unpowered"))),
                   dust_loss=float(rng.uniform(*R.rng("dust_loss"))),
                   crew_missions_per_yr=float(rng.choice([0.0, 1.0, 2.0], p=[0.25, 0.5, 0.25])),
                   crew_maint_hours=float(rng.uniform(*R.rng("crew_maint_hours"))),
                   tsr_speed_kmh=float(rng.uniform(*R.rng("tsr_speed_eff"))),
                   tsr_mtbf_yr=float(rng.uniform(*R.rng("tsr_mtbf_yr"))),
                   tsr_repair_days=float(rng.uniform(*R.rng("tsr_repair_days"))),
                   ka_sustain_p=float(rng.uniform(*R.rng("ka_sustain_p"))))


def keepalive_inventory(fault_rate_per_yr: float, park_fraction: float, hold_yr: float, p_sustain: float = 1.0,
                        quantile: float = 0.95) -> int:
    """Keep-alive module inventory rule (DESIGN DECISION, CDR-19).

    Stabilised-but-unrepaired assets "park" on a keep-alive module until a spare is fitted (robotically after the
    Earth spare arrives, or by crew for L0/L1 assets). By Little's law the mean number of modules in use is
    L = lambda_dep * T_hold with lambda_dep = park_fraction * p_sustain * fault rate (deployments) and T_hold the
    mean deployment time; the inventory is the Poisson ``quantile`` of L.
    """
    lam = max(0.0, park_fraction * p_sustain * fault_rate_per_yr * hold_yr)
    k, p, cdf = 0, math.exp(-lam), math.exp(-lam)
    while cdf < quantile:
        k += 1
        p *= lam / k
        cdf += p
    return k


R.define("ka_park_frac", "f_park", 0.14, "-", "ESTIMATE", "calibrated by simulations/capacity_study.py (CDR-19)", SUB,
         "fraction of fault events that leave a stabilised but unrepaired asset needing a keep-alive module",
         low=0.13, high=0.15)
R.define("ka_hold_yr", "T_hold", 1.1, "yr", "ESTIMATE", "calibrated by simulations/capacity_study.py (CDR-19; 1.0-1.2 yr "
         "unsaturated, up to 2 yr when saturated)", SUB, "mean keep-alive module deployment time", low=1.0, high=2.0)


def expected_fault_rate(n_assets: int) -> float:
    """Expected fault rate [1/yr] of a base over the log-uniform MTBF prior: N * E[1/MTBF]."""
    lo, hi = R.rng("asset_mtbf_yr")
    return n_assets * (1.0 / lo - 1.0 / hi) / math.log(hi / lo)


def keepalive_inventory_for_base(n_assets: int, quantile: float = 0.95) -> int:
    """MOD-KA inventory for a base of ``n_assets`` by the CDR-19 rule (at least one module)."""
    return max(1, keepalive_inventory(expected_fault_rate(n_assets), R.v("ka_park_frac"), R.v("ka_hold_yr"),
                                      R.v("ka_sustain_p"), quantile))


def monte_carlo(base: Scenario, n: int = 200, seed: int = 2026, sample: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    rows = []
    for k in range(n):
        sc = sample_scenario(base, rng) if sample else base
        m0, m1 = run_pair(sc, seed + 1000 * k)
        rows.append(dict(mtbf=sc.mtbf_yr, p_spare=sc.p_spare, t_survive=sc.t_survive_h, crew=sc.crew_missions_per_yr,
                         speed=sc.tsr_speed_kmh, tsr_mtbf=sc.tsr_mtbf_yr, frac_unp=sc.frac_unpowered,
                         A0=m0.availability, A1=m1.availability, dA=m1.availability - m0.availability,
                         lost0=m0.lost, lost1=m1.lost, eva0=m0.eva_crew_h, eva1=m1.eva_crew_h,
                         faults0=m0.faults, faults1=m1.faults, ka_demand=m1.ka_demand, ka_denied=m1.ka_denied,
                         ka_used=m1.ka_used, ka_hours=m1.ka_hours,
                         asset_yr0=m0.availability * sc.n_assets * sc.years,
                         asset_yr1=m1.availability * sc.n_assets * sc.years,
                         plost0=m0.lost - m0.lost_catastrophic, plost1=m1.lost - m1.lost_catastrophic,
                         mass0=m0.earth_mass_kg, mass1=m1.earth_mass_kg, resp=m1.mean_response_h,
                         util=m1.tsr_utilisation, tasks=m1.tasks_tsr, ok=m1.tasks_tsr_success))
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}
