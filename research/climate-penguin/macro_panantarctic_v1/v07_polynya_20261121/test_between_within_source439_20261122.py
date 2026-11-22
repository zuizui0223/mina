#!/usr/bin/env python3
"""Previously frozen 439 same-source between/within colony polynya audit.

Design: FROZEN_SCALE_BETWEEN_WITHIN_COLONY_TEST_20261122_JA.md.
The already-known site-FE slope is repeated for comparison, NOT independent
replication. Between-site: equal source-site means, no pseudoreplicated years.
No new radius, lag, outcome, geographic subset or causal model.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import verify_frozen_polynya_results as src

HERE=Path(__file__).resolve().parent
P=src.POLYNYA
Y=src.Y_OLD
Y1000=src.Y_AUTHOR
REGION=src.REGION
LAT="colony_lat"
YEAR="observed_season_mean"
CONTROL=list(src.BASE)+[YEAR,LAT]


def close(x,y,label,tol=1e-7):
    if abs(float(x)-float(y))>tol:
        raise ValueError(f"{label} changed: {x}, expected {y}")


def source_panel():
    iso, physical, auth, _, _, _, gate, rec=src.read_sources(
        HERE/"frozen_archives",HERE/"verification_inputs/matched_temporal358.csv")
    assert len(iso)==len(physical)==len(auth)==860
    d=iso.merge(physical[src.KEYS+[REGION,P]],on=src.KEYS,
                suffixes=("","_physical"),validate="one_to_one")
    assert d[REGION].equals(d[REGION+"_physical"])
    d=d.merge(auth[src.KEYS+[Y1000]],on=src.KEYS,validate="one_to_one")
    d=d[d[P].notna()].reset_index(drop=True)
    assert (len(d),d.site_id.nunique(),d[REGION].nunique())==(439,85,11)
    assert d.season.between(2004,2010).all()
    geo=pd.read_csv(HERE/"source_inputs/colony_geography.csv",
                    dtype={"site_id":str})
    geo=geo.loc[geo.radius_km.eq(100),["site_id",REGION,LAT]]
    assert len(geo)==88 and not geo.site_id.duplicated().any()
    d=d.merge(geo.rename(columns={REGION:"geo_region"}),on="site_id",
              validate="many_to_one")
    assert d[REGION].equals(d.geo_region)
    assert d[LAT].between(-90,-55).all()
    return d,{k:v["sha256"] for k,v in rec.items() if k.endswith(".zip")}


def collapse(d):
    fields=[Y,Y1000,P]+list(src.BASE)
    grouped=d.groupby(["site_id",REGION],sort=True)
    x=grouped[fields].mean().reset_index()
    x[YEAR]=grouped.season.mean().to_numpy()
    x["n_years"]=grouped.season.nunique().to_numpy()
    coords=grouped[LAT].first().reset_index()
    x=x.merge(coords,on=["site_id",REGION],validate="one_to_one")
    assert x.n_years.sum()==len(d)
    assert len(x)==85 and x.n_years.min()>=2
    return x


def fit(data,response,controls=(),region=True):
    y=data[response].to_numpy(float);p=data[P].to_numpy(float)
    d=pd.get_dummies(data[REGION].astype(str),dtype=float).to_numpy() if region else np.ones((len(data),1))
    for col in controls:
        v=data[col].to_numpy(float);sd=v.std(ddof=0)
        if sd<1e-12: raise ValueError(f"Fixed control has no variation: {col}")
        d=np.column_stack([d,(v-v.mean())/sd])
    p0=p-d@np.linalg.lstsq(d,p,rcond=1e-12)[0]
    y0=y-d@np.linalg.lstsq(d,y,rcond=1e-12)[0]
    if p0@p0<1e-16: raise ValueError("No source-site exposure support")
    beta=.1*float(p0@y0/(p0@p0))
    mat=np.column_stack([d,p])
    if np.linalg.matrix_rank(mat)!=mat.shape[1]:
        raise ValueError("Source-site model rank deficient; do not change formula")
    regSS={k:float((p0[data[REGION].eq(k).to_numpy()]**2).sum())
           for k in sorted(data[REGION].unique())}
    return {"beta_per_10pp_mil":beta,"n_sites":len(data),
            "n_reporting_regions":int(data[REGION].nunique()),
            "region_exposure_residual_ss":regSS,
            "condition_number":float(np.linalg.cond(mat)),
            "source_mean_polynya_range_pp":[float(p.min()*100),float(p.max()*100)],
            "controls":list(controls),"region_fixed_effects":region}


def fit_jackknife(data,response):
    full=fit(data,response,CONTROL)
    info=[k for k,ss in full["region_exposure_residual_ss"].items() if ss>1e-14]
    g=len(info)
    assert g==8,("Source region support drift",info)
    omissions=[]
    for reg in info:
        q=fit(data[data[REGION].ne(reg)],response,CONTROL)
        omissions.append({"region_removed":reg,"beta_per_10pp_mil":q["beta_per_10pp_mil"],
                          "n_sites":q["n_sites"]})
    b=full["beta_per_10pp_mil"]
    se=float(np.sqrt((g-1)/g*sum((z["beta_per_10pp_mil"]-b)**2 for z in omissions)))
    t=float(stats.t.ppf(.975,g-1))
    return {"full":full,"informative_regions":info,
            "n_informative_regions":g,
            "CV3_t7_95_interval":[b-t*se,b+t*se],
            "SE":se,"leave_region":omissions,
            "all_region_omission_positive":all(z["beta_per_10pp_mil"]>0 for z in omissions)}


def main():
    d,source_hashes=source_panel()
    sites=collapse(d)
    # Independently reproduce the exact existing site-FE+region-season
    # covariate slope rather than silently calling a separate response.
    fixed=src.FixedEffectProjection(d)
    prior=src.fit_frozen(d,src.MODEL_FEATURES["M_P"],Y,fixed)
    within=prior["polynya_per_10pp"]["estimate"]
    close(within,-1.0031091429244874,"Original frozen within")
    raw=fit(sites,Y,region=False)
    raw_region=fit(sites,Y,region=True)
    b1=fit_jackknife(sites,Y)
    b1cal=fit_jackknife(sites,Y1000)
    three=fit_jackknife(sites[sites.n_years>=3],Y)
    # B2 uses within-reporting-region×season centred raw variables
    # before computing equal-site means; geography and observed years
    # remain unchanged. Predefined coverage/calendar sensitivity.
    adjusted=d.copy()
    for col in [Y,Y1000,P]+list(src.BASE):
        adjusted[col]=adjusted[col]-adjusted.groupby([REGION,"season"])[col].transform("mean")
    standardized=collapse(adjusted)
    b2=fit_jackknife(standardized,Y)
    b2cal=fit_jackknife(standardized,Y1000)
    expected={
        "raw":(-.3187364003608803,raw["beta_per_10pp_mil"]),
        "region_only":(-.7947878035418499,raw_region["beta_per_10pp_mil"]),
        "B1":(-1.2947173494451913,b1["full"]["beta_per_10pp_mil"]),
        "B1_R1000":(-1.3102328482829049,b1cal["full"]["beta_per_10pp_mil"]),
        "B1_3plus":(-1.2555785728781161,three["full"]["beta_per_10pp_mil"]),
        "B2":(-1.2628804975755514,b2["full"]["beta_per_10pp_mil"]),
        "B2_R1000":(-1.279834888762967,b2cal["full"]["beta_per_10pp_mil"]),
    }
    for k,(reference,value) in expected.items():close(value,reference,k)
    conditions={
        "original_within_negative":within<0,
        "B1_between_positive":b1["full"]["beta_per_10pp_mil"]>0,
        "B1_CV3_interval_above_zero":b1["CV3_t7_95_interval"][0]>0,
        "B1_all_region_omissions_positive":b1["all_region_omission_positive"],
        "B1_observed_at_least_three_years_positive":three["full"]["beta_per_10pp_mil"]>0,
        "B2_regionseason_standardized_positive":b2["full"]["beta_per_10pp_mil"]>0,
    }
    verdict=("CONDITIONAL_SCALE_INVERSION_ONLY" if all(conditions.values())
             else "NO_GO_BETWEEN_VS_WITHIN_SIGN_INVERSION")
    out={
        "status":"PASS_SOURCE_LOCKED_439_BETWEEN_WITHIN_COMPARISON",
        "design_freeze":"FROZEN_SCALE_BETWEEN_WITHIN_COLONY_TEST_20261122_JA.md",
        "source_zip_sha256":source_hashes,
        "original": {"records":len(d),"sites":len(sites),"nominal_regions":11,
                     "year_counts":{str(a):int(n) for a,n in sites.n_years.value_counts().sort_index().items()},
                     "sites_three_or_more":int((sites.n_years>=3).sum()),
                     "site_latitude_minmax":[float(sites[LAT].min()),float(sites[LAT].max())],
                     "sites_per_region":{k:int(n) for k,n in sites[REGION].value_counts().sort_index().items()}},
        "within_frozen_site_FE_beta_per_10pp_mil":within,
        "B0_raw":raw,"B0_region_FE":raw_region,
        "B1_primary":b1,"B1_author_R1000":b1cal,
        "B1_at_least_three_years":three,
        "B2_regionseason_standardized":b2,
        "B2_R1000":b2cal,
        "predeclared_inversion_gates":conditions,
        "verdict":verdict,
        "published_Reaves_chick_bone_is_not_same_estimand":True,
        "no_causal_or_prey_switching_claim":True,
        "no_new_radius_or_lag_hypothesis_selection":True,
        "same_source_not_independent_ecological_replication":True,
        "warning":"Small number of unequal source regions; between-site means have unequal observation years, and measured proxy may vary with prey isotope baseline. No population or experimental inference."
    }
    output=HERE/"BETWEEN_WITHIN_POLYNYA_ORIGINAL439_EXACT_RESULT_20261122.json"
    output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"verdict":verdict,
        "within":within,"raw":raw["beta_per_10pp_mil"],
        "region_FE":raw_region["beta_per_10pp_mil"],
        "B1":b1["full"]["beta_per_10pp_mil"],
        "B1_CV3_95":b1["CV3_t7_95_interval"],
        "B1_calibrated":b1cal["full"]["beta_per_10pp_mil"],
        "B1_3plus":three["full"]["beta_per_10pp_mil"],
        "B2":b2["full"]["beta_per_10pp_mil"],
        "source_panel":out["original"],
        "gates":conditions},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
