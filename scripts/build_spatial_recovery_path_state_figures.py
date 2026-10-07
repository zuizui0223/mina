#!/usr/bin/env python3
"""Build figures for the path-versus-state spatial recovery manuscript."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROSS_COMPONENTS = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_ross(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {
        int(r["year"]): {k: int(r[k]) for k in ROSS_COMPONENTS}
        for r in rows
    }


def effective_number(values):
    total = float(sum(values))
    return total * total / sum(float(x) * float(x) for x in values)


def shares(values):
    total = float(sum(values))
    return [float(x) / total for x in values]


def tv(a, b):
    return 0.5 * sum(abs(x - y) for x, y in zip(a, b))


def save(fig, outdir: Path, stem: str):
    fig.tight_layout()
    fig.savefig(outdir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(outdir / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def fig1_three_recoveries(root: Path, outdir: Path):
    audit = read_json(root / "results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json")
    f = audit["focal_episode"]

    amount = 100 * f["aggregate"]["aggregate_loss_restored_fraction"]
    path = 100 * f["path_recovery"]["inverse_path_fidelity"]
    state = 100 * f["composition_state"]["state_distance_restored_fraction"]

    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.8))
    vals = [amount, path, state]
    titles = ["Amount recovery", "Path reversal", "State restoration"]
    subtitles = [
        "How much lost abundance returned?",
        "How much rebound followed prior local loss?",
        "How much compositional displacement was erased?",
    ]

    for ax, value, title, subtitle in zip(axes, vals, titles, subtitles):
        ax.bar([0], [value], width=0.55)
        ax.axhline(0, linewidth=0.8)
        ax.set_xlim(-0.6, 0.6)
        ax.set_xticks([])
        ax.set_ylim(-10, 110)
        ax.set_title(title, fontsize=11)
        ax.text(0.5, 0.91, subtitle, ha="center", va="top",
                transform=ax.transAxes, fontsize=8.5, wrap=True)
        ax.text(0, value + (4 if value >= 0 else -4), f"{value:.1f}%",
                ha="center", va="bottom" if value >= 0 else "top",
                fontsize=15, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

    axes[0].set_ylabel("Recovery score (%)")
    fig.suptitle(
        "One Ross rebound, three different answers to “did the population recover?”",
        fontsize=12,
        y=1.02,
    )
    save(fig, outdir, "figure1_three_recovery_dimensions")


def fig2_ross_path_and_state(root: Path, outdir: Path):
    inv = read_json(root / "results/ROSS_INVERSE_PATH_MISMATCH_V1.json")["six_component"]
    audit = read_json(root / "results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json")
    counts = read_ross(root / "external/ross_island_v2_frozen_counts.csv")

    labels = ["Royds", "Bird S", "Bird M", "Bird N", "Crozier W", "Crozier E"]
    expected = inv["scaled_inverse_path_expected_rebound"]
    observed = inv["rebound_gain"]

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0))

    ax = axes[0]
    lo = min(min(expected), min(observed)) * 0.72
    hi = max(max(expected), max(observed)) * 1.28
    ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1.0)
    for label, x, y in zip(labels, expected, observed):
        ax.scatter([x], [y], s=42)
        ax.annotate(label, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Rebound under exact inverse path")
    ax.set_ylabel("Observed rebound")
    ax.set_title("A  Rebound largely followed prior loss")
    ax.text(
        0.03, 0.97,
        "Cosine = 0.997\n"
        "Inverse-path fidelity = 90.59%",
        transform=ax.transAxes, va="top", fontsize=9,
    )

    ax = axes[1]
    years = [1999, 2001, 2002]
    x = list(range(len(years)))
    p = []
    for y in years:
        vals = [counts[y][k] for k in ROSS_COMPONENTS]
        p.append(shares(vals))

    bottom = [0.0] * len(years)
    for i, label in enumerate(labels):
        heights = [100 * p[j][i] for j in range(len(years))]
        ax.bar(x, heights, bottom=bottom, label=label)
        bottom = [bottom[j] + heights[j] for j in range(len(years))]

    ax.set_xticks(x, [str(y) for y in years])
    ax.set_ylabel("Share of breeding abundance (%)")
    ax.set_title("B  Composition crossed past the baseline state")
    ax.legend(fontsize=7, frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.text(
        0.02, 0.02,
        "1999→2001 TV = 5.09%\n"
        "1999→2002 TV = 4.97%\n"
        "2001→2002 TV = 9.75%",
        transform=ax.transAxes, va="bottom", fontsize=8.5,
    )

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    save(fig, outdir, "figure2_path_reversal_state_reweighting")


def fig3_ross_episode_calibration(root: Path, outdir: Path):
    audit = read_json(root / "results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json")

    episodes = audit["other_complete_down_up_episodes"] + [{
        "years": audit["focal_episode"]["years"],
        "aggregate_restoration": audit["focal_episode"]["aggregate"]["aggregate_loss_restored_fraction"],
        "inverse_path_fidelity": audit["focal_episode"]["path_recovery"]["inverse_path_fidelity"],
        "state_distance_restored_fraction": audit["focal_episode"]["composition_state"]["state_distance_restored_fraction"],
    }]
    episodes = sorted(episodes, key=lambda d: d["years"][0])

    labels = ["→".join(str(y) for y in d["years"]) for d in episodes]
    path = [100 * d["inverse_path_fidelity"] for d in episodes]
    state = [100 * d["state_distance_restored_fraction"] for d in episodes]

    fig, axes = plt.subplots(1, 2, figsize=(8.7, 3.8))

    ax = axes[0]
    ax.bar(range(len(labels)), path)
    ax.set_xticks(range(len(labels)), labels, rotation=20, ha="right")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Inverse-path fidelity (%)")
    ax.set_title("A  Path fidelity stayed high")
    for i, v in enumerate(path):
        ax.text(i, v + 1.5, f"{v:.1f}%", ha="center", va="bottom", fontsize=8.5)

    ax = axes[1]
    ax.bar(range(len(labels)), state)
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(range(len(labels)), labels, rotation=20, ha="right")
    ax.set_ylabel("Baseline compositional displacement erased (%)")
    ax.set_title("B  State restoration did not")
    for i, v in enumerate(state):
        ax.text(i, v + (2 if v >= 0 else -2), f"{v:.1f}%",
                ha="center", va="bottom" if v >= 0 else "top", fontsize=8.5)

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    save(fig, outdir, "figure3_ross_path_state_calibration")


def fig4_process_contrasts(root: Path, outdir: Path):
    palmer = read_json(root / "results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json")
    signy = read_json(root / "results/SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json")
    beau = read_json(root / "results/BEAUFORT_ISLAND_INTENSIFICATION_EXPANSION_RESULT_V1.json")
    b = beau["beaufort_2004_2010"]

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2))

    ax = axes[0]
    labels = ["Cormorant", "Humble", "Litchfield", "Signy"]
    changes = [
        palmer["observed"]["COR"]["fractional_change"],
        palmer["observed"]["HUM"]["fractional_change"],
        palmer["observed"]["LIT"]["fractional_change"],
        signy["primary"]["fractional_neff_change"],
    ]
    ax.bar(range(len(labels)), [100 * z for z in changes])
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(range(len(labels)), labels, rotation=20, ha="right")
    ax.set_ylabel("Change in effective breeding-unit number (%)")
    ax.set_title("A  Persistent decline: unequal attrition")
    for i, z in enumerate(changes):
        ax.text(i, 100*z - 2.5, f"{100*z:.0f}%", ha="center", va="top", fontsize=8.5)

    ax = axes[1]
    gains = [
        b["proportional_expected_new_subcolony_gain"],
        b["new_subcolony_pairs_2010"] - b["new_subcolony_pairs_2004"],
    ]
    ax.bar(["Proportional\nexpectation", "Observed"], gains)
    ax.set_ylabel("Gain in small/new Beaufort unit (pairs)")
    ax.set_title("B  Capacity release: unequal expansion")
    for i, z in enumerate(gains):
        ax.text(i, z + 8, f"{z:.0f}", ha="center", va="bottom", fontsize=8.5)
    ax.text(
        0.03, 0.50,
        f"Observed / expected = {b['observed_to_proportional_expected_new_gain_ratio']:.2f}×\n"
        "Independent movement evidence:\n"
        "Beaufort→Ross export declined",
        transform=ax.transAxes, va="top", fontsize=8.2,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.92),
    )

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    save(fig, outdir, "figure4_process_contrasts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--outdir", type=Path, default=Path("build/spatial_recovery_path_state_figures"))
    args = ap.parse_args()

    root = args.repo_root.resolve()
    outdir = args.outdir
    if not outdir.is_absolute():
        outdir = root / outdir
    outdir.mkdir(parents=True, exist_ok=True)

    fig1_three_recoveries(root, outdir)
    fig2_ross_path_and_state(root, outdir)
    fig3_ross_episode_calibration(root, outdir)
    fig4_process_contrasts(root, outdir)


if __name__ == "__main__":
    main()
