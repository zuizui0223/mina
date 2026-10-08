"""Inspect ONLY row positions and Excel cell type metadata in verified workbooks.

No worksheet cell text, numeric values, shared-string dictionary or outcome
states are read. The 12-row structural envelope was frozen *after* a prior
strict row-1-only header run but before cell content beyond row 1 was opened.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from audit_emperor_public_archive_headers import (
    FILES, M, P, R, ROOT, RECORD, download_public,
    metadata_for_pinned_record, resolve_manifest_name,
)

MAX_XML_ROWS=12


def inspect_row_shapes(path: Path) -> dict:
    with ZipFile(path) as archive:
        members=set(archive.namelist())
        wb=ET.fromstring(archive.read("xl/workbook.xml"))
        sheets=wb.find(M+"sheets")
        links=ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relmap={r.get("Id"):r.get("Target") for r in links.findall(P+"Relationship")}
        out=[]
        for sh in sheets:
            title=sh.get("name")
            loc=relmap.get(sh.get(R+"id",""),"")
            if loc.startswith("/xl/"):
                member=loc.lstrip("/")
            elif loc.startswith("xl/"):
                member=loc
            else:
                member="xl/"+loc.lstrip("/")
            if member not in members:
                out.append({"sheet":title,"status":"UNRESOLVED_TARGET"})
                continue
            rows=[]
            with archive.open(member) as stream:
                for event,cellrow in ET.iterparse(stream,events=("end",)):
                    if cellrow.tag!=M+"row":
                        continue
                    number=int(cellrow.get("r","0"))
                    if number>MAX_XML_ROWS:
                        break
                    cells=cellrow.findall(M+"c")
                    shared=sum(c.get("t")=="s" for c in cells)
                    inline=sum(c.get("t")=="inlineStr" for c in cells)
                    texts=sum(c.get("t")=="str" for c in cells)
                    formula=sum(c.find(M+"f") is not None for c in cells)
                    numeric=sum(
                        c.get("t") not in ("s","inlineStr","str")
                        for c in cells
                    )
                    # We intentionally do not inspect .text, .get('v') or xl/sharedStrings.
                    rows.append({
                        "row":number,
                        "n_xml_cells":len(cells),
                        "n_shared_string_cells":shared,
                        "n_inline_string_cells":inline,
                        "n_other_string_cells":texts,
                        "n_numeric_or_generic_type_cells":numeric,
                        "n_formula_tags":formula
                    })
                    cellrow.clear()
            candidate=next(
                (x["row"] for x in rows
                 if (x["n_shared_string_cells"]
                    +x["n_inline_string_cells"]
                    +x["n_other_string_cells"])>=2),
                None
            )
            out.append({
                "sheet":title,
                "status":"STRUCTURAL_SKETCH_ONLY",
                "rows":rows,
                "first_multi_string_row_candidate_UNVERIFIED":candidate
            })
        return {
            "max_rows_per_sheet_examined":MAX_XML_ROWS,
            "sheets":out,
            "n_sheets":len(out),
            "decoded_row_values":0,
            "shared_strings_dictionary_read":False,
            "headers_from_row2_onward_verified":False,
        }


def run(folder: Path,*,no_network=False)->dict:
    folder.mkdir(parents=True,exist_ok=True)
    manifest={"status":"SKIPPED_NO_NETWORK"} if no_network else metadata_for_pinned_record()
    report={
        "source":f"{ROOT}/records/{RECORD}",
        "scope":"ROW_LAYOUT_TYPES_ONLY_NO_CELL_VALUES",
        "metadata_status":manifest.get("status"),
        "files":{},"decoded_cell_values":0,"decoded_outcome_rows":0
    }
    for logical in FILES:
        if manifest.get("status")!="MANIFEST_VERIFIED":
            report["files"][logical]={"status":"MANIFEST_UNAVAILABLE_NO_DOWNLOAD"}
            continue
        identity=resolve_manifest_name(logical,manifest)
        if identity.get("status")!="SOURCE_IDENTITY_VERIFIED":
            report["files"][logical]=identity
            continue
        dest=folder/identity["name"]
        try:
            receipt=download_public(identity["name"],dest,identity["md5"])
            if receipt["status"]=="VERIFIED":
                receipt.update(inspect_row_shapes(dest))
            report["files"][logical]=receipt
        finally:
            dest.unlink(missing_ok=True)
    report["all_three_downloads_verified"]=all(
        z.get("status")=="VERIFIED" for z in report["files"].values()
    )
    report["all_fifty_one_sheet_layouts_sketchable"]=(
        report["all_three_downloads_verified"]
        and sum(z.get("n_sheets",0) for z in report["files"].values())==51
        and all(
            y.get("status")=="STRUCTURAL_SKETCH_ONLY"
            for z in report["files"].values() for y in z.get("sheets",[])
        )
    )
    report["sheets_with_candidate_multi_string_row"]=sum(
        y.get("first_multi_string_row_candidate_UNVERIFIED") is not None
        for z in report["files"].values() for y in z.get("sheets",[])
    )
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--cache",default=Path("/tmp/emp_archive_row_layout_v3"),type=Path)
    p.add_argument("--no-network",action="store_true")
    a=p.parse_args()
    data=run(a.cache,no_network=a.no_network)
    a.out.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    # output only aggregate facts; full structural receipt stays a workflow artifact
    print(json.dumps({
        "scope":data["scope"],
        "metadata_status":data["metadata_status"],
        "all_three_downloads_verified":data["all_three_downloads_verified"],
        "all_fifty_one_sheet_layouts_sketchable":data["all_fifty_one_sheet_layouts_sketchable"],
        "sheets_with_candidate_multi_string_row":data["sheets_with_candidate_multi_string_row"],
        "decoded_cell_values":data["decoded_cell_values"],
        "decoded_outcome_rows":data["decoded_outcome_rows"],
        "each_workbook":[{
            "name":key,"status":value.get("status"),
            "sheet_count":value.get("n_sheets"),
            "candidate_rows":[{"sheet":s["sheet"],
                "candidate_UNVERIFIED":s.get("first_multi_string_row_candidate_UNVERIFIED")}
                for s in value.get("sheets",[])]
        } for key,value in data["files"].items()]
    },indent=2))


if __name__=="__main__":
    main()
