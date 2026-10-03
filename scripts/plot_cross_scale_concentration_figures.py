"""Render publication-sized figures for the cross-scale concentration manuscript."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.plot_replicated_concentration_figures import figure1 as local_trajectory_figure
from scripts.plot_replicated_concentration_figures import figure3 as dominance_figure


LOCAL_ORDER = [
    "Cormorant",
    "Humble",
    "Litchfield",
    "Signy Adelie",
    "Signy chinstrap",
]

SPECIES_LABEL = {
    "ADPE": "Adelie",
    "CHPE": "Chinstrap",
    "GEPE": "Gentoo",
}


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(fig, out_dir: Path, stem: str) -> None:
    """Preserve native publication dimensions; do not expand with bbox_inches='tight'."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", dpi=300)
    fig.savefig(out_dir / f"{stem}.svg")
    fig.savefig(out_dir / f"{stem}.pdf")


def _p_text(value: float) -> str:
    text = f"{value:.3g}"
    return text.replace("e-0", "e−").replace("e-", "e−")


def figure2_scale_transfer(
    local_data_dir: Path,
    regional_receipt: Path,
    out_dir: Path,
) -> None:
    """Show within-system replication and regional scale transfer at <=18 cm width."""
    local_rows = _rows(local_data_dir / "figure2_summary.csv")
    local_lookup = {r["population"]: r for r in local_rows}
    local = [local_lookup[p] for p in LOCAL_ORDER]

    regional = _read_json(regional_receipt)
    declining = [p for p in regional["panels"] if p["direction"] == "decline"]
    declining.sort(key=lambda p: (p["region"], p["species"]))

    # 7.0 in = 17.78 cm, below Ecology's 18 cm maximum width.
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 4.6))

    names = [r["population"] for r in local]
    values = np.asarray(
        [100.0 * float(r["fractional_neff_change"]) for r in local]
    )
    pvals = np.asarray([float(r["cv20_p"]) for r in local])
    y = np.arange(len(local))

    bars = axes[0].barh(y, values, color="C0")
    axes[0].axvline(0.0, lw=1.0, color="0.25")
    axes[0].set_xlim(min(values) * 1.08, 0.0)
    axes[0].set_yticks(y, names)
    axes[0].invert_yaxis()
    axes[0].set_xlabel(
        "First-to-last change in effective components (%)", fontsize=7.5
    )
    axes[0].set_title("A. Within breeding systems", fontsize=8.5)
    axes[0].tick_params(labelsize=7)

    for bar, value, p in zip(bars, values, pvals):
        axes[0].text(
            value / 2.0,
            bar.get_y() + bar.get_height() / 2.0,
            f"{value:.0f}%  p={_p_text(p)}",
            ha="center",
            va="center",
            fontsize=6.5,
            color="white",
        )

    short_region = {
        "Central-west Antarctic Peninsula": "CW Peninsula",
        "South Shetland Islands": "S. Shetland Is.",
    }
    labels = [
        f"{SPECIES_LABEL[p['species']]} — {short_region[p['region']]}"
        for p in declining
    ]
    deltas = np.asarray(
        [float(p["delta_kappa_observation_error_null"]) for p in declining]
    )
    pvals_reg = np.asarray(
        [float(p["p_observation_error_null"]) for p in declining]
    )
    supported = np.asarray([bool(p["supported"]) for p in declining])
    y2 = np.arange(len(declining))

    axes[1].axvline(0.0, lw=1.0, color="0.25")
    axes[1].set_xlim(-0.02, max(deltas) + 0.18)
    for yi, delta, p, ok in zip(y2, deltas, pvals_reg, supported):
        marker = "o" if ok else "s"
        size = 52 if ok else 40
        axes[1].scatter([delta], [yi], marker=marker, s=size, color="C0")
        axes[1].plot([0.0, delta], [yi, yi], lw=1.0, color="C0")
        axes[1].text(
            delta + 0.012,
            yi,
            f"Δκ={delta:+.3f}, p={_p_text(p)}",
            va="center",
            fontsize=6.5,
        )

    axes[1].set_yticks(y2, labels)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Observation-error-calibrated Δκ", fontsize=7.5)
    axes[1].set_title("B. Regional monitored site networks", fontsize=8.5)
    axes[1].tick_params(labelsize=7)

    fig.text(
        0.01, 0.99, "Figure 2", ha="left", va="top", fontsize=9, fontweight="bold"
    )
    fig.suptitle(
        "Breeding-space concentration recurs across spatial levels",
        y=0.995,
        fontsize=9.5,
    )
    fig.text(
        0.73,
        0.015,
        "Circles: supported under both regional nulls; squares: same direction, not individually supported.",
        ha="center",
        fontsize=6.2,
    )
    fig.tight_layout(rect=(0.0, 0.065, 1.0, 0.96))
    _save(fig, out_dir, "figure2_cross_scale_transfer")
    plt.close(fig)


