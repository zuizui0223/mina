"""Render manuscript figures from mina's frozen figure-data package."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _save(fig, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.png", dpi=240, bbox_inches="tight")
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")


def figure1(data: Path, out: Path) -> None:
    import matplotlib.pyplot as plt

    rows = _rows(data / "figure1_sites.csv")
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    primary = [r for r in rows if r["site_role"] == "primary_true_island"]
    bench = [r for r in rows if r["site_role"] != "primary_true_island"]

    for group, marker, label in (
        (primary, "o", "Primary island"),
        (bench, "s", "Non-island benchmark"),
    ):
        ax.scatter(
            [float(r["longitude"]) for r in group],
            [float(r["latitude"]) for r in group],
            marker=marker,
            s=64,
            label=label,
        )
    for r in rows:
        ax.annotate(
            r["site_name"].replace(" Island", "").replace(" Point", ""),
            (float(r["longitude"]), float(r["latitude"])),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Palmer breeding-patch network")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    _save(fig, out, "figure1_palmer_network")
    plt.close(fig)


def figure2(data: Path, out: Path) -> None:
    import matplotlib.pyplot as plt

    rows = _rows(data / "figure2_trajectories.csv")
    pairs = _rows(data / "figure2_pairwise_synchrony.csv")
    islands = ["CHR", "COR", "HUM", "LIT", "TOR"]

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    ax = axes[0]
    for island in islands:
        local = [r for r in rows if r["island"] == island]
        ax.plot(
            [int(r["year"]) for r in local],
            [float(r["breeding_pairs"]) for r in local],
            marker="o",
            markersize=2.8,
            linewidth=1.2,
            label=island,
        )
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("Year")
    ax.set_ylabel("Breeding pairs (symlog)")
    ax.set_title("Five-island Adélie decline")
    ax.legend(frameon=False, ncol=2)

    matrix = np.eye(len(islands), dtype=float)
    look = {island: i for i, island in enumerate(islands)}
    for r in pairs:
        i, j = look[r["island_a"]], look[r["island_b"]]
        value = float(r["correlation"])
        matrix[i, j] = value
        matrix[j, i] = value
    im = axes[1].imshow(matrix, vmin=-1, vmax=1)
    axes[1].set_xticks(range(len(islands)), islands)
    axes[1].set_yticks(range(len(islands)), islands)
    axes[1].set_title("Annual-growth synchrony")
    for i in range(len(islands)):
        for j in range(len(islands)):
            axes[1].text(
                j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=8
            )
    fig.colorbar(im, ax=axes[1], label="Pearson r")
    _save(fig, out, "figure2_common_decline")
    plt.close(fig)


def figure3(data: Path, out: Path) -> None:
    import matplotlib.pyplot as plt

    trajectories = _rows(data / "figure3_concentration_trajectories.csv")
    slopes = _rows(data / "figure3_concentration_slopes.csv")
    islands = ("COR", "HUM", "LIT")

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.8))

    for island in islands:
        local = [r for r in trajectories if r["island"] == island]
        axes[0].plot(
            [int(r["year"]) for r in local],
            [float(r["relative_to_first"]) for r in local],
            marker="o",
            markersize=3,
            linewidth=1.3,
            label=island,
        )
    axes[0].axhline(1.0, linewidth=0.8)
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Effective colony number / first observed value")
    axes[0].set_title("Breeders concentrate during island decline")
    axes[0].legend(frameon=False)

    y = np.arange(len(slopes))
    observed = np.asarray([float(r["observed_slope"]) for r in slopes])
    means = np.asarray([float(r["null_mean_slope_cv20"]) for r in slopes])
    lower = np.asarray([float(r["null_q025_slope_cv20"]) for r in slopes])
    upper = np.asarray([float(r["null_q975_slope_cv20"]) for r in slopes])
    xerr = np.vstack([means - lower, upper - means])
    axes[1].errorbar(
        means,
        y,
        xerr=xerr,
        fmt="o",
        capsize=3,
        label="Fixed-composition CV20 null (95%)",
    )
    axes[1].scatter(
        observed,
        y,
        marker="D",
        s=52,
        label="Observed slope",
    )
    axes[1].axvline(0.0, linewidth=0.8)
    axes[1].set_yticks(y, [r["island"] for r in slopes])
    axes[1].invert_yaxis()
    axes[1].set_xlabel("N_eff slope per year")
    axes[1].set_title("Concentration exceeds a severe count-error null")
    axes[1].set_xlim(
        float(min(np.min(observed), np.min(lower))) - 0.085,
        float(max(np.max(upper), 0.0)) + 0.025,
    )
    for i, r in enumerate(slopes):
        p = float(r["cv20_one_sided_p"])
        label = "p=0.000010" if p < 0.00002 else f"p={p:.3f}"
        axes[1].text(
            observed[i] - 0.012,
            i,
            label,
            ha="right",
            va="center",
            fontsize=8,
        )
    axes[1].legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=1,
        fontsize=8,
    )

    fig.tight_layout()
    _save(fig, out, "figure3_breeding_concentration")
    plt.close(fig)

def figure4(data: Path, out: Path) -> None:
    import matplotlib.pyplot as plt

    rows = _rows(data / "figure4_mechanism_audit.csv")
    labels = [r["test"] for r in rows]
    values = [100 * float(r["relative_error_reduction"]) for r in rows]
    y = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    ax.barh(y, values)
    ax.axvline(0, linewidth=1)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Held-out error reduction (%)")
    ax.set_title("Prospective mechanism audit")
    for i, r in enumerate(rows):
        direction = (
            "direction match"
            if r["direction_matches"] == "true"
            else "opposite direction"
        )
        supported = (
            "supported"
            if r["decision_supported"] == "true"
            else "not supported"
        )
        if r.get("permutation_p"):
            supported += f"; block-perm p={float(r['permutation_p']):.3f}"
        if values[i] >= 0:
            text_x = values[i] + 0.25
            text_ha = "left"
        else:
            # Keep the annotation near the zero reference rather than at the
            # far negative bar tip, so a strongly negative validation result
            # cannot collide with the y-axis test label.
            text_x = 0.35
            text_ha = "left"
        ax.text(
            text_x,
            i,
            f"{direction}; {supported}",
            va="center",
            ha=text_ha,
            fontsize=7.5,
        )
    ax.grid(axis="x", alpha=0.2)
    _save(fig, out, "figure4_mechanism_audit")
    plt.close(fig)


def figure5(data: Path, out: Path) -> None:
    import matplotlib.pyplot as plt

    transitions = _rows(data / "figure5_colony_transitions.csv")
    states = _rows(data / "figure5_colony_states.csv")
    external = _rows(data / "figure5_external_torgersen.csv")[0]
    islands = ["CHR", "COR", "HUM", "LIT", "TOR"]

    x = np.asarray(
        [float(r["conditional_topology_residual"]) for r in transitions]
    )
    y = np.asarray(
        [float(r["conditional_growth_residual"]) for r in transitions]
    )
    slope = float((x @ y) / (x @ x))

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    axes[0].scatter(x, y, s=20, alpha=0.7)
    xx = np.linspace(float(np.min(x)), float(np.max(x)), 100)
    axes[0].plot(xx, slope * xx, linewidth=1.4)
    axes[0].axhline(0, linewidth=0.8)
    axes[0].axvline(0, linewidth=0.8)
    axes[0].set_xlabel("Effective-colony residual")
    axes[0].set_ylabel("Next-year growth residual")
    gain_perm_p = float(external.get("neff_gain_permutation_p", "nan"))
    beta_circ_p = float(external.get("neff_beta_circular_independent_p", "nan"))
    beta_joint_p = float(external.get("neff_beta_circular_joint_p", "nan"))
    axes[0].set_title(
        "Conditional colony-organization association\n"
        f"β={slope:.3f}; predictive-gain p={gain_perm_p:.3f}; "
        f"circular β p={beta_circ_p:.1e}; joint p={beta_joint_p:.4f}"
    )

    for island in islands:
        local = [
            r
            for r in states
            if r["island"] == island
            and r["effective_colony_number"] not in {"", None}
        ]
        axes[1].plot(
            [int(r["year"]) for r in local],
            [float(r["effective_colony_number"]) for r in local],
            linewidth=1.1,
            label=island,
        )
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Effective colony number")
    axes[1].set_title(
        "Within-island colony-network state\n"
        f"Torgersen mapped footprints: 23 → {external['active_subcolonies_2022']}"
    )
    axes[1].legend(frameon=False, ncol=2)
    _save(fig, out, "figure5_colony_network")
    plt.close(fig)


def main() -> int:
    import matplotlib

    matplotlib.use("Agg")

    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    a = p.parse_args()
    figure1(a.data_dir, a.out_dir)
    figure2(a.data_dir, a.out_dir)
    figure3(a.data_dir, a.out_dir)
    figure4(a.data_dir, a.out_dir)
    figure5(a.data_dir, a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
