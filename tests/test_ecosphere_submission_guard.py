from pathlib import Path

from mina.ecosphere_submission_guard import inspect


def test_submission_guard_passes_structure_but_stays_blocked(tmp_path):
    manuscript = tmp_path / "manuscript.md"
    title_page = tmp_path / "title.md"
    contract = tmp_path / "contract.json"

    manuscript.write_text(
        "# Common decline, divergent endpoints: hierarchical demography across Antarctic penguin breeding islands\n\n"
        "## Abstract\n"
        "One two three four five.\n\n"
        "**Keywords:** one; two; three; four; five; six\n",
        encoding="utf-8",
    )
    title_page.write_text(
        "## Open Research Statement\n"
        "https://github.com/zuizui0223/mina\n"
        "[AUTHOR 1]\n[Department]\n[ONE AUTHOR NAME]\n[EMAIL ADDRESS]\n",
        encoding="utf-8",
    )
    contract.write_text(
        """{
          "human_only_blockers": [
            "complete author list",
            "all affiliations",
            "single corresponding author",
            "author contributions",
            "funding",
            "conflict of interest",
            "complete AI tool inventory"
          ]
        }""",
        encoding="utf-8",
    )

    result = inspect(manuscript, title_page, contract)
    assert result["structural_checks"]["title_within_limit"] is True
    assert result["structural_checks"]["abstract_within_limit"] is True
    assert result["structural_checks"]["keywords_within_range"] is True
    assert result["ready_for_scholarone"] is False
    assert result["boundary"]["author_metadata_invented"] is False
