"""Source-native spatial pixel-union audit for Signy / 3 matched Chinstrap islands.

Unlike tag-level summaries, each unique published GAM raster pixel visited
by one or more original GPS tags appears once per site-year and model year.
This sensitivity detects shared model-cell pseudoreplication; adjacent cells
are spatially autocorrelated and not independent biological observations.
Sources & model are identical to main source GPS radial analysis, including
Freer GEM learned acoustic/salinity/ice and no independently verified ocean
navigation mask.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
import south_orkney_chinstrap_island_krill_v1 as island
import signy_gps_krill_access_v1 as source
import chinstrap_krill_geographic_vs_GPS_direction_v1 as radial

YEARS=island.PAIRS
PERIODS=("preseason","same_summer")
SOURCE_UNITS=308

def analyze(gps_source,model_source):
    tracks,qa=island.read_all_chinstrap(gps_source)
    model=source.source_models(model_source)
    centers=island.island_source_centers(tracks)
    unions=defaultdict(set)
    tagcounts=defaultdict(int)
    for track in tracks:
        site,year=track["island"],track["season"]
        center=centers[site,year]
        for period in PERIODS:
            fieldyear=year+(period=="same_summer")
            arr,tr=model[fieldyear]
            hours,cells=radial.source_selected_unique_cells(track,center,arr,tr)
            if cells:
                tagcounts[site,year,period]+=1
                unions[site,year,period].update(cells)
    all_results=[]
    for (site,year),center in sorted(centers.items()):
        for period in PERIODS:
            key=site,year,period
            rawcells=sorted(unions.get(key,set()))
            if not rawcells:
                raise ValueError("source island-year GPS cell union empty")
            arr,tr=model[year+(period=="same_summer")]
            _,rings,bins=radial.grid_reference(
               arr,tr,center["center_lat"],center["center_lon"])
            visited=[float(arr[r,c]) for r,c in rawcells]
            background=[rings[int(bins[r,c])] for r,c in rawcells]
            if not all(math.isfinite(x) for x in visited+background):
                raise ValueError("original GAM source cell invalid in union")
            rmean=statistics.mean(visited)
            bmean=statistics.mean(background)
            n_lower=sum(a<b for a,b in zip(visited,background))
            # 0.25 degree coarsening is only a support diagnostic and
            # not an independence assumption or validated ecological scale.
            blocks=set()
            for r,c in rawcells:
                lat=tr.f+(r+0.5)*tr.e
                lon=tr.c+(c+0.5)*tr.a
                blocks.add((math.floor(lat*4),math.floor(lon*4)))
            all_results.append({
                "island":site,"season_start":year,
                "model_period":period,"source_model_year":year+(period=="same_summer"),
                "n_original_source_GPS_qualified_deployments":tagcounts[key],
                "n_unique_native_GAM_visited_cells":len(rawcells),
                "n_unique_025degree_lon_lat_blocks":len(blocks),
                "n_cells_below_distance_matched_background":n_lower,
                "fraction_unique_GAM_cells_below_radial_background":n_lower/len(rawcells),
                "native_unique_cell_mean_GAM_g_m2":rmean,
                "native_unique_cell_distance_matched_mean_GAM_g_m2":bmean,
                "cell_union_GAM_div_radial_reference":rmean/bmean if bmean>0 else None,
                "original_GAM_cells_not_independent_ocean_observations":True
            })
    index={(r["island"],r["season_start"],r["model_period"]):r for r in all_results}
    pairs=[]
    for year,other in YEARS:
        for period in PERIODS:
            a=index["SI",year,period]
            b=index[other,year,period]
            ratio=b["cell_union_GAM_div_radial_reference"]/a["cell_union_GAM_div_radial_reference"]
            pairs.append({
                "season_start":year,"other_island":other,"model_period":period,
                "n_native_cells_other":b["n_unique_native_GAM_visited_cells"],
                "n_native_cells_Signy":a["n_unique_native_GAM_visited_cells"],
                "other_div_Signy_GAM_native_union_mean":b["native_unique_cell_mean_GAM_g_m2"]/a["native_unique_cell_mean_GAM_g_m2"],
                "other_div_Signy_radial_reference_on_unioned_cells":b["native_unique_cell_distance_matched_mean_GAM_g_m2"]/a["native_unique_cell_distance_matched_mean_GAM_g_m2"],
                "other_div_Signy_native_cell_union_radial_adjusted_ratio":ratio,
                "model_cells_spatially_autocorrelated_no_ecology_test":True
            })
    if len(tracks)!=SOURCE_UNITS or len(all_results)!=14 or len(pairs)!=6:
        raise ValueError("source original seven island-years or six same-year tests incomplete")
    return all_results,pairs,qa

def verify(records,pairs):
    n={(z["island"],z["season_start"],z["model_period"]):z for z in records}
    for year in (2011,2013,2015,2018):
        r=n["SI",year,"preseason"]
        if r["n_unique_native_GAM_visited_cells"]<5 or r["n_unique_025degree_lon_lat_blocks"]<2:
            raise ValueError("Signy model-cell support insufficient or GIS error")
        if r["n_cells_below_distance_matched_background"]>r["n_unique_native_GAM_visited_cells"]:
            raise ValueError("a native source cell counted more than once")
    for z in pairs:
        if not math.isclose(
            z["other_div_Signy_GAM_native_union_mean"]/
            z["other_div_Signy_radial_reference_on_unioned_cells"],
            z["other_div_Signy_native_cell_union_radial_adjusted_ratio"],
            abs_tol=1e-12
        ):
            raise ValueError("native-cell union decomposition identity failed")
    return True

def save(path,rows):
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--gps-zip",required=True,type=Path)
    parser.add_argument("--model-zip",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args()
    records,pairs,sourceqa=analyze(a.gps_zip,a.model_zip)
    if a.check:verify(records,pairs)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"seven_island_years_native_visited_GAM_cell_union.csv",records)
    save(a.out/"three_matched_islands_native_cell_union_contrasts.csv",pairs)
    output={
        "status":"SOURCE_GPS_VISITED_NATIVE_GAM_CELL_UNION_CROSSCHECK_NOT_INDEPENDENT_KRILL",
        "n_original_GPS_source_deployments":SOURCE_UNITS,
        "n_island_year_source_units":7,"n_source_native_cell_summaries":14,
        "n_same_species_matched_island_comparisons":3,
        "source_GPS_DOI":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
        "source_GAM_DOI":"10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32",
        "source_original_GPS_QA":sourceqa,
        "Signy_preseason_source":[r for r in records if r["island"]=="SI" and r["model_period"]=="preseason"],
        "matched_preseason_source":[r for r in pairs if r["model_period"]=="preseason"],
        "limits":[
            "Native published model pixels are not independent ecological spatial or acoustic sampling units.",
            "Counting each pixel only once removes within-year duplicated tag-pixel contributions but not spatial autocorrelation.",
            "The 0.25 degree block count is only spatial support, not a statistical effective sample size.",
            "GPS is not dive-confirmed or prey-capture location, publisher GAM already fit ice/salinity/acoustic survey data.",
            "Island geography and alternative azimuthal movement constraints remain unresolved; no causal, demographic or future prediction."
        ]
    }
    (a.out/"decision.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":output["status"],"signy":output["Signy_preseason_source"],
       "pairs":output["matched_preseason_source"],"verified":bool(a.check)},ensure_ascii=False))

if __name__=="__main__":main()
