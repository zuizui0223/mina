from mina.ecosphere_submission_metadata import (
    DEFAULT_REVIEW_CODE_URL,
    affiliation_lines,
    author_line,
    corresponding_text,
    present_address_text,
    validate_metadata,
)


def _complete():
    return {
        "authors":[
            {
                "name":"A. Author",
                "affiliation_ids":["1"],
                "corresponding":True,
                "email":"a@example.org",
            },
            {
                "name":"B. Author",
                "affiliation_ids":["2"],
                "corresponding":False,
                "email":None,
            },
        ],
        "affiliations":{
            "1":"Department A, University A, City, Country",
            "2":"Department B, University B, City, Country",
        },
        "present_addresses":[],
        "funding_acknowledgments":"Supported by grant X.",
        "additional_acknowledgments":"",
        "author_contributions":"A: Conceptualization; B: Data curation.",
        "conflict_of_interest":"The authors declare no conflicts of interest.",
        "ai_tool_inventory_confirmed":True,
        "additional_ai_tools":[],
        "dual_publication_statement":"No overlapping manuscript is under review elsewhere.",
        "review_code_url":DEFAULT_REVIEW_CODE_URL,
        "permanent_archive_doi":None,
    }


def test_empty_template_is_not_submission_ready():
    result=validate_metadata({
        "authors":[],
        "affiliations":{},
        "present_addresses":[],
        "funding_acknowledgments":None,
        "author_contributions":None,
        "conflict_of_interest":None,
        "ai_tool_inventory_confirmed":False,
        "additional_ai_tools":[],
        "dual_publication_statement":None,
        "review_code_url":DEFAULT_REVIEW_CODE_URL,
        "permanent_archive_doi":None,
    })
    assert result["ready_for_initial_submission_metadata"] is False
    assert result["post_acceptance_archive_pending"] is True


def test_complete_metadata_is_ready_without_zenodo_doi():
    data=_complete()
    result=validate_metadata(data)
    assert result["ready_for_initial_submission_metadata"] is True
    assert result["post_acceptance_archive_pending"] is True
    assert author_line(data)=="A. Author^1^*; B. Author^2^"
    assert "^1^ Department A" in affiliation_lines(data)
    assert present_address_text(data)=="None."
    assert corresponding_text(data)=="A. Author, a@example.org"


def test_multiple_corresponding_authors_fail():
    data=_complete()
    data["authors"][1]["corresponding"]=True
    data["authors"][1]["email"]="b@example.org"
    result=validate_metadata(data)
    assert result["ready_for_initial_submission_metadata"] is False
    assert "exactly_one_corresponding_author" in result["unresolved_fields"]
