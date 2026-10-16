#!/usr/bin/env python3
"""Build main figures for the PR189 spatial-reversal Ecology manuscript."""

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


def effective_number(values):
    total = float(sum(values))
    return total * total / sum(float(x) * float(x) for x in values)


def read_ross(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for r in rows:
        year = int(r["year"])
        out[year] = {k: int(r[k]) for k in ROSS_COMPONENTS}
    return out


def fig1_ross_path(root: Path, outdir: Path):
    counts = read_ross(root / "external/ross_island_v2_frozen_counts.csv")
    years = [1999, 2001, 2002, 2012]
    N = [sum(counts[y].values()) for y in years]
    E = [effective_number(counts[y].values()) for y in years]

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.5))
    x = list(range(len(years)))

    axes[0].plot(x, N, marker="o")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Breeding pairs")
    axes[0].set_title("Aggregate breeding abundance")
    axes[0].set_xticks(x, [str(y) for y in years])

    axes[1].plot(x, E, marker="o")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Effective breeding-unit number")
    axes[1].set_title("Spatial allocation")
    axes[1].set_xticks(x, [str(y) for y in years])

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(outdir / "figure1_ross_disturbance_rebound.png", dpi=300)
    fig.savefig(outdir / "figure1_ross_disturbance_rebound.pdf")
    plt.close(fig)


def fig2_inverse_path(root: Path, outdir: Path):
    r = read_json(root / "results/ROSS_INVERSE_PATH_MISMATCH_V1.json")["six_component"]
    units = [x.replace("Cape ", "") for x in r["units"]]
    short = ["Royds", "Bird S", "Bird M", "Bird N", "Crozier W", "Crozier E"]
    observed = r["rebound_gain"]
    expected = r["scaled_inverse_path_expected_rebound"]
    residual = r["observed_minus_scaled_inverse_path"]

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))

    # Panel A: broad spatial reversibility. Log axes keep the small components visible.
    ax = axes[0]
    lo = min(min(expected), min(observed)) * 0.75
    hi = max(max(expected), max(observed)) * 1.25
    ax.plot([lo, hi], [lo, hi], linewidth=1.0, linestyle="--")
    for label, x, y in zip(short, expected, observed):
        ax.scatter([x], [y], s=42)
        ax.annotate(label, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Exact inverse-path rebound")
    ax.set_ylabel("Observed rebound")
    ax.set_title("Most rebound tracks the loss")

    # Panel B: where the remaining allocation mismatch sits.
    ax = axes[1]
    x = list(range(len(short)))
    ax.bar(x, residual)
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(short, rotation=35, ha="right")
    ax.set_ylabel("Observed - inverse path")
    ax.set_title("Residual allocation mismatch")
    ax.text(
        0.02,
        0.98,
        "Loss restored = 96.97%\n"
        "Mismatch = 9.41% of rebound\n"
        "Cosine = 0.997",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
    )

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(outdir / "figure2_inverse_path_rebound.png", dpi=300)
    fig.savefig(outdir / "figure2_inverse_path_rebound.pdf")
    plt.close(fig)

def fig3_external_sign_tests(root: Path, outdir: Path):
    bird = read_json(root / "results/BIRD_ISLAND_GENTOO_SIX_UNIT_RECOVERY_ALLOCATION_V1.json")
    emp = read_json(root / "results/EMPEROR_GLOBAL_DECLINE_SPATIAL_REDUNDANCY_V1.json")

    fig, ax = plt.subplots(figsize=(6.0, 5.0))
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)

    bx = math.log(bird["aggregate"]["N1"] / bird["aggregate"]["N0"])
    by = math.log(bird["aggregate"]["E1"] / bird["aggregate"]["E0"])
    ax.scatter([bx], [by], marker="o", s=70)
    ax.annotate("Bird Island Gentoo", (bx, by), xytext=(6, 6), textcoords="offset points")

    ex = math.log(emp["primary"]["N2018"] / emp["primary"]["N2009"])
    ey = math.log(emp["primary"]["E2018"] / emp["primary"]["E2009"])
    ax.scatter([ex], [ey], marker="s", s=70)
    ax.annotate("Emperor global", (ex, ey), xytext=(6, -14), textcoords="offset points")

    for name, d in emp["regional_sensitivity"].items():
        x = math.log(d["N_ratio"])
        y = math.log(d["E_ratio"])
        ax.scatter([x], [y], marker=".")
        ax.annotate(name, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)

    ax.set_xlabel("log aggregate abundance ratio")
    ax.set_ylabel("log effective-unit-number ratio")
    ax.set_title("Prospective external sign tests")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(outdir / "figure3_external_sign_tests.png", dpi=300)
    fig.savefig(outdir / "figure3_external_sign_tests.pdf")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--outdir", type=Path, default=Path("build/spatial_reversal_figures"))
    args = ap.parse_args()

    root = args.repo_root.resolve()
    outdir = args.outdir
    if not outdir.is_absolute():
        outdir = root / outdir
    outdir.mkdir(parents=True, exist_ok=True)

    fig1_ross_path(root, outdir)
    fig2_inverse_path(root, outdir)
    fig3_external_sign_tests(root, outdir)


if __name__ == "__main__":
    main()
