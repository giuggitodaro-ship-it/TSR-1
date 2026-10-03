"""Minimal dimensional-analysis helper used by tests to check key formulas (directive §34).

A :class:`Dim` is a vector of SI base-dimension exponents (M, L, T, I, Θ). Only multiplication,
division and integer/rational powers are needed to verify that model equations are dimensionally
consistent.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Dim:
    M: Fraction = Fraction(0)
    L: Fraction = Fraction(0)
    T: Fraction = Fraction(0)
    I: Fraction = Fraction(0)
    K: Fraction = Fraction(0)

    def __mul__(self, o: "Dim") -> "Dim":
        return Dim(self.M + o.M, self.L + o.L, self.T + o.T, self.I + o.I, self.K + o.K)

    def __truediv__(self, o: "Dim") -> "Dim":
        return Dim(self.M - o.M, self.L - o.L, self.T - o.T, self.I - o.I, self.K - o.K)

    def __pow__(self, p) -> "Dim":
        p = Fraction(p)
        return Dim(self.M * p, self.L * p, self.T * p, self.I * p, self.K * p)


DIMLESS = Dim()
M = Dim(M=Fraction(1))
L = Dim(L=Fraction(1))
T = Dim(T=Fraction(1))
I = Dim(I=Fraction(1))
K = Dim(K=Fraction(1))
N = M * L / T**2            # newton
Pa = N / L**2               # pascal
J = N * L                   # joule
W = J / T                   # watt
V = W / I                   # volt
OHM = V / I                 # ohm


def deg2rad(x: float) -> float:
    import math
    return x * math.pi / 180.0


def rad2deg(x: float) -> float:
    import math
    return x * 180.0 / math.pi


KWH = 3.6e6   # J per kWh
WH = 3600.0   # J per Wh
HOUR = 3600.0
DAY = 86400.0
YEAR = 365.25 * DAY
