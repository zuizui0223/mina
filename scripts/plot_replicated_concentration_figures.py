"""Render publication-sized figures for replicated breeding-space concentration."""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ORDER = ["Cormorant", "Humble", "Litchfield", "Signy Adelie", "Signy chinstrap"]


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _save(fig, out_dir: Path, stem: str) -> None:
    """Preserve native <=18 cm publication width."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png", dpi=300)
    fig.savefig(out_dir / f"{stem}.svg")
    fig.savefig(out_dir / f"{stem}.pdf")


def figure1(data_dir: Path, out_dir: Path) -> None:
    rows = _rows(data_dir / "figure1_trajectories.csv")
    by_pop: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_pop[row["population"]].append(row)

    # 7.0 in = 17.78 cm, below Ecology's 18 cm maximum width.
    fig, axes = plt.subplots(2, 3, figsize=(7.0, 4.9), sharey=True)
    axes = axes.ravel()

    for ax, pop in zip(axes[:5], ORDER):
        local = sorted(by_pop[pop], key=lambda r: int(r["year"]))
        years = np.asarray([int(r["year"]) for r in local])
        abundance = np.asarray(
            [float(r["abundance_index_first100"]) for r in local]
        )
        neff = np.asarray(
            [float(r["neff_index_first100"]) for r in local]
        )
        ax.plot(
            years,
            abundance,
            marker="o",
            ms=2.7,
            lw=1.2,
            label="Breeding pairs",
        )
        ax.plot(
            years,
            neff,
            marker="s",
            ms=2.7,
            lw=1.2,
            ls="--",
            label="Effective monitored components",
        )
        ax.axhline(100, lw=1.0, ls=":", alpha=0.5)
        ax.set_title(pop, fontsize=8.2)
        ax.set_xlabel("Year", fontsize=7.5)
        ax.grid(alpha=0.15)
        ax.tick_params(labelsize=6.8)

    axes[0].set_ylabel("Index (first eligible season = 100)", fontsize=7.5)
    axes[3].set_ylabel("Index (first eligible season = 100)", fontsize=7.5)
    axes[5].axis("off")

    handles, labels = axes[0].get_legend_handles_labels()
    axes[5].legend(handles, labels, loc="center", frameon=False, fontsize=6.6)
    axes[5].text(
        0.5,
        0.28,
        "Five declining populations\nTwo species · Two Antarctic systems",
        ha="center",
        va="center",
        transform=axes[5].transAxes,
        fontsize=7.5,
    )

    fig.suptitle(
        "Population decline is accompanied by loss of effective monitored breeding components",
        y=0.99,
        fontsize=9.2,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.955))
    _save(fig, out_dir, "figure1_replicated_trajectories")
    plt.close(fig)


def figure2(data_dir: Path, out_dir: Path) -> None:
    """Legacy local summary retained for provenance, now at publication size."""
    rows = _rows(data_dir / "figure2_summary.csv")
    lookup = {r["population"]: r for r in rows}
    local = [lookup[p] for p in ORDER]

    frac = np.asarray(
        [100.0 * float(r["fractional_neff_change"]) for r in local]
    )
    pvals = np.asarray([float(r["cv20_p"]) for r in local])
    sig = -np.log10(pvals)
    slopes = [float(r["observed_neff_slope"]) for r in local]
    y = np.arange(len(local))

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 4.6), sharey=True)

    axes[0].barh(y, frac)
    axes[0].axvline(0, lw=1.0)
    axes[0].set_yticks(y, ORDER)
    axes[0].invert_yaxis()
    axes[0].set_xlabel(
        "Change in effective monitored components (%)", fontsize=7.5
    )
    axes[0].set_title("Biological magnitude", fontsize=8.5)
    axes[0].tick_params(labelsize=7)
    for yi, value in zip(y, frac):
        axes[0].text(
            value / 2.0,
            yi,
            f"{value:.0f}%",
            va="center",
            ha="center",
            color="white",
            fontsize=7,
        )

    axes[1].barh(y, sig)
    axes[1].axvline(-math.log10(0.05), lw=1.0, ls="--")
    axes[1].set_xlabel("−log10(CV20 null p)", fontsize=7.5)
    axes[1].set_title("Severe count-error null", fontsize=8.5)
    axes[1].tick_params(labelsize=7)
    for yi, s, p, beta in zip(y, sig, pvals, slopes):
        ptxt = f"{p:.1e}".replace("e-0", "e−").replace("e-", "e−")
        axes[1].text(
            s + 0.06,
            yi,
            f"p={ptxt}\nβ={beta:.3f}/yr",
            va="center",
            fontsize=6.5,
        )

    fig.suptitle(
        "Breeding-space contraction is repeated across five population units",
        y=0.99,
        fontsize=9.2,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    _save(fig, out_dir, "figure2_cross_population_summary")
    plt.close(fig)


def figure3(data_dir: Path, out_dir: Path) -> None:
    rows = _rows(data_dir / "figure3_dominance_routes.csv")
    lookup = {r["population"]: r for r in rows}

    fig, axes = plt.subplots(2, 3, figsize=(7.0, 4.9), sharex=True, sharey=True)
    axes = axes.ravel()

    for ax, pop in zip(axes[:5], ORDER):
        r = lookup[pop]
        x = np.asarray([0, 1], dtype=float)
        init = np.asarray([
            100.0 * float(r["initial_dom_share_first"]),
            100.0 * float(r["initial_dom_share_last"]),
        ])
        final = np.asarray([
            100.0 * float(r["final_dom_share_first"]),
            100.0 * float(r["final_dom_share_last"]),
        ])
        same = str(r["initial_dominant"]) == str(r["final_dominant"])

        def clean_unit(value: str) -> str:
            text = str(value)
            return text[:-2] if text.endswith(".0") else text

        if same:
            ax.plot(x, init, marker="o", lw=1.8, ms=3)
            ax.text(
                0.02,
                init[0] + 2,
                clean_unit(r["initial_dominant"]),
                fontsize=6.5,
            )
        else:
            ax.plot(
                x,
                init,
                marker="o",
                lw=1.5,
                ms=3,
                label="Initial dominant",
            )
            ax.plot(
                x,
                final,
                marker="s",
                lw=1.5,
                ms=3,
                ls="--",
                label="Final dominant",
            )
            ax.text(
                0.02,
                init[0] + 2,
                f"initial: {clean_unit(r['initial_dominant'])}",
                fontsize=6.3,
            )
            final_label_y = final[1] - 8 if final[1] > 90 else final[1] + 2
            ax.text(
                0.52,
                final_label_y,
                f"final: {clean_unit(r['final_dominant'])}",
                fontsize=6.3,
            )

        ax.set_xlim(-0.08, 1.08)
        ax.set_ylim(0, 105)
        ax.set_xticks([0, 1], ["First", "Last"])
        ax.set_title(pop, fontsize=8.2)
        ax.grid(axis="y", alpha=0.15)
        ax.tick_params(labelsize=6.8)
        ax.text(
            0.5,
            0.04,
            r["route"],
            ha="center",
            va="bottom",
            transform=ax.transAxes,
            fontsize=6.8,
        )

    axes[0].set_ylabel("Share of breeding pairs (%)", fontsize=7.5)
    axes[3].set_ylabel("Share of breeding pairs (%)", fontsize=7.5)
    axes[5].axis("off")

    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        axes[5].legend(handles, labels, loc="center", frameon=False, fontsize=6.6)
    axes[5].text(
        0.5,
        0.24,
        "Palmer: dominant code changes\nSigny: initial unit remains dominant",
        ha="center",
        va="center",
        transform=axes[5].transAxes,
        fontsize=7.3,
    )

    fig.suptitle(
        "Post-hoc nominal census-unit trajectories",
        y=0.99,
        fontsize=9.2,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.955))
    _save(fig, out_dir, "figureS1_nominal_dominance_routes")
    plt.close(fig)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    a = p.parse_args()
    figure1(a.data_dir, a.out_dir)
    figure2(a.data_dir, a.out_dir)
    figure3(a.data_dir, a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
