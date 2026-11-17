#!/usr/bin/env python3
"""Original SCAR gut/other prey measurements: sampling support and MAPPPD overlap.
This does not estimate climate effects or pool incomparable prey fraction types.
"""
from pathlib import Path
import argparse,hashlib,io,json,zipfile
import numpy as np
import pandas as pd
from pyproj import Geod
GH_SOURCE="https://zenodo.org/records/20047874"
PIN_MD5="5e098c268ce0028704bc4b06300cb0ef"
MATCH_DISTANCE_KM=25
GEO=Geod(ellps="WGS84")
GROUP_COLS=["source_id","predator_name","location","observation_date_start","observation_date_end","identification_method"]

def read_source(source_zip,atlas_zip):
    raw=Path(source_zip).read_bytes()
    md5=hashlib.md5(raw).hexdigest()
    if md5!=PIN_MD5 or len(raw)!=9543574:
        raise ValueError("Original SCAR source MD5/size changed")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:raise ValueError("Corrupt publisher ZIP")
        d=pd.read_csv(z.open("scar_diet.csv"),dtype=str,low_memory=False)
        sources=pd.read_csv(z.open("scar_sources.csv"),dtype=str,low_memory=False)
    with zipfile.ZipFile(atlas_zip) as z:
        atlas=pd.read_csv(z.open("panantarctic_595_site_inventory.csv"))
    if len(atlas)!=595 or atlas.site_id.nunique()!=595:
        raise ValueError("Original MAPPPD 595 colony geography drift")
    need={"record_id","source_id","predator_name","location","west","east","south","north",
          "observation_date_start","observation_date_end","prey_name","prey_worms_class",
          "identification_method","fraction_diet_by_weight","fraction_diet_by_prey_items",
          "fraction_occurrence","is_secondary_data"}
    if not need.issubset(d):raise ValueError(f"SCAR diet source columns missing {need-set(d)}")
    if not (10000<len(d)<200000):raise ValueError("Unexpected SCAR diet source scale")
    return d,sources,atlas,md5

