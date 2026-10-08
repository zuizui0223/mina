"""Spatial-radius sensitivity of existing outcome-exposed Ledda ice source receipts.

Only fixed radii 1,3,5 km, fixed 6 years and two publication centroids;
no new site selection, no ecological inferential fit or bird data access.
"""
import argparse
import json
from pathlib import Path

YEARS=(2009,2010,2011,2012,2013,2014)
RADII=("1","3","5")
CENTERS=("LaRue_original","Fretwell_alternative")


def readout(paired,historical):
    if paired["status"]!="PAIRED_PREIMAGE_PHYSICAL_TRAJECTORIES_EXTRACTED_NOT_BREEDING_HABITABILITY":
        raise ValueError("Paired source not valid")
    if historical["decision"]!="EXPLORATORY_PHYSICAL_ANCHOR_SERIES_AVAILABLE_ONLY" or not historical["all_years_read"]:
        raise ValueError("Historical source not valid")
    by_year={}
    for x in paired["year_results"]:
        year=x["year"]
        if year not in (2011,2014) or year in by_year:
            raise ValueError("Unexpected paired year")
        if x["original"]["status"]!="EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED" or x["alternative"]["status"]!="ALTERNATIVE_PUBLISHED_CENTROID_ICE_PIXEL_CONTEXT_READ":
            raise ValueError("Missing physical source")
        d={}
        for r in RADII:
            z=x["trajectory_by_radius"][r]["last_completed_preimage_composite"]
            d[r]={
                "LaRue_original":[z["original_class4_cells"],z["original_n_cells"]],
                "Fretwell_alternative":[z["alternative_class4_cells"],z["alternative_n_cells"]]
            }
        by_year[year]=d
    for x in historical["year_results"]:
        year=x["year"]
        if year not in (2009,2010,2012,2013) or year in by_year or x["status"]!="EXPLORATORY_HISTORIC_INDEPENDENT_PHYSICAL_GRID_READ":
            raise ValueError("Unexpected or absent historical year source")
        d={}
        for r in RADII:
            d[r]={}
            for center in CENTERS:
                z=x["preimage_physical_by_site_and_radius"][center][r]["last_fully_preimage"]
                d[r][center]=[z["class4_pixels"],z["valid_pixels"]]
        by_year[year]=d
    if tuple(sorted(by_year))!=YEARS:
        raise ValueError("Incomplete year set")
    for d in by_year.values():
        for r in RADII:
            for center in CENTERS:
                a,n=d[r][center]
                if type(a)!=int or type(n)!=int or n<=0 or not 0<=a<=n:
                    raise ValueError("Invalid source class-4 histogram")
    return {
        "status":"EXPLORATORY_FROZEN_SPATIAL_RADIUS_SENSITIVITY",
        "years":list(YEARS),
        "radii_km":[1,3,5],
        "physical_class4_observations":{
            str(y):{r:{
                center:{"ice_cells":by_year[y][r][center][0],
                        "n_cells":by_year[y][r][center][1],
                        "ice_fraction":by_year[y][r][center][0]/by_year[y][r][center][1]}
                for center in CENTERS}
                for r in RADII} for y in YEARS
        },
        "2014_disagreement_by_radius":{
            r:(by_year[2014][r]["LaRue_original"][0]==0 and
               by_year[2014][r]["Fretwell_alternative"][0]>0)
            for r in RADII
        },
        "new_penguin_records_opened":0,
        "nest_site_breeding_viability_proven":False,
        "causal_social_or_ice_effect_inferred":False,
        "PR189_changed":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--paired",type=Path,required=True)
    p.add_argument("--historical",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=readout(json.loads(a.paired.read_text()),json.loads(a.historical.read_text()))
    a.out.write_text(json.dumps(d,indent=2)+"\n")
    print("RADIUS_SENSITIVITY",d["status"])
    for y,v in d["physical_class4_observations"].items():
        for r,pair in v.items():
            print("ICE_RADIUS",y,r,"km",
                  *(f"{name}:{s['ice_cells']}/{s['n_cells']}"
                    for name,s in pair.items()))
    print("2014_SPATIAL_DISCORDANCE",d["2014_disagreement_by_radius"])
    print("NO_NEW_PENGUIN_OR_CAUSAL_EVIDENCE")


if __name__=="__main__":
    main()
