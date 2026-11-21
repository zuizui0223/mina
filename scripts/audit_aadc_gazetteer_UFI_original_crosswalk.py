#!/usr/bin/env python3
"""Read-only AADC author-defined indirect site ID -> original rock polygon UFI gate.

2016 potential-habitat original spreadsheet carries Geog_Site_ID and
SCAR_Gazeteer_Place_ID, while original polygon DBF has UFI/Subgroup. Test
EXACT equality of original author identifiers, never suffixes, nearest point,
or biology-informed matching. No actual nest footprint or land change claim.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import quote
import requests
import shapefile
import openpyxl

from scripts.audit_aadc_2025_seabird_riskset_original_schema import SETS,download_original
from scripts.audit_aadc_2025_eight_species_original_riskset import ORIGINAL_SHA256,txt

AADC_ORIGINAL_GEO_UUID="3F139A80-800D-46BD-A7C0-D29734DAE090"
GIS_DBF="Potential habitat/shapefile/islands_and_continental_rock_by_subgroup8.dbf"
OLD_SPREADSHEET_NAME=SETS["2016_icefree_site_atlas"]["name"]
EXPECTED_GEO_DBF_BYTES=356443

def original_event_roster(path):
    j=json.loads(path.read_text(encoding="utf-8"))
    if j.get("status")!="AADC_EIGHT_SPECIES_VERIFIED_DETECTION_QUALITY_SOURCE_GATE":
        raise ValueError("not original AADC expert-validated event receipt")
    events=j["strict_all_expert_Y_and_high_A_certainty_support"]["AP_event_source_rows"]
    site_ids=sorted({str(e["geog_site_id"]) for e in events})
    if len(events)!=16 or len(site_ids)!=14:
        raise ValueError("Original 16/14 AADC event scope drift")
    return site_ids

def old_spreadsheet(session):
    spec=SETS["2016_icefree_site_atlas"]
    raw,meta=download_original(session,spec)
    if meta["sha256"]!=ORIGINAL_SHA256["2016_icefree_site_atlas"]:
        raise ValueError("Original publisher 2016 workbook SHA mismatch")
    book=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    try:
        ws=book["2_Geographic sites"]
        it=ws.iter_rows(values_only=True)
        headers=[txt(v).strip().lower() for v in next(it)]
        if "geog_site_id" not in headers or "scar_gazeteer_place_id" not in headers:
            raise ValueError(f"Unrecognized original author crosswalk headers {headers}")
        rows=[dict(zip(headers,row)) for row in it]
    finally:book.close()
    if len(rows)!=4884:
        raise ValueError("Original 2016 geog-site workbook count changed")
    bycode=defaultdict(list)
    for r in rows:
        k=txt(r.get("geog_site_id"))
        if k:bycode[k].append(r)
    return bycode,{"sha256":meta["sha256"],"row_count":len(rows),"original_fields":headers}

def publisher_dbf(session):
    uuid=AADC_ORIGINAL_GEO_UUID
    url=(f"https://data.aad.gov.au/eds/api/dataset/{quote(uuid)}/object/download"
         f"?prefix={quote(GIS_DBF,safe='')}")
    with session.get(url,stream=True,timeout=(20,90)) as resp:
        resp.raise_for_status()
        data=resp.content
    if len(data)!=EXPECTED_GEO_DBF_BYTES:
        raise ValueError("Original AADC polygon DBF bytes changed")
    r=shapefile.Reader(dbf=io.BytesIO(data),encoding="latin1")
    try:
        fields=[x[0].lower() for x in r.fields[1:]]
        if not {"ufi","subgroup"}.issubset(fields):
            raise ValueError("Original UFI/Subgroup polygon DBF columns missing")
        idx=fields.index("ufi")
        subgroup=fields.index("subgroup")
        recs=[(txt(x[idx]),txt(x[subgroup])) for x in r.iterRecords()]
        n=r.numRecords
    finally:r.close()
    return recs,{"sha256":hashlib.sha256(data).hexdigest(),"rows":n,"source_fields":fields}

def run(source):
    ids=original_event_roster(source)
    with requests.Session() as session:
        bycode,wb=old_spreadsheet(session)
        polygon_rows,dbf=publisher_dbf(session)
    lookup=defaultdict(list)
    for ix,(ufi,sg) in enumerate(polygon_rows):
        if ufi:lookup[ufi].append({"original_polygon_row_index":ix,"original_subgroup":sg})
    matched=[]
    r_ambiguous=[]
    notin=[]
    missing_gaz=[]
    no_match=[]
    for code in ids:
        arr=bycode.get(code,[])
        if len(arr)!=1:
            notin.append({"site_id":code,"original_2016_geog_row_count":len(arr)})
            continue
        gaz=txt(arr[0].get("scar_gazeteer_place_id"))
        if not gaz:
            missing_gaz.append(code)
            continue
        polygons=lookup.get(gaz,[])
        if len(polygons)==1:
            matched.append({"site_id":code,"original_scar_place_id":gaz,
                            "original_polygon_row_index":polygons[0]["original_polygon_row_index"],
                            "source_subgroup":polygons[0]["original_subgroup"],
                            "source_is_verified_nest_patch":False})
        elif len(polygons)>1:
            r_ambiguous.append({"site_id":code,"source_place_id":gaz,
                                "polygon_rows":len(polygons)})
        else:
            no_match.append({"site_id":code,"source_gazetteer_id":gaz})
    return {
        "status":"AADC_2016_ORIGINAL_AUTHOR_IDENTIFIER_CROSSWALK_SOURCE_GATE",
        "source_event_geographic_site_ids":ids,
        "original_event_source_run":44530909415,
        "original_workbook":wb,
        "original_rock_polygon_dbf":dbf,
        "matched_by_exact_gazetteer_UFI":len(matched),
        "one_to_one_source_polygon_matches":matched,
        "geographic_site_not_unique_or_missing_2016":notin,
        "site_with_no_original_SCAR_place_id":missing_gaz,
        "SCAR_place_id_matching_more_than_one_polygon":r_ambiguous,
        "SCAR_place_id_not_found_in_original_UFI":no_match,
        "confirmed_physical_nest_patch_georeferencing":False,
        "confirmed_historical_ice_loss":False,
        "ecological_effect_fitted":False,
        "note":"Exact source-place ID equality is GIS identity QA only. A mapped place/rock polygon is not the actual occupied nesting patch or newly deglaciated rock."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-events",required=True,type=Path)
    ap.add_argument("--out-json",required=True,type=Path)
    a=ap.parse_args()
    try:out=run(a.source_events)
    except Exception as e:
        out={"status":"HOLD_2016_GAZETTEER_UFI_ORIGINAL_CROSSWALK",
             "reason":f"{type(e).__name__}: {str(e)}"[:260],
             "ecological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":out["status"],
                      "matched":out.get("matched_by_exact_gazetteer_UFI"),
                      "missing2016":len(out.get("geographic_site_not_unique_or_missing_2016",[])),
                      "unmatched_Gaz_UFI":len(out.get("SCAR_place_id_not_found_in_original_UFI",[]))},sort_keys=True))
if __name__=="__main__":main()
