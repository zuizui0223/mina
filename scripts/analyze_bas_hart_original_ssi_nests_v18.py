#!/usr/bin/env python3
"""BAS Hart original South Sandwich 2019-20 UAV nest count ledger V18.

First-party small CSV site × count-category, with direct species-labelled
versus unknown/mixed and extrapolated nests explicitly separated. No causal
island/spatial effects. 2022 ZAVO chinstrap source ambiguity cannot be ignored.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path

from audit_bas_hart_ssi_count_source_v17 import (
    choose_source,obtain_source_count_bytes,parse_original_counts
)

SOURCE_SHA="3206e74af11b3424bc59cb1c451f1eaeb490de6677d0b7b91b85e3a9fa68cede"
ROW_CLASSES=(
 "Chinstrap","Chinstrap_estimate","Mixed","Mixed_estimate","Adelie",
 "Gentoo","Macaroni","Unknown","Unknown_estimate","Total"
)
SITE_IDS=(
 "Zavodovski","Candlemas","Ashen_Hills","Bellingshausen_Island",
 "Beach_Point","Hewison_Point","Herd_Point"
)
SOURCE_SPECIES=("Adelie","Chinstrap","Gentoo","Macaroni")
UNASSIGNED=("Mixed","Unknown")
EXTRAPOLATED=("Chinstrap_estimate","Mixed_estimate","Unknown_estimate")
PHYSICAL_ISLAND_GROUP={
 "Zavodovski":"Zavodovski_Island",
 "Candlemas":"Candlemas_Island",
 "Ashen_Hills":"Saunders_Island",
 "Bellingshausen_Island":"Bellingshausen_Island",
 "Beach_Point":"Thule_Island",
 "Hewison_Point":"Thule_Island",
 "Herd_Point":"Thule_Island",
}


def source_matrix_counts(rows,source_schema):
    if not source_schema["original_wide_site_by_count_category_matrix"]:
        raise ValueError("SCHEMA_STOP original publisher is not the authenticated SSI wide tally")
    if tuple(source_schema["source_column_names"])!=("",*SITE_IDS):
        raise ValueError("SOURCE_STOP original count CSV order or locality identity drift")
    if tuple(row[""] for row in rows)!=ROW_CLASSES:
        raise ValueError("SOURCE_STOP original 10 category labels or row order changed")
    data={}
    for row in rows:
        label=row[""]
        for site in SITE_IDS:
            value=str(row.get(site,"") or "").strip()
            if value=="":
                parsed=None
            else:
                try:
                    parsed=float(value)
                except ValueError as e:
                    raise ValueError("SOURCE_STOP nonnumeric first-party reported count") from e
                if not math.isfinite(parsed) or parsed<0:
                    raise ValueError("SOURCE_STOP original reported nest count nonfinite/negative")
                if label not in EXTRAPOLATED+("Total",) and abs(parsed-round(parsed))>1e-8:
                    raise ValueError("SOURCE_STOP original directly reported nest count non-integer")
            data[label,site]=parsed
    return data


def ledger(data):
    locality=[]
    for site in SITE_IDS:
        observations={k:data[k,site] for k in ROW_CLASSES}
        identity={k:observations[k] for k in SOURCE_SPECIES}
        direct_species=sum(v for v in identity.values() if v is not None)
        direct_unknown=sum(observations[k] for k in UNASSIGNED if observations[k] is not None)
        estimated=sum(observations[k] for k in EXTRAPOLATED if observations[k] is not None)
        total=observations["Total"]
        rawsum=direct_species+direct_unknown+estimated
        additive=bool(total is not None and abs(total-rawsum)<=max(1.,abs(total)*1e-6))
        percent=direct_species/total if additive and total>0 else None
        source_taxa=[k for k,v in identity.items() if v is not None and v>0]
        locality.append({
            "original_survey_locality":site,
            "gazetteer_parent_physical_island_name":PHYSICAL_ISLAND_GROUP[site],
            "original_source_penguin_taxa_positive_and_labelled":source_taxa,
            "original_reported_species_labelled_nest_cells":identity,
            "original_source_four_species_labelled_sum":int(direct_species),
            "original_source_counted_mixed_or_unknown_species_nests":int(direct_unknown),
            "original_source_spatially_extrapolated_nests":estimated,
            "publisher_source_locality_reported_total":total,
            "source_sum_of_all_separately_listed_nonmissing_category_cells":rawsum,
            "publisher_reported_total_equals_source_cell_arithmetic":additive,
            "source_total_minus_visible_component_sum":(total-rawsum if total is not None else None),
            "fraction_species_identified_source_labeled_nests_of_total_if_reconciled":percent,
            "source_original_nonreported_species_taxon_are_true_absence":False,
            "source_complete_island_population_survey_verified":False,
            "original_zavo_chinstrap_2022_supplement_may_create_mixed_year_label":site=="Zavodovski",
            "source_raster_imagery_distortion_reconstruction_applies":site=="Zavodovski",
            "original_Candlemas_only_Adelie_countable_due_image_resolution":site=="Candlemas",
        })
    if len(locality)!=7:
        raise ValueError("SOURCE_STOP original seven survey sites changed")
    groups=defaultdict(list)
    for row in locality:
        groups[row["gazetteer_parent_physical_island_name"]].append(row)
    result={
       "status":"BAS_SOUTH_SANDWICH_ORIGINAL_SOURCE_2019_2020_NEST_LEDGER_V18",
       "original_survey_locality_n":len(locality),
       "locality_to_physical_island_grouping_from_gazetteer_not_GIS_verified":PHYSICAL_ISLAND_GROUP,
       "original_named_physical_island_group_n":len(groups),
       "original_taxonomically_resolved_species_count_rows":list(SOURCE_SPECIES),
       "mixed_and_unknown_original_count_categories":list(UNASSIGNED),
       "source_non_field_count_extrapolation_categories":list(EXTRAPOLATED),
       "reported_source_count_data_by_original_survey_locality":locality,
       "source_locality_counts_with_selfconsistent_total":sum(
           r["publisher_reported_total_equals_source_cell_arithmetic"] for r in locality),
       "source_localities_with_total_nonadditivity":[
           {"locality":r["original_survey_locality"],
            "source_total_minus_sum":r["source_total_minus_visible_component_sum"]}
           for r in locality if not r["publisher_reported_total_equals_source_cell_arithmetic"]],
       "sensitivity_additive_total_identifiability_fraction_by_locality":{
           r["original_survey_locality"]:r["fraction_species_identified_source_labeled_nests_of_total_if_reconciled"]
           for r in locality},
       "aggregated_physical_island_group_site_counts_only":{
            k:len(v) for k,v in sorted(groups.items())
       },
       "animal_nests_observed_at_all_original_nonreported_taxa":False,
       "publisher_2022_Zavodovski_chinstrap_revisit_as_independent_2020":False,
       "data_site_nests_are_islandwide_complete_breeding_abundances":False,
       "source_species_nest_temporal_replicates_n":0,
       "ecological_island_effect_model_fitted":False,
       "direct_observed_colony_interaction_or_competition_proven":False,
    }
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-manifest",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    result={"status":"HOLD_BAS_ORIGINAL_NEST_LEDGER_V18","ecological_island_effect_model_fitted":False}
    try:
        manifest=json.loads(args.source_manifest.read_text(encoding="utf-8"))
        target=choose_source(manifest)
        raw=obtain_source_count_bytes(target["source_file_url_https"])
        if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
            raise ValueError("SOURCE_STOP original Hart small census CSV SHA drift")
        rows,schema=parse_original_counts(raw)
        data=source_matrix_counts(rows,schema)
        result=ledger(data)
        result["source_original_publisher_csv_sha256"]=SOURCE_SHA
        result["source_original_publisher_csv_bytes"]=len(raw)
        result["original_source_dataset_doi"]="10.5285/28222725-c53d-40f4-9350-49c368899f0b"
        result["source_physical_island_geography_references"]=[
           "Hewison, Herd, Beach Point: Thule Island; SGSSI gazetteer and original 2019–2020 UAV survey methods",
           "Ashen Hills: Saunders Island; SGSSI gazetteer and BAS Saunders geology",
           "Candlemas, Bellingshausen, Zavodovski: named publisher locations"
        ]
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:900]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
