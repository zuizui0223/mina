#!/usr/bin/env python3
"""Verify a novel independent Adélie feather bulk+AA isotope dataset (USAP 602094).

Only source metadata, sample/time/site/feather synthesis provenance. Explicitly
DO NOT inspect or aggregate trophic-position or any isotope response values.
Freeze: FROZEN_USAP602094_ADELIE_AA_BASELINE_VS_TP_SOURCE_GATE.md.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re
from collections import Counter
from pathlib import Path
from urllib.parse import quote
import requests

DATASET=602094
ORIGINAL_NAME="Michelson_2026_Adelie_Feathers_SIA_CSIA_Data.csv"
PUBLISHER_MD5="f9a91c9d9bf3dba9607bf0767df8c206"
URL="https://www.usap-dc.org/api/v2.0/datafiles/"+str(DATASET)+"/"+quote(ORIGINAL_NAME)
METADATA_URL="https://www.usap-dc.org/api/v2.0/datasets/"+str(DATASET)
SOURCE="https://www.usap-dc.org/view/dataset/"+str(DATASET)
HEAD={"User-Agent":"mina-Antarctic-independent-penguin-amino-acid-source-metadata/1.0",
      "Accept":"text/csv,application/octet-stream;q=0.9,*/*;q=0.1"}

def get(url):
    try:
        r=requests.get(url,headers=HEAD,timeout=55,allow_redirects=True)
        return r
    except Exception as e:return {"error":f"{type(e).__name__}: {str(e)[:360]}"}
def signal(value):
    return str(value or "").strip()
def category(k):
    k=k.casefold().strip()
    if any(v in k for v in ("trophic","phenylalanine","glutamic","delta","d15","d13","isotope","bulk","_tp","tp_")):
        return "OUTCOME_OR_DERIVED_ISOTOPE_NO_READ"
    if any(v in k for v in ("moult","molt","synthes","formation","formed","growth_period","wintering")):
        return "FEATHER_FORMATION_OR_TIMING_METADATA"
    if any(v in k for v in ("collect","sample_year","sample date","sample_date","date","year","age","period","historic","modern","decade")):
        return "SAMPLE_TIMING_METADATA_NOT_AUTOMATIC_FORMATION"
    if any(v in k for v in ("location","colony","site","region","latitude","longitude","lat_","lon_","lat","lon","island","coords")):
        return "SPATIAL_METADATA"
    if any(v in k for v in ("specimen","bird","tissue","feather","sex","sample","individual","museum","source","institution","id")):
        return "SAMPLE_IDENTITY_METADATA"
    return "UNKNOWN_NEVER_AUTO_USE_AS_Y_OR_COVARIATE"

def main(a):
    a.out.mkdir(parents=True,exist_ok=True)
    initial={
       "source_dataset":DATASET,"official_site":SOURCE,"dataset_DOI":"10.15784/602094",
       "published_original_filename":ORIGINAL_NAME,"expected_publisher_MD5":PUBLISHER_MD5,
       "frozen_contract":"FROZEN_USAP602094_ADELIE_AA_BASELINE_VS_TP_SOURCE_GATE.md",
       "source_is_independent_of_Youngflesh_optical_isotope_paper":True,
       "guano_summer_vs_feather_molt_season_not_equated":True,
       "no_trophic_position_or_phenylalanine_isotope_values_read":True,
       "no_isotope_regression_or_polynya_alignment_attempted":True
    }
    meta=get(METADATA_URL)
    initial["official_API_metadata_status"]=(
      {"http_status":meta.status_code,"content_type":meta.headers.get("content-type"),
       "final_domain":requests.utils.urlparse(meta.url).hostname}
        if not isinstance(meta,dict) else meta)
    response=get(URL)
    if isinstance(response,dict):
        initial.update({"status":"NO_GO_USAP_SOURCE_DOWNLOAD_UNVERIFIED","source_error":response})
    else:
        initial["source_download_http_status"]=response.status_code
        initial["source_download_content_type"]=response.headers.get("content-type")
        initial["source_download_size_bytes"]=len(response.content)
        initial["source_download_final_domain"]=requests.utils.urlparse(response.url).hostname
        initial["actual_original_content_md5"]=hashlib.md5(response.content).hexdigest()
        initial["actual_original_content_sha256"]=hashlib.sha256(response.content).hexdigest()
        if response.status_code!=200 or initial["actual_original_content_md5"]!=PUBLISHER_MD5:
            initial["status"]="NO_GO_USAP_SOURCE_DOWNLOAD_UNVERIFIED"
            initial["source_error"]="Official API content unavailable or different from published MD5; do NOT use mislabeled HTML/error as isotope dataset"
            initial["source_response_prefix_first_60_bytes"]=response.content[:60].decode("utf8","replace")
        else:
            raw=response.content.decode("utf-8-sig")
            reader=csv.DictReader(io.StringIO(raw))
            if reader.fieldnames is None:raise ValueError("Original 2026 AA isotope CSV lacks headers")
            columns=list(reader.fieldnames)
            if len(columns)!=len(set(columns)):raise ValueError("Published AA CSV has repeated column name")
            rows=list(reader)
            if not rows:raise ValueError("Original AA published isotope CSV empty")
            for r in rows:
                if set(r)!=set(columns):raise ValueError("Damaged actual row schema in source CSV")
            classified={c:category(c) for c in columns}
            # Only read values of columns confidently recognized as metadata;
            # unknown and all isotope/TP-related fields remain unopened in the audit.
            summaries=[]
            for c,cls in classified.items():
                info={"field":c,"classification":cls}
                if cls in {"SPATIAL_METADATA","FEATHER_FORMATION_OR_TIMING_METADATA",
                           "SAMPLE_TIMING_METADATA_NOT_AUTOMATIC_FORMATION"}:
                    values=[signal(row[c]) for row in rows]
                    nonempty=[v for v in values if v]
                    info["n_nonempty"]=len(nonempty)
                    info["n_unique_nonempty"]=len(set(nonempty))
                    info["unique_values_if_35_or_fewer"]=sorted(set(nonempty))[:35] if len(set(nonempty))<=35 else None
                summaries.append(info)
            a.out.joinpath("OFFICIAL602094_SOURCE_COLUMN_CLASSIFICATION_NO_Y.json").write_text(
                json.dumps(summaries,indent=2,ensure_ascii=False)+"\n")
            actual_year_columns=[c for c in columns if re.search(r"(moult|molt|synthesis|formation|feather.?grow)",c,re.I)]
            initial.update({
              "status":"USAP602094_ORIGINAL_CSV_SOURCE_MD5_VALIDATED_METADATA_ONLY",
              "real_actual_original_rows":len(rows),"real_actual_original_columns":len(columns),
              "original_column_names":columns,
              "original_metadata_fields":summaries,
              "feather_formation_explicit_field_candidates":actual_year_columns,
              "original_has_explicit_moult_date_metadata":bool(actual_year_columns),
              "independent_CSI_AA_TP_Y_source_content_saved":False,
              "source_year_is_not_automatically_feather_growth_year":True,
              "pre_Y_scientific_support_gate":"PENDING_MANUAL_SAMPLE_TIME_SITE_INTERPRETATION",
              "no_independent_polynya_association_ever_computed_in_this_audit":True,
            })
    a.out.joinpath("USAP602094_PUBLISHED_AA_TP_SOURCE_METADATA_ONLY_VERDICT.json").write_text(
        json.dumps(initial,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":initial.get("status"),
      "source_http":initial.get("source_download_http_status"),
      "source_md5":initial.get("actual_original_content_md5"),
      "rows":initial.get("real_actual_original_rows"),
      "columns":initial.get("original_column_names"),
      "candidate_feather_formation_fields":initial.get("feather_formation_explicit_field_candidates"),
      "safe_metadata":initial.get("original_metadata_fields"),
      "source_error":initial.get("source_error"),
      "no_outcome_read_or_tested":True},indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
