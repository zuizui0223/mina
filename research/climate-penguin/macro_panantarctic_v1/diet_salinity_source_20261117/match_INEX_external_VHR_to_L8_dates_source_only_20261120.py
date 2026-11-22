#!/usr/bin/env python3
"""Exact original source ID INEX VHR true guano-area dates vs L8 source scenes.
NOT true pixel labels, NOT L8 delta15N proxy, NOT a polynya association.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import pandas as pd

VHR_SHA="cbd2f443e88300caef449eb428e571d9123f77d47e5a1087f5e30f2afd9fcd2e"
L8_SHA="575dc514c6103b1aaefb0bce1bf7f5084aedc5d2c4edb3519d0ac03af82a2750"
VHR_CSV="independent_2013_2021_VHR_only_strict_original_site_years.csv"
L8_CSV="original_88_L8_real_scene_metadata_no_Y.csv"

def read_checked(zippath,sha,member):
    raw=Path(zippath).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("Pinned source ZIP checksum changed")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip():raise ValueError("Original ZIP source CRC failed")
        names=[n for n in z.namelist() if n==member or n.endswith("/"+member)]
        if len(names)!=1:raise ValueError("Original source member ambiguous")
        return pd.read_csv(io.BytesIO(z.read(names[0])))

def main(a):
    v=read_checked(a.vhr_zip,VHR_SHA,VHR_CSV)
    s=read_checked(a.scene_zip,L8_SHA,L8_CSV)
    if len(v)!=3 or set(v.Colony_code)!={"INEX"} or set(v.Season)!={2013,2017,2018}:
        raise ValueError("Independent VHR strict site-year source drift")
    s=s.loc[(s.site_id=="INEX")&(s.period=="new")].copy()
    s["true_source_day"]=pd.to_datetime(s.source_scene_datetime,utc=True).dt.tz_localize(None).dt.normalize()
    rows=[]
    for ref in v.sort_values("Season").itertuples(index=False):
        d=s.loc[s.season.eq(ref.Season)].copy()
        if d.empty:raise ValueError("New Landsat8 source dates missing at INEX")
        original_day=pd.to_datetime(str(int(ref.Date)),format="%Y%m%d")
        d["days_offset"]=(d.true_source_day-original_day).dt.days
        d["abs_days_offset"]=d.days_offset.abs()
        closest=d.sort_values(["abs_days_offset","source_scene_datetime","scene_id"]).iloc[0]
        eligible=d.loc[d.abs_days_offset.le(8)&d.eo_cloud_cover_scene_percent.notna()]
        if eligible.empty:raise ValueError("No original L8 scene within 8 days of VHR")
        leastcloud=eligible.sort_values(["eo_cloud_cover_scene_percent","abs_days_offset","scene_id"]).iloc[0]
        for rule,scene in (("nearest_date",closest),("lowest_cloud_within_8_days",leastcloud)):
            rows.append(dict(site_id="INEX",source_region="Victoria Land",season=int(ref.Season),
                VHR_observation_date=original_day.date().isoformat(),
                true_VHR_guano_area_m2=float(ref.Guano_area),
                source_L8_scene_id=str(scene.scene_id),
                source_L8_scene_date=scene.true_source_day.date().isoformat(),
                fixed_scene_rule=rule,day_offset=int(scene.days_offset),
                original_scene_overall_cloud_pct=float(scene.eo_cloud_cover_scene_percent),
                n_L8_candidates_this_site_season=int(len(d))))
    a.out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out/"INEX_three_independent_VHR_dates_L8_original_scene_source_only.csv",index=False)
    r=dict(status="INEX_EXACT_2013_2017_2018_L8_VHR_DATE_OVERLAP_SOURCE_ONLY",
      original_source_site="INEX",original_source_region="Victoria Land",
      exact_source_seasons=[2013,2017,2018],n_independent_sites=1,n_independent_regions=1,
      L8_date_matches=rows,VHR_area_not_pixel_level_guano_mask=True,
      L8_scene_presence_not_proof_guano_pixel_presence=True,
      no_future_isotope_proxy_computed=True,no_new_polynya_effect_fitted=True)
    (a.out/"INEX_2013_2017_2018_L8_VHR_SOURCE_DATE_GATE.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--vhr-zip",type=Path,required=True)
    p.add_argument("--scene-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
