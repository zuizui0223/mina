"""Submission-format guard for the Ecosphere-targeted manuscript."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAX_ABSTRACT_WORDS=350
MIN_KEYWORDS=6
MAX_KEYWORDS=12
REQUIRED_DOIS=(
    "10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e",
    "10.6073/pasta/4207e529832840db2282498d9f4f4f05",
    "10.6073/pasta/3eefb45dbfb784c3cabe3690ea46fe9e",
)
HUMAN_PLACEHOLDERS=(
    "[FINAL AUTHOR LIST AND ORDER]",
    "[FINAL AFFILIATIONS",
    "[ONE CORRESPONDING AUTHOR NAME]",
    "[EMAIL]",
)


def _words(text: str) -> int:
    cleaned=re.sub(r"[#*_\`|]", " ", text)
    return len(re.findall(r"\b\S+\b", cleaned))


def _section(text: str,start: str,end: str) -> str:
    a=text.find(start)
    b=text.find(end,a+len(start))
    if a<0 or b<0:
        raise ValueError(f"missing section boundary {start!r} -> {end!r}")
    return text[a+len(start):b].strip()


def _field(text: str,label: str) -> str:
    m=re.search(rf"(?m)^\*\*{re.escape(label)}:\*\*\s*(.+)$",text)
    if not m:
        raise ValueError(f"missing title-page field: {label}")
    return m.group(1).strip()


def validate(
    manuscript: str|Path,
    title_page: str|Path,
    ai_disclosure: str|Path,
) -> dict[str,object]:
    m=Path(manuscript).read_text(encoding="utf-8")
    t=Path(title_page).read_text(encoding="utf-8")
    ai=Path(ai_disclosure).read_text(encoding="utf-8")

    if _field(t,"Journal")!="Ecosphere":
        raise ValueError("title page journal must be Ecosphere")
    if _field(t,"Manuscript type")!="Article":
        raise ValueError("Ecosphere manuscript type must be Article")
    if _field(t,"Subject Track")!="Animal Ecology":
        raise ValueError("frozen first-shot subject track must be Animal Ecology")

    title_match=re.search(r"(?m)^#\s+(.+)$",m)
    if not title_match:
        raise ValueError("manuscript title missing")
    manuscript_title=title_match.group(1).strip()
    title_page_title=_field(t,"Title")
    if manuscript_title!=title_page_title:
        raise ValueError(
            f"title mismatch: manuscript={manuscript_title!r}; title_page={title_page_title!r}"
        )

    abstract=_section(m,"## Abstract","## Introduction")
    abstract_words=_words(abstract)
    if abstract_words>MAX_ABSTRACT_WORDS:
        raise ValueError(
            f"abstract too long: {abstract_words}>{MAX_ABSTRACT_WORDS}"
        )
    if re.search(r"@[A-Za-z][A-Za-z0-9_:-]*",abstract):
        raise ValueError("citation key found in Ecosphere abstract")
    if re.search(r"https?://|www\.",abstract,re.I):
        raise ValueError("URL found in Ecosphere abstract")

    kw_match=re.search(
        r"(?ms)^## Key words/phrases\s*\n\s*(.+?)(?:\n\n|\Z)",
        t,
    )
    if not kw_match:
        raise ValueError("title page missing Key words/phrases section")
    keywords=[x.strip() for x in kw_match.group(1).replace("\n"," ").split(";") if x.strip()]
    if not MIN_KEYWORDS<=len(keywords)<=MAX_KEYWORDS:
        raise ValueError(
            f"keyword count {len(keywords)} outside {MIN_KEYWORDS}-{MAX_KEYWORDS}"
        )

    for doi in REQUIRED_DOIS:
        if doi not in t:
            raise ValueError(f"Open Research Statement missing DOI {doi}")
    if "https://github.com/zuizui0223/mina" not in t:
        raise ValueError("Open Research Statement missing peer-review code location")
    if not ("Dryad" in t or "Zenodo" in t):
        raise ValueError("Open Research Statement missing intended permanent archive")

    required_headings=(
        "## Abstract",
        "## Introduction",
        "## Materials and Methods",
        "## Results",
        "## Discussion",
        "## Conclusion",
        "## References",
    )
    missing=[h for h in required_headings if h not in m]
    if missing:
        raise ValueError(f"missing Article headings: {missing}")

    lower=m.lower()
    prohibited=(
        "predicts local resilience",
        "effective colony number robustly predicts",
        "effective colony number provides a positive predictive pillar",
        "pc1 = 96.4% is a novel",
    )
    bad=[x for x in prohibited if x in lower]
    if bad:
        raise ValueError(f"prohibited post-diagnostic claims found: {bad}")
    for required in ("0.262","conditional association","timescale-dependent"):
        if required.lower() not in lower:
            raise ValueError(f"required post-diagnostic phrase missing: {required}")

    if "OpenAI ChatGPT" not in ai:
        raise ValueError("AI disclosure template does not identify the tool")
    if "full responsibility" not in ai:
        raise ValueError("AI disclosure template lacks author-responsibility language")

    unresolved=[p for p in HUMAN_PLACEHOLDERS if p in t]

    return {
        "target":"Ecosphere",
        "article_type":"Article",
        "subject_track":"Animal Ecology",
        "manuscript_title":manuscript_title,
        "abstract_words":abstract_words,
        "keyword_count":len(keywords),
        "keywords":keywords,
        "abstract_citation_url_check":"pass",
        "open_research_check":"pass",
        "post_diagnostic_claim_check":"pass",
        "ai_disclosure_template_check":"pass",
        "human_metadata_complete":len(unresolved)==0,
        "unresolved_human_placeholders":unresolved,
        "export_requirements_not_checkable_in_markdown":[
            "continuous line numbering",
            "double spacing",
            "12-point Times New Roman",
            "Letter portrait page size",
            "1-inch margins",
            "page numbering",
        ],
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--manuscript",required=True,type=Path)
    p.add_argument("--title-page",required=True,type=Path)
    p.add_argument("--ai-disclosure",required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(
        validate(a.manuscript,a.title_page,a.ai_disclosure),
        indent=2,sort_keys=True
    ))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