def figure3_regional_endpoints(
    regional_receipt: Path,
    out_dir: Path,
) -> None:
    """Render descriptive regional endpoints at <=18 cm width."""
    receipt = _read_json(regional_receipt)
    panels = receipt["panels"]

    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.axvline(0.0, lw=1.0, color="0.25")
    ax.axhline(0.0, lw=1.0, color="0.25")

    for panel in panels:
        dn = 100.0 * (
            float(panel["last_total"]) / float(panel["first_total"]) - 1.0
        )
        de = 100.0 * (
            float(panel["last_E"]) / float(panel["first_E"]) - 1.0
        )
        decline = panel["direction"] == "decline"
        marker = "o" if decline else "^"
        color = "C0" if decline else "C1"
        ax.scatter([dn], [de], marker=marker, s=52, color=color)

        short_region = (
            "CWAP"
            if panel["region"] == "Central-west Antarctic Peninsula"
            else "SSI"
            if panel["region"] == "South Shetland Islands"
            else "Victoria"
        )
        label = f"{SPECIES_LABEL[panel['species']]} {short_region}"
        offset = (5, 5)
        if panel["species"] == "CHPE" and panel["region"] == "South Shetland Islands":
            offset = (5, 9)
        ax.annotate(
            label,
            (dn, de),
            xytext=offset,
            textcoords="offset points",
            fontsize=7,
        )

    ax.scatter([], [], marker="o", s=52, color="C0", label="Declining network")
    ax.scatter([], [], marker="^", s=52, color="C1", label="Increasing network")
    ax.legend(frameon=False, loc="lower right", fontsize=7)

    ax.set_xlabel("First-to-last abundance change (%)", fontsize=8)
    ax.set_ylabel("First-to-last effective-site change (%)", fontsize=8)
    fig.text(
        0.01, 0.99, "Figure 3", ha="left", va="top", fontsize=9, fontweight="bold"
    )
    ax.set_title(
        "Abundance recovery need not rebuild regional site distribution",
        fontsize=9,
    )
    ax.tick_params(labelsize=7.5)
    fig.text(
        0.5,
        0.015,
        "Descriptive endpoints only; no regional hysteresis test was frozen.",
        ha="center",
        fontsize=6.8,
    )
    fig.tight_layout(rect=(0.0, 0.055, 1.0, 1.0))
    _save(fig, out_dir, "figure3_regional_endpoint_context")
    plt.close(fig)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--local-data-dir", required=True, type=Path)
    p.add_argument("--regional-receipt", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    a = p.parse_args()

    local_trajectory_figure(a.local_data_dir, a.out_dir)
    figure2_scale_transfer(a.local_data_dir, a.regional_receipt, a.out_dir)
    figure3_regional_endpoints(a.regional_receipt, a.out_dir)
    dominance_figure(a.local_data_dir, a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