def audit(d,sources,atlas,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # Ensure the name is given for the predator, not merely a prey item.
    names=d.predator_name.fillna("").str.strip().str.lower()
    species_map={"pygoscelis adeliae":"Adelie",
                 "pygoscelis antarcticus":"Chinstrap",
                 "pygoscelis antarctica":"Chinstrap",
                 "pygoscelis papua":"Gentoo"}
    target=d.loc[names.isin(species_map)].copy()
    target["species_group"]=target.predator_name.str.strip().str.lower().map(species_map)
    counts={"scar_diet_rows_all_taxa":len(d),
            "scar_sources_in_source_registry":int(sources.source_id.nunique()),
            "target_pygoscelis_prey_rows":len(target),
            "target_source_ids":int(target.source_id.nunique()),
            "target_species_counts":target.groupby("species_group").size().astype(int).to_dict(),
            "source_methods":target.identification_method.fillna("NA").value_counts().head(30).astype(int).to_dict(),
            "prey_classes":target.prey_worms_class.fillna("NA").value_counts().head(20).astype(int).to_dict(),
            "secondary_flag":target.is_secondary_data.fillna("NA").value_counts().head(10).astype(int).to_dict()}
    for f in ["fraction_diet_by_weight","fraction_diet_by_prey_items","fraction_occurrence"]:
        x=pd.to_numeric(target[f],errors="coerce")
        counts[f+"_available"]=int(x.notna().sum())
        counts[f+"_valid_zero_to_one"]=int(x.between(0,1).sum())
        counts[f+"_min_max"]=[float(x.min()) if x.notna().any() else None,float(x.max()) if x.notna().any() else None]
    # Geography: no broad polygons quietly promoted to precise local estimates.
    for c in ("west","east","south","north"):
        target[c]=pd.to_numeric(target[c],errors="coerce")
    target["lon_mid"]=(target.west+target.east)/2
    target["lat_mid"]=(target.south+target.north)/2
    # Source bbox size in true geodesic km.
    good=target[["west","east","south","north"]].notna().all(axis=1)
    a=target.loc[good]
    if len(a):
        _,_,dx=GEO.inv(a.west.to_numpy(),a.lat_mid.to_numpy(),a.east.to_numpy(),a.lat_mid.to_numpy())
        _,_,dy=GEO.inv(a.lon_mid.to_numpy(),a.south.to_numpy(),a.lon_mid.to_numpy(),a.north.to_numpy())
        target.loc[good,"source_bbox_km"]=np.hypot(dx/1000,dy/1000)
    target["start"]=pd.to_datetime(target.observation_date_start,errors="coerce")
    target["end"]=pd.to_datetime(target.observation_date_end,errors="coerce")
    target["duration_days"]=(target.end-target.start).dt.days
    target["calendar_season"]=np.where(target.start.dt.month.isin([1,2]),target.start.dt.year-1,target.start.dt.year)
    target["single_breeding_season"]=(
        target.start.notna()&target.end.notna()&
        target.duration_days.between(0,122)&
        target.start.dt.month.isin([11,12,1,2])&
        target.end.dt.month.isin([11,12,1,2])&
        target.calendar_season.between(1991,2020))
    # No cross-season field date allowed even if dates happen to be Nov-Feb.
    end_season=np.where(target.end.dt.month.isin([1,2]),target.end.dt.year-1,target.end.dt.year)
    target["single_breeding_season"] &= (target.calendar_season==end_season)
    precise=target.loc[target.single_breeding_season & target.source_bbox_km.le(25) &
                       target.lat_mid.le(-55)].copy()
    coords=atlas[["site_id","latitude","longitude","source_region"]].drop_duplicates()
    # each prey row is NOT an independent diet sample: only record geography/season metadata.
    source_groups=precise.groupby(GROUP_COLS,dropna=False).agg(
        prey_row_count=("record_id","size"),
        n_distinct_prey=("prey_name","nunique"),
        n_weight_fractions=("fraction_diet_by_weight",lambda x:int(pd.to_numeric(x,errors="coerce").notna().sum())),
        species_group=("species_group","first"),
        lon_mid=("lon_mid","first"),lat_mid=("lat_mid","first"),
        source_bbox_km=("source_bbox_km","first"),
        calendar_season=("calendar_season","first"),
    ).reset_index()
    atlas_lon=coords.longitude.to_numpy(dtype=float)
    atlas_lat=coords.latitude.to_numpy(dtype=float)
    links=[]
    for row in source_groups.itertuples(index=False):
        _,_,metres=GEO.inv(np.full(len(coords),row.lon_mid),np.full(len(coords),row.lat_mid),
                          atlas_lon,atlas_lat)
        dk=np.asarray(metres)/1000
        order=np.argsort(dk)
        first,second=int(order[0]),int(order[1])
        matches=bool(dk[first]<=MATCH_DISTANCE_KM and dk[second]>MATCH_DISTANCE_KM)
        links.append({"source_id":row.source_id,"source_species":row.species_group,
              "source_location":str(row.location),"source_season":int(row.calendar_season),
              "source_date_start":row.observation_date_start,
              "source_date_end":row.observation_date_end,
              "source_method":str(row.identification_method),
              "diet_prey_rows_in_group":int(row.prey_row_count),
              "diet_prey_taxa_in_group":int(row.n_distinct_prey),
              "diet_weight_entries_in_group":int(row.n_weight_fractions),
              "original_geo_bbox_km":float(row.source_bbox_km),
              "nearest_original_site":str(coords.iloc[first].site_id),
              "nearest_original_site_region":str(coords.iloc[first].source_region),
              "original_site_distance_km":float(dk[first]),
              "nearest_site_is_unique_within25km":matches})
    link=pd.DataFrame(links)
    if not link.empty:
        link.to_csv(out/"original_scar_precise_penguin_diet_candidate_source_panels.csv",index=False)
        selected=link.loc[link.nearest_site_is_unique_within25km]
    else:selected=link
    r={"status":"SOURCE_SCAR_DIET_PANEL_SUPPORT_GATE_NO_CLIMATE_OR_Diet_EFFECT",
       "source":GH_SOURCE,"md5":PIN_MD5,
       **counts,
       "target_exact_single_season_raw_prey_rows":int(target.single_breeding_season.sum()),
       "target_coastal_single_season_precise_bbox_raw_prey_rows":int(len(precise)),
       "unique_source_location_season_method_groups_precise":int(len(link)),
       "original_mapppd_match_groups_unique_within25km":int(len(selected)),
       "matched_original_mapppd_colony_sites":int(selected.nearest_original_site.nunique()) if len(selected) else 0,
       "matched_original_mapppd_regions":int(selected.nearest_original_site_region.nunique()) if len(selected) else 0,
       "matched_source_seasons":int(selected.source_season.nunique()) if len(selected) else 0,
       "matched_source_original_studies":int(selected.source_id.nunique()) if len(selected) else 0,
       "matched_groups_with_quantitative_weight_preys":int((selected.diet_weight_entries_in_group>0).sum()) if len(selected) else 0,
       "not_independent_sample_counts":"prey rows, sample IDs, and multiple records of a single study cannot be counted as independent climate replications",
       "no_false_absences":True,"no_pool_mixed_diet_methods":True,"no_climate_response_estimated":True}
    if len(selected):
        r["matched_source_methods"]=selected.source_method.value_counts().head(20).astype(int).to_dict()
        r["matched_source_species"]=selected.source_species.value_counts().astype(int).to_dict()
        r["matched_source_region_counts"]=selected.nearest_original_site_region.value_counts().astype(int).to_dict()
    (out/"original_scar_pygoscelis_diet_source_support_receipt.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(r,indent=2,ensure_ascii=False))
    return r

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--scar-zip",required=True)
    p.add_argument("--atlas-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    d,sources,atlas,md5=read_source(a.scar_zip,a.atlas_zip)
    audit(d,sources,atlas,a.out)

if __name__=="__main__":main()
