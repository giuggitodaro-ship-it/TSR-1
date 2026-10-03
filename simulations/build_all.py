"""Rebuild every generated artefact of the TSR-1 study in dependency order.

    PYTHONPATH=src python simulations/build_all.py              # full Monte Carlo sizes (≈ 6 min)
    PYTHONPATH=src python simulations/build_all.py --quick      # reduced sizes (smoke test)
    PYTHONPATH=src python simulations/build_all.py --docs-only  # regenerate documents from existing results

Order: models/simulations → figures → materials matrix → component specs → trade-study documents → design freeze,
CDR, verdict and summaries → bibliography → paper. Each step reads only files written by earlier steps, so a
single run leaves the repository internally consistent.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    ("figures/make_figures.py", []),
    ("engineering/build_materials_matrix.py", []),
    ("engineering/build_specs.py", []),
    ("trade_studies/build_trade_docs.py", []),
    ("results/build_reports.py", []),
    ("paper/build_bib.py", []),
    ("paper/build_paper.py", []),
]


def run(script: str, args: list[str]) -> None:
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    print(f"→ {script} {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, str(ROOT / script), *args], check=True, cwd=ROOT, env=env)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--docs-only", action="store_true")
    a = ap.parse_args()
    if not a.docs_only:
        run("simulations/run_all.py", ["--quick"] if a.quick else [])
    for script, args in STEPS:
        run(script, args)
    print("all artefacts rebuilt")


if __name__ == "__main__":
    main()
