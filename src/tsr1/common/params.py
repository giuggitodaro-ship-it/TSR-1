"""Central parameter register (directive §34).

Every important numerical parameter is a :class:`Param` with value, unit, uncertainty range,
provenance class, source reference, derivation and owning subsystem. Models obtain values with
``REGISTRY.v("name")`` so that no important number lives only inside prose or code literals.
Calculated values produced by models are recorded with :meth:`Registry.calc` so they appear in the
exported register next to the inputs they derive from.

Provenance classes (directive §2):
    SOURCE      measured or specified externally (cite S0xx / L0xx)
    CALCULATED  derived mathematically in this project (cite model function)
    ASSUMPTION  engineering assumption (cite A-xx)
    DESIGN      design decision taken after a trade study (cite TS-xx)
    ESTIMATE    value with significant uncertainty (cite basis)
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Iterable, Optional

PROVENANCE = ("SOURCE", "CALCULATED", "ASSUMPTION", "DESIGN", "ESTIMATE")
LAST_UPDATE = "2026-10-03"


@dataclass(frozen=True)
class Param:
    name: str
    symbol: str
    value: float
    unit: str
    provenance: str
    source: str
    subsystem: str
    derivation: str = ""
    low: Optional[float] = None
    high: Optional[float] = None
    note: str = ""
    updated: str = LAST_UPDATE

    def __post_init__(self) -> None:
        if self.provenance not in PROVENANCE:
            raise ValueError(f"{self.name}: bad provenance {self.provenance!r}")
        if not self.source:
            raise ValueError(f"{self.name}: every parameter needs a source/derivation reference")
        if self.low is not None and self.high is not None:
            if not (self.low <= self.value <= self.high) and not math.isnan(self.value):
                raise ValueError(f"{self.name}: value {self.value} outside [{self.low}, {self.high}]")

    @property
    def range_str(self) -> str:
        if self.low is None and self.high is None:
            return ""
        return f"[{_fmt(self.low)}, {_fmt(self.high)}]"


def _fmt(x: Optional[float]) -> str:
    if x is None:
        return ""
    if isinstance(x, (int,)) or (isinstance(x, float) and x.is_integer() and abs(x) < 1e7):
        return str(int(x)) if float(x).is_integer() else str(x)
    return f"{x:.6g}"


@dataclass
class Registry:
    params: dict = field(default_factory=dict)

    def add(self, p: Param, overwrite: bool = False) -> Param:
        if p.name in self.params and not overwrite:
            old = self.params[p.name]
            if old != p:
                raise KeyError(f"parameter {p.name!r} already registered with different content")
            return old
        self.params[p.name] = p
        return p

    def define(self, name: str, symbol: str, value: float, unit: str, provenance: str, source: str,
               subsystem: str, derivation: str = "", low: Optional[float] = None,
               high: Optional[float] = None, note: str = "") -> float:
        """Register an input parameter and return its value."""
        self.add(Param(name, symbol, float(value), unit, provenance, source, subsystem, derivation,
                       low, high, note))
        return float(value)

    def calc(self, name: str, symbol: str, value: float, unit: str, derivation: str, subsystem: str,
             low: Optional[float] = None, high: Optional[float] = None, note: str = "") -> float:
        """Record a CALCULATED value (overwrites previous record of the same calculation)."""
        p = Param(name, symbol, float(value), unit, "CALCULATED", derivation, subsystem,
                  derivation, low, high, note)
        self.params[name] = p
        return float(value)

    def v(self, name: str) -> float:
        try:
            return self.params[name].value
        except KeyError as e:
            raise KeyError(f"unregistered parameter {name!r}") from e

    def get(self, name: str) -> Param:
        return self.params[name]

    def rng(self, name: str) -> tuple[float, float]:
        p = self.params[name]
        lo = p.low if p.low is not None else p.value
        hi = p.high if p.high is not None else p.value
        return lo, hi

    def with_value(self, name: str, value: float) -> "Registry":
        """Return a shallow copy with one value replaced (for sensitivity studies)."""
        new = Registry(dict(self.params))
        new.params[name] = replace(self.params[name], value=float(value), low=None, high=None)
        return new

    def __contains__(self, name: str) -> bool:
        return name in self.params

    def items(self) -> Iterable:
        return self.params.items()

    def export_csv(self, path: Path) -> int:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["name", "symbol", "value", "unit", "uncertainty_range", "provenance", "source",
                        "derivation", "subsystem", "note", "last_update"])
            for name in sorted(self.params, key=lambda n: (self.params[n].subsystem, n)):
                p = self.params[name]
                w.writerow([p.name, p.symbol, _fmt(p.value), p.unit, p.range_str, p.provenance, p.source,
                            p.derivation, p.subsystem, p.note, p.updated])
        return len(self.params)


REGISTRY = Registry()
