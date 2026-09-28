"""Human-controlled metadata for the Ecosphere v0.6 submission package."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_REVIEW_CODE_URL = "https://github.com/zuizui0223/mina"


def load_metadata(path: str | Path) -> dict[str, Any]:
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data,dict):
        raise ValueError("submission metadata must be a JSON object")
    return data


def _text(value: Any) -> str:
    return value.strip() if isinstance(value,str) else ""


def _authors(data: dict[str,Any]) -> list[dict[str,Any]]:
    value=data.get("authors")
    if not isinstance(value,list):
        return []
    return [x for x in value if isinstance(x,dict)]


def validate_metadata(data: dict[str,Any]) -> dict[str,Any]:
    unresolved: list[str]=[]
    authors=_authors(data)
    affiliations=data.get("affiliations")
    if not authors:
        unresolved.append("authors")
    if not isinstance(affiliations,dict) or not affiliations:
        unresolved.append("affiliations")
        affiliations={}

    corresponding=[]
    for index,author in enumerate(authors,1):
        name=_text(author.get("name"))
        if not name:
            unresolved.append(f"authors[{index}].name")
        ids=author.get("affiliation_ids")
        if not isinstance(ids,list) or not ids:
            unresolved.append(f"authors[{index}].affiliation_ids")
            ids=[]
        for affiliation_id in ids:
            key=str(affiliation_id)
            if not _text(affiliations.get(key)):
                unresolved.append(
                    f"authors[{index}].affiliation_ids references missing {key}"
                )
        if bool(author.get("corresponding")):
            corresponding.append(author)
            email=_text(author.get("email"))
            if not email or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email):
                unresolved.append(f"authors[{index}].email")

    if len(corresponding)!=1:
        unresolved.append("exactly_one_corresponding_author")

    for key,value in affiliations.items():
        if not _text(value):
            unresolved.append(f"affiliations.{key}")

    for field in (
        "funding_acknowledgments",
        "author_contributions",
        "conflict_of_interest",
        "dual_publication_statement",
    ):
        if not _text(data.get(field)):
            unresolved.append(field)

    if data.get("ai_tool_inventory_confirmed") is not True:
        unresolved.append("ai_tool_inventory_confirmed")

    tools=data.get("additional_ai_tools")
    if tools is None:
        unresolved.append("additional_ai_tools")
    elif not isinstance(tools,list) or any(not _text(item) for item in tools):
        unresolved.append("additional_ai_tools")

    review_url=_text(data.get("review_code_url"))
    if not review_url:
        unresolved.append("review_code_url")

    present=data.get("present_addresses")
    if present is None:
        unresolved.append("present_addresses")
    elif not isinstance(present,list) or any(not _text(item) for item in present):
        unresolved.append("present_addresses")

    additional_ack=data.get("additional_acknowledgments")
    if additional_ack is not None and not isinstance(additional_ack,str):
        unresolved.append("additional_acknowledgments")

    # A permanent archive DOI is deliberately not required for initial
    # ScholarOne submission. It becomes mandatory only if the paper is accepted.
    permanent=_text(data.get("permanent_archive_doi"))

    return {
        "schema_version":1,
        "ready_for_initial_submission_metadata":len(unresolved)==0,
        "unresolved_fields":sorted(set(unresolved)),
        "author_count":len(authors),
        "corresponding_author_count":len(corresponding),
        "review_code_url":review_url or None,
        "permanent_archive_doi":permanent or None,
        "post_acceptance_archive_pending":not bool(permanent),
    }


def require_complete_metadata(data: dict[str,Any]) -> None:
    result=validate_metadata(data)
    if not result["ready_for_initial_submission_metadata"]:
        raise ValueError(
            "submission metadata incomplete: "
            + ", ".join(result["unresolved_fields"])
        )


def author_line(data: dict[str,Any]) -> str:
    parts=[]
    for author in _authors(data):
        ids=[str(value) for value in author.get("affiliation_ids",[])]
        marker=",".join(ids)
        rendered=_text(author.get("name"))
        if marker:
            rendered+=f"^{marker}^"
        if bool(author.get("corresponding")):
            rendered+="*"
        parts.append(rendered)
    return "; ".join(parts)


def affiliation_lines(data: dict[str,Any]) -> str:
    affiliations=data.get("affiliations") or {}
    return "\n".join(
        f"^{key}^ {value}"
        for key,value in affiliations.items()
        if _text(value)
    )


def present_address_text(data: dict[str,Any]) -> str:
    values=data.get("present_addresses")
    if not isinstance(values,list) or not values:
        return "None."
    return "; ".join(_text(value) for value in values)


def corresponding_text(data: dict[str,Any]) -> str:
    for author in _authors(data):
        if bool(author.get("corresponding")):
            return f"{_text(author.get('name'))}, {_text(author.get('email'))}"
    return ""


def ai_disclosure_suffix(data: dict[str,Any]) -> str:
    tools=data.get("additional_ai_tools")
    if not isinstance(tools,list) or not tools:
        return ""
    joined="; ".join(_text(item) for item in tools if _text(item))
    return (
        " Additional AI tools disclosed by the authors were: "
        + joined
        + "."
    )


def main() -> int:
    import argparse

    parser=argparse.ArgumentParser()
    parser.add_argument("--metadata",required=True,type=Path)
    parser.add_argument("--out",type=Path)
    parser.add_argument("--require-complete",action="store_true")
    args=parser.parse_args()
    data=load_metadata(args.metadata)
    result=validate_metadata(data)
    if args.require_complete:
        require_complete_metadata(data)
    payload=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload,encoding="utf-8")
    print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
