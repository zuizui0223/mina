"""Guard the manuscript against numeric drift and prohibited causal claims."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from .synthesis import build


PROHIBITED = (
    "sea ice is unimportant",
    "sea ice is irrelevant",
    "colony-network diversity causally protects",
    "effective colony number causally protects",
    "large breeding groups are harmful",
    "fragmentation causes the effective-colony",
    "colony-code-level validation was confirmed",
)


def citation_keys(text: str) -> set[str]:
    return set(re.findall(r"@([A-Za-z][A-Za-z0-9_:-]*)", text))


def bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@[A-Za-z]+\{([^,]+),", text))


def validate(
    manuscript: str | Path,
    captions: str | Path,
    bibliography: str | Path,
    results_dir: str | Path,
) -> dict[str, object]:
    text=Path(manuscript).read_text(encoding="utf-8")
    cap=Path(captions).read_text(encoding="utf-8")
    bib=Path(bibliography).read_text(encoding="utf-8")
    synth=build(results_dir)

    d=synth["five_island_decline"]
    c=synth["local_colony_state"]
    required=(
        f'{100*float(d["pc1_variance_fraction"]):.1f}%',
        f'{float(d["median_annual_growth_correlation"]):.3f}',
        f'{100*float(d["unique_year_fraction"]):.1f}%',
        f'{100*float(d["unique_island_fraction"]):.1f}%',
        f'{float(c["effective_colony_number"]["beta"]):+.4f}',
        "phenomenon-level",
        "crosswalk",
    )
    missing=[item for item in required if item not in text+cap]
    if missing:
        raise ValueError(f"manuscript/captions missing frozen items: {missing}")

    lower=(text+"\n"+cap).lower()
    bad=[phrase for phrase in PROHIBITED if phrase in lower]
    if bad:
        raise ValueError(f"prohibited manuscript claims found: {bad}")

    cited=citation_keys(text+"\n"+cap)
    available=bib_keys(bib)
    unknown=sorted(cited-available)
    if unknown:
        raise ValueError(f"citation keys missing from bibliography: {unknown}")

    return {
        "manuscript_words":len(text.split()),
        "caption_words":len(cap.split()),
        "citation_keys":sorted(cited),
        "citation_count":len(cited),
        "required_frozen_items":list(required),
        "prohibited_claim_check":"pass",
        "unknown_citations":unknown,
        "synthesis_id":synth["synthesis_id"],
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--manuscript",required=True,type=Path)
    p.add_argument("--captions",required=True,type=Path)
    p.add_argument("--bibliography",required=True,type=Path)
    p.add_argument("--results",default=Path("results"),type=Path)
    a=p.parse_args()
    result=validate(a.manuscript,a.captions,a.bibliography,a.results)
    import json
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
