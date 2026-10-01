#!/usr/bin/env python3
"""Assemble the anonymous JBI review manuscript with frozen figures in place.

This is submission/display packaging only. It does not read raw ecological data
or change scientific values. The source manuscript deliberately uses lightweight
Markdown/LaTeX notation that is convenient in git but not always interpreted as
Word math by Pandoc. This builder normalizes presentation-only math syntax before
Pandoc/citeproc creates the anonymous review DOCX.
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

_SINGLE_MATH_VARIABLES = {"t", "i", "j", "k", "u", "h", "G", "N", "C", "E", "Q", "R", "S"}
_GREEK_START = {"β", "γ", "ρ", "δ", "λ", "α"}


def _normalize_fragment(value: str) -> str:
    """Repair manuscript shorthand only inside an already-mathematical fragment."""
    value = value.replace("gamma_{AH}", r"\gamma_{AH}")
    value = re.sub(r"\bgamma_A\b", r"\\gamma_A", value)
    value = re.sub(r"(?<!\\)mathrm\{", r"\\mathrm{", value)
    return value


def normalize_math(text: str) -> str:
    """Normalize git-friendly manuscript math into Pandoc-friendly math.

    Scientific expressions are unchanged. Transformations are display-only:
    single-$ multiline fences become $$ display fences, explicit \( ... \)
    becomes dollar inline math, pseudo-math parentheses are wrapped, and a few
    raw textual subscript identifiers are repaired for Word rendering.
    """
    text = text.replace(
        "**C_recruit = −0.0422, p = 0.988**",
        r"**$C_{\mathrm{recruit}} = -0.0422, p = 0.988$**",
    )
    text = text.replace(
        "**δ_past = 0.0296, p = 0.00154**",
        r"**$\delta_{\mathrm{past}} = 0.0296, p = 0.00154$**",
    )
    text = text.replace(
        "**|gamma_AH| = 0.498**",
        r"**$|\gamma_{AH}| = 0.498$**",
    )
    text = text.replace("γ_AH", r"$\gamma_{AH}$")
    text = text.replace("γ_A", r"$\gamma_A$")

    protected: list[str] = []

    def protect_explicit(match: re.Match[str]) -> str:
        protected.append(match.group(1))
        return f"@@MATH{len(protected)-1}@@"

    text = re.sub(r"\\\((.*?)\\\)", protect_explicit, text)
    parenthetical = re.compile(r"\(([^()\n]+)\)")

    def wrap_parenthetical(match: re.Match[str]) -> str:
        value = match.group(1).strip()
        if "$" in value or "@@MATH" in value or "*" in value:
            return match.group(0)
        no_spaces = not any(ch.isspace() for ch in value)
        has_operator = any(op in value for op in "=<>")
        math_like = (
            "\\" in value
            or "_" in value
            or value in _SINGLE_MATH_VARIABLES
            or (no_spaces and has_operator)
            or (value[:1] in _GREEK_START and has_operator)
        )
        if not math_like:
            return match.group(0)
        return "$(" + _normalize_fragment(value) + ")$"

    out_lines: list[str] = []
    in_display = False
    for line in text.splitlines():
        if line.strip() == "$":
            out_lines.append("$$")
            in_display = not in_display
            continue

        if (not in_display) and line.lstrip().startswith("![]("):
            out_lines.append(line)
            continue

        if in_display:
            line = line.replace(
                r"\mathrm{ice\text{-}free\ area}",
                r"\text{ice-free area}",
            )
            line = line.replace(
                r"\mathrm{Tier\ 2\ Habitat\ Complex\ richness}",
                r"\text{Tier 2 Habitat Complex richness}",
            )
            line = line.replace(
                r"\#\{T_{\mathrm{perm}}\leq T_{\mathrm{obs}}\}",
                r"\text{count}\{T_{\mathrm{perm}}\leq T_{\mathrm{obs}}\}",
            )
            out_lines.append(line)
        else:
            out_lines.append(parenthetical.sub(wrap_parenthetical, line))

    if in_display:
        raise ValueError("unbalanced single-dollar display-math fence")

    normalized = "\n".join(out_lines)
    for idx, value in enumerate(protected):
        normalized = normalized.replace(f"@@MATH{idx}@@", "$" + value + "$")
    return normalized


def parse_captions(text: str) -> dict[int, str]:
    """Return complete Markdown captions keyed by figure number."""
    matches = list(
        re.finditer(r"^## Figure (\d+)\.\s*(.+)$", text, flags=re.MULTILINE)
    )
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
    return f"![]({image.as_posix()}){{width=95%}}\n\n{captions[number]}"


def build(manuscript: Path, captions_path: Path, fig_dir: Path, out: Path) -> None:
    text = normalize_math(manuscript.read_text(encoding="utf-8"))
    captions = parse_captions(
        normalize_math(captions_path.read_text(encoding="utf-8"))
    )
    if sorted(captions) != [1, 2, 3, 4]:
        raise ValueError(f"expected captions 1-4, got {sorted(captions)}")

    for marker, numbers in MARKERS.items():
        if text.count(marker) != 1:
            raise ValueError(
                f"expected one marker {marker!r}, found {text.count(marker)}"
            )
        replacement = "\n\n".join(
            figure_block(number, fig_dir, captions) for number in numbers
        )
        text = text.replace(marker, replacement)

    leftovers = [marker for marker in MARKERS if marker in text]
    if leftovers:
        raise ValueError(f"unreplaced figure markers: {leftovers}")

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
