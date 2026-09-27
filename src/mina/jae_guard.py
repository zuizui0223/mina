"""Submission-format guard for the JAE-targeted manuscript."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAX_TOTAL_WORDS = 8500
MAX_ABSTRACT_WORDS = 350
MAX_KEYWORDS = 8
REQUIRED_HEADINGS = (
    "## Abstract",
    "## Introduction",
    "## Materials and Methods",
    "## Results",
    "## Discussion",
    "## Data availability",
    "## References",
)


def _words(text: str) -> int:
    cleaned = re.sub(r"[#*_\`|]", " ", text)
    return len(re.findall(r"\b\S+\b", cleaned))


def _section(text: str, start: str, end: str) -> str:
    a = text.find(start)
    b = text.find(end, a + len(start))
    if a < 0 or b < 0:
        raise ValueError(f"missing section boundary {start!r} -> {end!r}")
    return text[a + len(start):b].strip()


def validate(
    manuscript: str | Path,
    captions: str | Path,
    bibliography: str | Path,
) -> dict[str, object]:
    m = Path(manuscript).read_text(encoding="utf-8")
    c = Path(captions).read_text(encoding="utf-8")
    b = Path(bibliography).read_text(encoding="utf-8")

    missing = [heading for heading in REQUIRED_HEADINGS if heading not in m]
    if missing:
        raise ValueError(f"missing JAE headings: {missing}")

    abstract = _section(m, "## Abstract", "## Introduction")
    abstract_words = _words(abstract)
    if abstract_words > MAX_ABSTRACT_WORDS:
        raise ValueError(
            f"abstract too long: {abstract_words}>{MAX_ABSTRACT_WORDS}"
        )

    numbered = re.findall(r"(?m)^\s*([1-9][0-9]*)\.\s+", abstract)
    expected = [str(i) for i in range(1, len(numbered) + 1)]
    if numbered != expected or len(numbered) < 3:
        raise ValueError(
            "abstract must use consecutive numbered factual statements; "
            f"observed={numbered}"
        )

    match = re.search(r"(?m)^\*\*Keywords:\*\*\s*(.+)$", abstract)
    if not match:
        raise ValueError("missing Keywords line inside abstract section")
    keywords = [item.strip() for item in match.group(1).split(";") if item.strip()]
    if len(keywords) > MAX_KEYWORDS:
        raise ValueError(f"too many keywords: {len(keywords)}>{MAX_KEYWORDS}")
    if [item.casefold() for item in keywords] != sorted(
        item.casefold() for item in keywords
    ):
        raise ValueError("keywords are not alphabetical")

    total_words = _words(m) + _words(c) + _words(b)
    if total_words > MAX_TOTAL_WORDS:
        raise ValueError(
            f"submission text too long: {total_words}>{MAX_TOTAL_WORDS}"
        )

    if re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        m,
    ):
        raise ValueError("email address found in anonymized main manuscript")
    if "zuizui0223" in m.lower():
        raise ValueError(
            "repository owner identifier found in anonymized main manuscript"
        )

    data = _section(m, "## Data availability", "## References")
    for doi in (
        "10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e",
        "10.6073/pasta/4207e529832840db2282498d9f4f4f05",
        "10.6073/pasta/3eefb45dbfb784c3cabe3690ea46fe9e",
    ):
        if doi not in data:
            raise ValueError(
                f"required public-data DOI absent from Data availability: {doi}"
            )

    return {
        "target": "Journal of Animal Ecology",
        "article_type": "Research Article",
        "manuscript_words": _words(m),
        "caption_words": _words(c),
        "bibliography_words": _words(b),
        "total_submission_words_approx": total_words,
        "abstract_words": abstract_words,
        "abstract_statement_count": len(numbered),
        "keyword_count": len(keywords),
        "keywords": keywords,
        "headings_check": "pass",
        "anonymization_surface_check": "pass",
        "data_availability_check": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", required=True, type=Path)
    parser.add_argument("--captions", required=True, type=Path)
    parser.add_argument("--bibliography", required=True, type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            validate(args.manuscript, args.captions, args.bibliography),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
