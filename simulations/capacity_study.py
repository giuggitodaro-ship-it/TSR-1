"""Capacity study: when does one TSR-1 (and two keep-alive modules) saturate?

    PYTHONPATH=src python simulations/capacity_study.py

Sweeps fault load (assets × 1/MTBF) and evaluates 1 vs 2 TSR-1 units and 2/4/8 keep-alive modules with the
nominal (non-sampled) scenario. Writes simulations/results/capacity_study.json and .csv.
"""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tsr1.reliability.value_model import Scenario, monte_carlo  # noqa: E402

RES = ROOT / "simulations" / "results"


def main(n_runs: int = 60):
    p_env = json.loads((RES / "recovery.json").read_text())["p_env"]["R4 winch + 2 spades + 2 helical anchors"]["mid"]
    base = Scenario(recovery_envelope_p=p_env)
    rows = []
    for n_assets, mtbf in ((30, 4.0), (30, 1.5), (60, 4.0), (60, 1.5), (60, 1.0)):
        for n_tsr in (1, 2):
            for ka in (2, 4, 8):
                r = monte_carlo(replace(base, n_assets=n_assets, mtbf_yr=mtbf, n_tsr=n_tsr, keepalive_modules=ka),
                                n=n_runs, seed=777, sample=False)
                rows.append(dict(n_assets=n_assets, mtbf_yr=mtbf, faults_per_yr=n_assets / mtbf, n_tsr=n_tsr,
                                 keepalive_modules=ka, dA=float(np.mean(r["dA"])), lost0=float(np.mean(r["lost0"])),
                                 lost1=float(np.mean(r["lost1"])), mass_avoided_kg=float(np.mean(r["mass0"] - r["mass1"])),
                                 response_h=float(np.nanmean(r["resp"])), utilisation=float(np.mean(r["util"]))))
                print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rows[-1].items()}, flush=True)
    (RES / "capacity_study.json").write_text(json.dumps(rows, indent=1))
    with open(RES / "capacity_study.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
