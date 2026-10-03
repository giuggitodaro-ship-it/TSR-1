"""Servicing success probability by asset compatibility level (directive §7).

Each service task is decomposed into sequential steps; the probability that the step succeeds
depends on how well the asset supports robotic servicing at that level (L0–L3). Step probabilities
are ENGINEERING ASSUMPTIONS (no lunar servicing statistics exist, literature gap L-3) expressed as
ranges; the nominal value is the range midpoint. Task success allows a limited number of attempts
(independent retries of the whole sequence after re-planning).

    P_task(L) = 1 − (1 − Π_k p_k(L))^n_attempts

The same structure gives crew-EVA success with crew step probabilities (crew dexterity makes L0/L1
interfaces far more workable than for robots, but EVA is only possible while crew are present).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tsr1.common.params import REGISTRY as R

R.define("robot_step_factor", "k_skill", 1.0, "-", "ASSUMPTION",
         "A-31 / CDR-09: multiplier on every robotic step probability (pessimism case 0.9)", "reliability",
         "robot dexterity/maturity factor", low=0.9, high=1.0)

LEVELS = ("L0", "L1", "L2", "L3")

# step -> level -> (low, high) success probability (ENGINEERING ASSUMPTION A-31)
ROBOT_STEPS = {
    "approach_position":  {"L0": (0.95, 0.99), "L1": (0.96, 0.99), "L2": (0.97, 0.995), "L3": (0.98, 0.999)},
    "diagnose":           {"L0": (0.30, 0.60), "L1": (0.70, 0.90), "L2": (0.80, 0.92), "L3": (0.92, 0.98)},
    "engage_interface":   {"L0": (0.10, 0.40), "L1": (0.40, 0.70), "L2": (0.85, 0.95), "L3": (0.95, 0.99)},
    "release_fasteners":  {"L0": (0.05, 0.30), "L1": (0.30, 0.60), "L2": (0.85, 0.95), "L3": (0.95, 0.99)},
    "extract_insert_oru": {"L0": (0.05, 0.30), "L1": (0.40, 0.70), "L2": (0.85, 0.95), "L3": (0.92, 0.98)},
    "mate_connectors":    {"L0": (0.10, 0.40), "L1": (0.50, 0.80), "L2": (0.85, 0.95), "L3": (0.95, 0.99)},
    "functional_test":    {"L0": (0.85, 0.95), "L1": (0.90, 0.97), "L2": (0.92, 0.98), "L3": (0.95, 0.99)},
    "clean_surface":      {"L0": (0.75, 0.92), "L1": (0.80, 0.94), "L2": (0.85, 0.96), "L3": (0.90, 0.98)},
    "connect_power":      {"L0": (0.02, 0.15), "L1": (0.60, 0.85), "L2": (0.85, 0.95), "L3": (0.95, 0.99)},
    "attach_tow_point":   {"L0": (0.40, 0.75), "L1": (0.70, 0.90), "L2": (0.80, 0.95), "L3": (0.90, 0.98)},
}
CREW_STEPS = {
    "approach_position":  {"L0": (0.97, 0.995), "L1": (0.98, 0.995), "L2": (0.98, 0.999), "L3": (0.99, 0.999)},
    "diagnose":           {"L0": (0.60, 0.85), "L1": (0.80, 0.95), "L2": (0.85, 0.95), "L3": (0.92, 0.98)},
    "engage_interface":   {"L0": (0.50, 0.80), "L1": (0.80, 0.95), "L2": (0.90, 0.98), "L3": (0.95, 0.99)},
    "release_fasteners":  {"L0": (0.40, 0.75), "L1": (0.75, 0.92), "L2": (0.90, 0.98), "L3": (0.95, 0.99)},
    "extract_insert_oru": {"L0": (0.40, 0.75), "L1": (0.75, 0.92), "L2": (0.90, 0.98), "L3": (0.95, 0.99)},
    "mate_connectors":    {"L0": (0.50, 0.80), "L1": (0.80, 0.95), "L2": (0.90, 0.98), "L3": (0.95, 0.99)},
    "functional_test":    {"L0": (0.88, 0.96), "L1": (0.90, 0.97), "L2": (0.92, 0.98), "L3": (0.95, 0.99)},
    "clean_surface":      {"L0": (0.85, 0.97), "L1": (0.88, 0.97), "L2": (0.90, 0.98), "L3": (0.92, 0.99)},
    "connect_power":      {"L0": (0.20, 0.50), "L1": (0.75, 0.92), "L2": (0.90, 0.98), "L3": (0.95, 0.99)},
    "attach_tow_point":   {"L0": (0.60, 0.85), "L1": (0.80, 0.95), "L2": (0.85, 0.97), "L3": (0.90, 0.98)},
}
TASKS = {
    "oru_replace": ("approach_position", "diagnose", "engage_interface", "release_fasteners", "extract_insert_oru",
                    "mate_connectors", "functional_test"),
    "dust_clean": ("approach_position", "clean_surface", "functional_test"),
    "emergency_power": ("approach_position", "connect_power"),
    "recovery_rig": ("approach_position", "attach_tow_point"),
    "inspection": ("approach_position", "diagnose"),
}
ATTEMPTS = {"oru_replace": 2, "dust_clean": 2, "emergency_power": 2, "recovery_rig": 2, "inspection": 1}


def step_p(step: str, level: str, actor: str = "robot", rng: np.random.Generator | None = None) -> float:
    table = ROBOT_STEPS if actor == "robot" else CREW_STEPS
    lo, hi = table[step][level]
    k = R.v("robot_step_factor") if actor == "robot" else 1.0
    if rng is None:
        return k * 0.5 * (lo + hi)
    return k * float(rng.uniform(lo, hi))


def task_success(task: str, level: str, actor: str = "robot", rng: np.random.Generator | None = None,
                 attempts: int | None = None) -> float:
    p = 1.0
    for s in TASKS[task]:
        p *= step_p(s, level, actor, rng)
    n = ATTEMPTS[task] if attempts is None else attempts
    return 1.0 - (1.0 - p) ** n


@dataclass
class SuccessTable:
    robot: dict
    crew: dict


def success_table(rng: np.random.Generator | None = None) -> SuccessTable:
    rob = {t: {L: task_success(t, L, "robot", rng) for L in LEVELS} for t in TASKS}
    crw = {t: {L: task_success(t, L, "crew", rng) for L in LEVELS} for t in TASKS}
    return SuccessTable(rob, crw)


def success_distribution(task: str, level: str, actor: str = "robot", n: int = 4000, seed: int = 7):
    rng = np.random.default_rng(seed)
    return np.array([task_success(task, level, actor, rng) for _ in range(n)])
