#!/usr/bin/env python3
"""Pan-Antarctic 595 breeding-site observed records: macro source coverage atlas.

Full source-grain: observed colony × species × season, not fake presence/absence.
The 25 Landsat sites are NOT this study's source denominator. No correlation or
significance result is selected here; original full geographic coverage first.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/"outputs"
OUT.mkdir(parents=True,exist_ok=True)
FILES={
 "observed":("outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv",
             "fc134e364cf38699fa7611d7dee5fbbbcb370c0a"),
 "mapped_land":("outputs/vegetation_response_v1/site_species_cohort.csv",
                "23fea5988889303ecdc16f4b5309073cf38e366a"),
 "historical_sic":("outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv",
                   "4fcea71c2d8b1069b6ad143f6522061ed434daf5")
}
SP=("ADPE","CHPE","GEPE")

def load(name):
    p,expected=FILES[name]
    raw=(ROOT/p).read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if actual!=expected:raise ValueError(f"Original source blob changed for {name}: {actual}")
    with (ROOT/p).open(encoding="utf-8-sig",newline="") as f:
        a=list(csv.DictReader(f))
    if not a:raise ValueError("Empty source "+name)
    return a

def integer(x,name):
    n=float(x)
    if not math.isfinite(n) or n<0 or not n.is_integer():
        raise ValueError(f"Original {name} not nonnegative finite integer")
    return int(n)
def save(path,records):
    if not records:raise ValueError("Cannot write empty macro source output")
    with (OUT/path).open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]))
        writer.writeheader();writer.writerows(records)

def main():
    from pyproj import Transformer
    raw=load("observed")
    land=load("mapped_land")
    ice=load("historical_sic")
    if (len(raw),len(land),len(ice))!=(2999,246,9600):
        raise ValueError("Source file row number drifted")
    all_sites={r["site_id"] for r in raw}
    all_focal=[r for r in raw if r["species_id"] in SP]
    methods=defaultdict(Counter)
    valid=[]
    for row in all_focal:
        if row["method"].strip() in ("","unknown") or row["n_methods"].strip()!="1":
            continue
        count=integer(row["count"],"nest count")
        if count<0:raise ValueError("Impossible negative source count")
        lat=float(row["latitude"]);lon=float(row["longitude"])
        if not(-90<=lat<=-55 and -180<=lon<=180):
            raise ValueError("Invalid Antarctic source coordinate")
        year=int(row["season"])
        if not 1800<=year<=2100:raise ValueError("Original season outside plausible source time")
        valid.append((row,count,year,lat,lon))
        methods[row["site_id"],row["species_id"]][row["method"]]+=1
    if len(all_sites)!=627 or len(all_focal)!=2861 or len(valid)!=2724 or len(methods)!=707:
        raise ValueError("Original pan-Antarctic focal/known survey method support changed")
    fixed={
        key:sorted(freq.items(),key=lambda z:(-z[1],z[0]))[0][0]
        for key,freq in methods.items()
    }
    # Different methods are never mixed within same original site and species.
    observed=[]
    seen=set()
    for row,count,year,lat,lon in valid:
        key=(row["site_id"],row["species_id"])
        if row["method"]!=fixed[key]:continue
        uniq=(row["site_id"],row["species_id"],year)
        if uniq in seen:raise ValueError("Original unique site×species×season grain duplicated")
        seen.add(uniq)
        observed.append({
            "site_id":row["site_id"],"site_name":row["site_name"],
            "source_region":row["region"],
            "species":row["species_id"],"season":year,
            "original_survey_method":row["method"],
            "observed_nest_count":count,
            "observed_zero_is_actual_source_count":count==0,
            "latitude":lat,"longitude":lon,
            "not_recorded_species_or_year_is_not_an_absence":True
        })
    observed.sort(key=lambda x:(x["site_id"],x["season"],x["species"]))
    site_species=defaultdict(list)
    by_site=defaultdict(list)
    by_region=defaultdict(list)
    same_year=defaultdict(list)
    for z in observed:
        site_species[z["site_id"],z["species"]].append(z)
        by_site[z["site_id"]].append(z)
        by_region[z["source_region"]].append(z)
        same_year[z["site_id"],z["season"]].append(z)
    if len(observed)!=2456 or len(by_site)!=595 or len(site_species)!=707 or len(by_region)!=18:
        raise ValueError("Full continental colony sample count drifted")
    if len(same_year)!=2071:raise ValueError("Site-year support changed")
    all_multi=[(k,v) for k,v in same_year.items() if len(v)>=2]
    all_three=[(k,v) for k,v in same_year.items() if len(v)==3]
    if len(all_multi)!=303 or len(all_three)!=82:
        raise ValueError("Co-censused mixed-species sample support drifted")
    land_sites={x["site_id"] for x in land}
    ice_sites={x["site_id"] for x in ice}
    if len(land_sites)!=222 or len(ice_sites)!=40 or len(land_sites&set(by_site))!=222 or len(ice_sites&set(by_site))!=40:
        raise ValueError("Existing vegetation/ice original spatial coverage drifted")
    if len(land_sites&ice_sites&set(by_site))!=31:
        raise ValueError("Original three-source geographic intersection changed")
    proj=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    inventory=[]
    blocks100=defaultdict(set);blocks250=defaultdict(set)
    for site,rows in sorted(by_site.items()):
        coords={(r["latitude"],r["longitude"]) for r in rows}
        if len(coords)!=1:raise ValueError("Site ID coordinates changed across years/species: "+site)
        lat,lon=next(iter(coords))
        x,y=proj.transform(lon,lat)
        if not(math.isfinite(x) and math.isfinite(y)):
            raise ValueError("Source site cannot be polar projected")
        b100=f"{math.floor(x/100000)}:{math.floor(y/100000)}"
        b250=f"{math.floor(x/250000)}:{math.floor(y/250000)}"
        blocks100[b100].add(site);blocks250[b250].add(site)
        yr=sorted({r["season"] for r in rows})
        distinct={r["species"] for r in rows}
        inventory.append({
            "site_id":site,"site_name":rows[0]["site_name"],
            "source_region":rows[0]["source_region"],
            "latitude":lat,"longitude":lon,
            "polar_100km_fixed_grid_block":b100,
            "polar_250km_fixed_grid_block":b250,
            "n_original_observed_species":len(distinct),
            "observed_species_codes":";".join(sorted(distinct)),
            "n_source_species_year_observations":len(rows),
            "n_unique_census_seasons":len(yr),
            "first_census_season":yr[0],"last_census_season":yr[-1],
            "in_1991to2020_historical_SIC_source":site in ice_sites,
            "in_2017to2023_mapped_land_context_source":site in land_sites,
            "both_historical_SIC_and_mapped_land_source":site in ice_sites and site in land_sites,
            "unobserved_taxa_are_not_known_absent":True
        })
    region_rows=[]
    for region,rows in sorted(by_region.items()):
        uniq={r["site_id"] for r in rows}
        subset=[r for r in inventory if r["source_region"]==region]
        region_rows.append({
            "original_source_region":region,
            "n_distinct_observed_sites":len(uniq),
            "n_original_known_method_species_year_rows":len(rows),
            "n_sites_with_Adelie_observed":len({r["site_id"] for r in rows if r["species"]=="ADPE"}),
            "n_sites_with_Chinstrap_observed":len({r["site_id"] for r in rows if r["species"]=="CHPE"}),
            "n_sites_with_Gentoo_observed":len({r["site_id"] for r in rows if r["species"]=="GEPE"}),
            "n_sites_with_at_least_two_species_recorded":sum(r["n_original_observed_species"]>=2 for r in subset),
            "n_historical_SIC_sites":sum(r["in_1991to2020_historical_SIC_source"] for r in subset),
            "n_static_mapped_land_sites":sum(r["in_2017to2023_mapped_land_context_source"] for r in subset),
            "n_polar_100km_grid_blocks":len({r["polar_100km_fixed_grid_block"] for r in subset}),
            "note":"Original site records are sampling opportunities; no unrecorded species absence inference."
        })
    coincident=[]
    for (site,year),rows in sorted(same_year.items()):
        if len(rows)<2:continue
        species={r["species"]:r for r in rows}
        coincident.append({
            "site_id":site,"census_season":year,
            "source_region":rows[0]["source_region"],
            "number_species_actually_recorded_same_year":len(species),
            "ADPE_observed_nests":species["ADPE"]["observed_nest_count"] if "ADPE" in species else "",
            "CHPE_observed_nests":species["CHPE"]["observed_nest_count"] if "CHPE" in species else "",
            "GEPE_observed_nests":species["GEPE"]["observed_nest_count"] if "GEPE" in species else "",
            "count_methods_recorded":";".join(sorted({r["original_survey_method"] for r in rows})),
            "missing_species_not_zero":True
        })
    years=[z["season"] for z in observed]
    count_by_species={sp:{
          "observed_count_rows":len([z for z in observed if z["species"]==sp]),
          "sites":len({z["site_id"] for z in observed if z["species"]==sp}),
          "observed_zero_rows":sum(z["species"]==sp and z["observed_nest_count"]==0 for z in observed)}
          for sp in SP}
    site_pairs=Counter((s,sp) for s,sp in site_species)
    longitudinal=Counter()
    for rows in site_species.values():
        longitudinal[len({r["season"] for r in rows})]+=1
    modern=[r for r in observed if 2017<=r["season"]<=2023]
    panel={
        "status":"PAN_ANTARCTIC_FULL_SOURCE_MACRO_PANEL_SUCCESS",
        "n_original_all_penguin_unambiguous_site_species_year":len(raw),
        "n_original_all_penguin_sites":len(all_sites),
        "n_focal_ADPE_CHPE_GEPE_original_rows":len(all_focal),
        "n_focal_known_single_method_rows_pre_most_frequent_method":len(valid),
        "n_focal_original_observed_count_rows_after_method_selection":len(observed),
        "n_focal_unique_sites":len(by_site),
        "n_unique_site_species":len(site_species),
        "n_original_source_regions":len(by_region),
        "original_census_year_range":[min(years),max(years)],
        "n_observed_site_years":len(same_year),
        "n_siteyears_with_2or3_species_actually_recorded":len(all_multi),
        "n_siteyears_with_all_3_species_actually_recorded":len(all_three),
        "n_sites_with_any_multispecies_record":sum(len({r["species"] for r in rows})>1 for rows in by_site.values()),
        "n_sites_with_all_3_species_ever_recorded":sum(len({r["species"] for r in rows})==3 for rows in by_site.values()),
        "n_sites_with_all_3_species_same_year":len({site for (site,year),rows in all_three}),
        "n_site_species_at_least_2_observed_years":sum(len(v)>=2 for v in site_species.values()),
        "n_site_species_at_least_5_observed_years":sum(len(v)>=5 for v in site_species.values()),
        "n_site_species_at_least_10_observed_years":sum(len(v)>=10 for v in site_species.values()),
        "n_modern_2017to2023_original_census_rows":len(modern),
        "n_modern_2017to2023_sites":len({z["site_id"] for z in modern}),
        "n_sites_with_existing_30year_ice":sum(z["in_1991to2020_historical_SIC_source"] for z in inventory),
        "n_sites_with_existing_2017to2023_land_context":sum(z["in_2017to2023_mapped_land_context_source"] for z in inventory),
        "n_sites_with_both_ice_and_land":sum(z["both_historical_SIC_and_mapped_land_source"] for z in inventory),
        "n_polar100km_source_blocks":len(blocks100),
        "n_polar250km_source_blocks":len(blocks250),
        "species_support":count_by_species,
        "source_git_blobs":{key:sha for key,(_,sha) in FILES.items()},
        "critical_limits":[
            "All records are observed breeding sites, not ecological range-wide complete survey/background",
            "Unrecorded site/species/year is missing, never an ecological absence",
            "19th-century and 2025 records have different survey effort/technology",
            "Site-code multiplicity across nearby colonies/regions and polar grid-cell shared environments require spatial block inference",
            "Multiple species recorded in different years are not a confirmed co-occurrence in one year",
            "Existing climate historical SIC only covers 40 of 595 full observed sites",
            "2017-2023 static mapped vegetation exists for 222 of 595 sites; it is not a long-term annual green-up time series",
            "100km/250km EPSG3031 grid bins are spatial-dependence diagnostics, not equal-area true habitat census areas"
        ]}
    save("source_observed_2456.csv",observed)
    save("panantarctic_595_site_inventory.csv",inventory)
    save("panantarctic_18_region_inventory.csv",region_rows)
    save("observed_multi_species_same_year_303.csv",coincident)
    (OUT/"macro_original_coverage.json").write_text(json.dumps(panel,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PAN_ANTARCTIC_MACRO_INVENTORY="+json.dumps(panel,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
