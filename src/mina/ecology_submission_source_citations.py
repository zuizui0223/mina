"""Add verified original dataset citations in *production* without editing frozen science.

This is bibliographic compliance for ESA Open Research, not a newly analyzed
dataset or an altered statistical endpoint. Final source/version choices
must be approved by the human authors.
"""
from __future__ import annotations

METHOD_HEADER = "### Evidence design and transparency"
REQUIRED_DATA_CITATION_KEYS = (
    "rossSeaAerialData2026",
    "palmerLterPenguinCensus2020",
    "signyAdelieMonitoring2021",
)
OPEN_RESEARCH_METHODS_CITATION = (
    "The original monitoring datasets underlying the spatial census comparisons "
    "are archived and individually citable: the Ross Sea Adélie aerial census "
    "[@rossSeaAerialData2026], the Palmer Station Antarctica LTER Adélie census "
    "[@palmerLterPenguinCensus2020], and the Signy Island Adélie monitoring "
    "dataset [@signyAdelieMonitoring2021]. Source-year subsets and derived "
    "calculations are specified in the version-controlled provenance and "
    "reproducibility records. Exact data versions and reuse terms are subject "
    "to final author verification."
)


def cite_public_sources_in_production_methods(body: str, *, production: bool) -> str:
    """Use the same original Methods subsection; only bibliographic text is added."""
    if not production:
        return body
    if body.count(METHOD_HEADER) != 1:
        raise ValueError("Frozen manuscript Methods citation anchor missing or repeated")
    return body.replace(METHOD_HEADER,
                        METHOD_HEADER + "\n\n" + OPEN_RESEARCH_METHODS_CITATION, 1)
