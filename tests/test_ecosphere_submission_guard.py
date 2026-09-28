import json

from mina.ecosphere_submission_guard import inspect


def _base_files(tmp_path):
    manuscript=tmp_path/"manuscript.md"
    title_page=tmp_path/"title.md"
    contract=tmp_path/"contract.json"

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
        json.dumps(
            {
                "human_only_blockers":[
                    "complete author list",
                    "all affiliations",
                    "single corresponding author",
                    "author contributions",
                    "funding",
                    "conflict of interest",
                    "complete AI tool inventory",
                    "dual-publication overlap statement",
                ],
                "word_preview":{
                    "preview_generated_and_visually_checked":True
                },
                "post_acceptance_tasks":["mint archive DOI"],
            }
        ),
        encoding="utf-8",
    )
    return manuscript,title_page,contract


def test_submission_guard_passes_structure_but_stays_blocked(tmp_path):
    manuscript,title_page,contract=_base_files(tmp_path)
    result=inspect(manuscript,title_page,contract)
    assert result["structural_checks"]["title_within_limit"] is True
    assert result["structural_checks"]["abstract_within_limit"] is True
    assert result["structural_checks"]["keywords_within_range"] is True
    assert result["structural_checks"]["preview_word_qa_recorded"] is True
    assert result["ready_for_scholarone"] is False
    assert result["boundary"]["author_metadata_invented"] is False
    assert result["boundary"][
        "permanent_archive_doi_required_before_initial_submission"
    ] is False


def test_complete_metadata_plus_final_word_qa_reaches_ready(tmp_path):
    manuscript,title_page,contract=_base_files(tmp_path)
    metadata=tmp_path/"metadata.json"
    metadata.write_text(
        json.dumps(
            {
                "authors":[
                    {
                        "name":"A. Author",
                        "affiliation_ids":["1"],
                        "corresponding":True,
                        "email":"a@example.org",
                    }
                ],
                "affiliations":{
                    "1":"Department A, University A, City, Country"
                },
                "present_addresses":[],
                "funding_acknowledgments":"Supported by grant X.",
                "additional_acknowledgments":"",
                "author_contributions":"A: Conceptualization, analysis, writing.",
                "conflict_of_interest":"The author declares no conflict.",
                "ai_tool_inventory_confirmed":True,
                "additional_ai_tools":[],
                "dual_publication_statement":"No overlapping manuscript is under review elsewhere.",
                "review_code_url":"https://github.com/zuizui0223/mina",
                "permanent_archive_doi":None,
            }
        ),
        encoding="utf-8",
    )
    result=inspect(
        manuscript,
        title_page,
        contract,
        metadata=metadata,
        word_qa_confirmed=True,
    )
    assert result["metadata_validation"][
        "ready_for_initial_submission_metadata"
    ] is True
    assert result["ready_for_scholarone"] is True
    assert result["post_acceptance_tasks"]==["mint archive DOI"]
