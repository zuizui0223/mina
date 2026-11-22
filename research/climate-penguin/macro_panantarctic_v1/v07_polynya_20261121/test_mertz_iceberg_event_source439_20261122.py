#!/usr/bin/env python3
"""2010 Mertz/B-09B event, outcome-blind geographies and years frozen before Y.

Uses the original 439 historical same-source optical and 100-km polynya panel.
No new independent penguin diet samples. Every control and treated site ID, and
the 2006-09 baseline / 2010 single post year, is fixed by the companion design.
No p-values are computed or implied by the DiD bookkeeping.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import verify_frozen_polynya_results as source

HERE=Path(__file__).resolve().parent
GEO=HERE/"source_inputs/colony_geography.csv"
FROZEN=HERE/"FROZEN_MERTZ_2010_ICEBERG_EVENT_BIOLOGICAL_GATE_20261122_JA.md"
P=source.POLYNYA
Y=source.Y_OLD
Y1000=source.Y_AUTHOR
TREATED={"BIEN","CHUN","CURZ","DENI","JULE","MACK","PGEO","PIGE","PMAR","WATT"}
CONTROL={"ADAR","ARTH","CHAL","CHAP","COTT","DAVI","DOWN","DUKE",
         "HBAY","HOLL","MALL","MIDG","ODBE","PISL","POSS","SHLY","SVEN","WHTY"}
YRS=set(range(2006,2011))


def near(actual,expected,label,precision=1e-9):
    if abs(float(actual)-float(expected))>precision:
        raise ValueError(f"{label}: {actual} != pinned {expected}")


def inputs():
    assert FROZEN.is_file()
    iso,phy,auth,_,_,_,_,receipts=source.read_sources(
        HERE/"frozen_archives",HERE/"verification_inputs/matched_temporal358.csv")
    src_geo=pd.read_csv(GEO,dtype={"site_id":str})
    src_geo=src_geo.loc[src_geo.radius_km.eq(100),
                        ["site_id","colony_lat","colony_lon"]]
    assert len(src_geo)==88 and src_geo.site_id.nunique()==88
    d=iso.merge(phy[["site_id","season",P]],on=["site_id","season"],
                validate="one_to_one")
    d=d.merge(auth[["site_id","season",Y1000]],on=["site_id","season"],
              validate="one_to_one").dropna(subset=[P])
    assert (len(d),d.site_id.nunique(),d.source_region.nunique())==(439,85,11)
    d=d.merge(src_geo,on="site_id",validate="many_to_one")
    d=d.loc[d.season.isin(YRS)].copy()
    year_counts=d.groupby("site_id").season.nunique()
    d=d.loc[d.site_id.isin(year_counts[year_counts.eq(5)].index)].copy()
    treated=d.colony_lat.between(-70,-65)&d.colony_lon.between(139,146)
    control=d.colony_lat.between(-73,-65)&d.colony_lon.between(100,180)&~d.colony_lon.between(135,150)
    d=d.loc[treated|control].copy()
    d["treated"]=d.site_id.isin(TREATED).astype(int)
    assert set(d.loc[d.treated.eq(1),"site_id"])==TREATED
    assert set(d.loc[d.treated.eq(0),"site_id"])==CONTROL
    assert len(d)==140 and d.groupby("site_id").season.nunique().eq(5).all()
    assert d.groupby(["site_id","season"]).size().eq(1).all()
    d["control_band"]=np.where(
        d.treated.eq(1),"Mertz",
        np.where(d.colony_lon.le(135),"western_100_135E","eastern_150_180E"))
    return d.sort_values(["site_id","season"]).reset_index(drop=True),{
        k:val["sha256"] for k,val in receipts.items() if k.endswith(".zip")}


def groups(df,response):
    means=df.groupby(["season","treated"])[response].mean().unstack("treated")
    assert means.shape==(5,2) and set(means.columns)=={0,1}
    diffs=means[1]-means[0]
    p0=diffs.loc[2006:2009]
    did=float(diffs.loc[2010]-p0.mean())
    placebo={str(yr):float(p0.loc[yr]-p0.drop(yr).mean()) for yr in range(2006,2010)}
    prepost={}
    for k,label in [(0,"controls"),(1,"treated")]:
        pre=float(means.loc[2006:2009,k].mean())
        post=float(means.loc[2010,k])
        prepost[label]={"pre_mean":pre,"post_2010":post,"post_minus_pre":post-pre}
    return {
        "difference_in_differences":did,
        "yearly_group_means":{
            str(year):{"treated":float(means.loc[year,1]),"control":float(means.loc[year,0]),
                       "treated_minus_control":float(diffs.loc[year])}
            for year in range(2006,2011)},
        "group_pre_post":prepost,
        "pre_event_pseudo_year_placebos":placebo,
        "2010_abs_exceeds_every_preyear_placebo":
            abs(did)>max(abs(v) for v in placebo.values()),
    }


def matched_region_tests(df,response):
    data={}
    for reg in ["Victoria Land","Wilkes Land"]:
        panel=df.loc[df.source_region.eq(reg)]
        sites={str(i):int(z.site_id.nunique()) for i,z in panel.groupby("treated")}
        assert sites.keys()=={"0","1"}
        data[reg]={"sites":sites,"result":groups(panel,response)}
    return data


def band_controls(df,response):
    z={}
    for band in ["western_100_135E","eastern_150_180E"]:
        subset=df.loc[df.treated.eq(1)|df.control_band.eq(band)]
        z[band]={"control_sites":int(subset.loc[subset.treated.eq(0),"site_id"].nunique()),
                 "result":groups(subset,response)}
    return z


def twoway_fe(df,response,added=()):
    data=df.sort_values(["site_id","season"]).reset_index(drop=True)
    site=pd.get_dummies(data.site_id,dtype=float,drop_first=True).to_numpy()
    yr=pd.get_dummies(data.season.astype(str),dtype=float,drop_first=True).to_numpy()
    one=np.ones((len(data),1))
    event=(data.treated*data.season.eq(2010)).to_numpy(float).reshape(-1,1)
    X=np.column_stack([one,site,yr,event])
    if added:
        c=data[list(added)].to_numpy(float)
        sd=c.std(axis=0)
        if not np.all(sd>1e-12):raise ValueError("Control has constant column")
        X=np.column_stack([X,(c-c.mean(axis=0))/sd])
    rank=int(np.linalg.matrix_rank(X))
    if rank!=X.shape[1]:raise ValueError("Two-way FE design lost rank")
    beta=np.linalg.lstsq(X,data[response].to_numpy(float),rcond=1e-11)[0]
    return {"event_treated_x_2010_coefficient":float(beta[1+site.shape[1]+yr.shape[1]]),
            "n":len(data),"site_intercepts":site.shape[1]+1,
            "year_effects":yr.shape[1]+1,"rank":rank,"controls":list(added),
            "not_a_causal_treatment_effect":True}


def main(outdir):
    d,hashes=inputs()
    Pstats=groups(d,P)
    Ystats=groups(d,Y)
    Rstats=groups(d,Y1000)
    near(Pstats["difference_in_differences"]*100,-5.551313910139313,"Physical shock in percentage points",1e-8)
    near(Ystats["difference_in_differences"],-.554639781229934,"Optical Y DiD",1e-8)
    near(Rstats["difference_in_differences"],-.5450154012291886,"R1000 Y DiD",1e-8)
    regionP=matched_region_tests(d,P)
    regionY=matched_region_tests(d,Y)
    regionR=matched_region_tests(d,Y1000)
    bY=band_controls(d,Y)
    bP=band_controls(d,P)
    model={name:{
        "original_Y":twoway_fe(d,Y,fields),
        "author_R1000_Y":twoway_fe(d,Y1000,fields),
        "winter_P":twoway_fe(d,P,fields)
      } for name,fields in [
         ("site_year_FE_only",()),
         ("add_original_summer_and_image_date_controls",tuple(source.BASE)),
         ("add_summer_salinity_also",tuple(source.BASE)+ (source.SALINITY,))
      ]}
    near(model["site_year_FE_only"]["original_Y"]["event_treated_x_2010_coefficient"],
         Ystats["difference_in_differences"],"TWFE matches balanced raw did")
    gates={
      "physical_polynya_contraction":Pstats["difference_in_differences"]<0,
      "physical_2010_exceeds_preyear_placebo":Pstats["2010_abs_exceeds_every_preyear_placebo"],
      "original_optical_Y_increases":Ystats["difference_in_differences"]>0,
      "R1000_optical_Y_increases":Rstats["difference_in_differences"]>0,
      "both_matched_source_regions_original_Y_increase":
          all(regionY[reg]["result"]["difference_in_differences"]>0
              for reg in regionY),
      "original_Y_2010_exceeds_preyear_placebo":
          Ystats["2010_abs_exceeds_every_preyear_placebo"]
    }
    status="DESCRIPTIVE_EVENT_SIGN_CONCORDANCE_ONLY" if all(gates.values()) else "NO_GO_EVENT_BIOLOGICAL_RESPONSE"
    d["post_2010"]=d.season.eq(2010)
    columns=["site_id","season","source_region","colony_lat","colony_lon",
             "source_wet_grid_x","source_wet_grid_y","treated","control_band",
             "post_2010",P,Y,Y1000,"n_observed_days","n_source_pixels",
             *source.BASE,source.SALINITY]
    outdir.mkdir(parents=True,exist_ok=True)
    table=outdir/"MERTZ2010_ORIGINAL28SITE_X_5YEAR_SOURCE_PANEL.csv"
    d[columns].to_csv(table,index=False,float_format="%.17g")
    baseline_checks={}
    for field in [Y,Y1000,P,source.SALINITY,
                  "author_SIC_150km_NovFeb_center_approx_fraction",
                  "GLORYS_NovFeb_thetao_C","n_observed_days","n_source_pixels"]:
        baseline_checks[field]=groups(d,field)
    report={
        "status":"PASS_FROZEN_MERTZ_EVENT_SOURCE_JOIN_AND_COMPLETE_YEAR_DESIGN",
        "frozen_design":"FROZEN_MERTZ_2010_ICEBERG_EVENT_BIOLOGICAL_GATE_20261122_JA.md",
        "event":"2010-02 iceberg B09B collision with Mertz glacier tongue; winter P June–October 2010; optical response Nov 2010–Feb 2011",
        "original_full_panel_size":439,"event_panel_rows":len(d),"event_years":[2006,2007,2008,2009,2010],
        "treated_site_ids":sorted(TREATED),"control_site_ids":sorted(CONTROL),
        "treated_sites":10,"control_sites":18,
        "n_unique_ocean_wet_cells_treated":int(d.loc[d.treated.eq(1),["source_wet_grid_y","source_wet_grid_x"]].drop_duplicates().shape[0]),
        "n_unique_ocean_wet_cells_control":int(d.loc[d.treated.eq(0),["source_wet_grid_y","source_wet_grid_x"]].drop_duplicates().shape[0]),
        "physical_first_stage":{"raw_fraction_units":Pstats,
            "percentage_points_did":Pstats["difference_in_differences"]*100},
        "biological_outcome_original_optical_proxy":Ystats,
        "biological_outcome_author_R1000_same_lab_and_pixels":Rstats,
        "region_matched_original_Y":regionY,
        "region_matched_R1000_Y":regionR,
        "region_matched_physical_P":regionP,
        "predefined_distant_control_band_Y":bY,
        "predefined_distant_control_band_P":bP,
        "site_year_FE_covariate_sensitivities":model,
        "original_process_and_summer_environment_confounding_diagnostics":baseline_checks,
        "predeclared_event_sign_gate":gates,
        "event_biological_status":status,
        "causal_mediation_or_independent_validation":"NO_GO_ALWAYS_THIS_DESIGN",
        "single_post_event_year":True,
        "post_winter_summer_covariates_are_not_preintervention_confounds":True,
        "source_zip_sha256":hashes,
        "warning":"Controls are geographically distant in two clusters, original 28 sites share only 26 unique wet cells, weather and changed ice access are simultaneous event channels, and observed 2006–09 placebo changes can be larger than the 2010 Y contrast. No statistical p value or causal instrument is identified.",
    }
    path=outdir/"MERTZ2010_ICEBERG_POLYNYA_OPTICAL_EVENT_GATE_RESULT.json"
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"Y_event_gate":status,
        "physical_DID_pp":report["physical_first_stage"]["percentage_points_did"],
        "Y_DID_per_mil":Ystats["difference_in_differences"],
        "R1000_Y_DID_per_mil":Rstats["difference_in_differences"],
        "preyear_Y_placebos":Ystats["pre_event_pseudo_year_placebos"],
        "by_region_Y":{k:val["result"]["difference_in_differences"] for k,val in regionY.items()},
        "covariate_adjusted_Y_event":{k:v["original_Y"]["event_treated_x_2010_coefficient"] for k,v in model.items()},
        "gate":gates,"rows":len(d)},indent=2,ensure_ascii=False))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",type=Path,default=HERE/"mertz_2010_event_outputs")
    args=ap.parse_args()
    main(args.out_dir)
