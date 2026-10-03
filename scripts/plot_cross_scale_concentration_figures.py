"""Render figures for the cross-scale breeding-space concentration manuscript."""
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
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out_dir / f"{stem}.pdf", bbox_inches="tight")


def figure2_scale_transfer(local_data_dir: Path, regional_receipt: Path, out_dir: Path) -> None:
    """Put the strongest local and regional evidence on a common visual page."""
    local_rows = _rows(local_data_dir / "figure2_summary.csv")
    local_lookup = {r["population"]: r for r in local_rows}
    local = [local_lookup[p] for p in LOCAL_ORDER]

    regional = _read_json(regional_receipt)
    declining = [p for p in regional["panels"] if p["direction"] == "decline"]
    declining.sort(key=lambda p: (p["region"], p["species"]))

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.3))

    # Panel A: local replicated endpoint.
    names = [r["population"] for r in local]
    values = np.asarray([100.0 * float(r["fractional_neff_change"]) for r in local])
    pvals = np.asarray([float(r["cv20_p"]) for r in local])
    y = np.arange(len(local))
    axes[0].barh(y, values)
    axes[0].axvline(0.0, lw=0.9)
    axes[0].set_yticks(y, names)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("First-to-last change in effective components (%)")
    axes[0].set_title("A. Within breeding systems")
    for yi, value, p in zip(y, values, pvals):
        axes[0].text(
            value - 1.5,
            yi,
            f"{value:.0f}%   p={p:.3g}",
            ha="right",
            va="center",
            fontsize=8.5,
        )

    # Panel B: regional scale-transfer result.
    labels = [
        f"{SPECIES_LABEL[p['species']]} — {p['region']}"
        for p in declining
    ]
    deltas = np.asarray([float(p["delta_kappa_observation_error_null"]) for p in declining])
    pvals_reg = np.asarray([float(p["p_observation_error_null"]) for p in declining])
    supported = np.asarray([bool(p["supported"]) for p in declining])
    y2 = np.arange(len(declining))
    axes[1].axvline(0.0, lw=0.9)
    for yi, delta, p, ok in zip(y2, deltas, pvals_reg, supported):
        marker = "o" if ok else "s"
        size = 70 if ok else 48
        axes[1].scatter([delta], [yi], marker=marker, s=size)
        axes[1].plot([0.0, delta], [yi, yi], lw=1.1)
        axes[1].text(
            delta + 0.012,
            yi,
            f"Δκ={delta:+.3f}, p={p:.3g}",
            va="center",
            fontsize=8.5,
        )
    axes[1].set_yticks(y2, labels)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Observation-error-calibrated Δκ")
    axes[1].set_title("B. Regional monitored site networks")
    axes[1].text(
        0.02,
        -0.18,
        "Circles: individually supported under both frozen regional nulls; squares: same direction, not individually supported.",
        transform=axes[1].transAxes,
        fontsize=8.5,
        va="top",
    )

    fig.suptitle(
        "Breeding-space concentration recurs when the spatial component is moved one level up",
        y=1.02,
    )
    fig.tight_layout()
    _save(fig, out_dir, "figure2_cross_scale_transfer")
    plt.close(fig)


def figure3_regional_endpoints(regional_receipt: Path, out_dir: Path) -> None:
    """Describe how abundance and effective-site endpoints co-move regionally."""
    receipt = _read_json(regional_receipt)
    panels = receipt["panels"]

    fig, ax = plt.subplots(figsize=(8.4, 6.2))
    ax.axvline(0.0, lw=0.9)
    ax.axhline(0.0, lw=0.9)

    for panel in panels:
        dn = 100.0 * (float(panel["last_total"]) / float(panel["first_total"]) - 1.0)
        de = 100.0 * (float(panel["last_E"]) / float(panel["first_E"]) - 1.0)
        marker = "o" if panel["direction"] == "decline" else "^"
        ax.scatter([dn], [de], marker=marker, s=65)
        short_region = (
            "CWAP"
            if panel["region"] == "Central-west Antarctic Peninsula"
            else "SSI"
            if panel["region"] == "South Shetland Islands"
            else "Victoria"
        )
        label = f"{SPECIES_LABEL[panel['species']]} {short_region}"
        ax.annotate(label, (dn, de), xytext=(5, 5), textcoords="offset points", fontsize=8.5)

    ax.set_xlabel("First-to-last abundance change (%)")
    ax.set_ylabel("First-to-last effective-site change (%)")
    ax.set_title("Regional endpoint changes: abundance recovery need not rebuild site distribution")
    ax.text(
        0.02,
        0.02,
        "Circles: declining networks; triangles: increasing networks.\nDescriptive endpoints only; no regional hysteresis test was frozen.",
        transform=ax.transAxes,
        fontsize=8.5,
        va="bottom",
    )
    fig.tight_layout()
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
