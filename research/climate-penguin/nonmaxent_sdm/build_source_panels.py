#!/usr/bin/env python3
"""Create source-pinned observation-only panels for non-MaxEnt penguin abundance GAMs.

Never generate unobserved species-site-year absences. Never copy a 2017-2023
vegetation composite onto 1991-2020 climate years.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "nest_census": (
        "outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv",
        "fc134e364cf38699fa7611d7dee5fbbbcb370c0a",
    ),
    "monthly_ice": (
        "outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv",
        "4fcea71c2d8b1069b6ad143f6522061ed434daf5",
    ),
    "contemporary_vegetation": (
        "outputs/vegetation_response_v1/site_species_cohort.csv",
        "23fea5988889303ecdc16f4b5309073cf38e366a",
    ),
}
SPECIES = ("ADPE", "CHPE", "GEPE")
MONTHS = (8, 9, 10, 11)

def source_csv(key):
    relative, expected = SOURCES[key]
    path = ROOT / relative
    data = path.read_bytes()
    got = hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\x00" + data
    ).hexdigest()
    if got != expected:
        raise ValueError(f"Original Git blob changed: {relative} {got}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows

def number(v, desc):
    if v is None or str(v).strip() == "":
        raise ValueError(f"Missing source number: {desc}")
    n = float(v)
    if not math.isfinite(n):
        raise ValueError(f"Invalid source number: {desc}")
    return n

def int_source(v,desc):
    n=number(v,desc)
    if not n.is_integer():
        raise ValueError("Expected integer "+desc)
    return int(n)

def spherical(lat, lon):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    return (
        math.cos(lat_rad) * math.cos(lon_rad),
        math.cos(lat_rad) * math.sin(lon_rad),
        math.sin(lat_rad),
    )

def csvwrite(path, rows):
    if not rows:
        raise ValueError("Empty output "+str(path))
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    obs=source_csv("nest_census")
    ice=source_csv("monthly_ice")
    land=source_csv("contemporary_vegetation")
    if (len(obs),len(ice),len(land)) != (2999,9600,246):
        raise ValueError("Original rows or input grain has changed")
    near=defaultdict(dict)
    marine_sites=set()
    for row in ice:
        if int_source(row["inner_km"],"inner_km")!=0:continue
        if row["complete_month"]!="True" or int_source(row["days"],"days")!=int_source(row["supported_days"],"supported_days"):
            raise ValueError("Incomplete SIC source month")
        site=row["site_id"]
        year=int_source(row["year"],"SIC year")
        month=int_source(row["month"],"SIC month")
        if month not in MONTHS or year<1991 or year>2020:raise ValueError("Source SIC period not frozen")
        key=(site,year)
        if month in near[key]:
            raise ValueError("Duplicate SIC site-year-month")
        near[key][month]=number(row["sic_mean"],"SIC")
        marine_sites.add(site)
    if len(marine_sites)!=40 or len(near)!=1200 or any(set(v)!=set(MONTHS) for v in near.values()):
        raise ValueError("Source 40×30×4 SIC keys changed")
    sic={k:sum(v.values())/4. for k,v in near.items()}
    site_means={site:sum(sic[site,year] for year in range(1991,2021))/30.
                for site in marine_sites}
    # Select one original known method per site×species, by observation frequency
    # only; count value never used in inclusion or tie handling.
    eligible=[]
    methods=defaultdict(Counter)
    unique=set()
    for row in obs:
        site=row["site_id"]
        species=row["species_id"]
        year=int_source(row["season"],"census season")
        if species not in SPECIES or site not in marine_sites or not(1991<=year<=2020):
            continue
        if (site,year) not in sic:
            continue
        method=row["method"].strip()
        if method=="unknown" or int_source(row["n_methods"],"n_methods")!=1:
            continue
        count=int_source(row["count"],"nest count")
        if count<0:
            raise ValueError("Negative source observed count")
        key=(site,species,year)
        if key in unique:
            raise ValueError("Duplicate selected original count grain")
        unique.add(key)
        methods[site,species][method]+=1
        eligible.append((row,year,count,method))
    selected={key:sorted(kv.items(),key=lambda x:(-x[1],x[0]))[0][0]
              for key,kv in methods.items()}
    marine=[]
    for row,year,count,method in eligible:
        site=row["site_id"]
        species=row["species_id"]
        if selected[site,species]!=method:
            continue
        lat=number(row["latitude"],"latitude")
        lon=number(row["longitude"],"longitude")
        a,b,c=spherical(lat,lon)
        region=row["region"].strip()
        marine.append({
            "site_id":site,"site_species":site+"_"+species,
            "species":species,"region":region,
            "year":year,"observed_nest_count":count,"log1p_nests":math.log1p(count),
            "method":method,"latitude":lat,"longitude":lon,
            "sphere_x":a,"sphere_y":b,"sphere_z":c,
            "sic_AugNov_0to100km_pct":sic[site,year],
            "sic_30y_site_mean_pct":site_means[site],
            "sic_site_anomaly_per10pp":(sic[site,year]-site_means[site])/10.,
            "record_is_an_actual_original_count":True,
            "zero_is_observed_not_imputed":count==0
        })
    marine.sort(key=lambda z:(z["site_id"],z["species"],z["year"]))
    by_species={sp:[r for r in marine if r["species"]==sp] for sp in SPECIES}
    expected={"ADPE":(482,40,20),"CHPE":(84,8,24),"GEPE":(95,8,0)}
    for sp,v in by_species.items():
        if (len(v),len({r["site_id"] for r in v}),
            sum(r["observed_nest_count"]==0 for r in v))!=expected[sp]:
            raise ValueError("Source/method selection drift for "+sp)
    if len(marine)!=661 or len({r["site_species"] for r in marine})!=56:
        raise ValueError("Marine original known-site count panel drift")

    land_panel=[]
    land_source_site_species=set()
    for row in land:
        site=row["site_id"]
        species=row["species_id"]
        if species not in SPECIES:continue
        key=(site,species)
        if key in land_source_site_species:
            raise ValueError("Duplicate original terrestrial site species")
        land_source_site_species.add(key)
        # Only mapped positive vegetation: '0' means not a verified absence.
        if row["positive_mapped_detection"]!="True":
            continue
        area=number(row["mapped_terrestrial_union_area_2km_m2"],"composite vegetation area")
        nseason=int_source(row["observed_seasons"],"modern observed seasons")
        count=number(row["count_median"],"modern observed median nest count")
        lat=number(row["latitude"],"modern latitude")
        lon=number(row["longitude"],"modern longitude")
        if area<=0 or count<0 or nseason<1:
            raise ValueError("Positive modern source vegetation or nest count invalid")
        a,b,c=spherical(lat,lon)
        land_panel.append({
            "site_id":site,"species":species,"region":row["region"],
            "latitude":lat,"longitude":lon,
            "sphere_x":a,"sphere_y":b,"sphere_z":c,
            "observed_seasons":nseason,"log1p_observed_seasons":math.log1p(nseason),
            "first_observed_season":int_source(row["first_observed_season"],"modern first year"),
            "last_observed_season":int_source(row["last_observed_season"],"modern last year"),
            "observed_nest_count_median":count,
            "log1p_nest_median":math.log1p(count),
            "static_mapped_vegetation_2km_m2":area,
            "log1p_static_vegetation_area_m2":math.log1p(area),
            "one_composite_2017to2023_not_yearly_ndvi":True,
            "not_known_empty_other_sites":True
        })
    land_panel.sort(key=lambda z:(z["site_id"],z["species"]))
    if len(land_source_site_species)!=246 or len(land_panel)!=197:
        raise ValueError("Contemporary source positive-detection cohort changed")
    if {sp:sum(r["species"]==sp for r in land_panel) for sp in SPECIES}!={"ADPE":33,"CHPE":117,"GEPE":47}:
        raise ValueError("Modern site/species count changed")
    csvwrite(OUT/"marine_observed_site_species_year_661.csv",marine)
    csvwrite(OUT/"contemporary_vegetation_site_species_197.csv",land_panel)
    result={
        "status":"SOURCE_PINNED_OBSERVATION_ONLY_GAM_PANELS_PASS",
        "original_git_blobs":{key:sha for key,(path,sha) in SOURCES.items()},
        "n_original_unambiguous_site_species_season":len(obs),
        "n_original_ice_monthly":len(ice),
        "n_original_modern_site_species":len(land),
        "marine_observed_rows":len(marine),
        "marine_observed_nest_zeros":sum(r["observed_nest_count"]==0 for r in marine),
        "marine_unique_sites":len({r["site_id"] for r in marine}),
        "marine_unique_site_species":len({r["site_species"] for r in marine}),
        "marine_unique_region_labels":len({r["region"] for r in marine}),
        "marine_counts_by_species":{sp:{"rows":len(v),"sites":len({z["site_id"] for z in v}),
                                      "actual_observed_zeros":sum(z["observed_nest_count"]==0 for z in v)}
                                    for sp,v in by_species.items()},
        "contemporary_positive_vegetation_site_species_rows":len(land_panel),
        "contemporary_positive_species_rows":{sp:sum(r["species"]==sp for r in land_panel) for sp in SPECIES},
        "model_domain":["marine: actually surveyed breeding site/species/year counts ONLY, 1991-2020",
                        "land: actually surveyed current site/species medians ONLY, source 2017-2023",
                        "unobserved species-site-years are missing, not sampled absences",
                        "static terrestrial composite cannot be the 1991-2020 annual vegetation variable",
                        "surveys selected in space/time; p-values are conditional uncorrected associations, not SDM occupancy evidence"]
    }
    (OUT/"source_coverage.json").write_text(json.dumps(result,indent=2)+"\n")
    print("NONMAXENT_SDM_SOURCE_GATE="+json.dumps(result,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
