"""Original-source comparability of species within frozen MAPPPD5 381 pairs.

Checks shared original site/year, publisher citation, vantage and ERA5 grid.
Records observational growth contrasts only; no causal species climate effects.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from itertools import combinations
from collections import defaultdict,Counter
from pathlib import Path

COHORT_SHA="cb3a337811431169f687c0d4ffc4ee159d0d0f35e3fac60b9282563d514fa87f"
ERA5_SHA="f2bad55bc9b714351b8bc30031b1518eece43138f77d4047657a3e145911e9a6"

def read(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def analyze(rows):
    groups=defaultdict(list)
    for row in rows:
        if row["month_census_verified"]!="False" or row["physical_island_polygon_verified"]!="False":
            raise ValueError("SOURCE_STOP field census chronology or land status changed")
        start,end=int(row["start_year"]),int(row["end_year"])
        if end!=start+1:raise ValueError("SOURCE_STOP interval is not adjacent")
        groups[row["site_id"],start,end].append(row)
    output=[]
    for (site,start,end),raw in sorted(groups.items()):
        if len(set(z["species_id"] for z in raw))!=len(raw):
            raise ValueError("SOURCE_STOP duplicate species within original site-year")
        for a,b in combinations(sorted(raw,key=lambda z:z["species_id"]),2):
            same_climate=(a["era5_grid_id"]==b["era5_grid_id"] and
                math.isclose(float(a["delta_September_ERA5_C"]),
                             float(b["delta_September_ERA5_C"]),abs_tol=1e-10) and
                math.isclose(float(a["delta_AugNov_ERA5_C"]),
                             float(b["delta_AugNov_ERA5_C"]),abs_tol=1e-10))
            if not same_climate:raise ValueError("SOURCE_STOP same site year not identical ERA5")
            same_citation=bool(a["publisher_citekey"].strip()) and a["publisher_citekey"]==b["publisher_citekey"]
            same_vantage=bool(a["publisher_vantage"].strip()) and a["publisher_vantage"]==b["publisher_vantage"]
            strict=bool(same_citation and same_vantage)
            ga,gb=float(a["delta_log1p_nests"]),float(b["delta_log1p_nests"])
            output.append({
              "site_id":site,"start_year":start,"end_year":end,
              "source_region":a["source_region"],"species_a":a["species_id"],"species_b":b["species_id"],
              "same_original_source_citation":same_citation,
              "same_original_vantage":same_vantage,
              "eligible_same_source_and_vantage":strict,
              "same_original_ERA5_grid":same_climate,
              "growth_a_minus_growth_b":ga-gb,
              "growth_sign_agreement":(ga*gb>0) if ga!=0 and gb!=0 else None,
              "same_field_census_day_verified":False,
              "nest_polygons_both_verified":False
            })
    strict=[x for x in output if x["eligible_same_source_and_vantage"]]
    nkeys=len({(z["site_id"],z["start_year"]) for z in strict})
    sites={z["site_id"] for z in strict}
    regions={z["source_region"] for z in strict}
    return output,{
      "schema":1,"status":"ORIGINAL_MULTISPECIES_SHARED_SITE_YEAR_SOURCE_SUPPORT",
      "original_source_pair_rows":len(rows),
      "all_cross_species_same_site_year_pair_rows":len(output),
      "strict_same_citation_and_vantage_pair_rows":len(strict),
      "strict_unique_site_year_groups":nkeys,
      "strict_unique_original_site_IDs":len(sites),
      "strict_original_regions":sorted(regions),
      "strict_original_species_pair_counts":dict(sorted(Counter(
        x["species_a"]+"|"+x["species_b"] for x in strict).items())),
      "fixed_min_same_source_site_years":10,
      "fixed_min_distinct_source_site_IDs":3,
      "fixed_min_regions":2,
      "direct_species_comparison_source_gate":nkeys>=10 and len(sites)>=3 and len(regions)>=2,
      "recorded_count_change_comparisons_are_exploratory_only":True,
      "field_census_dates_verified_simultaneous":False,
      "physical_island_breeding_area_measured":False,
      "climate_species_interaction_fitted":False,"p_values":None
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-381-dir",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    root=args.original_381_dir
    original_json=json.loads((root/"macro_three_species_count_climate_exploratory_v1.json").read_text())
    if original_json["status"]!="POST_EXPLORATION_CLIMATE_COUNTS_ASSOCIATION_NO_CAUSAL_ATTRIBUTION":
        raise ValueError("SOURCE_STOP unverified original source result")
    if original_json["original_381_cohort_source_sha256"]!=COHORT_SHA or original_json["source_original_ERA5_sha256"]!=ERA5_SHA:
        raise ValueError("SOURCE_STOP original source SHA changed")
    src=root/"original_MAPPPD5_381_pairs_count_ERA5_join.csv"
    rows=read(src)
    if len(rows)!=381 or dict(Counter(z["species_id"] for z in rows))!={
        "ADPE":294,"CHPE":29,"GEPE":58}:
        raise ValueError("SOURCE_STOP original 381 pairs changed")
    comparisons,receipt=analyze(rows)
    receipt["input_original_count_join_sha256"]=sha(src)
    with (args.out/"same_source_site_year_species_pairs.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["site_id","start_year","end_year","source_region","species_a","species_b",
             "same_original_source_citation","same_original_vantage",
             "eligible_same_source_and_vantage","same_original_ERA5_grid",
             "growth_a_minus_growth_b","growth_sign_agreement",
             "same_field_census_day_verified","nest_polygons_both_verified"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(comparisons)
    (args.out/"same_source_site_year_species_source_result.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("PENGUIN_SPECIES_SOURCE_CROSSWALK_GATE="+json.dumps(receipt,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
