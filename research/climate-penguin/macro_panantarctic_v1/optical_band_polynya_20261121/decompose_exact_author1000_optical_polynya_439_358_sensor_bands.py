#!/usr/bin/env python3
"""Measurement-equation attribution, NOT newly tested environmental mechanism.

Same exact 860 source pixels/439 P/358 P0-P1; 21 sensor intercept/band features
from previously frozen Youngflesh 103 guano R1000 PLSR L4/5/7 coefficients.
The 21 signed contributions SUM to the existing environmental regression beta.
No changing site/season/exposure/controls; no new 2013+ Y; no causal claim.
"""
from __future__ import annotations
import argparse,importlib.util,io,json,hashlib,zipfile
from pathlib import Path
import numpy as np,pandas as pd

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/"author_isotope_polynya_sensitivity_20261121"
SOURCE_FILE=SRC/"compare_fixed_439_polynya_358_temporal_with_author_1000_PLSR_ensemble.py"
PRIOR_ARTIFACT_SHA="be0234fef11a11b5b19129c8a84db0ab90dbe80b7cd6a71a3e733e36eaa1e342"
SOURCE_PREVIOUS_Y_MEMBER="old439_358_new_Y_method_sensitivity/original_860_same_source_old_single_vs_author_R1000_PLSR_optical_Y.csv"
PRIOR_RESULTS={
  "M_P":-1.02334031992733,
  "M_SP":-0.9411358938647068,
  "P0_minus_P1":-0.6932686855748454,
}

def prior_zip_member(path,member):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=PRIOR_ARTIFACT_SHA:
        raise ValueError("Original author-ensemble successful output SHA drift")
    with zipfile.ZipFile(path) as z:
        if z.testzip():raise ValueError("Prior output archive ZIP member CRC failure")
        if member not in z.namelist():raise ValueError("Original same 860 source Y member missing")
        return pd.read_csv(io.BytesIO(z.read(member)))

def load_fixed_module():
    spec=importlib.util.spec_from_file_location("authorfixed",SOURCE_FILE)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def contribution(data,z,columns,c,model_columns,vector,group_label,module):
    # x and z projected with exactly the same site×region-year FE as previously
    # fitted; baseline 439 and 358 fits have already been frozen.
    x=module.demean_two_fe(data[model_columns].to_numpy(float),data)
    if np.linalg.matrix_rank(x)!=len(model_columns):
        raise ValueError("Original frozen environmental model design not full rank")
    Z=module.demean_two_fe(z,data)
    projection=np.linalg.lstsq(x,Z,rcond=None)[0]
    beta_features=0.1*np.asarray(vector@projection,float)
    if beta_features.shape!=(21,):raise ValueError("Expected 21 sensor/band environmental coefficients")
    b=np.asarray(c.mean(axis=1),float)
    per_feature=beta_features*b
    ensembles=beta_features@c
    point=float(per_feature.sum())
    if abs(point-float(np.mean(ensembles)))>1e-9:
        raise ValueError("Original 1000 ensemble additive coefficients do not sum")
    rec=[]
    for index,name in enumerate(columns):
        sensor,band=name.split("_",1)
        rec.append({"model":group_label,"sensor":sensor,"spectral_component":band,
            "frozen_source_feature":name,
            "mean_author_PLSR1000_lab_coefficient":float(b[index]),
            "original_FE_residualized_predictor_band_beta_per_10pp":float(beta_features[index]),
            "additive_effect_beta_per_10pp_‰":float(per_feature[index])})
    groups=[]
    for band in ["intercept","B1","B2","B3","B4","B5","B7"]:
        s=sum(r["additive_effect_beta_per_10pp_‰"] for r in rec if r["spectral_component"]==band)
        groups.append({"model":group_label,"spectral_component":band,
            "sum_across_all_three_original_Landsat_sensors_beta_per_10pp_‰":float(s)})
    return point,rec,groups,{
       "model":group_label,"beta_sum_all_21_sensor_band_components_per_10pp_‰":point,
       "expected_original_author_R1000_same_observations_beta":PRIOR_RESULTS[group_label],
       "aggregation_exact_within_tolerance":bool(abs(point-PRIOR_RESULTS[group_label])<1e-6),
       "calibration_only_1000_signed_2p5_97p5":np.quantile(ensembles,[.025,.975]).tolist(),
       "calibration_only_1000_fraction_negative":float(np.mean(ensembles<0)),
       "large_opposing_spectral_contributions_possible":True,
       "band_sum_is_linear_measurement_identity_not_independent_causal_effect":True}

