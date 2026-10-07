#!/usr/bin/env python3
"""Build figures for the integrated process-dependent spatial-memory manuscript."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(fig, outdir: Path, stem: str):
    fig.tight_layout()
    fig.savefig(outdir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(outdir / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def fig1_concept(root: Path, outdir: Path):
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.0))
    titles = [
        "A  Temporary breeding-state / access shock",
        "B  Persistent demographic attrition",
        "C  Breeding-capacity change",
    ]
    top = [
        "S mostly retained\nq changes strongly\nK broadly retained",
        "S changes unequally\namong breeding units\nq and K may also vary",
        "K changes\nnew/expanded breeding space\nchanges feasible allocation",
    ]
    bottom = [
        "Observed n can collapse\nwhile latent site affiliation persists\n→ old template can reappear",
        "Relative demographic contribution changes\n→ composition can be rewritten",
        "Redistribution can shift scale\nwithin island ↔ between islands",
    ]
    systems = ["Ross 1999→2001→2002", "Palmer + Signy decline", "Beaufort capacity release"]

    for ax, title, t, b, system in zip(axes, titles, top, bottom, systems):
        ax.axis("off")
        ax.set_title(title, fontsize=11, loc="left")
        ax.text(
            0.5, 0.82, t,
            ha="center", va="center", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.45", fill=False),
            transform=ax.transAxes,
        )
        ax.annotate(
            "",
            xy=(0.5, 0.57), xytext=(0.5, 0.70),
            xycoords=ax.transAxes,
            arrowprops=dict(arrowstyle="->", linewidth=1.2),
        )
        ax.text(
            0.5, 0.47,
            r"$n_{i,t}=\min\{K_{i,t},\,S_{i,t}q_{i,t}\}$",
            ha="center", va="center", fontsize=12,
            transform=ax.transAxes,
        )
        ax.annotate(
            "",
            xy=(0.5, 0.27), xytext=(0.5, 0.39),
            xycoords=ax.transAxes,
            arrowprops=dict(arrowstyle="->", linewidth=1.2),
        )
        ax.text(
            0.5, 0.17, b,
            ha="center", va="center", fontsize=9.5,
            transform=ax.transAxes,
        )
        ax.text(
            0.5, 0.02, system,
            ha="center", va="bottom", fontsize=9, fontweight="bold",
            transform=ax.transAxes,
        )

    fig.suptitle(
        "Observed breeding abundance is an expressed state; different processes alter S, q, or K",
        y=1.02,
        fontsize=12,
    )
    save(fig, outdir, "figure1_expressed_latent_capacity_model")


def fig2_ross(root: Path, outdir: Path):
    r = read_json(root / "results/ROSS_INVERSE_PATH_MISMATCH_V1.json")["six_component"]

    labels = ["Royds", "Bird S", "Bird M", "Bird N", "Crozier W", "Crozier E"]
    expected = r["scaled_inverse_path_expected_rebound"]
    observed = r["rebound_gain"]
    residual = r["observed_minus_scaled_inverse_path"]

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))

    ax = axes[0]
    lo = min(min(expected), min(observed)) * 0.72
    hi = max(max(expected), max(observed)) * 1.28
    ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1.0)
    for label, x, y in zip(labels, expected, observed):
        ax.scatter([x], [y], s=45)
        ax.annotate(label, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Rebound under exact inverse path")
    ax.set_ylabel("Observed 2001→2002 rebound")
    ax.set_title("Ross rebound largely retraced shock loss")
    ax.text(
        0.03, 0.97,
        f"Aggregate loss restored = {100*r['aggregate_loss_restored_fraction']:.1f}%\n"
        f"Cosine = {r['loss_gain_cosine_similarity']:.3f}\n"
        f"Mismatch = {100*r['half_L1_reallocation_fraction_of_rebound']:.2f}% of rebound",
        transform=ax.transAxes, va="top", fontsize=9,
    )

    ax = axes[1]
    x = list(range(len(labels)))
    ax.bar(x, residual)
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Observed − exact-inverse rebound (pairs)")
    ax.set_title("Residual reallocation")
    ax.text(
        0.03, 0.97,
        "Positive residual concentrated\nat Cape Crozier West",
        transform=ax.transAxes, va="top", fontsize=9,
    )

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    save(fig, outdir, "figure2_ross_inverse_path")


def fig3_attrition(root: Path, outdir: Path):
    palmer = read_json(root / "results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json")
    signy = read_json(root / "results/SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json")

    labels = ["Cormorant", "Humble", "Litchfield", "Signy"]
    changes = [
        palmer["observed"]["COR"]["fractional_change"],
        palmer["observed"]["HUM"]["fractional_change"],
        palmer["observed"]["LIT"]["fractional_change"],
        signy["primary"]["fractional_neff_change"],
    ]

    fig, ax = plt.subplots(figsize=(7.3, 4.5))
    x = list(range(len(labels)))
    ax.bar(x, [100 * z for z in changes])
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Change in effective breeding-unit number (%)")
    ax.set_title("Persistent decline concentrated breeders beyond proportional thinning")
    for i, z in enumerate(changes):
        ax.text(i, 100*z - 2.5, f"{100*z:.0f}%", ha="center", va="top", fontsize=9)
    ax.set_ylim(-92, 6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, outdir, "figure3_persistent_attrition")


def fig4_beaufort(root: Path, outdir: Path):
    d = read_json(root / "results/BEAUFORT_ISLAND_INTENSIFICATION_EXPANSION_RESULT_V1.json")
    b = d["beaufort_2004_2010"]

    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.0))

    ax = axes[0]
    years = ["2004", "2010"]
    shares = [100*b["new_subcolony_share_2004"], 100*b["new_subcolony_share_2010"]]
    ax.bar(years, shares)
    ax.set_ylabel("Small/new unit share of Beaufort breeders (%)")
    ax.set_title("Small/new unit gained representation")
    for i, z in enumerate(shares):
        ax.text(i, z + 0.03, f"{z:.2f}%", ha="center", va="bottom", fontsize=9)

    ax = axes[1]
    gains = [
        b["proportional_expected_new_subcolony_gain"],
        b["new_subcolony_pairs_2010"] - b["new_subcolony_pairs_2004"],
    ]
    ax.bar(["Proportional\nexpectation", "Observed"], gains)
    ax.set_ylabel("2004→2010 gain in small/new unit (pairs)")
    ax.set_title("Growth exceeded fixed-composition expectation")
    for i, z in enumerate(gains):
        ax.text(i, z + 8, f"{z:.0f}", ha="center", va="bottom", fontsize=9)
    ax.text(
        0.03, 0.52,
        f"Observed / expected = {b['observed_to_proportional_expected_new_gain_ratio']:.2f}×\n"
        "Independent movement evidence:\n"
        "Beaufort→Ross visitation declined after 2005",
        transform=ax.transAxes, va="top", fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.92),
    )

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    save(fig, outdir, "figure4_beaufort_capacity_release")


def fig5_boundary(root: Path, outdir: Path):
    bird = read_json(root / "results/BIRD_ISLAND_GENTOO_SIX_UNIT_RECOVERY_ALLOCATION_V1.json")
    emp = read_json(root / "results/EMPEROR_GLOBAL_DECLINE_SPATIAL_REDUNDANCY_V1.json")

    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)

    bx = math.log(bird["aggregate"]["N1"] / bird["aggregate"]["N0"])
    by = math.log(bird["aggregate"]["E1"] / bird["aggregate"]["E0"])
    ax.scatter([bx], [by], marker="o", s=75)
    ax.annotate("Bird Island Gentoo", (bx, by), xytext=(6, 6), textcoords="offset points")

    ex = math.log(emp["primary"]["N2018"] / emp["primary"]["N2009"])
    ey = math.log(emp["primary"]["E2018"] / emp["primary"]["E2009"])
    ax.scatter([ex], [ey], marker="s", s=75)
    ax.annotate("Emperor global", (ex, ey), xytext=(6, -14), textcoords="offset points")

    for name, d in emp["regional_sensitivity"].items():
        x = math.log(d["N_ratio"])
        y = math.log(d["E_ratio"])
        ax.scatter([x], [y], marker=".")
        ax.annotate(name, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=7.5)

    ax.set_xlabel("log aggregate abundance ratio")
    ax.set_ylabel("log effective-unit-number ratio")
    ax.set_title("Aggregate direction does not fix spatial direction")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, outdir, "figure5_boundary_signs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--outdir", type=Path, default=Path("build/spatial_memory_integrated_figures"))
    args = ap.parse_args()

    root = args.repo_root.resolve()
    outdir = args.outdir
    if not outdir.is_absolute():
        outdir = root / outdir
    outdir.mkdir(parents=True, exist_ok=True)

    fig1_concept(root, outdir)
    fig2_ross(root, outdir)
    fig3_attrition(root, outdir)
    fig4_beaufort(root, outdir)
    fig5_boundary(root, outdir)


if __name__ == "__main__":
    main()
