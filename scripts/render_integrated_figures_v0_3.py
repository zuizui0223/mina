#!/usr/bin/env python3
"""Render integrated manuscript v0.3 figures from frozen figure-data tables.

The renderer never reads raw ecological source data. All inputs are derived by
scripts/build_integrated_figure_data_v0_3.py from committed result receipts.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(fig: plt.Figure, out_dir: Path, stem: str) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / f"{stem}.pdf"
    png = out_dir / f"{stem}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return [str(pdf), str(png)]


def _panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.12,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        va="bottom",
        ha="left",
    )


def render_figure2(data_dir: Path, out_dir: Path) -> list[str]:
    concentration = pd.read_csv(data_dir / "figure2a_palmer_concentration.csv")
    lag = pd.read_csv(data_dir / "figure2b_palmer_lag_profile.csv")
    validation = pd.read_csv(data_dir / "figure2c_palmer_metric_validation.csv")

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2))

    # A. Within-island concentration: endpoint change plus fixed-null p values.
    ax = axes[0]
    x = np.arange(len(concentration))
    for i, row in concentration.reset_index(drop=True).iterrows():
        ax.plot(
            [i - 0.12, i + 0.12],
            [row["first_neff"], row["last_neff"]],
            marker="o",
            linewidth=1.5,
        )
        ax.text(
            i,
            max(row["first_neff"], row["last_neff"]) + 0.18,
            f"p={row['cv20_p']:.3g}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(concentration["island"].tolist(), rotation=18, ha="right")
    ax.set_ylabel("Effective colony number")
    ax.set_title("Concentration during decline")
    ax.grid(axis="y", alpha=0.25)
    _panel_label(ax, "A")

    # B. Lag profile of the colony-wide state.
    ax = axes[1]
    ax.axhline(0.0, linewidth=1.0)
    ax.plot(lag["lag_years"], lag["beta"], marker="o", linewidth=1.4)
    coupled = lag[lag["mechanically_coupled"].astype(bool)]
    primary = lag[lag["primary_bias_resistant"].astype(bool)]
    ax.scatter(coupled["lag_years"], coupled["beta"], marker="x", s=65, zorder=3)
    ax.scatter(primary["lag_years"], primary["beta"], marker="s", s=60, zorder=3)
    for _, row in lag.iterrows():
        ax.text(
            row["lag_years"],
            row["beta"] + (0.008 if row["beta"] >= 0 else -0.012),
            f"p={row['one_sided_p']:.3g}",
            ha="center",
            va="bottom" if row["beta"] >= 0 else "top",
            fontsize=7.5,
        )
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Lag (years)")
    ax.set_ylabel("State coefficient, β")
    ax.set_title("Short-lived history")
    ax.grid(axis="y", alpha=0.25)
    _panel_label(ax, "B")

    # C. Independent metric validation and post-result common-panel diagnostic.
    ax = axes[2]
    labels = [
        "REPRO mean\nlag 1",
        "REPRO mean\nlag 2",
        "Any-crèche\nsensitivity",
        "Colony-wide state\ncommon panel",
        "Nest mean\ncommon panel",
    ]
    validation = validation.copy()
    validation["plot_label"] = labels[: len(validation)]
    y = np.arange(len(validation))[::-1]
    ax.axvline(0.0, linewidth=1.0)
    for yi, (_, row) in zip(y, validation.iterrows()):
        role = str(row["inference_role"])
        marker = "s" if "posthoc" in role else ("^" if "sensitivity" in role else "o")
        ax.scatter(row["beta"], yi, marker=marker, s=55)
        if pd.notna(row["null_q025"]) and pd.notna(row["null_q975"]):
            ax.plot([row["null_q025"], row["null_q975"]], [yi, yi], linewidth=1.2)
        if pd.notna(row["one_sided_p"]):
            ax.text(
                row["beta"] + 0.008,
                yi,
                f"p={row['one_sided_p']:.3g}",
                va="center",
                fontsize=7.5,
            )
    ax.set_yticks(y)
    ax.set_yticklabels(validation["plot_label"])
    ax.set_xlabel("Redistribution coefficient, β")
    ax.set_title("Independent metric check")
    ax.grid(axis="x", alpha=0.25)
    _panel_label(ax, "C")

    fig.suptitle(
        "Palmer decline: spatial concentration and short-lived colony-state history",
        fontsize=13,
        y=1.02,
    )
    fig.tight_layout()
    return _save(fig, out_dir, "figure2_palmer_dynamic_history_v0_3")


def render_figure3(data_dir: Path, out_dir: Path) -> list[str]:
    species = pd.read_csv(data_dir / "figure3_species_interactions.csv")
    null = pd.read_csv(data_dir / "figure3_paper_level_null.csv").iloc[0]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.1))

    ax = axes[0]
    y = np.arange(len(species))[::-1]
    ax.axvline(0.0, linewidth=1.0)
    ax.scatter(species["gamma_ah"], y, s=70)
    for yi, (_, row) in zip(y, species.iterrows()):
        ax.text(
            row["gamma_ah"] + 0.035,
            yi,
            f"p={row['raw_p_value']:.3g}",
            va="center",
            fontsize=8,
        )
    label_map = {"ADPE": "Adélie", "CHPE": "Chinstrap", "GEPE": "Gentoo"}
    ax.set_yticks(y)
    ax.set_yticklabels([label_map.get(x, x) for x in species["species_id"]])
    ax.set_xlabel("Area × heterogeneity effect, γAH")
    ax.set_title("Species-specific estimates")
    ax.grid(axis="x", alpha=0.25)
    _panel_label(ax, "A")

    ax = axes[1]
    ax.axvline(0.0, linewidth=1.0)
    ax.plot([null["null_q01"], null["null_q99"]], [0, 0], linewidth=1.0)
    ax.plot([null["null_q05"], null["null_q95"]], [0, 0], linewidth=5.0)
    ax.scatter([null["null_median"]], [0], marker="D", s=55, label="Null median")
    ax.scatter(
        [null["observed_median_gamma_ah"]],
        [0],
        marker="*",
        s=140,
        label="Observed median",
    )
    ax.set_yticks([])
    ax.set_xlabel("Cross-species median γAH")
    ax.set_title(f"Frozen permutation null (p={null['permutation_p']:.4f})")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.grid(axis="x", alpha=0.25)
    _panel_label(ax, "B")

    fig.suptitle(
        "Static island architecture: concordant direction without confirmatory support",
        fontsize=13,
        y=1.02,
    )
    fig.tight_layout()
    return _save(fig, out_dir, "figure3_antarctic_interaction_v0_3")


def render_figure4(data_dir: Path, out_dir: Path) -> list[str]:
    scale = pd.read_csv(data_dir / "figure4_scale_sensitivity.csv")
    detect = pd.read_csv(data_dir / "figure4_detectable_effect.csv")

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2))

    ax = axes[0]
    richness = scale[scale["metric"] == "tier2_richness"].sort_values("radius_m")
    ax.axhline(0.0, linewidth=1.0)
    ax.plot(
        richness["radius_m"] / 1000.0,
        richness["median_gamma_ah"],
        marker="o",
        linewidth=1.4,
        label="Tier 2 richness",
    )
    shannon = scale[scale["metric"] == "tier2_shannon"]
    if len(shannon):
        ax.scatter(
            shannon["radius_m"] / 1000.0,
            shannon["median_gamma_ah"],
            marker="s",
            s=65,
            label="Tier 2 Shannon",
        )
    ax.set_xticks([1, 2, 5])
    ax.set_xlabel("Landscape radius (km)")
    ax.set_ylabel("Cross-species median γAH")
    ax.set_title("Spatial-support sensitivity")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.25)
    _panel_label(ax, "A")

    ax = axes[1]
    x = detect["abs_truth_gamma_ah"].to_numpy()
    y = detect["detection_fraction"].to_numpy()
    yerr = np.vstack(
        [
            y - detect["wilson_low"].to_numpy(),
            detect["wilson_high"].to_numpy() - y,
        ]
    )
    ax.errorbar(x, y, yerr=yerr, marker="o", linewidth=1.3, capsize=2)
    ax.axhline(0.8, linewidth=1.0, linestyle="--")
    ax.axhline(0.9, linewidth=1.0, linestyle=":")
    ax.axvline(0.3182260358, linewidth=1.0, linestyle="-.", label="Observed |median|")
    ax.axvline(0.49765625, linewidth=1.0, linestyle="--", label="MDE80")
    ax.axvline(0.5385714286, linewidth=1.0, linestyle=":", label="MDE90")
    ax.set_ylim(-0.02, 1.03)
    ax.set_xlabel("|True common γAH|")
    ax.set_ylabel("Detection probability")
    ax.set_title("Detectable common effect")
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    ax.grid(alpha=0.25)
    _panel_label(ax, "B")

    fig.suptitle(
        "Why the Antarctic-wide result remains non-confirmatory",
        fontsize=13,
        y=1.02,
    )
    fig.tight_layout()
    return _save(fig, out_dir, "figure4_scale_and_detectability_v0_3")


def render_all(data_dir: Path, out_dir: Path) -> list[str]:
    outputs: list[str] = []
    outputs.extend(render_figure2(data_dir, out_dir))
    outputs.extend(render_figure3(data_dir, out_dir))
    outputs.extend(render_figure4(data_dir, out_dir))
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    outputs = render_all(args.data_dir, args.out_dir)
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