def main(a):
    if not (HERE/"FROZEN_SAME_439_358_AUTHOR_PLSR_BAND_ATTRIBUTION_JA.md").is_file():
        raise ValueError("Prespecified historical diagnostic contract missing")
    m=load_fixed_module()
    old,pix=m.source(a)
    coeff=m.coeffs(a)
    features,columns=m.pixel_to_season_linear_source(pix,old)
    assert len(columns)==21
    join=old.merge(features[["site_id","season"]+columns],on=["site_id","season"],validate="one_to_one")
    if len(join)!=860:raise ValueError("Source 860 original site-season membership drift")
    join[m.Y_NEW]=join[columns].to_numpy(float)@coeff.mean(axis=1)
    previous=prior_zip_member(a.prior_author_sensitivity_zip,SOURCE_PREVIOUS_Y_MEMBER)
    check=join.merge(previous[["site_id","season",m.Y_NEW]],on=["site_id","season"],
        validate="one_to_one",suffixes=("","_previous"))
    if len(check)!=860 or np.max(abs(check[m.Y_NEW]-check[m.Y_NEW+"_previous"]))>1e-9:
        raise ValueError("Original author R1000 860 Y not exactly reproduced from source selected pixel bands")
    d=join.loc[join[m.P].notna()].copy().reset_index(drop=True)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(439,85,11):
        raise ValueError("Original 439 site-season fixed support drift")
    d["region_year"]=d.source_region+"__"+d.season.astype(str)
    z439=d[columns].to_numpy(float)
    effects=[];bands=[];models=[]
    for name,feature_list in [("M_P",m.BASE+[m.P]),("M_SP",m.BASE+[m.SAL,m.P])]:
        v=np.zeros(len(feature_list));v[-1]=1
        val,df,grp,md=contribution(d,z439,columns,coeff,feature_list,v,name,m)
        if not md["aggregation_exact_within_tolerance"]:raise ValueError("Existing 439 P betas drift")
        effects.extend(df);bands.extend(grp);models.append(md)
    temporal=pd.read_csv(a.temporal_fixed_358)
    if (len(temporal),temporal.site_id.nunique(),temporal.source_region.nunique())!=(358,85,11):
        raise ValueError("Prior P0/P1 temporal 358 original data changed")
    dt=temporal.merge(features[["site_id","season"]+columns],
        on=["site_id","season"],validate="one_to_one")
    if len(dt)!=358 or dt.duplicated(["site_id","season"]).any():
        raise ValueError("Temporal 358 exact support mismatch")
    dt["region_year"]=dt.source_region+"__"+dt.season.astype(str)
    cols=m.TEMPERATURE_TIME_BASE+["P0","P1"]
    vec=np.zeros(len(cols));vec[-2:]=[1.,-1.]
    val,df,grp,md=contribution(dt,dt[columns].to_numpy(float),columns,coeff,cols,vec,"P0_minus_P1",m)
    if not md["aggregation_exact_within_tolerance"]:raise ValueError("Existing placebo P0-P1 beta drift")
    effects.extend(df);bands.extend(grp);models.append(md)
    a.out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(effects).to_csv(a.out/"ORIGINAL439_358_21_SENSORS_BANDS_ADDITIVE_1000_R_PLSR_BETA_ATTRIBUTION.csv",index=False)
    pd.DataFrame(bands).to_csv(a.out/"ORIGINAL439_358_7_BAND_GROUP_SIGNED_BETA_ATTRIBUTION.csv",index=False)
    summary={
       "status":"ORIGINAL_SAME_439_358_AUTHOR_R1000_OPTICAL_BAND_ATTRIBUTION_COMPUTED_NOT_INDEPENDENT_ECOLOGY",
       "source_original_860_pixel_total":int(old.n_source_pixels.sum()),
       "source_original_observed_days":int(old.n_observed_days.sum()),
       "source_original_sites":88,
       "source_actual_439_site_seasons":len(d),
       "source_actual_358_temporal_site_seasons":len(dt),
       "original_source_sensors":[4,5,7],
       "published_author_source_103_lab_specimen_folds":1000,
       "source_R1000_preregistered_measurement_method_reproduced":True,
       "same_860_original_author_Y_exact_to_previous_saved_output":True,
       "original_preregistered_band_attribution_results":models,
       "Landsat_original_lab_1000_ensemble_weights_same_as_previous":True,
       "sensor_intercept_and_each_spectral_band_kept_separate":True,
       "interpretation_is_an_algebraic_measurement_decomposition_only":True,
       "no_2013_2021_new_OLI_or_current_guano_Y":True,
       "no_independent_baseline_corrected_amino_acid_TP":True,
       "no_separate_measured_krill_or_POM_isotope":True,
       "no_candidate_band_removed_or_selected_by_effect_direction":True
    }
    (a.out/"AUTHOR_R1000_SAME_439_358_OPTICAL_BAND_ATTRIBUTION_RECEIPT.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":summary["status"],
       "models":models,"grouped_band_contributions":bands,
       "source_860_same_Y_exact":True,
       "measured_separate_amino_acid_TP":False},indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--old-isotope-zip",type=Path,required=True)
    p.add_argument("--old-physical-zip",type=Path,required=True)
    p.add_argument("--original-l7-coefficients-zip",type=Path,required=True)
    p.add_argument("--original-pixels",type=Path,required=True)
    p.add_argument("--coefficients-dir",type=Path,required=True)
    p.add_argument("--prior-author-sensitivity-zip",type=Path,required=True)
    p.add_argument("--temporal-fixed-358",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
