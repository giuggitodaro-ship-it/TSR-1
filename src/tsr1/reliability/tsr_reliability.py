"""TSR-1 self-reliability: redundancy, degraded modes and ORU-level repair (directive §23, §24).

Monte Carlo over 10 years. Each ORU class has a calendar failure rate (ESTIMATE, wide range — no lunar
data). Capability states:
  FULL      all functions available
  DEGRADED  mobility ≥ 5/6 wheels and ≥ one safety computer and ≥ one comm link and power OK, but some
            servicing function lost (arm, crane, winch, PTM, autonomy computer)
  LOST      mobility < 4/6 driven wheels, or both safety computers, or all comm links, or battery < 2/4
            modules, or PCDU < 2/3 converters
Failed ORUs are replaced after ``repair_days`` if a spare is available (probability p_spare_tsr) — by a
peer TSR (if n_peer ≥ 1) or by crew/Earth-supplied spare otherwise (longer delay).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from tsr1.common.params import REGISTRY as R

SUB = "reliability"

# ORU class: (count, required_for_full, failure rate per unit per year (nominal), low, high)
ORU_CLASSES = {
    "drive_unit":        (6, 6, 0.030, 0.010, 0.090),
    "steer_unit":        (6, 6, 0.020, 0.007, 0.060),
    "dexterous_arm":     (1, 1, 0.080, 0.030, 0.240),
    "crane":             (1, 1, 0.050, 0.020, 0.150),
    "winch":             (1, 1, 0.030, 0.010, 0.090),
    "autonomy_computer": (1, 1, 0.050, 0.020, 0.150),
    "safety_computer":   (2, 2, 0.020, 0.007, 0.060),
    "battery_module":    (4, 4, 0.010, 0.003, 0.030),
    "pcdu_converter":    (3, 3, 0.015, 0.005, 0.045),
    "ptm":               (1, 1, 0.040, 0.015, 0.120),
    "lidar":             (2, 2, 0.050, 0.020, 0.150),
    "camera":            (10, 10, 0.020, 0.007, 0.060),
    "comm_link":         (3, 3, 0.030, 0.010, 0.090),
    "thermal_loop":      (1, 1, 0.010, 0.003, 0.030),
}
for k, (n, req, lam, lo, hi) in ORU_CLASSES.items():
    R.define(f"lambda_{k}", f"λ_{k}", lam, "1/yr", "ESTIMATE",
             "A: calendar failure rate incl. dust/thermal cycling; no lunar data (literature gap L-3)", SUB,
             f"{n} unit(s)", low=lo, high=hi)


@dataclass
class TsrRelResult:
    p_capable_10yr: float          # P(not LOST at end of 10 yr)
    p_full_10yr: float
    availability_full: float       # time-average fraction FULL
    availability_capable: float    # time-average fraction not LOST
    fault_rate_per_yr: float       # mean repairable-fault rate (for value model MTBF_T)
    mean_outage_days: float


def _state(counts_ok: dict) -> int:
    """0 = LOST, 1 = DEGRADED, 2 = FULL."""
    if (counts_ok["drive_unit"] < 4 or counts_ok["safety_computer"] < 1 or counts_ok["comm_link"] < 1
            or counts_ok["battery_module"] < 2 or counts_ok["pcdu_converter"] < 2):
        return 0
    full = all(counts_ok[k] >= ORU_CLASSES[k][1] for k in ORU_CLASSES)
    if full:
        return 2
    return 1


def simulate_tsr(years: float = 10.0, n_runs: int = 2000, repair_days: float = 30.0, p_spare_tsr: float = 0.85,
                 peer: bool = False, seed: int = 11, sample_rates: bool = True) -> TsrRelResult:
    rng = np.random.default_rng(seed)
    T = years * 365.25
    cap_end = full_end = 0
    a_full = a_cap = 0.0
    faults_total = 0
    outage_total = 0.0
    rep = min(repair_days, 7.0) if peer else repair_days      # peer TSR swaps ORUs within ~a week
    for _ in range(n_runs):
        events = []
        for k, (n, req, lam, lo, hi) in ORU_CLASSES.items():
            lam_k = np.exp(rng.uniform(np.log(lo), np.log(hi))) if sample_rates else lam
            for u in range(n):
                t = rng.exponential(365.25 / lam_k)
                while t < T:
                    events.append((t, k))
                    faults_total += 1
                    if rng.random() < p_spare_tsr:
                        d = rng.exponential(rep)
                        events.append((t + d, "+" + k))
                        outage_total += d
                        t = t + d + rng.exponential(365.25 / lam_k)
                    else:
                        outage_total += T - t
                        break
        events.sort()
        ok = {k: ORU_CLASSES[k][0] for k in ORU_CLASSES}
        t_prev, st = 0.0, 2
        lost = False
        for t, k in events:
            if t > T:
                break
            dt = t - t_prev
            a_full += dt * (st == 2)
            a_cap += dt * (st >= 1)
            if k.startswith("+"):
                ok[k[1:]] += 1
            else:
                ok[k] -= 1
            st = _state(ok)
            t_prev = t
            if st == 0:
                lost = True
                # a lost TSR cannot self-repair; peer/crew recovery may still occur (repair events continue)
        dt = T - t_prev
        a_full += dt * (st == 2)
        a_cap += dt * (st >= 1)
        cap_end += st >= 1
        full_end += st == 2
    return TsrRelResult(cap_end / n_runs, full_end / n_runs, a_full / (n_runs * T), a_cap / (n_runs * T),
                        faults_total / (n_runs * years), outage_total / max(faults_total, 1))


SERVICING_CRITICAL = ("dexterous_arm", "autonomy_computer", "ptm", "crane", "winch", "thermal_loop")


def critical_fault_rate(which: str = "nominal") -> float:
    """Rate [1/yr] of single-string faults that remove a servicing function (value-model TSR outages)."""
    col = {"nominal": 2, "low": 3, "high": 4}[which]
    return sum(ORU_CLASSES[k][col] * ORU_CLASSES[k][0] for k in SERVICING_CRITICAL)
