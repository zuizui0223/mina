"""Original 771 strict MAPPPD× already acquired 40-site ERA5 support bridge.

This is a source-availability diagnostic with NO breeding count effects or
p-values, and no survey-month imputation. Uses published original source only.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SITES=ROOT/"outputs/climate_penguin/daily_ice_locations.csv"
REQUIRED_PAIR_SHA="dfb72e533ab1e14846cb6551f0e2a6aa90f007c955f0b19f9c90fca03aca6d14"
REQUIRED_ERA5_SHA="f2bad55bc9b714351b8bc30031b1518eece43138f77d4047657a3e145911e9a6"

def read(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_support(pair,climate,roster):
    assert len(pair)==771 and len(climate)==40*30*12
    assert len(roster)==40 and len({r["site_id"] for r in roster})==40
    frozen={r["site_id"]:r for r in roster}
    available={}
    for r in climate:
        site=r["site_id"]
        if site not in frozen:raise ValueError("SOURCE_STOP unlisted climatological site")
        key=(site,int(r["year"]),int(r["month"]))
        if key in available:raise ValueError("SOURCE_STOP duplicate original ERA5 source month")
        grid=(round(float(r["returned_grid_latitude"]),6),
              round(float(r["returned_grid_longitude"]),6))
        val=r["complete_month"]=="True" and r["air2m_mean_c"]!=""
        if val and not math.isfinite(float(r["air2m_mean_c"])):
            raise ValueError("SOURCE_STOP invalid climate value")
        available[key]={"valid":val,"grid_id":f"{grid[0]}|{grid[1]}"}
    assert len(available)==40*30*12
    candidate=[]
    for r in pair:
        site=r["site_id"]
        first,last=int(r["start"]),int(r["end"])
        if last!=first+1 or r["same_source_and_vantage"]!="True":
            raise ValueError("SOURCE_STOP original paired-year ancestry invariant broken")
        physical=site in frozen
        coords_ok=False
        if physical:
            d=frozen[site]
            coords_ok=(abs(float(r["source_point_latitude"])-float(d["latitude"]))<=0.001 and
                abs(float(r["source_point_longitude"])-float(d["longitude"]))<=0.001)
        within_years=1991<=first and last<=2020
        monthly={}
        grids=set()
        if physical and coords_ok and within_years:
            for label,months in (("september",[9]),("aug_nov",[8,9,10,11])):
                vals=[available[(site,y,m)] for y in (first,last) for m in months]
                monthly[label]=all(x["valid"] for x in vals)
                grids.update(x["grid_id"] for x in vals)
        if len(grids)>1:raise ValueError("SOURCE_STOP same site changes actual reanalysis grid")
        candidate.append({
            "site_id":site,"species_id":r["species_id"],"source_region":r["source_region"],
            "start":first,"end":last,
            "in_fixed_original_40_sites":physical,
            "source_coordinate_matches_fixed_site":coords_ok if physical else None,
            "original_ERA5_1991_2020_year_overlap":within_years,
            "paired_september_ERA5_complete":monthly.get("september",False),
            "paired_aug_nov_ERA5_complete":monthly.get("aug_nov",False),
            "actual_ERA5_grid_id":next(iter(grids)) if grids else None,
            "survey_month_verified":False,
            "original_count_magnitudes_reestimated":False,
            "source_site_island_identity_verified":False
        })
    elig=[r for r in candidate if r["paired_september_ERA5_complete"]]
    n_bysp=Counter(x["species_id"] for x in elig)
    regions=Counter(x["source_region"] for x in elig)
    siteids={x["site_id"] for x in elig}
    climatology_grids={x["actual_ERA5_grid_id"] for x in elig}
    no_climate=sum(r["in_fixed_original_40_sites"] and
                  r["original_ERA5_1991_2020_year_overlap"] and
                  not r["paired_september_ERA5_complete"] for r in candidate)
    out={
        "schema":1,"status":"ORIGINAL_ANNUAL_CLIMATE_OVERLAP_SUPPORT_ONLY",
        "original_MAPPPD_v5_strict_paired_rows":len(pair),
        "already_frozen_40_sites":len(frozen),
        "n_source_candidate_pairs_fitting_original_40_site_and_climate_window":len(elig),
        "by_species":dict(sorted(n_bysp.items())),
        "by_publisher_region":dict(sorted(regions.items())),
        "eligible_original_site_ids":len(siteids),
        "actual_ERA5_grids_with_eligible_original_site_ids":len(climatology_grids),
        "eligible_annual_pairs_without_full_8_11_climate":sum(
            x["paired_september_ERA5_complete"] and not x["paired_aug_nov_ERA5_complete"] for x in candidate),
        "unmatched_fixed_coordinate_pairs":sum(x["in_fixed_original_40_sites"] and
              not x["source_coordinate_matches_fixed_site"] for x in candidate),
        "year_eligible_with_missing_ERA5":no_climate,
        "year_outside_frozen_ERA5":sum(not x["original_ERA5_1991_2020_year_overlap"] for x in candidate),
        "macro_source_overlap_gate":{
            "min_three_species":3,"min_sites":20,"min_regions":4,
            "pass":len(n_bysp)==3 and len(siteids)>=20 and len(regions)>=4
        },
        "chronological_pre_count_exposure_identifiable":False,
        "physical_island_effect_identifiable":False,
        "no_species_response_or_climate_effect_fitted":True,
        "no_actual_survey_month_from_source":True,
        "note":"40-site roster originated from Adélie candidates and does not represent unbiased 95-site or Antarctic macro coverage. Do not promote to population or temperature effect."
    }
    return candidate,out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--macro-source-dir",required=True,type=Path)
    p.add_argument("--era5-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    pairs=args.macro_source_dir/"original_MAPPPD5_strict_three_taxa_macro_pair_support.csv"
    era=args.era5_dir/"era5_monthly_1991_2020.csv"
    if sha(pairs)!=REQUIRED_PAIR_SHA or sha(era)!=REQUIRED_ERA5_SHA:
        raise ValueError("SOURCE_STOP source SHA differs from verified pinned artifacts")
    grid=read(SITES)
    roster=[x for x in grid if x["cohort"]=="macro_40"]
    rows,support=source_support(read(pairs),read(era),roster)
    support["source_SHA256"]={"original_771_pairs":sha(pairs),"original_ERA5_40_sites":sha(era),
                             "original_fixed_site_registry":sha(SITES)}
    with (args.out/"original_MAPPPD5_ERA5_40site_overlap_v1.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (args.out/"original_MAPPPD5_ERA5_40site_overlap_receipt_v1.json").write_text(
        json.dumps(support,indent=2,ensure_ascii=False)+"\n")
    print("MAPPPD5_ERA5_CLIMATE_OVERLAP_RECEIPT="+json.dumps(support,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
