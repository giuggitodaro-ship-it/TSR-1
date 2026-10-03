"""Generate all TSR-1 technical figures from simulation results (directive §40).

    PYTHONPATH=src python figures/make_figures.py

Reads simulations/results/*.json and the baseline configuration; writes figures/*.png and copies to
paper/figures/. Palette: validated categorical order (blue, orange, aqua, yellow, magenta, green);
thin marks, recessive hairline grid, legends for ≥ 2 series plus sparse direct labels, no dual axes.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RES = ROOT / "simulations" / "results"
OUT = ROOT / "figures"

SURF = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
GOOD, WARN, CRIT = "#0ca30c", "#fab219", "#d03b3b"
FOOT = "TODARO CORP. TSR-1 — independent conceptual study (not affiliated with NASA/ESA)"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-", "axes.spines.top": False,
    "axes.spines.right": False, "lines.linewidth": 2.0, "lines.solid_capstyle": "round", "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
    "figure.dpi": 110, "savefig.dpi": 160,
})


def J(name):
    return json.loads((RES / name).read_text())


def save(fig, name):
    # place the footer below everything already drawn (incl. rotated tick labels) so it never overlaps a label
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    y = min(-0.01, bb.y0 / fig.get_figheight() - 0.01)
    fig.text(0.01, y, FOOT, fontsize=7, color=MUTED, ha="left", va="top")
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def box(ax, x, y, w, h, text, fc="#ffffff", ec=INK2, fs=8.5, bold=False, tc=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, p, q, color=INK2, style="-|>", lw=1.0, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=10, color=color, lw=lw, linestyle=ls))


def blank(ax):
    ax.set_axis_off()
    ax.grid(False)


# ======================================================================================== diagrams
def fig_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 7.2))
    blank(ax)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.4)
    ax.set_title("TSR-1 system architecture and external interfaces")
    bat_kwh = J("baseline_summary.json")["battery"]["usable_eol_kwh"]
    box(ax, 3.4, 2.6, 5.2, 2.4, "", fc="#f4f3f0")
    ax.text(6.0, 4.8, "TSR-1 vehicle", ha="center", fontsize=10, fontweight="bold")
    subs = [("Mobility\n6-wheel rocker-bogie\nbody lowering", 3.55, 3.6), ("Manipulation\n2× 7-DOF dex arms\n+ 150 kg crane", 5.25, 3.6),
            ("Service spine\n6 standard slots\n150 kg", 6.95, 3.6), (f"Power\n{bat_kwh:.0f} kWh Li-ion (EOL)\n120 VDC bus · PTM", 3.55, 2.75),
            ("Avionics & autonomy\nHPSC + 2× safety RT", 5.25, 2.75), ("Recovery\n4 kN winch, spades,\nhelical anchors", 6.95, 2.75)]
    for t, x, y in subs:
        box(ax, x, y, 1.55, 0.78, t, fs=7.5)
    ext = [("Disabled / serviced assets\nL0–L3 (rovers, towers, arrays,\nstorage, science, landers)", 9.3, 3.3, C[1]),
           ("Lunar grid / charging node\n3 kVAC + UMIC → 120 VDC\n(ISPSIS, < 100 m exchange)", 0.2, 4.6, C[3]),
           ("Base surface network\n~10 km comm-tower cells\n(LTE-class) + peer mesh", 0.2, 3.0, C[0]),
           ("Lunar relay (LunaNet /\nMoonlight) + DTE ≈ 51 %\nDTN store-and-forward", 0.2, 1.4, C[0]),
           ("Earth MOC + local base ops\ntask-level approvals at\nhold points", 4.2, 0.4, C[2]),
           ("Crew (intermittent)\nTSR ORU repair, local\nteleop backup", 9.3, 1.3, C[2]),
           ("Peer TSR-class vehicle\nmutual ORU servicing\ngrapple fixtures", 9.3, 5.4, C[4]),
           ("Spares depot / landers\nORUs, keep-alive modules\n(MOD-KA)", 4.2, 6.1, C[5])]
    for t, x, y, col in ext:
        box(ax, x, y, 2.5, 1.0, t, ec=col, fs=7.5)
    arrow(ax, (8.6, 3.8), (9.3, 3.8), style="<|-|>")
    ax.text(8.95, 3.88, "mech · power\ndata · inspect", fontsize=6.5, ha="center", va="bottom", color=INK2)
    arrow(ax, (2.7, 5.1), (3.4, 4.6), style="<|-|>")
    arrow(ax, (2.7, 3.5), (3.4, 3.5), style="<|-|>")
    arrow(ax, (2.7, 1.9), (3.4, 2.8), style="<|-|>")
    arrow(ax, (5.45, 1.4), (5.45, 2.6), style="<|-|>")
    arrow(ax, (9.3, 1.8), (8.6, 2.8), style="<|-|>")
    arrow(ax, (9.3, 5.8), (8.6, 4.8), style="<|-|>")
    arrow(ax, (5.45, 6.1), (5.45, 5.0), style="<|-|>")
    save(fig, "fig01_system_architecture.png")


def fig_rover_configuration(cfg, base):
    o = cfg.opts
    r, b = o.wheel_r, o.wheel_b
    xs = cfg.vehicle.axle_x
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw=dict(width_ratios=[1.35, 1]))
    # ---- side view
    ax = axs[0]
    ax.set_title("Side view (deployed, crane and arm stowed) — dimensions in m")
    ax.set_aspect("equal")
    ax.axhline(0, color=INK2, lw=1)
    gc = o.ground_clearance
    ax.add_patch(Rectangle((-o.wheelbase / 2, gc), o.wheelbase, 0.45, fc="#e9eef6", ec=INK2, lw=1))
    ax.text(0, gc + 0.32, "chassis torque box / WEB", ha="center", va="center", fontsize=7.5, color=INK2)
    for x in xs:
        ax.add_patch(Circle((x, r), r, fc="#d9d8d3", ec=INK2, lw=1))
        ax.add_patch(Circle((x, r), 0.08, fc=INK2, ec=INK2))
        ax.add_patch(Rectangle((x - r - 0.05, 2 * r + 0.02), 2 * r + 0.1, 0.05, fc=MUTED, ec="none"))
    # rocker-bogie links
    ax.plot([xs[0], 0.2, xs[2] + 0.65], [r, 0.62, 0.62], color=INK2, lw=2)
    ax.plot([xs[1], xs[2] + 0.65, xs[2]], [r, 0.62, r], color=INK2, lw=2)
    # mast
    xm = o.wheelbase / 2 - 0.2
    ax.plot([xm, xm], [gc + 0.45, 2.1], color=INK2, lw=3)
    ax.add_patch(Rectangle((xm - 0.18, 2.05), 0.36, 0.14, fc=C[0], ec="none"))
    ax.text(xm + 0.25, 2.12, "NavCam/IR/LEDs", fontsize=7, va="center")
    # spine & payload
    ax.add_patch(Rectangle((-0.9, gc + 0.45), 1.4, 0.3, fc="#f3e1d6", ec=C[1], lw=1))
    ax.text(-0.2, gc + 0.6, "service spine", ha="center", fontsize=7)
    # crane stowed
    ax.plot([0.3, 1.3], [gc + 0.82, gc + 0.82], color=C[2], lw=3)
    ax.text(0.8, gc + 0.9, "crane boom (stowed)", ha="center", fontsize=7)
    # arm stowed
    ax.plot([xm - 0.05, 0.55, 0.9], [gc + 0.55, gc + 0.62, gc + 0.62], color=C[0], lw=3)
    # winch & spades
    ax.add_patch(Rectangle((-o.wheelbase / 2 - 0.25, 0.18), 0.2, 0.18, fc=C[3], ec="none"))
    ax.annotate("winch, fairlead 0.25", xy=(-o.wheelbase / 2 - 0.15, 0.27), xytext=(-2.35, 1.15), fontsize=7,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.plot([-o.wheelbase / 2 - 0.2, -o.wheelbase / 2 - 0.35], [gc + 0.1, 0.05], color=C[1], lw=3)
    # dims
    L = o.wheelbase + 2 * r + 0.1
    ax.annotate("", (-L / 2, -0.25), (L / 2, -0.25), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(0, -0.36, f"overall length {L:.2f}", ha="center", fontsize=8)
    ax.annotate("", (xs[0], -0.12), (xs[2], -0.12), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(0, -0.19, f"wheelbase {o.wheelbase:.2f}", ha="center", fontsize=7)
    ax.annotate("", (2.05, 0), (2.05, 2.19), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(2.1, 1.1, "mast height 2.19", fontsize=7, rotation=90, va="center")
    ax.annotate("", (-1.65, 0), (-1.65, gc), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(-1.75, gc / 2, f"clearance {gc:.2f}\n(lowered 0.10)", fontsize=7, ha="right", va="center")
    ax.text(0.0, r - 0.24, f"Ø{2*r:.2f} × {b:.2f}\nTi wheels", fontsize=6.5, ha="center", va="center")
    ax.set_xlim(-2.4, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.grid(False)
    ax.set_xlabel("x [m] (forward →)")
    ax.set_ylabel("z [m]")
    # ---- top view
    ax = axs[1]
    ax.set_title("Top view with component CoM positions (marker area ∝ mass)")
    ax.set_aspect("equal")
    W = o.track + b
    ax.add_patch(Rectangle((-o.wheelbase / 2, -0.75), o.wheelbase, 1.5, fc="#e9eef6", ec=INK2, lw=1))
    for x in xs:
        for s in (1, -1):
            ax.add_patch(Rectangle((x - r, s * o.track / 2 - b / 2), 2 * r, b, fc="#d9d8d3", ec=INK2, lw=0.8))
    groups = {}
    for c_ in cfg.comps:
        groups.setdefault(c_.subsystem, []).append(c_)
    subs = sorted(groups, key=lambda s: -sum(cc.predicted for cc in groups[s]))
    for i, s in enumerate(subs[:8]):
        pts = np.array([cc.pos for cc in groups[s]])
        ms = np.array([cc.predicted for cc in groups[s]])
        ax.scatter(pts[:, 0], pts[:, 1], s=np.clip(ms * 3, 8, 400), color=C[i % 8], alpha=0.75,
                   edgecolors=SURF, linewidths=1.5, label=s, zorder=3)
    com = cfg.com()
    ax.plot(com[0], com[1], marker="P", ms=12, color=INK, mec=SURF, mew=1.5, zorder=5)
    ax.text(com[0] + 0.1, com[1] - 0.18, f"CoM ({com[0]:+.2f}, {com[1]:+.2f}, z={com[2]:.2f})", fontsize=7.5)
    ax.annotate("", (-W / 2 * 0 - 1.95, -W / 2), (-1.95, W / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(-2.05, 0, f"overall width {W:.2f}\ntrack {o.track:.2f}", rotation=90, va="center", ha="right", fontsize=7)
    ax.set_xlim(-2.5, 2.2)
    ax.set_ylim(-1.5, 1.5)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=4, fontsize=7.5)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    save(fig, "fig02_rover_configuration_dimensions.png")


def fig_layout_table(cfg):
    """Plan view of the deck drawn from design.layout (the same geometry the mass model and closure use)."""
    from tsr1.common.params import REGISTRY as R
    from tsr1.design.layout import tool_rack
    lay = cfg.derived["layout"]
    L, Wd = cfg.opts.wheelbase, min(cfg.opts.track - 0.5, 1.5)
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.set_aspect("equal")
    ax.set_title("Deck layout, plan view to scale (front → right); WEB below deck shown dashed")
    ax.add_patch(Rectangle((-L / 2, -Wd / 2), L, Wd, fc="#f4f3f0", ec=INK2, lw=1.2))
    styles = {"radiator": (C[0], "Radiator (zenith, OSR + EDS film)"), "service_spine": (C[1], "Service spine\n2 × 3 slots of 0.45 m"),
              "crane_turntable": (C[2], "Crane\nturntable"), "sensor_mast_base": (C[4], "Mast"),
              "dex_arm_R_base": (C[3], "Dex arm R\n(upright stow)"), "dex_arm_L_base": (C[3], "Dex arm L\n(upright stow)")}
    for k, it in lay.items():
        col, lab = styles[k]
        ax.add_patch(Rectangle((it.x0, it.y0), it.x1 - it.x0, it.y1 - it.y0, fc=SURF, ec=col, lw=1.8, zorder=2))
        cx, cy = it.centre
        txt = f"{lab}\n{it.area:.2f} m²" if k in ("radiator", "service_spine") else lab
        dy = {"radiator": 0.56, "service_spine": 0.36}.get(k, 0.0)          # keep clear of the boom line and WEB outline
        ax.text(cx, cy + dy, txt, ha="center", va="center", fontsize=7 if it.area > 0.1 else 6, zorder=6,
                bbox=dict(fc=SURF, ec="none", pad=1.5) if dy else None)
    sp = lay["service_spine"]
    for r_ in range(2):
        for c_ in range(3):
            ax.add_patch(Rectangle((sp.x0 + r_ * 0.45 + 0.02, sp.y0 + c_ * 0.45 + 0.02), 0.41, 0.41, fc="none",
                                   ec=C[1], lw=0.6, ls=":", zorder=2))
    # stowed crane boom (rearward over the spine)
    xb = cfg.derived["crane_base"][0]
    ax.plot([xb, xb - cfg.opts.crane_boom], [0, 0], color=C[2], lw=2.5, alpha=0.8, zorder=4)
    ax.text(-0.75, -0.07, "crane boom (stowed, rearward)", fontsize=6.5, color=INK2, ha="center", va="top", zorder=6)
    # WEB below deck
    wl, ww = R.v("web_L"), R.v("web_W")
    wx = R.v("web_x")
    ax.add_patch(Rectangle((wx - wl / 2, -ww / 2), wl, ww, fc="none", ec=MUTED, lw=1.2, ls="--", zorder=5))
    ax.text(wx, -ww / 2 + 0.05, f"WEB below deck {wl:.1f} × {ww:.1f} × {R.v('web_H'):.2f} m", ha="center", va="bottom", fontsize=6.5,
            color=MUTED)
    tr = tool_rack(L, Wd)
    ax.add_patch(Rectangle((tr.x0, tr.y0), tr.x1 - tr.x0, tr.y1 - tr.y0, fc=C[5], ec="none", alpha=0.6))
    ax.text(tr.x1 + 0.05, 0, "tool rack on\nfront face", fontsize=6.5, va="center")
    ax.annotate("", (-L / 2, -Wd / 2 - 0.25), (L / 2, -Wd / 2 - 0.25), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(0, -Wd / 2 - 0.3, f"deck {L:.1f} m", ha="center", va="top", fontsize=8)
    ax.annotate("", (-L / 2 - 0.35, -Wd / 2), (-L / 2 - 0.35, Wd / 2), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax.text(-L / 2 - 0.4, 0, f"{Wd:.1f} m", rotation=90, ha="right", va="center", fontsize=8)
    from tsr1.design.layout import check_layout
    chk = check_layout(lay, L, Wd)
    ax.text(0, -Wd / 2 - 0.5, f"deck items {chk['used_area']:.2f} of {chk['deck_area']:.2f} m²; "
            f"{'no overlaps' if chk['ok'] else 'OVERLAPS: ' + str(chk['overlaps'])} (closure GEOM-5)",
            ha="center", va="top", fontsize=7, color=INK2)
    ax.set_xlim(-L / 2 - 0.6, L / 2 + 0.45)
    ax.set_ylim(-Wd / 2 - 0.65, Wd / 2 + 0.15)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    save(fig, "fig03_subsystem_layout.png")


def fig_service_spine():
    fig, ax = plt.subplots(figsize=(13, 2.9))
    blank(ax)
    ax.set_xlim(0, 13)
    ax.set_ylim(1.75, 3.95)
    ax.set_title("Modular service spine: slot interface and module library")
    ax.add_patch(Rectangle((0.5, 2.0), 6.2, 0.35, fc="#e9eef6", ec=INK2))
    ax.text(3.6, 2.17, "Al 7075 rail · 120 VDC (≤ 1 kW/slot) · Ethernet/TSN data · 1-wire ID · passive thermal pad",
            ha="center", va="center", fontsize=7.5)
    mods = [("MOD-ORU\ncradle", C[1], 1), ("MOD-KA keep-alive\n(double slot)", C[3], 2), ("MOD-REC\nrecovery kit", C[2], 1),
            ("MOD-RPT\nrepeater", C[0], 1), ("ORU spare", C[4], 1)]
    slot = 0
    for t, col, n in mods:
        x = 0.6 + slot * 1.02
        w = 0.9 + (n - 1) * 1.02
        ax.add_patch(Rectangle((x, 2.4), w, 1.0, fc=SURF, ec=col, lw=1.6))
        ax.text(x + w / 2, 2.9, t, ha="center", va="center", fontsize=7)
        for k in range(n):
            ax.add_patch(Rectangle((x + k * 1.02 + 0.25, 2.35), 0.4, 0.07, fc=INK2))
        slot += n
    ax.text(3.6, 3.65, "6 slots (drawn in a row; arranged 2 × 3 on the deck, Fig. 3), each: androgynous latch (HOTDOCK-class), "
            "robot-graspable handle + fiducial", ha="center", fontsize=7.5)
    m_ka = J("value_model.json")["keepalive_module_kg"]
    lib = [f"Module limits per slot: ≤ 40 kg, 0.45 × 0.45 m footprint, ≤ 0.6 m high (MOD-KA {m_ka:.0f} kg over 2 slots); ≤ 150 kg total",
           "Installation/removal by either dex arm (≤ 20 kg) or crane + arm (≤ 150 kg)",
           "Same interface on asset ORUs (L2/L3) and on host vehicles → modules portable to\n   utility-rover / LTV hosts (service-kit option, CDR-01)",
           "Excluded: fluid servicing module (no fluid-serviceable asset identified)"]
    for i, t in enumerate(lib):
        ax.text(7.1, 3.55 - i * 0.42 - (0.12 if i == 3 else 0), "• " + t, fontsize=7.5, color=INK, va="top")
    save(fig, "fig04_service_spine.png")


def fig_workspace(cfg):
    from tsr1.manipulation.arm import workspace_samples
    dex = cfg.derived["dex"]
    crane = cfg.derived["crane"]
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    fig.subplots_adjust(wspace=0.3)
    ax = axs[0]
    ax.set_title("Dexterous-arm workspace (pitch plane)")
    ax.set_aspect("equal")
    xa, za = cfg.opts.wheelbase / 2 - 0.15, 1.05
    pts = workspace_samples(dex.spec, base=(xa, za), n=45)
    pts = pts[pts[:, 1] >= 0.0]                       # the ground bounds the workspace
    ax.scatter(pts[:, 0], pts[:, 1], s=2, color=C[0], alpha=0.25, label="reachable points (joint sweep)")
    ax.axhline(0, color=INK2, lw=1)
    ax.add_patch(Rectangle((-cfg.opts.wheelbase / 2, cfg.opts.ground_clearance), cfg.opts.wheelbase, 0.45,
                           fc="#e9eef6", ec=INK2))
    ax.plot(xa, za, "o", ms=8, color=INK, mec=SURF, mew=2)
    ax.text(xa + 0.05, za + 0.08, "shoulder", fontsize=7.5)
    ax.text(xa + 0.2, -0.12, f"ground reach to x ≈ {xa + math.sqrt(max(dex.reach**2 - za**2, 0)):.2f} m", fontsize=7.5, va="top")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("z [m]")
    ax.set_xlim(-1.6, 3.2)
    ax.set_ylim(-0.35, 2.8)
    ax.legend(loc="upper left", fontsize=7.5)
    ax = axs[1]
    st = J("stability.json")
    lv = np.array(st["crane_capacity_level"])
    sl = np.array(st["crane_capacity_15deg"])
    ax.set_title("Crane hook-load limit vs reach (side lift, TF ≥ 1.5)")
    ax.plot(lv[:, 0], lv[:, 1], color=C[0], label="stability limit, level")
    ax.plot(sl[:, 0], sl[:, 1], color=C[1], ls="--", label="stability limit, 15° lateral (load downhill)")
    ax.axhline(cfg.opts.heavy_payload, color=C[2], label=f"structural/winch rating {cfg.opts.heavy_payload:.0f} kg")
    ax.set_yscale("log")
    ax.set_xlabel("horizontal reach from crane base [m]")
    ax.set_ylabel("hook load [kg] (log scale)")
    ax.set_ylim(100, 4000)
    ax.legend(fontsize=8, loc="upper right")
    save(fig, "fig05_manipulator_workspace_crane_capacity.png")


def fig_power_architecture(cfg):
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    blank(ax)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 5.6)
    bat = cfg.derived["battery"]
    ax.set_title("Electrical power architecture (ISPSIS-compatible 120 VDC)")
    box(ax, 0.3, 2.3, 2.1, 1.1, f"Li-ion PPR battery\n{bat.nameplate_kwh:.1f} kWh nameplate\n{bat.n_series}s{bat.n_parallel}p ≈ {bat.v_nominal:.0f} V",
        ec=C[0])
    box(ax, 3.1, 3.5, 2.2, 0.9, "PCDU bus regulator\nbidir. buck-boost 4 kW\n→ regulated 120 VDC", ec=C[0])
    box(ax, 3.1, 1.2, 2.2, 0.9, "Power-transfer module\nisolated bidir. 3 kW\n(single stage, η≈0.95)", ec=C[1])
    box(ax, 6.0, 4.4, 2.0, 0.7, "120 VDC primary bus\nSSPC-protected", ec=INK2)
    box(ax, 6.0, 3.3, 2.0, 0.7, "28 VDC avionics bus\n(isolated converters)", ec=INK2)
    box(ax, 8.6, 4.4, 2.6, 0.7, "Drives, arms, crane, winch,\nheaters, mast", ec=MUTED)
    box(ax, 8.6, 3.3, 2.6, 0.7, "Computers, sensors, radios", ec=MUTED)
    box(ax, 6.0, 1.2, 2.0, 0.9, "Tether reel 25 m\n2 × %.1f mm² Cu\n3 %% drop @ 3 kW" % cfg.derived["tether"].area_mm2, ec=C[1])
    box(ax, 8.6, 1.2, 2.6, 0.9, "Dust-tolerant connector\nISPSIS 120 VDC port\n→ asset / grid node", ec=C[1])
    box(ax, 0.3, 4.4, 2.1, 0.8, "Vertical PV 1.5 m²\n+ MPPT (≈166 W avg)", ec=C[3])
    box(ax, 0.3, 0.4, 2.1, 0.8, "Diagnostics: V/I, insulation\nresistance, LISN", ec=C[2])
    arrow(ax, (2.4, 3.0), (3.1, 3.9))
    arrow(ax, (2.4, 2.7), (3.1, 1.6), style="<|-|>")
    arrow(ax, (1.35, 4.4), (1.35, 3.4))
    arrow(ax, (5.3, 4.0), (6.0, 4.7))
    arrow(ax, (5.3, 3.8), (6.0, 3.6))
    arrow(ax, (8.0, 4.75), (8.6, 4.75))
    arrow(ax, (8.0, 3.65), (8.6, 3.65))
    arrow(ax, (5.3, 1.65), (6.0, 1.65), style="<|-|>")
    arrow(ax, (8.0, 1.65), (8.6, 1.65), style="<|-|>")
    arrow(ax, (1.35, 1.2), (1.35, 2.3), style="<|-|>")
    ax.text(5.75, 0.55, "Single-point ground at battery return (ISPSIS); galvanic isolation at the external port",
            fontsize=7.5, ha="center", color=INK2)
    save(fig, "fig06_power_architecture.png")


def fig_autonomy():
    fig, ax = plt.subplots(figsize=(11, 6))
    blank(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.2)
    ax.set_title("Layered autonomy with an independent deterministic safety layer")
    layers = [("Mission planner — task queue, priorities (unpowered assets first), energy/comm-window scheduling", C[0]),
              ("Task planner — DRM templates → verified skill sequences; hold points; ML: anomaly ranking (advisory)", C[0]),
              ("Verified robotic skills — grasp handle, mate connector, drive fastener, rig line, deploy spade, clean", C[1]),
              ("Motion planning — collision-checked arm/crane/drive paths; terrain cost map (LiDAR + stereo)", C[1]),
              ("Real-time control — joint/wheel servo, impedance/force control, winch tension loop (1 kHz)", C[2]),
              ("Actuators — wheel drives, steering, joints, crane, winch, spades, PTM switches", MUTED)]
    for i, (t, col) in enumerate(layers):
        y = 5.2 - i * 0.85
        box(ax, 0.3, y, 7.2, 0.62, t, ec=col, fs=7.8)
        if i < len(layers) - 1:
            arrow(ax, (3.9, y), (3.9, y - 0.23))
    box(ax, 8.0, 0.95, 2.7, 4.85, "Deterministic safety layer\n(dual RT computers, cross-checked)\n\n• force/torque limits\n• speed limits near crew\n"
        "• tip-factor monitor (CoP)\n• winch tension limit\n• keep-out zones\n• power-port interlocks\n• watchdog → safe hold\n\n"
        "Formally verified / fully tested;\nindependent of ML components", ec=CRIT, fs=7.5)
    for i in range(2, 6):
        y = 5.2 - i * 0.85 + 0.31
        arrow(ax, (8.0, y), (7.5, y), color=CRIT, style="-|>", ls="--")
    ax.text(3.9, 0.35, "Learned components may rank, classify and propose; they never command torques/currents.",
            ha="center", fontsize=8, color=INK2)
    save(fig, "fig07_autonomy_architecture.png")


def fig_comms():
    fig, ax = plt.subplots(figsize=(11, 5.4))
    blank(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.6)
    tr = J("trades.json")["comms"]
    ax.set_title("Communications architecture and link availability")
    box(ax, 4.3, 2.2, 2.4, 1.0, "TSR-1\nS-band relay 5 W / 10 dBi\nsurface radio · UHF mesh", ec=C[0], bold=True, fs=8)
    box(ax, 0.3, 3.9, 2.4, 0.9, "Surface comm towers\n~10 km cells (LTE-class)", ec=C[0])
    box(ax, 4.4, 4.4, 2.2, 0.9, "Lunar relay (LunaNet /\nMoonlight-class)", ec=C[0])
    box(ax, 8.3, 4.4, 2.4, 0.9, "Earth MOC (DSN/commercial)\nRTT ≈ 2.6 s + processing", ec=C[2])
    box(ax, 0.3, 0.6, 2.4, 0.9, "Serviced asset\n(standard data I/F, L3)", ec=C[1])
    box(ax, 8.3, 0.6, 2.4, 0.9, "Peer TSR / MOD-RPT\nrepeater into PSRs", ec=C[4])
    box(ax, 8.3, 2.3, 2.4, 0.9, "Local base operations\n(crew habitat)", ec=C[2])
    for p, q in (((2.7, 4.3), (4.4, 2.9)), ((5.5, 4.4), (5.5, 3.2)), ((6.6, 4.85), (8.3, 4.85)), ((2.7, 1.0), (4.4, 2.3)),
                 ((6.6, 2.3), (8.3, 1.0)), ((6.6, 2.7), (8.3, 2.75)), ((1.5, 3.9), (1.5, 1.5))):
        arrow(ax, p, q, style="<|-|>")
    lb = tr["link_10000km"]
    ax.text(7.45, 3.55, f"relay link @10 000 km: ≈{lb['max_rate_bps']/1e3:.0f} kbit/s\n@3 000 km: ≈{tr['link_3000km']['max_rate_bps']/1e6:.1f} Mbit/s",
            fontsize=7.5, ha="center")
    av = tr["availability"]
    y = 0.15
    ax.text(5.5, y + 0.15, "  ·  ".join(f"{k.split(' ')[0]} {v:.2f}" for k, v in av.items()), ha="center", fontsize=7.5, color=INK2)
    save(fig, "fig08_communications_architecture.png")


def fig_workflow():
    fig, ax = plt.subplots(figsize=(12, 3.9))
    blank(ax)
    ax.set_xlim(0, 12)
    ax.set_ylim(0.4, 4.7)
    ax.set_title("Servicing workflow (DRM-2 electrical failure) with failure branches")
    steps = ["Fault telemetry /\nloss of signal", "Plan & approve\n(task level)", "Traverse\n(≈8 h @10 km)", "Stand-off\ninspection",
             "Connect ISPSIS\nkeep-alive 300 W", "Diagnose bus,\nidentify ORU", "Swap ORU\n(dex arm / crane)", "Functional\ntest", "Disconnect,\nreturn, report"]
    for i, s in enumerate(steps):
        x = 0.2 + i * 1.3
        box(ax, x, 3.6, 1.15, 0.9, s, ec=C[0], fs=7.2)
        if i < len(steps) - 1:
            arrow(ax, (x + 1.15, 4.05), (x + 1.3, 4.05))
    br = [(2, "hazard on route\n→ re-plan / hold", WARN), (3, "unpowered > t_survive\n→ asset lost\n(recorded)", CRIT),
          (4, "connector/port\ndamaged → L0 path:\ninspect only", WARN),
          (6, "no spare / ORU fault\n→ leave MOD-KA,\nrequest spare", WARN), (7, "test fails\n→ retry once /\nescalate", WARN)]
    for i, t, col in br:
        x = 0.2 + i * 1.3
        box(ax, x - 0.04, 1.5, 1.23, 1.1, t, ec=col, fs=6.2)
        arrow(ax, (x + 0.575, 3.6), (x + 0.575, 2.6), color=col, ls="--")
    ax.text(6.0, 0.7, "Hold points (human approval): power connection · fastener release on load path · ORU insertion · winch > 1 kN",
            ha="center", fontsize=8, color=INK2)
    save(fig, "fig09_servicing_workflow.png")


# ======================================================================================== data charts
def fig_mass_budget(cfg):
    from tsr1.common.params import REGISTRY as R
    rows = sorted(cfg.subsystem_table(), key=lambda t: t[2])
    fig, ax = plt.subplots(figsize=(10, 6))
    names = [r[0] for r in rows]
    cbe = np.array([r[1] for r in rows])
    mga = np.array([r[2] - r[1] for r in rows])
    y = np.arange(len(rows))
    ax.barh(y, cbe, height=0.6, color=C[0], label="CBE")
    ax.barh(y, mga, left=cbe + 1.5, height=0.6, color=C[3], label="MGA (AIAA S-120A categories)")
    for i, (c_, m_) in enumerate(zip(cbe, mga)):
        ax.text(c_ + m_ + 5, i, f"{c_ + m_:.0f}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(y, names)
    ax.set_xlabel("mass [kg]")
    ax.set_title(f"Bottom-up mass budget — CBE {cfg.cbe():.0f} kg → predicted {cfg.predicted():.0f} kg → "
                 f"dry allocation {cfg.dry_mass_allocation:.0f} kg (+{R.v('system_margin'):.0%}) → delivered {cfg.delivered_mass:.0f} kg",
                 fontsize=10)
    ax.legend(loc="lower right")
    ax.grid(axis="y", visible=False)
    save(fig, "fig10_mass_budget.png")


def fig_power_budget():
    e = J("energy_power_thermal.json")
    modes = list(e["mode_power_W"].keys())
    vals = [e["mode_power_W"][m] for m in modes]
    web = [e["web_dissipation_W"][m] for m in modes]
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw=dict(width_ratios=[1.3, 1]))
    ax = axs[0]
    y = np.arange(len(modes))
    ax.barh(y - 0.17, vals, height=0.3, color=C[0], label="bus load (avg)")
    ax.barh(y + 0.17, web, height=0.3, color=C[1], label="WEB heat (incl. conversion losses)")
    ax.set_yticks(y, [m.replace("_", " ") for m in modes])
    ax.invert_yaxis()
    ax.set_xlabel("power [W]")
    ax.set_title("Average power by operating mode")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="y", visible=False)
    ax = axs[1]
    drms = e["drms"]
    use = e["battery"]["usable_eol_kwh"]
    ids = [d["id"] for d in drms]
    en = [d["energy_kwh"] for d in drms]
    ens = [d["energy_with_solar_kwh"] for d in drms]
    x = np.arange(len(ids))
    ax.bar(x - 0.18, en, width=0.34, color=C[0], label="no solar")
    ax.bar(x + 0.18, ens, width=0.34, color=C[2], label="with vertical PV (50 % sunlit)")
    ax.axhline(use - e["reserve_kwh"], color=CRIT, lw=1.5, label=f"usable EOL − 50 h reserve = {use - e['reserve_kwh']:.1f} kWh")
    ax.set_xticks(x, ids)
    ax.set_ylabel("sortie energy [kWh]")
    ax.set_title("DRM energy at the 10 km service edge")
    ax.set_ylim(0, 1.25 * max(use - e["reserve_kwh"], max(en)))
    ax.legend(fontsize=7.5, loc="upper right")
    save(fig, "fig11_power_energy_budget.png")


def fig_mobility():
    m = J("mobility.json")
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.6))
    fig.subplots_adjust(wspace=0.42)
    ax = axs[0]
    for i, (k, lab) in enumerate((("nominal", "nominal (Table 9.14)"), ("conservative", "conservative (lunar-g penalty)"),
                                  ("weak", "weak (lower bounds)"))):
        c = m["dp_curves"][k]
        ax.plot(c["slip"], c["dp_over_w"], color=C[i], ls=["-", "--", ":"][i], label=lab)
    ax.axvline(0.4, color=MUTED, lw=1)
    ax.text(0.41, 0.43, "design slip limit", fontsize=7, color=INK2)
    ax.set_xlabel("slip i")
    ax.set_ylabel("drawbar pull / wheel load")
    ax.set_title("Single-wheel drawbar pull (Ø0.9 × 0.40 m)", fontsize=10)
    ax.legend(fontsize=7.5, loc="lower right")
    ax = axs[1]
    s = m["slopes_deg"]
    keys = ["nominal", "conservative", "weak", "one_wheel_out", "two_wheels_out", "nominal_20pct"]
    labs = ["nominal", "conservative", "weak soil", "1 drive failed", "2 drives failed", "nominal, i≤0.2"]
    vals = [s[k] for k in keys]
    ax.barh(range(len(keys)), vals, height=0.55, color=[C[0], C[1], C[1], C[3], C[3], C[0]])
    for i, v_ in enumerate(vals):
        ax.text(v_ + 0.3, i, f"{v_:.1f}°", va="center", fontsize=8)
    ax.set_yticks(range(len(keys)), labs)
    ax.invert_yaxis()
    ax.set_xlabel("max climbable slope [deg] (i ≤ 0.4 unless noted)")
    ax.set_title("Vehicle slope capability")
    ax.grid(axis="y", visible=False)
    ax = axs[2]
    t = m["tow_capacity"]
    ax.plot([r["slope_deg"] for r in t], [r["nominal_N"] for r in t], "o-", color=C[0], ms=6, mec=SURF, mew=1.5, label="direct tow, nominal")
    ax.plot([r["slope_deg"] for r in t], [r["conservative_N"] for r in t], "s--", color=C[1], ms=6, mec=SURF, mew=1.5,
            label="direct tow, conservative")
    ax.axhline(4000 / 1.5, color=C[2], label="anchored winch planned limit (4 kN / 1.5)")
    ax.set_yscale("symlog", linthresh=100)
    ax.set_xlabel("slope [deg]")
    ax.set_ylabel("available pull [N]")
    ax.set_title("Direct towing vs anchored winching")
    ax.set_ylim(-20, 8000)
    ax.legend(fontsize=7.5, loc="lower left")
    save(fig, "fig12_mobility_results.png")


def fig_recovery():
    r = J("recovery.json")
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
    fig.subplots_adjust(wspace=0.28)
    for j, key in enumerate(("free_kg", "locked_kg")):
        ax = axs[j]
        for i, (name, cur) in enumerate(r["curves"]["curves"].items()):
            if name.startswith("R2"):
                continue
            yv = np.array(cur[key], float)
            yv[yv < 1.0] = np.nan                     # no recoverable mass: leave the curve open instead of a 1 kg floor
            ax.plot(cur["slopes"], yv, color=C[i % 8], marker="o", ms=5, mec=SURF, mew=1.2,
                    label=name.split(" ", 1)[1] if j == 0 else None)
        ax.set_yscale("log")
        ax.set_xlabel("slope [deg]")
        ax.set_ylabel("max recoverable target mass [kg] (log)")
        ax.set_title(f"{'Free-rolling target (brakes released)' if j == 0 else 'Brake-locked target'}, FoS 1.5")
        ax.axhline(450, color=MUTED, lw=1)
        ax.text(0.3, 480, "450 kg rover", fontsize=7, color=INK2)
        ax.axhline(1500, color=MUTED, lw=1)
        ax.text(0.3, 1580, "1.5 t LTV-class", fontsize=7, color=INK2)
    axs[0].legend(fontsize=7, loc="lower left")
    save(fig, "fig13_recovery_envelopes.png")
    # p_env bars
    fig, ax = plt.subplots(figsize=(9, 4))
    names = list(r["p_env"].keys())
    mid = [r["p_env"][n]["mid"] for n in names]
    lo = [r["p_env"][n]["high"] for n in names]
    hi = [r["p_env"][n]["low"] for n in names]
    weak = [r["p_env"][n]["weak_soil"] for n in names]
    y = np.arange(len(names))
    ax.barh(y, mid, height=0.5, color=C[0], label="mid extraction estimate")
    ax.errorbar(mid, y, xerr=[np.array(mid) - np.array(lo), np.array(hi) - np.array(mid)], fmt="none", ecolor=INK2,
                capsize=3, lw=1, label="range over extraction-resistance bounds")
    ax.plot(weak, y, "D", color=C[1], ms=7, mec=SURF, mew=1.5, label="half-strength soil")
    ax.set_yticks(y, [n for n in names])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("fraction of sampled immobilisation cases recoverable")
    ax.set_title("Recovery architecture trade (TS-05)")
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
    ax.grid(axis="y", visible=False)
    save(fig, "fig14_recovery_trade.png")


def fig_stability():
    st = J("stability.json")
    cases = [c for c in st["cases"] if not c["case"].startswith("C1 stowed, level")]
    import textwrap
    names = ["\n".join(textwrap.wrap(c["case"], 48)) for c in cases]
    tf = [min(float(c["tip_factor"]) if c["tip_factor"] != "inf" else 200.0, 200.0) for c in cases]
    fig, ax = plt.subplots(figsize=(10, 6.4))
    y = np.arange(len(names))
    cols = [CRIT if t < 1.5 else C[0] for t in tf]
    ax.barh(y, tf, height=0.55, color=cols)
    ax.axvline(1.5, color=CRIT, lw=1.2)
    ax.text(1.55, len(names) - 0.6, "required 1.5", fontsize=7.5, color=INK2)
    ax.set_xscale("log")
    ax.set_yticks(y, names, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel("tipping factor (restoring / overturning moment, log; ∞ shown as 200)")
    ax.set_title(f"Static stability cases — static tip-over angles {st['static_tip_angles_deg'][0]:.0f}° longitudinal / "
                 f"{st['static_tip_angles_deg'][1]:.0f}° lateral", fontsize=10)
    ax.grid(axis="y", visible=False)
    save(fig, "fig15_stability_analysis.png")


def fig_servicing_reliability():
    s = J("servicing_success.json")
    rel = J("tsr_reliability.json")
    fig, axs = plt.subplots(1, 2, figsize=(14, 4.6))
    fig.subplots_adjust(wspace=0.45)
    ax = axs[0]
    levels = ["L0", "L1", "L2", "L3"]
    x = np.arange(4)
    for i, (actor, lab) in enumerate((("robot", "TSR-1 (robot)"), ("crew", "crew EVA"))):
        d = s[actor]["oru_replace"]
        p50 = np.array([d[L]["p50"] for L in levels])
        p10 = np.array([d[L]["p10"] for L in levels])
        p90 = np.array([d[L]["p90"] for L in levels])
        ax.bar(x + (i - 0.5) * 0.36, p50, width=0.32, color=C[i], label=lab)
        ax.errorbar(x + (i - 0.5) * 0.36, p50, yerr=[p50 - p10, p90 - p50], fmt="none", ecolor=INK2, capsize=3, lw=1)
    ax.set_xticks(x, levels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("P(ORU replacement success), P10–P50–P90")
    ax.set_xlabel("asset compatibility level")
    ax.set_title("Servicing success vs compatibility level")
    ax.legend(fontsize=8)
    ax = axs[1]
    keys = ["no_repair", "slow_repair", "crew_repair", "peer"]
    labs = ["no ORU repair", "repair 120 d", "repair 30 d (baseline)", "peer TSR 7 d"]
    cap = [rel[k]["p_capable_10yr"] for k in keys]
    full = [rel[k]["availability_full"] for k in keys]
    y = np.arange(4)
    ax.barh(y - 0.17, cap, height=0.3, color=C[0], label="P(servicing-capable at 10 yr)")
    ax.barh(y + 0.17, full, height=0.3, color=C[3], label="time fraction fully functional")
    ax.set_yticks(y, labs)
    ax.set_xlim(0, 1.05)
    ax.set_title("TSR-1 self-reliability (10 yr Monte Carlo)")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.grid(axis="y", visible=False)
    save(fig, "fig16_reliability_model.png")


def fig_value():
    v = J("value_model.json")
    mc = np.load(RES / "value_mc_base.npz")
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
    ax = axs[0]
    ax.hist(mc["A0"], bins=25, color=C[1], alpha=0.75, label="without TSR-1")
    ax.hist(mc["A1"], bins=25, color=C[0], alpha=0.75, label="with TSR-1")
    ax.set_xlabel("10-yr mean infrastructure availability")
    ax.set_ylabel("Monte Carlo replicates")
    ax.set_title(f"Availability, {v['base_scenario']['n_assets']} assets (epistemic MC)")
    ax.legend(fontsize=8)
    ax = axs[1]
    ax.hist(100 * mc["dA"], bins=25, color=C[0])
    ax.axvline(100 * np.percentile(mc["dA"], 10), color=INK2, lw=1)
    ax.text(100 * np.percentile(mc["dA"], 10), ax.get_ylim()[1] * 0.9, " P10", fontsize=7.5)
    ax.set_xlabel("availability gain ΔA [percentage points]")
    ax.set_title("Availability gain distribution")
    ax = axs[2]
    ax.hist((mc["mass0"] - mc["mass1"]) / 1000, bins=25, color=C[2])
    ax.axvline(v["tsr_lifecycle_mass_kg"] / 1000, color=CRIT, lw=1.5)
    ax.text(v["tsr_lifecycle_mass_kg"] / 1000, ax.get_ylim()[1] * 0.9, " TSR-1 life-cycle mass", fontsize=7.5)
    ax.set_xlabel("Earth-supplied mass avoided over 10 yr [t]")
    ax.set_title("Logistics mass avoided")
    save(fig, "fig17_montecarlo_results.png")
    sw = v["asset_sweep"]
    N = [s_["n_assets"] for s_ in sw]
    fig, axs = plt.subplots(1, 4, figsize=(20, 4.6))
    fig.subplots_adjust(wspace=0.32)
    ax = axs[0]
    ax.plot(N, [100 * s_["dA_mean"] for s_ in sw], "o-", color=C[0], ms=6, mec=SURF, mew=1.5, label="mean")
    ax.fill_between(N, [100 * s_["dA_p10"] for s_ in sw], [100 * s_["dA_p90"] for s_ in sw], color=C[0], alpha=0.12,
                    label="P10–P90")
    ax.set_xlabel("number of distributed assets")
    ax.set_ylabel("ΔA [pp]")
    ax.set_title("Availability gain vs scale")
    ax.legend(fontsize=8)
    ax = axs[1]
    ax.plot(N, [s_["net_mass_benefit"] / 1000 for s_ in sw], "o-", color=C[2], ms=6, mec=SURF, mew=1.5)
    ax.axhline(0, color=INK2, lw=1)
    if v["break_even_assets"]:
        ax.axvline(v["break_even_assets"], color=MUTED, lw=1)
        ax.text(v["break_even_assets"], ax.get_ylim()[0] * 0.8 if ax.get_ylim()[0] < 0 else 0.1,
                f" break-even ≈ {v['break_even_assets']:.0f} assets", fontsize=8)
    ax.set_xlabel("number of distributed assets")
    ax.set_ylabel("net Earth-mass benefit [t]")
    ax.set_title("Net logistics benefit (avoided − TSR-1 life-cycle)", fontsize=10)
    ax = axs[2]
    ax.plot(N, [s_["eva_avoided_mean"] for s_ in sw], "o-", color=C[1], ms=6, mec=SURF, mew=1.5)
    ax.set_xlabel("number of distributed assets")
    ax.set_ylabel("crew EVA avoided over 10 yr [crew-h]")
    ax.set_title("Crew time avoided")
    ax = axs[3]
    ax.plot(N, [s_["plost0_mean"] for s_ in sw], "s--", color=C[1], ms=6, mec=SURF, mew=1.5, label="without TSR-1")
    ax.plot(N, [s_["plost1_mean"] for s_ in sw], "o-", color=C[0], ms=6, mec=SURF, mew=1.5, label="with TSR-1")
    ax.set_xlabel("number of distributed assets")
    ax.set_ylabel("preventable asset losses over 10 yr")
    ax.set_title("Preventable losses (excl. non-serviceable)", fontsize=10)
    ax.legend(fontsize=8)
    save(fig, "fig18_value_vs_infrastructure_scale.png")


def fig_capacity():
    cap = J("capacity_study.json")
    loads = sorted({(c["n_assets"], c["mtbf_yr"]) for c in cap}, key=lambda k: k[0] / k[1])
    fig, axs = plt.subplots(1, 3, figsize=(17, 5.0))
    fig.subplots_adjust(wspace=0.3)
    ax = axs[0]
    for j, (n, m) in enumerate(loads):
        rows = sorted([c for c in cap if c["n_assets"] == n and c["mtbf_yr"] == m and c["n_tsr"] == 1],
                      key=lambda c: c["keepalive_modules"])
        k = [c["keepalive_modules"] for c in rows]
        ax.plot(k, [c["plost1"] for c in rows], "o-", color=C[j], ms=6, mec=SURF, mew=1.5,
                label=f"{n} assets, MTBF {m:g} yr ({n / m:.0f} faults/yr)")
        ax.plot([k[-1] + 0.6], [rows[0]["plost0"]], marker="s", color=C[j], ms=6, mec=SURF, mew=1.5, ls="none")
    ax.set_xticks([2, 4, 8])
    ax.set_xlabel("keep-alive modules in inventory (one TSR-1)")
    ax.set_ylabel("preventable losses over 10 yr")
    ax.set_title("Losses vs keep-alive inventory")
    handles, labels = ax.get_legend_handles_labels()
    handles.append(plt.Line2D([], [], marker="s", color=INK2, ls="none", ms=6))
    labels.append("without TSR-1 (squares at right)")
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.07))
    ax = axs[1]
    for j, (n, m) in enumerate(loads):
        rows = sorted([c for c in cap if c["n_assets"] == n and c["mtbf_yr"] == m and c["n_tsr"] == 1],
                      key=lambda c: c["keepalive_modules"])
        ax.plot([c["keepalive_modules"] for c in rows], [c["kg_per_asset_yr1"] for c in rows], "o-", color=C[j], ms=6,
                mec=SURF, mew=1.5)
        ax.plot([8.6], [rows[0]["kg_per_asset_yr0"]], marker="s", color=C[j], ms=6, mec=SURF, mew=1.5, ls="none")
    ax.set_xticks([2, 4, 8])
    ax.set_xlabel("keep-alive modules in inventory (one TSR-1)")
    ax.set_ylabel("Earth mass per available asset-year [kg]")
    ax.set_title("Earth mass per available asset-year")
    ax = axs[2]
    x = np.arange(len(loads))
    r1 = [next(c for c in cap if (c["n_assets"], c["mtbf_yr"]) == L and c["n_tsr"] == 1 and c["keepalive_modules"] == 4)
          for L in loads]
    r2 = [next(c for c in cap if (c["n_assets"], c["mtbf_yr"]) == L and c["n_tsr"] == 2 and c["keepalive_modules"] == 4)
          for L in loads]
    ax.bar(x - 0.2, [c["response_h"] for c in r1], 0.38, color=C[0], label="one TSR-1")
    ax.bar(x + 0.2, [c["response_h"] for c in r2], 0.38, color=C[1], label="two TSR-1")
    for i in range(len(loads)):
        ax.text(x[i], max(r1[i]["response_h"], r2[i]["response_h"]) + 0.3,
                f"losses {r1[i]['plost1']:.0f} / {r2[i]['plost1']:.0f}", ha="center", fontsize=7, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n / m:.0f}/yr" for n, m in loads])
    ax.set_ylim(0, 1.2 * max(c["response_h"] for c in r1))
    ax.set_xlabel("fault load (4 keep-alive modules)")
    ax.set_ylabel("mean response time [h]")
    ax.set_title("Response time: one vs two rovers")
    ax.legend(fontsize=8, loc="lower right")
    save(fig, "fig22_capacity_study.png")


def fig_sensitivity():
    s = J("sensitivity.json")
    fig, axs = plt.subplots(2, 2, figsize=(14, 8.4))
    for ax, key, title in ((axs[0, 0], "slope", "Max slope [deg] — soil parameters"),
                           (axs[0, 1], "mass", "Delivered mass [kg] — MER/MGA parameters"),
                           (axs[1, 0], "drm2_energy", "DRM-2 energy [kWh]"),
                           (axs[1, 1], "recovery", "Recovery envelope probability")):
        rows = s[key][:8][::-1]
        base = rows[0]["f_nominal"] if rows else 0
        for i, r in enumerate(rows):
            lo, hi = r["f_low"] - base, r["f_high"] - base
            ax.barh(i, lo, height=0.55, color=C[1], left=base)
            ax.barh(i, hi, height=0.55, color=C[0], left=base)
        ax.axvline(base, color=INK, lw=1)
        ax.set_yticks(range(len(rows)), [f"{r['parameter']} [{r['low']:.3g}, {r['high']:.3g}]" for r in rows], fontsize=7.5)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch
    axs[0, 0].legend(handles=[Patch(color=C[1], label="parameter at low bound"), Patch(color=C[0], label="parameter at high bound")],
                     fontsize=7.5, loc="lower right")
    fig.suptitle("One-at-a-time sensitivity (tornado) — bars show change from nominal", x=0.01, ha="left",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig19_sensitivity_tornado.png")
    mm = np.array(s["mass_mc"]["samples"])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(mm, bins=20, color=C[0])
    ax.axvline(1500, color=CRIT, lw=1.5)
    ax.text(1505, ax.get_ylim()[1] * 0.85, "Argonaut-class 1.5 t", fontsize=8)
    ax.set_xlabel("delivered mass [kg]")
    ax.set_ylabel("samples")
    ax.set_title(f"Mass Monte Carlo (MER + MGA uncertainty): P50 {s['mass_mc']['p50']:.0f} kg, "
                 f"P90 {s['mass_mc']['p90']:.0f} kg, P(≤1.5 t) = {s['mass_mc']['p_le_1500']:.2f}", fontsize=10)
    save(fig, "fig20_mass_monte_carlo.png")


def fig_comparison():
    systems = ["Apollo LRV", "VIPER", "LTV (CLV-1/Pegasus)", "FLEX (uncrewed)", "Lunar Utility Rover*", "Dextre (ISS)", "TSR-1"]
    caps = ["crew transport", "autonomous ops", "cargo ≥ 500 kg", "dexterous servicing", "heavy ORU (≥100 kg)",
            "vehicle recovery", "emergency power (120 VDC)", "dust remediation", "multi-standard I/F", "PSR excursion"]
    # 0 none, 1 limited/claimed, 2 primary capability (from S027, S035, S036, S037, S005, S067 and this study)
    M = np.array([
        [2, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 1, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 2, 0, 1, 0, 0, 0, 1, 0],
        [0, 2, 2, 1, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 2, 2, 0, 0, 0, 1, 0],
        [0, 2, 1, 2, 2, 2, 2, 2, 2, 1],
    ])
    fig, ax = plt.subplots(figsize=(12, 5))
    cmap = matplotlib.colors.ListedColormap(["#f0efec", SEQ[2], SEQ[5]])
    ax.imshow(M, cmap=cmap, vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(caps)), caps, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(systems)), systems, fontsize=8.5)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, ["—", "limited", "primary"][M[i, j]], ha="center", va="center", fontsize=6.8,
                    color="#ffffff" if M[i, j] == 2 else INK)
    ax.grid(False)
    ax.set_title("Capability comparison (public descriptions; *NASA architecture element, not yet procured)")
    save(fig, "fig21_comparison_matrix.png")


def main():
    from tsr1.design.configuration import Options, build
    cfgfile = json.loads((ROOT / "simulations" / "configs" / "run_config.json").read_text())
    opts = cfgfile["baseline_options"]
    opts["dex_links"] = tuple(opts["dex_links"])
    cfg = build(Options(**opts))
    base = J("baseline_summary.json")
    fig_system_architecture()
    fig_rover_configuration(cfg, base)
    fig_layout_table(cfg)
    fig_service_spine()
    fig_workspace(cfg)
    fig_power_architecture(cfg)
    fig_autonomy()
    fig_comms()
    fig_workflow()
    fig_mass_budget(cfg)
    fig_power_budget()
    fig_mobility()
    fig_recovery()
    fig_stability()
    fig_servicing_reliability()
    fig_value()
    fig_capacity()
    fig_sensitivity()
    fig_comparison()
    (ROOT / "paper" / "figures").mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("fig*.png"):
        shutil.copy(p, ROOT / "paper" / "figures" / p.name)


if __name__ == "__main__":
    main()
