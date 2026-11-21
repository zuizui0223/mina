#!/usr/bin/env python3
"""Frozen AA 602094 original Site×collection-year geospatial alignment only.

No AA TP/Phe/bulk values read; use only flags complete. Compare 2004–2010
samples with original 88 pre-2013 Youngflesh isotope-proxy site locations
(genuine source ARTIFACT 14539723210, original isotope artifact 14328755565).
2/10/25km are fixed metadata tests, NOT a causal or temporal polynya fit.
"""
from __future__ import annotations
import argparse,zipfile,hashlib,io,json
from pathlib import Path
import pandas as pd
from pyproj import Geod

PUBLISHED_AA_MD5="f9a91c9d9bf3dba9607bf0767df8c206"
AA_MEMBER="usapdc_602094/Michelson_2026_Adelie_Feathers_SIA_CSIA_Data.csv"
ORIGINAL88_GEO_SHA="702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96"
ORIGINAL860_ISO_SHA="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
ORIGINAL88_GEO_MEMBER="source_original_88_site_polynya_25km_100km_native_grid_geography.csv"
ORIGINAL860_ISO_MEMBER="matched_860_original_isotope_ocean_ice_site_seasons.csv"
MEASURED=["d15N","Phe_d15N","Glu_d15N","Trophic_position"]

def checked_member(path,filename,sha=None):
    if sha and hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha:
        raise ValueError("Original pinned GitHub Actions artifact SHA mismatch")
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError("Original source ZIP CRC failure")
        names=[n for n in z.namelist() if n==filename or n.endswith("/"+filename)]
        if len(names)!=1:raise ValueError("Original publisher source ZIP member missing/ambiguous")
        return z.read(names[0])

def main(a):
    if not (Path(__file__).parent/"FROZEN_AA_OLD88_SOURCE_GEOGRAPHY_MATCH_ONLY_20261121_JA.md").exists():
        raise ValueError("Geographic comparison requires committed frozen source-only spec")
    aa=checked_member(a.aa_zip,AA_MEMBER)
    if hashlib.md5(aa).hexdigest()!=PUBLISHED_AA_MD5:
        raise ValueError("User original CSV not publisher MD5 identical")
    d=pd.read_csv(io.BytesIO(aa),low_memory=False)
    if d.shape!=(108,45) or d.Sample_ID.nunique()!=108:
        raise ValueError("Original true feather source denominator drift")
    # Measurement fields inspected only for complete flags: no outcome fit/value!
    sel=d[MEASURED].notna().all(axis=1)&d.Year_collected.between(2004,2010)
    aa=d.loc[sel].copy()
    if len(aa)!=7 or aa.groupby(["Site","Year_collected"]).ngroups!=6:
        raise ValueError("Original measured 2004-10 specimen/time source metadata changed")
    geo=pd.read_csv(io.BytesIO(checked_member(a.original88_geography_zip,
                              ORIGINAL88_GEO_MEMBER,ORIGINAL88_GEO_SHA)))
    geo=geo.loc[geo.radius_km.eq(100)].copy()
    if len(geo)!=88 or geo.site_id.nunique()!=88:
        raise ValueError("Exactly original88 geolocated study sites not recovered")
    old=pd.read_csv(io.BytesIO(checked_member(a.original860_zip,
                            ORIGINAL860_ISO_MEMBER,ORIGINAL860_ISO_SHA)),
                   usecols=["site_id","season"])
    if len(old)!=860 or old.site_id.nunique()!=88:
        raise ValueError("Old source 860 support membership drift")
    old_pairs=set(zip(old.site_id,old.season))
    geod=Geod(ellps="WGS84")
    records=[]
    for (site,year),f in aa.groupby(["Site","Year_collected"]):
        locations=f[["Latitude","Longitude","Coordinate_source"]].drop_duplicates()
        for _,loc in locations.iterrows():
            opts=[]
            for _,v in geo.iterrows():
                _,_,meters=geod.inv(float(loc.Longitude),float(loc.Latitude),
                                   float(v.colony_lon),float(v.colony_lat))
                opts.append((float(meters)/1000,str(v.site_id),str(v.source_region),
                             float(v.colony_lat),float(v.colony_lon)))
            opts.sort()
            best=opts[0]
            records.append(dict(
                AA_Source_Site=str(site),
                AA_Year_collected_not_moult=int(year),
                n_source_feather_samples=int(len(f)),
                AA_recorded_lat=float(loc.Latitude),
                AA_recorded_lon=float(loc.Longitude),
                AA_geo_reference=str(loc.Coordinate_source),
                original88_nearest_site_id=best[1],
                original88_nearest_region=best[2],
                source_geodesic_km=round(best[0],6),
                same_geographic_point_within_2km=best[0]<=2,
                same_geographic_vicinity_within_10km=best[0]<=10,
                same_geographic_vicinity_within_25km=best[0]<=25,
                source_original860_nearest_site_has_record_in_same_collection_year=
                   (best[1],int(year)) in old_pairs))
    out=pd.DataFrame(records).sort_values(
        ["AA_Source_Site","AA_Year_collected_not_moult","source_geodesic_km"])
    a.out.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.out/"USAP602094_2004_2010_source_geo_nearest_original88_NO_Y.csv",index=False)
    unique=out.drop_duplicates(["AA_Source_Site","AA_Year_collected_not_moult"])
    result={
       "status":"NO_ORIGINAL88_SAME_COLONY_25KM_AA_SITE_SOURCE_SUPPORT_BEFORE_Y",
       "publisher_AA_CSV_MD5":PUBLISHED_AA_MD5,
       "original88_source_artifact_sha256":ORIGINAL88_GEO_SHA,
       "original860_source_artifact_sha256":ORIGINAL860_ISO_SHA,
       "original_AA_2004_10_complete_feather_individuals":int(len(aa)),
       "source_AA_distinct_site_collection_years":int(aa.groupby(["Site","Year_collected"]).ngroups),
       "source_AA_unique_site_labels":int(aa.Site.nunique()),
       "source_88_original_site_ids":len(geo),
       "source_nearest_distance_min_km":float(out.source_geodesic_km.min()),
       "source_nearest_distance_max_km":float(out.source_geodesic_km.max()),
       "AA_site_collection_years_within_2km":int(unique.same_geographic_point_within_2km.sum()),
       "AA_site_collection_years_within_10km":int(unique.same_geographic_vicinity_within_10km.sum()),
       "AA_site_collection_years_within_25km":int(unique.same_geographic_vicinity_within_25km.sum()),
       "nearest_old_source_site_had_year_record_but_not_spatially_same":int(
          out.source_original860_nearest_site_has_record_in_same_collection_year.sum()),
       "no_isotope_or_trophic_position_numbers_opened":True,
       "no_new_or_old_polynya_effect_fit":True,
       "feather_collection_year_NOT_feather_synthesis_year":True,
       "old_guano_pixel_center_not_exact_feather_collection_colony":True
    }
    (a.out/"USAP602094_2004_10_original88_source_geography_verdict.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--aa-zip",type=Path,required=True)
    p.add_argument("--original88-geography-zip",type=Path,required=True)
    p.add_argument("--original860-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
