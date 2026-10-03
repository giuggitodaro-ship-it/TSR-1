"""Static stability of TSR-1 under gravity, manipulator payloads and winch loads (directive §11, §26).

Frame: ground-fixed plane under the vehicle, x forward, y left, z up (normal to local ground).
The slope is represented by rotating the gravity vector: a longitudinal slope θx (nose up) and a
lateral slope θy (left side up).

For a set of external loads acting ON the vehicle (weights, line tensions, tool reactions) with
resultant force F and moment M about the origin, the ground reaction must pass through the centre
of pressure p on the ground plane:  p_x = −M_y / F_z,  p_y = M_x / F_z  (F_z < 0).
Tip-over stability requires p to lie inside the support polygon; the margin is the signed distance
from p to the nearest polygon edge. The tipping factor about the critical edge is the ratio of
restoring to overturning moments.

Sliding: the horizontal resultant must not exceed the available ground shear resistance
F_h ≤ Σ (c·A_i + N_i tan δ) + passive resistance of deployed spades/anchors.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from tsr1.environment.lunar import G_MOON


@dataclass
class Load:
    force: np.ndarray        # [N] acting on vehicle, ground frame
    point: np.ndarray        # [m] application point
    label: str = ""


@dataclass
class StabilityResult:
    cop: np.ndarray
    margin: float            # signed distance to nearest edge [m] (>0 stable)
    tip_factor: float        # restoring/overturning moment about critical edge (inf if no overturning)
    critical_edge: int
    f_normal: float          # total normal load on ground [N]
    f_horizontal: float      # horizontal resultant to be resisted [N]


def gravity_vector(theta_x: float = 0.0, theta_y: float = 0.0, g: float = G_MOON) -> np.ndarray:
    """Unit-mass gravity in the slope-fixed frame. θx>0: nose up (downhill = −x);
    θy>0: left side up (downhill = −y)."""
    gx = -g * math.sin(theta_x)
    gy = -g * math.sin(theta_y) * math.cos(theta_x)
    gz = -g * math.cos(theta_x) * math.cos(theta_y)
    return np.array([gx, gy, gz])


def weight(mass: float, point, theta_x=0.0, theta_y=0.0, label="") -> Load:
    return Load(mass * gravity_vector(theta_x, theta_y), np.asarray(point, float), label)


def convex_polygon(points) -> np.ndarray:
    """Counter-clockwise convex hull (monotone chain) of 2-D support points."""
    pts = sorted(map(tuple, np.asarray(points, float)[:, :2]))
    if len(pts) < 3:
        raise ValueError("support polygon needs ≥ 3 points")

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1])


def evaluate(loads: list[Load], support: np.ndarray) -> StabilityResult:
    F = np.sum([l.force for l in loads], axis=0)
    M = np.sum([np.cross(l.point, l.force) for l in loads], axis=0)
    if F[2] >= 0:
        return StabilityResult(np.array([np.nan, np.nan]), -np.inf, 0.0, -1, F[2], math.hypot(F[0], F[1]))
    p = np.array([-M[1] / F[2], M[0] / F[2]])
    poly = convex_polygon(support)
    n = len(poly)
    best_d, best_i, tipf = np.inf, -1, np.inf
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        e = b - a
        nrm = np.array([e[1], -e[0]]) / np.linalg.norm(e)   # outward normal for CCW polygon
        d = -np.dot(p - a, nrm)                              # >0 inside
        if d < best_d:
            best_d, best_i = d, i
    # tipping factor about the critical edge: split each load's moment about the edge axis
    a, b = poly[best_i], poly[(best_i + 1) % n]
    axis = np.append(b - a, 0.0)
    axis /= np.linalg.norm(axis)
    origin = np.append(a, 0.0)
    restoring, overturning = 0.0, 0.0
    for l in loads:
        m = np.dot(np.cross(l.point - origin, l.force), axis)
        # sign convention: for CCW polygon, moments with m < 0 about edge axis rotate the vehicle inward
        if m < 0:
            restoring += -m
        else:
            overturning += m
    tipf = restoring / overturning if overturning > 1e-9 else np.inf
    return StabilityResult(p, best_d, tipf, best_i, -F[2], math.hypot(F[0], F[1]))


@dataclass
class SupportConfig:
    """Ground contacts and their sliding resistance."""
    points: np.ndarray                 # (k, 2 or 3) contact points
    contact_area: float                # total contact area for cohesion term [m^2]
    tan_delta: float                   # interface friction coefficient
    cohesion: float                    # interface adhesion [Pa]
    passive_resistance: float = 0.0    # spades/anchors horizontal capacity [N]
    label: str = ""

    def sliding_capacity(self, normal: float) -> float:
        return self.cohesion * self.contact_area + normal * self.tan_delta + self.passive_resistance


def rectangle(length: float, width: float, x0: float = 0.0) -> np.ndarray:
    hl, hw = length / 2, width / 2
    return np.array([[x0 + hl, hw], [x0 + hl, -hw], [x0 - hl, -hw], [x0 - hl, hw]])
