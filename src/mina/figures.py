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

    rows = _rows(data / "figure3_mechanism_audit.csv")
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
        ax.text(
            values[i] + (0.25 if values[i] >= 0 else -0.25),
            i,
            f"{direction}; {supported}",
            va="center",
            ha="left" if values[i] >= 0 else "right",
            fontsize=7.5,
        )
    ax.grid(axis="x", alpha=0.2)
    _save(fig, out, "figure3_mechanism_audit")
    plt.close(fig)


def figure4(data: Path, out: Path) -> None:
    import matplotlib.pyplot as plt

    transitions = _rows(data / "figure4_colony_transitions.csv")
    states = _rows(data / "figure4_colony_states.csv")
    external = _rows(data / "figure4_external_torgersen.csv")[0]
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
    axes[0].set_title(
        f"Conditional colony-network signal (β={slope:.3f})"
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
    _save(fig, out, "figure4_colony_network")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
