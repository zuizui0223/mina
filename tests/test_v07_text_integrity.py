from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "docs" / "MANUSCRIPT_ECOSPHERE_V0_7.md"
CAPTIONS = ROOT / "docs" / "FIGURE_CAPTIONS_V6.md"

EXPECTED_TITLE = (
    "Hierarchical demography of Antarctic penguin breeding islands: "
    "divergent fate and measurement-sensitive buffering"
)


def _bad_controls(text: str) -> list[int]:
    return [
        ord(char)
        for char in text
        if ord(char) < 32 and char not in {"\n", "\r", "\t"}
    ]


def test_v07_text_has_no_control_characters():
    assert _bad_controls(MANUSCRIPT.read_text(encoding="utf-8")) == []
    assert _bad_controls(CAPTIONS.read_text(encoding="utf-8")) == []


def test_v07_title_is_measurement_error_aware():
    title = MANUSCRIPT.read_text(encoding="utf-8").splitlines()[0]
    assert title == "# " + EXPECTED_TITLE
    assert len(EXPECTED_TITLE) <= 120


def test_v07_measurement_error_literature_is_cited():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    assert "@santinjanin2014" in text
    assert "@loreau2021" in text


def test_v07_forbidden_buffering_claims_do_not_return():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    forbidden = (
        "most detectable temporal compensation occurs within islands",
        "principal observable temporal compensation lay below the island level",
        "larger and robust variability reduction occurred",
        "The strongest inference is thus hierarchical rather than predictive",
        "hierarchy is measurement-error robust",
    )
    assert all(token not in text for token in forbidden)
