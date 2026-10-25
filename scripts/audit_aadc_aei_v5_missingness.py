#!/usr/bin/env python3
"""V5 AADC AEI label-dependent missingness diagnosis, no ecological model fit.

Explicit original P/A states are used ONLY to audit V4 cohort selection.
Both the V4 positive/negative outcomes and V1/V2 associations are immutable.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
import requests

from audit_aadc_original_workbook_headers_v11 import public_dataset_manifests
from audit_aadc_geography_editions_v1 import parse_geo
from build_aadc_potential_site_network_v1 import site_point_network
from join_aadc_original_site_occupancy_v13 import fetch_original_sources, rows_linked
from evaluate_aadc_site_option_network_p_a_v1 import original_sample

CASES=(
    "INDEPENDENT_NONANIMAL_HABITAT",
    "ONLY_ANIMAL_DERIVED_CLASSIFIED_AEI_CELLS",
    "NO_AEI_MAPPED_CELLS"
)


def classify_source_atlas(summarypath:Path,featurespath:Path):
    result=json.loads(summarypath.read_text(encoding="utf-8"))
    if result.get("status")!="AADC_7785_INDEPENDENT_AEI_HABITAT_ATLAS_V3":
        raise ValueError("SOURCE_STOP original AEI atlas identity changed")
    if hashlib.sha256(featurespath.read_bytes()).hexdigest()!=result["derived_7785_site_habitat_feature_CSV_SHA256"]:
        raise ValueError("SOURCE_STOP frozen original AEI features SHA mismatch")
    site_status={}
    with featurespath.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sid=r["original_geographic_site_id"]
            if sid in site_status:
                raise ValueError("SOURCE_STOP original AADC source geographic site duplicated")
            all_n=int(r["all_classified_icefree_pixel_count"])
            nonanimal=int(r["independent_nonanimal_mapped_pixel_count"])
            animal=int(r["outcome_label_linked_pixels_excluded"])
            if all_n!=nonanimal+animal:
                raise ValueError("SOURCE_STOP original AEI cell classes do not partition")
            if nonanimal>0:
                status=CASES[0]
            elif all_n>0:
                status=CASES[1]
            else:
                status=CASES[2]
            if (r["independently_mapped_habitat_coverage"]=="True")!=(status==CASES[0]):
                raise ValueError("SOURCE_STOP source mapped AEI coverage flag inconsistent")
            site_status[sid]=status
    if len(site_status)!=7785:
        raise ValueError("SOURCE_STOP full original 2025 geographical source frame missing")
    original_counts=Counter(site_status.values())
    expected=result["independent_breeding_habitat_summary"]["all_2025"]["sites_with_nonanimal_mapped_habitat_pixels"]
    if original_counts[CASES[0]]!=expected:
        raise ValueError("SOURCE_STOP original V3 mapped independent coverage summary drift")
    return site_status,{
        "all_original_geographic_sites":len(site_status),
        "original_geography_only_source_class_case_counts":dict(original_counts),
        "original_raster_SHA256_record":result["derived_7785_site_habitat_feature_CSV_SHA256"],
    }


def audit_missingness(source:pd.DataFrame,site_case:dict):
    frame=source.copy()
    frame["aei_case"]=frame.site_id.map(site_case)
    if frame.aei_case.isna().any():
        raise ValueError("SOURCE_STOP original survey site absent from full 2025 AEI atlas")
    responses={}
    for programme in ("ADELIE","FLYING"):
        d=frame.loc[frame.source_programme.eq(programme)]
        grouped={}
        for outcome in (0,1):
            part=d.loc[d.outcome.eq(outcome)]
            counts=Counter(part.aei_case)
            n=len(part)
            grouped["P" if outcome else "A"]={
                "source_P_A_rows":n,
                "distinct_original_geographic_site_IDs":int(part.site_id.nunique()),
                "AEI_coverage_class_row_counts":{z:counts[z] for z in CASES},
                "fraction_rows_with_independent_AEI_habitat":
                    counts[CASES[0]]/n if n else None,
                "distinct_original_sites_with_independent_AEI_habitat":
                    int(part.loc[part.aei_case.eq(CASES[0])].site_id.nunique()),
            }
        p=grouped["P"]["fraction_rows_with_independent_AEI_habitat"]
        absent=grouped["A"]["fraction_rows_with_independent_AEI_habitat"]
        grouped["P_minus_A_row_coverage_percentage_points"]=(
            (p-absent)*100 if p is not None and absent is not None else None)
        grouped["original_total_site_IDs"]=int(d.site_id.nunique())
        grouped["source_AEI_coverage_by_author_site_class"]={}
        for land_label,value in (("island",1.),("continent",0.)):
            layer=d.loc[d.island.eq(value)]
            cnt=Counter(layer.aei_case)
            grouped["source_AEI_coverage_by_author_site_class"][land_label]={
                "observation_rows":len(layer),
                "distinct_original_sites":int(layer.site_id.nunique()),
                "independent_habitat_coverage_fraction_of_rows":
                    cnt[CASES[0]]/len(layer) if len(layer) else None,
                "observation_rows_per_map_source_category":dict(cnt),
            }
        grouped["source_AEI_coverage_by_2021_historical_site_inclusion"]={}
        for k,flag in (("2021_shared",1.),("2025_only",0.)):
            layer=d.loc[d.original_site_id_in_2021.eq(flag)]
            cnt=Counter(layer.aei_case)
            grouped["source_AEI_coverage_by_2021_historical_site_inclusion"][k]={
                "observation_rows":len(layer),
                "distinct_original_sites":int(layer.site_id.nunique()),
                "independent_habitat_coverage_fraction_of_rows":
                    cnt[CASES[0]]/len(layer) if len(layer) else None,
            }

        site_ever_P=d.groupby("site_id").outcome.max()
        site_case_df=pd.DataFrame({
            "ever_explicit_P":site_ever_P,
            "AEI_case":[site_case[s] for s in site_ever_P.index],
        })
        by_site={}
        for ever in (0,1):
            z=site_case_df.loc[site_case_df.ever_explicit_P.eq(ever)]
            cc=Counter(z.AEI_case)
            by_site["ever_P_observed" if ever else "only_A_observed"]={
                "distinct_original_site_IDs":len(z),
                "mapped_independent_habitat_site_fraction":
                    cc[CASES[0]]/len(z) if len(z) else None,
                "site_category_counts":{k:cc[k] for k in CASES},
            }
        grouped["distinct_site_history_rather_than_repeated_rows"]=by_site
        responses[programme]=grouped

    return {
        "status":"AADC_AEI_V5_AFTER_ECOLOGY_SOURCE_MISSINGNESS",
        "source_original_explicit_P_A_rows_in_diagnostic":len(frame),
        "source_original_distinct_geographic_sites_in_diagnostic":int(frame.site_id.nunique()),
        "source_programme_outcome_and_mapping_missingness":responses,
        "V4_original_AEI_habitat_predictor_eligibility_criterion_unchanged":True,
        "reporting_only_no_new_ecological_model_fitted":True,
        "nonreporting_NR_recoded_as_absence":False,
        "source_classified_penguin_pixels_not_independent_habitat_predictor":True,
        "P_A_coverage_difference_demonstrates_causal_biotic_island_effect":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--atlas-summary",type=Path,required=True)
    p.add_argument("--atlas-features",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    site_case,receipt=classify_source_atlas(a.atlas_summary,a.atlas_features)
    with requests.Session() as session:
        manifests,mreceipt=public_dataset_manifests(session)
        originals,source_receipts=fetch_original_sources(session,manifests)
    _qa,original_surveys,geog=rows_linked(originals)
    old,_=parse_geo(originals["potential_geography_2021"],old=True)
    new,_=parse_geo(originals["potential_geography_2025"],old=False)
    conv=Transformer.from_crs(4326,3031,always_xy=True)
    data=[]
    for site,g in new.items():
        x,y=conv.transform(g["lon"],g["lat"])
        data.append({"site_id":site,"source_class":g["feature"],"x":x,"y":y})
    network,_=site_point_network(data,set(old))
    sample,sourceqa=original_sample(original_surveys,geog,network)
    result=audit_missingness(sample,site_case)
    result["original_AEI_source_only_coverage_receipt"]=receipt
    result["original_AADC_source_workbook_SHA256"]={
        k:v["original_SHA256"] for k,v in source_receipts.items()}
    result["original_source_P_A_sample_report"]=sourceqa
    result["original_AADC_public_manifest_sha256"]=mreceipt["source_sha256"]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
