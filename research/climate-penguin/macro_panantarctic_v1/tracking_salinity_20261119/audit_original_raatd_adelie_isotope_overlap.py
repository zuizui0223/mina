#!/usr/bin/env python3
"""Source-pinned RAATD Adélie location/time overlap with existing isotope panel.

A SOURCE COVERAGE audit ONLY. RAATD filtered tracking coordinates measure
estimated locations, not true prey consumption, dive intent, or salinity use.
A deployment within distance of a MAPPPD colony is not evidence its tracked
individual sampled guano at that colony or any isotope directly.

Original 2020 RAATD filtered-noTMB Zenodo 3722948 published MD5 fixed.
Original mina optical δ15N 860 original source site×season and 595 MAPPPD
site IDs fixed. Neither original publisher raw tracking files nor individual
identifiers/contact data are retained in output.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod

RAATD_MD5="168e5b9b5c4ed20bb84dd00145acb0a5"
RAATD_RECORD="https://zenodo.org/records/3722948"
ISOTOPE_SOURCE_SHA256="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
ATLAS_SOURCE_SHA256="add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a"
GEO=Geod(ellps="WGS84")
RADII=[5,25,100]
MONTHS=[11,12,1,2]

def pinned_zip(path,checksum,algorithm):
    rawpath=Path(path)
    h=hashlib.new(algorithm)
    with rawpath.open("rb") as f:
        for block in iter(lambda:f.read(8*1024*1024),b""):
            h.update(block)
    if h.hexdigest()!=checksum:
        raise ValueError(f"Published original source {rawpath.name} {algorithm} checksum changed: {h.hexdigest()}")
    z=zipfile.ZipFile(path)
    if z.testzip() is not None:
        raise ValueError("Original source zip CRC corrupt")
    return z

def original_isotope_and_sites(iso_zip,atlas_zip):
    with pinned_zip(iso_zip,ISOTOPE_SOURCE_SHA256,"sha256") as z:
        isotope=pd.read_csv(z.open("matched_860_original_isotope_ocean_ice_site_seasons.csv"))
    with pinned_zip(atlas_zip,ATLAS_SOURCE_SHA256,"sha256") as z:
        atlas=pd.read_csv(z.open("panantarctic_595_site_inventory.csv"))
    if (len(isotope),isotope.site_id.nunique(),isotope.source_region.nunique())!=(860,88,13):
        raise ValueError("Original isotope site×season cohort changed")
    if (len(atlas),atlas.site_id.nunique())!=(595,595):
        raise ValueError("Frozen original MAPPPD colony geography changed")
    if isotope.duplicated(["site_id","season"]).any():
        raise ValueError("Duplicated original isotope season")
    sites=isotope[["site_id","source_region"]].drop_duplicates().merge(
        atlas[["site_id","latitude","longitude"]],
        on="site_id",validate="one_to_one")
    if len(sites)!=88 or sites[["latitude","longitude"]].isna().any().any():
        raise ValueError("Original isotope colony geo crosswalk failed")
    return isotope,sites

def find_source_members(z):
    names=[x.filename for x in z.infolist() if
           not x.is_dir() and x.filename.lower().endswith(".csv") and
           not x.filename.split("/")[-1].startswith(".")]
    meta=[n for n in names if "metadata" in n.lower()]
    ade=[n for n in names if "adpe" in n.lower() and "metadata" not in n.lower()]
    if len(meta)!=1 or len(ade)!=1:
        raise ValueError("Original RAATD archive metadata / ADPE filtered CSV could not be uniquely identified: "+repr(names[:80]))
    return meta[0],ade[0],names

def read_original_adpe(raatd_zip):
    with pinned_zip(raatd_zip,RAATD_MD5,"md5") as z:
        mname,tname,names=find_source_members(z)
        # RAATD 2020 publisher metadata contain legacy Windows/Latin-1
        # contact and site-name bytes (0x95 etc.), not strictly UTF-8.
        # All join IDs and geographic numeric fields are ASCII; encoding
        # does not modify any tracked coordinates, times or source ID.
        meta=pd.read_csv(z.open(mname),dtype=str,low_memory=False,encoding="latin1")
        track=pd.read_csv(z.open(tname),dtype=str,low_memory=False,encoding="latin1")
    for df in [meta,track]:
        df.columns=[c.strip().lower().replace(".","_") for c in df.columns]
    expected_meta={"individual_id","abbreviated_name","deployment_decimal_latitude",
                   "deployment_decimal_longitude","deployment_year","device_type","deployment_site"}
    expected_track={"individual_id","date","decimal_latitude","decimal_longitude"}
    if not expected_meta.issubset(meta):
        raise ValueError("RAATD metadata 2020 schema differs: "+repr(sorted(meta.columns.tolist())))
    if not expected_track.issubset(track):
        raise ValueError("RAATD filtered ADPE coordinate/date schema differs: "+repr(sorted(track.columns.tolist())))
    meta=meta.loc[meta.abbreviated_name.fillna("").str.upper().str.strip()=="ADPE"].copy()
    track=track.loc[track.individual_id.notna()].copy()
    if not (250<=len(meta)<=2000 and 200<=track.individual_id.nunique()<=900):
        raise ValueError("Filtered ADPE source scale unexpectedly changed; check original archive")
    if len(track)!=90202:
        raise ValueError(f"Expected 2020 paper 90,202 original filtered ADPE location fixes, got {len(track)}")
    if meta.individual_id.duplicated().any():
        raise ValueError("RAATD ADPE individual deployment IDs are not unique; do not multiply source matches")
    track["obs_date"]=pd.to_datetime(track.date,utc=True,errors="coerce")
    if track.obs_date.isna().any():
        raise ValueError("Unparseable filtered RAATD temporal point(s)")
    meta["deployment_decimal_latitude"]=pd.to_numeric(meta.deployment_decimal_latitude,errors="coerce")
    meta["deployment_decimal_longitude"]=pd.to_numeric(meta.deployment_decimal_longitude,errors="coerce")
    meta["deployment_year"]=pd.to_numeric(meta.deployment_year,errors="coerce")
    linked=set(track.individual_id)
    meta=meta.loc[meta.individual_id.isin(linked)].copy()
    if len(meta)!=track.individual_id.nunique():
        raise ValueError("Missing original RAATD deployment metadata for filtered ADPE tracked individuals")
    track["year"]=track.obs_date.dt.year
    track["month"]=track.obs_date.dt.month
    track=track.loc[track.month.isin(MONTHS)].copy()
    track["season"]=np.where(track.month.isin([1,2]),track.year-1,track.year)
    track=track.loc[track.season.between(1996,2012)]
    if track.empty:raise ValueError("No source original Adélie Nov–Feb tracking data in 1996–2012")
    track=track[["individual_id","season","obs_date"]].copy()
    trk=track.groupby(["individual_id","season"],as_index=False).agg(
        tracking_filtered_fixes_in_novfeb=("obs_date","size"),
        first_observed_filtered_fix=("obs_date","min"),
        last_observed_filtered_fix=("obs_date","max"))
    del track
    m=meta.merge(trk,on="individual_id",validate="one_to_many")
    m["device_type"]=m.device_type.fillna("UNKNOWN").str.upper().str.strip()
    return m,meta,{"original_members":len(names),"metadata_member":mname,
                     "ADPE_filtered_member":tname,
                     "original_filtered_adpe_location_fixes_all_years":90202,
                     "original_filtered_adpe_individuals_all_years":len(meta),
                     "original_filtered_adpe_individual_seasons_novfeb_1996_2012":len(trk),
                     "original_filtered_adpe_distinct_seasons":int(trk.season.nunique()),
                     "original_filtered_adpe_study_seasons":sorted(map(int,trk.season.unique()))}

def assign_source_geography(m,sites):
    # a single metadata row per deployment individual may map to multiple seasons.
    j=m.drop_duplicates("individual_id").copy()
    good=j.deployment_decimal_latitude.between(-90,-50)&j.deployment_decimal_longitude.between(-180,180)
    j=j.loc[good].copy()
    loc=sites[["site_id","latitude","longitude"]].reset_index(drop=True)
    lats=loc.latitude.to_numpy(float);lons=loc.longitude.to_numpy(float)
    matching=[]
    for rec in j.itertuples(index=False):
        n=len(loc)
        _,_,dist=GEO.inv(np.full(n,rec.deployment_decimal_longitude),
                         np.full(n,rec.deployment_decimal_latitude),lons,lats)
        d=np.asarray(dist,float)/1000
        a,b=np.argsort(d)[:2]
        matching.append({
            "individual_id":rec.individual_id,
            "nearest_isotope_site_id":str(loc.iloc[a].site_id),
            "nearest_isotope_distance_km":float(d[a]),
            "next_nearest_isotope_distance_km":float(d[b]),
            "RAATD_device_type":rec.device_type
        })
    if not matching:
        raise ValueError("No source valid RAATD Adélie deployment coordinates")
    proximity=pd.DataFrame(matching)
    df=m.merge(proximity,on="individual_id",how="inner",validate="many_to_one")
    # The truly specific source colony match is an unambiguous nearest original
    # MAPPPD colony within the specified km radius.
    for km in RADII:
        df[f"original_single_colony_unique_{km}km"]=(
            df.nearest_isotope_distance_km<=km)&(df.next_nearest_isotope_distance_km>km)
        df[f"original_some_colony_near_{km}km"]=df.nearest_isotope_distance_km<=km
    return df

def audit(data,allmeta,source_detail,isotope,sites,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    src_isotope=isotope[["site_id","season","source_region"]].drop_duplicates()
    available=set(map(tuple,src_isotope[["site_id","season"]].itertuples(index=False,name=None)))
    groups=[]
    for radius in RADII:
        # Two distinct location notions. "Nearest within radius" increases
        # with radius; "unique single colony within radius" need NOT.
        # A deployment may be 2km from the nearest known colony but have
        # another different colony 8km away, making 25km ambiguous.
        nearest=data.loc[data[f"original_some_colony_near_{radius}km"]].copy()
        nearest["candidate_pair"]=list(zip(nearest.nearest_isotope_site_id,nearest.season))
        nearest=nearest.loc[nearest.candidate_pair.isin(available)].copy()
        q=data.loc[data[f"original_single_colony_unique_{radius}km"]].copy()
        q["matched_isotope_site_season"]=list(zip(q.nearest_isotope_site_id,q.season))
        q["genuine_matched_site_season"]=q.matched_isotope_site_season.isin(available)
        overlap=q.loc[q.genuine_matched_site_season].copy()
        precise=overlap.loc[overlap.RAATD_device_type.isin(["GPS","PTT"])]
        if not overlap.empty:
            x=overlap[["individual_id","nearest_isotope_site_id","season","RAATD_device_type"]].drop_duplicates()
            ids=x.rename(columns={"nearest_isotope_site_id":"site_id"}).merge(
                src_isotope,on=["site_id","season"],validate="many_to_one")
            for_name=ids
        else:
            for_name=pd.DataFrame(columns=["individual_id","site_id","season","source_region","RAATD_device_type"])
        groups.append({
            "radius_km":radius,
            "n_deployments_nearest_isotope_site_within_radius_regardless_ambiguous":int(data[f"original_some_colony_near_{radius}km"].sum()),
            "n_nearest_source_isotope_site_seasons_same_year":int(nearest[["nearest_isotope_site_id","season"]].drop_duplicates().shape[0]),
            "n_nearest_source_isotope_sites_same_year":int(nearest.nearest_isotope_site_id.nunique()),
            "n_nearest_source_reporting_regions_same_year":int(nearest.nearest_isotope_site_id.map(
                src_isotope.drop_duplicates("site_id").set_index("site_id").source_region).nunique()),
            "n_nearest_source_individuals_same_year":int(nearest.individual_id.nunique()),
            "n_nearest_ambiguous_individual_seasons_same_year":int((nearest.next_nearest_isotope_distance_km<=radius).sum()),
            "n_raatd_original_deployment_individual_seasons_near":len(q),
            "n_raatd_original_deployment_individuals_near":int(q.individual_id.nunique()),
            "n_raatd_original_isotope_site_seasons_matched":int(for_name[["site_id","season"]].drop_duplicates().shape[0]),
            "n_source_isotope_sites_with_true_temporal_match":int(for_name.site_id.nunique()),
            "n_source_reporting_regions_with_true_temporal_match":int(for_name.source_region.nunique()),
            "n_source_actual_breeding_seasons_with_match":int(for_name.season.nunique()),
            "n_source_RAADT_individuals_with_true_temporal_match":int(for_name.individual_id.nunique()),
            "n_raatd_GPS_PTT_individuals_with_true_temporal_match":int(precise.individual_id.nunique()),
            "n_raatd_GPS_PTT_matched_isotope_site_seasons":int(precise[["nearest_isotope_site_id","season"]].drop_duplicates().shape[0]),
            "n_original_source_isotope_site_seasons_total":860,
            "n_original_source_isotope_sites_total":88,
            "n_individuals_not_independent_predator_populations":True
        })
    # Do not erase the 5-km genuine closest-colony matches when the 25-km
    # distance window overlaps two distinct catalogued penguin colonies.
    # The secondary nearest-site report flags ambiguity and is NOT an
    # individually confirmed breeding-colony or guano-sample link.
    for radius, scheme in [(5,"unique"),(25,"nearest")]:
        if scheme=="unique":
            matched=data.loc[data[f"original_single_colony_unique_{radius}km"]].copy()
        else:
            matched=data.loc[data[f"original_some_colony_near_{radius}km"]].copy()
        matched["key"]=list(zip(matched.nearest_isotope_site_id,matched.season))
        matched=matched.loc[matched.key.isin(available)].copy()
        matched["ambiguous_other_isotope_colony_in_radius"]=(matched.next_nearest_isotope_distance_km<=radius)
        table=matched.groupby(["nearest_isotope_site_id","season"],as_index=False).agg(
            RAATD_n_source_individuals=("individual_id","nunique"),
            RAATD_n_source_deployment_seasons=("season","size"),
            RAATD_n_GPS_PTT_individuals=("RAATD_device_type",lambda x:int(x.isin(["GPS","PTT"]).sum())),
            n_filtered_pos_estimates_novfeb=("tracking_filtered_fixes_in_novfeb","sum"),
            nearest_deployment_km_min=("nearest_isotope_distance_km","min"),
            nearest_deployment_km_max=("nearest_isotope_distance_km","max"),
            any_other_colony_ambiguous=("ambiguous_other_isotope_colony_in_radius","any"))
        table=table.rename(columns={"nearest_isotope_site_id":"site_id"})
        table=table.merge(src_isotope,on=["site_id","season"],validate="one_to_one")
        if table.duplicated(["site_id","season"]).any():
            raise ValueError("Multiple source metadata site-year associations erroneously joined")
        table.to_csv(out/f"original_raatd_adelie_isotope_site_season_support_{radius}km_{scheme}.csv",index=False)
    pd.DataFrame(groups).to_csv(out/"original_raatd_source_geographic_temporal_overlap_gate.csv",index=False)
    dev_meta=allmeta.device_type.fillna("UNKNOWN").str.upper().value_counts().astype(int).to_dict()
    strict=groups[0]
    # Fixed before seeing this original source: >=12 strict 5-km unique
    # site-seasons with >=3 original GPS/PTT individuals each, >=3 distinct
    # reporting regions and >=3 different source breeding seasons.
    strict_table=pd.read_csv(out/"original_raatd_adelie_isotope_site_season_support_5km_unique.csv")
    strong=strict_table.loc[strict_table.RAATD_n_GPS_PTT_individuals>=3]
    gate=(len(strong)>=12 and strong.source_region.nunique()>=3
          and strong.season.nunique()>=3)
    report={
        "status":"GO_TRACKING_ISOTOPE_SOURCE_OVERLAP" if gate else "NO_GO_TRACKING_ISOTOPE_MACRO_JOIN",
        "original_RAATD_source":RAATD_RECORD,
        "original_RAATD_source_md5":RAATD_MD5,
        "original_isotope_source_sha256":ISOTOPE_SOURCE_SHA256,
        "original_MAPPPD_atlas_sha256":ATLAS_SOURCE_SHA256,
        "first_pass_radii_km":RADII,
        "temporal_match":"original observed isotope Nov–following-February breeding season, not deployment-year only",
        "source_member_inventory":source_detail,
        "RAATD_metadata_device_types_after_ADPE_filtered_ID_link":dev_meta,
        "source_88_isotope_colonies":len(sites),
        "source_860_isotope_site_seasons":len(isotope),
        "source_overlap_by_radius":groups,
        "strict_5km_actual_colony_seasons_with_min3_GPS_PTT_individuals":int(len(strong)),
        "strict_5km_actual_regions_with_min3_GPS_PTT_individuals":int(strong.source_region.nunique()),
        "strict_5km_actual_seasons_with_min3_GPS_PTT_individuals":int(strong.season.nunique()),
        "fixed_minimum_gate":"strict 5km unique source colony match: >=12 site-seasons with >=3 GPS/PTT original individuals each, >=3 source reporting regions and >=3 source seasons",
        "can_move_to_multi_region_used_available_isotope_integration":bool(gate),
        "unique_site_25km_match_count_is_not_monotonic_in_radius":True,
        "attribution_limit":"Individual tracked deployment within 5/25/100km of isotope-observed known colony, NOT same individual or observed guano sample; only near-colony spatial support.",
        "filtered_locations_not_direct_feeding_or_dive_observations":True,
        "GLS_estimates_not_used_as_high_precision_GPS_tracks":True,
        "RAATD_tracking_only_can_test_habitat_use_not_fish_krill_choice":True,
        "birdlife_metadata_public_but_tracks_require_owner_permission":True,
        "not_ready_to_extrapolate_0p834_salinity_slope_to_tracking_or_future":True,
        "third_party_original_coordinates_and_contact_emails_not_redistributed":True,
    }
    (out/"raatd_adelie_2020_original_isotope_overlap_verdict.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

def main():
    p=argparse.ArgumentParser()
    for arg in ["raatd-zip","isotope-zip","atlas-zip","out"]:
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    isotope,sites=original_isotope_and_sites(a.isotope_zip,a.atlas_zip)
    ra,meta,detail=read_original_adpe(a.raatd_zip)
    joined=assign_source_geography(ra,sites)
    audit(joined,meta,detail,isotope,sites,a.out)

if __name__=="__main__":
    main()
