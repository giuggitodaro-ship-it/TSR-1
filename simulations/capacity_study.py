"""Capacity study: when does one TSR-1 (and its keep-alive inventory) saturate?

    PYTHONPATH=src python simulations/capacity_study.py      (also called by run_all.py)

Sweeps fault load (assets × 1/MTBF) and evaluates 1 vs 2 TSR-1 units and 2/4/8 keep-alive modules with the
nominal (non-sampled) scenario. Reports total losses and *preventable* losses (excluding non-serviceable
"catastrophic" faults, whose number grows with operating exposure, i.e. with availability itself), Earth mass per
available asset-year, keep-alive demand, and the keep-alive inventory given by the analytic rule
``value_model.keepalive_inventory`` (CDR-19). Writes simulations/results/capacity_study.json and .csv.
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
from tsr1.reliability.value_model import YEAR_H, Scenario, keepalive_inventory, monte_carlo  # noqa: E402

RES = ROOT / "simulations" / "results"
CASES = ((30, 4.0), (30, 1.5), (60, 4.0), (60, 1.5), (60, 1.0))


def main(n_runs: int = 60, seed: int = 777, verbose: bool = True) -> list[dict]:
    p_env = json.loads((RES / "recovery.json").read_text())["p_env"]["R4 winch + 2 spades + 2 helical anchors"]["mid"]
    base = Scenario(recovery_envelope_p=p_env)
    rows = []
    for n_assets, mtbf in CASES:
        for n_tsr in (1, 2):
            for ka in (2, 4, 8):
                sc = replace(base, n_assets=n_assets, mtbf_yr=mtbf, n_tsr=n_tsr, keepalive_modules=ka)
                r = monte_carlo(sc, n=n_runs, seed=seed, sample=False)
                f1 = float(np.mean(r["faults1"])) / sc.years
                park = float(np.sum(r["ka_demand"]) / max(1.0, np.sum(r["faults1"])))
                hold = float(np.sum(r["ka_hours"]) / max(1.0, np.sum(r["ka_used"])) / YEAR_H)
                rows.append(dict(n_assets=n_assets, mtbf_yr=mtbf, faults_per_yr_nominal=n_assets / mtbf,
                                 n_tsr=n_tsr, keepalive_modules=ka,
                                 dA=float(np.mean(r["dA"])), lost0=float(np.mean(r["lost0"])),
                                 lost1=float(np.mean(r["lost1"])), plost0=float(np.mean(r["plost0"])),
                                 plost1=float(np.mean(r["plost1"])), faults0=float(np.mean(r["faults0"])),
                                 faults1=float(np.mean(r["faults1"])),
                                 mass_avoided_kg=float(np.mean(r["mass0"] - r["mass1"])),
                                 kg_per_asset_yr0=float(np.mean(r["mass0"] / r["asset_yr0"])),
                                 kg_per_asset_yr1=float(np.mean(r["mass1"] / r["asset_yr1"])),
                                 ka_demand=float(np.mean(r["ka_demand"])), ka_denied=float(np.mean(r["ka_denied"])),
                                 ka_used=float(np.mean(r["ka_used"])), park_fraction=park, ka_hold_yr=hold,
                                 ka_rule_q95=keepalive_inventory(f1, park, hold, sc.ka_sustain_p, 0.95),
                                 response_h=float(np.nanmean(r["resp"])), utilisation=float(np.mean(r["util"]))))
                if verbose:
                    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rows[-1].items()}, flush=True)
    (RES / "capacity_study.json").write_text(json.dumps(rows, indent=1))
    with open(RES / "capacity_study.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    main()
