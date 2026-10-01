#!/usr/bin/env python3
"""Assemble the anonymous JBI review manuscript with frozen figures in place.

This script is display/submission packaging only. It does not read raw ecological
data or change any scientific value. Citations are left as Pandoc citation keys;
Pandoc/citeproc renders them in the workflow.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


FIGURES = {
    1: "figure1_shared_decline_jbi_v0_5.png",
    2: "figure2_palmer_dynamic_history_jbi_v0_5.png",
    3: "figure3_antarctic_interaction_jbi_v0_5.png",
    4: "figure4_scale_and_detectability_jbi_v0_5.png",
}

MARKERS = {
    "[**Figure 1–2 near here**]": [1, 2],
    "[**Figure 3 near here**]": [3],
    "[**Figure 4 near here**]": [4],
}

SUBMISSION_NOTATION_REPLACEMENTS = {
    r"(C_{\mathrm{recruit}}>0)": r"\(C_{\mathrm{recruit}}>0\)",
    r"(t\rightarrow t+1)": r"\(t\rightarrow t+1\)",
    r"(t+1\rightarrow t+2)": r"\(t+1\rightarrow t+2\)",
    r"(\rho_1 = 0.0639)": r"\(\rho_1 = 0.0639\)",
    r"((\rho_2) *p* = 0.0764; (\rho_3) *p* = 0.111)": (
        r"(\(\rho_2\), *p* = 0.0764; \(\rho_3\), *p* = 0.111)"
    ),
    r"(gamma_{AH}=-0.304)": r"\(\gamma_{AH}=-0.304\)",
    r"(gamma_{AH}=-1.184)": r"\(\gamma_{AH}=-1.184\)",
    r"(gamma_{AH}=-0.318)": r"\(\gamma_{AH}=-0.318\)",
    r"(gamma_A=-0.280)": r"\(\gamma_A=-0.280\)",
    r"(gamma_A=-0.200)": r"\(\gamma_A=-0.200\)",
    r"(gamma_A=-0.071)": r"\(\gamma_A=-0.071\)",
    r"**|gamma_AH| = 0.498**": r"**|γ_AH| = 0.498**",
}


def parse_captions(text: str) -> dict[int, str]:
    """Return complete Markdown captions keyed by figure number."""
    matches = list(re.finditer(r"^## Figure (\d+)\.\s*(.+)$", text, flags=re.MULTILINE))
    captions: dict[int, str] = {}
    for idx, match in enumerate(matches):
        number = int(match.group(1))
        title = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        captions[number] = f"**Figure {number}. {title}**\n\n{body}"
    return captions


def figure_block(number: int, fig_dir: Path, captions: dict[int, str]) -> str:
    if number not in captions:
        raise ValueError(f"missing caption for Figure {number}")
    image = fig_dir / FIGURES[number]
    if not image.exists() or image.stat().st_size == 0:
        raise FileNotFoundError(image)
    return (
        f"![]({image.as_posix()}){{width=95%}}\n\n"
        f"{captions[number]}"
    )


def build(manuscript: Path, captions_path: Path, fig_dir: Path, out: Path) -> None:
    text = manuscript.read_text(encoding="utf-8")
    captions = parse_captions(captions_path.read_text(encoding="utf-8"))
    if sorted(captions) != [1, 2, 3, 4]:
        raise ValueError(f"expected captions 1-4, got {sorted(captions)}")

    for marker, numbers in MARKERS.items():
        if text.count(marker) != 1:
            raise ValueError(f"expected one marker {marker!r}, found {text.count(marker)}")
        replacement = "\n\n".join(
            figure_block(number, fig_dir, captions) for number in numbers
        )
        text = text.replace(marker, replacement)

    leftovers = [marker for marker in MARKERS if marker in text]
    if leftovers:
        raise ValueError(f"unreplaced figure markers: {leftovers}")

    # Submission-format cleanup only: convert a small set of legacy inline
    # LaTeX-like strings to Pandoc math without changing values or claims.
    for source, target in SUBMISSION_NOTATION_REPLACEMENTS.items():
        text = text.replace(source, target)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", required=True, type=Path)
    parser.add_argument("--captions", required=True, type=Path)
    parser.add_argument("--fig-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    build(args.manuscript, args.captions, args.fig_dir, args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
