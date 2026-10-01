#!/usr/bin/env python3
"""Render JBI v0.5 Figures 1-4 from frozen integrated figure data.

Figure 1 reuses the frozen Palmer site/trajectory plotting logic. Figures 2-4
delegate to scripts/render_integrated_figures_v0_3.py after replacing only the
panel-label presentation with JBI-style lower-case labels.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _save(fig: plt.Figure, out_dir: Path, stem: str) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / f"{stem}.pdf"
    png = out_dir / f"{stem}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return [str(pdf), str(png)]


def render_figure1(palmer_data: Path, out_dir: Path) -> list[str]:
    sites = _rows(palmer_data / "figure1_sites.csv")
    trajectories = _rows(palmer_data / "figure1_trajectories.csv")
    islands = ["CHR", "COR", "HUM", "LIT", "TOR"]
    focal_names = {
        "Christine Island",
        "Cormorant Island",
        "Humble Island",
        "Litchfield Island",
        "Torgersen Island",
    }
    focal_sites = [row for row in sites if row["site_name"] in focal_names]
    if len(focal_sites) != 5:
        raise ValueError(f"expected five focal Palmer islands, observed {len(focal_sites)}")

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7))
    ax = axes[0]
    ax.scatter(
        [float(row["longitude"]) for row in focal_sites],
        [float(row["latitude"]) for row in focal_sites],
        marker="o",
        s=58,
    )
    for row in focal_sites:
        ax.annotate(
            row["site_name"].replace(" Island", ""),
            (float(row["longitude"]), float(row["latitude"])),
            xytext=(4, 3),
            textcoords="offset points",
            fontsize=7.5,
        )
    mean_lat = float(np.mean([float(row["latitude"]) for row in focal_sites]))
    # Local equirectangular aspect correction for geographic lon/lat coordinates.
    ax.set_aspect(1.0 / np.cos(np.deg2rad(mean_lat)))
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    bar_km = 2.0
    km_per_degree_lon = 111.32 * np.cos(np.deg2rad(mean_lat))
    bar_deg = bar_km / km_per_degree_lon
    x0 = xmin + 0.06 * (xmax - xmin)
    y0 = ymin + 0.07 * (ymax - ymin)
    ax.plot([x0, x0 + bar_deg], [y0, y0], linewidth=2)
    ax.text(
        x0 + bar_deg / 2,
        y0 + 0.012 * (ymax - ymin),
        "2 km",
        ha="center",
        va="bottom",
        fontsize=8,
    )
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")
    ax.set_title("(a) Palmer breeding-island system")
    ax.grid(alpha=0.2)

    ax = axes[1]
    for island in islands:
        local = [row for row in trajectories if row["island"] == island]
        ax.plot(
            [int(row["year"]) for row in local],
            [float(row["breeding_pairs"]) for row in local],
            marker="o",
            markersize=2.5,
            linewidth=1.1,
            label=island,
        )
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("Year")
    ax.set_ylabel("Breeding pairs (symlog)")
    ax.set_title("(b) Shared decline and divergent endpoints")
    ax.legend(frameon=False, ncol=2, fontsize=8)
    fig.tight_layout()
    return _save(fig, out_dir, "figure1_shared_decline_jbi_v0_5")


def _load_v03_renderer(repo_root: Path):
    path = repo_root / "scripts" / "render_integrated_figures_v0_3.py"
    spec = importlib.util.spec_from_file_location("integrated_v03_renderer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load renderer {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def jbi_panel_label(ax, label: str) -> None:
        ax.text(
            -0.12,
            1.04,
            f"({str(label).lower()})",
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            va="bottom",
            ha="left",
        )

    module._panel_label = jbi_panel_label
    return module


def render_latest_figures(repo_root: Path, integrated_data: Path, out_dir: Path) -> list[str]:
    module = _load_v03_renderer(repo_root)
    outputs: list[str] = []

    # Delegate all scientific plotting logic to the frozen v0.3 renderer.
    before = set(out_dir.glob("*")) if out_dir.exists() else set()
    module.render_figure2(integrated_data, out_dir)
    module.render_figure3(integrated_data, out_dir)
    module.render_figure4(integrated_data, out_dir)

    rename = {
        "figure2_palmer_dynamic_history_v0_3": "figure2_palmer_dynamic_history_jbi_v0_5",
        "figure3_antarctic_interaction_v0_3": "figure3_antarctic_interaction_jbi_v0_5",
        "figure4_scale_and_detectability_v0_3": "figure4_scale_and_detectability_jbi_v0_5",
    }
    for old, new in rename.items():
        for ext in ("pdf", "png"):
            src = out_dir / f"{old}.{ext}"
            dst = out_dir / f"{new}.{ext}"
            if not src.exists():
                raise FileNotFoundError(src)
            src.replace(dst)
            outputs.append(str(dst))
    after = set(out_dir.glob("*"))
    unexpected = [
        str(path) for path in sorted(after - before)
        if "_v0_3." in path.name
    ]
    if unexpected:
        raise RuntimeError(f"unrenamed v0.3 outputs remain: {unexpected}")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--palmer-data", required=True, type=Path)
    parser.add_argument("--integrated-data", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    outputs = render_figure1(args.palmer_data, args.out_dir)
    outputs.extend(
        render_latest_figures(args.repo_root, args.integrated_data, args.out_dir)
    )
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
