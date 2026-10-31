"""Original macro 3-penguin nest growth matched to 1993-2020 GLORYS + OSI September.

Strict 10y single-method panel; no missing/unknown as zero. Descriptive macro r, rolling year
and simultaneously withheld site / native ocean-grid external validation. Never project
unvalidated future nest abundance.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs"
OUT = SOURCE / "historical_ocean_macro_v1"
MARINE_SHA256 = "a167b389f9c8e4ba7f18c886025b4abfe19c7b67000c675064f93ad4fb5aee42"
INPUTS = {
    "bio": ("comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"),
    "ice": ("climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"),
    "grid": ("climate_penguin/ocean_grid_support.csv","5d0f90cab39e192645b3ff3406a40349a0ff22d0"),
    "timing": ("climate_penguin/historical_count_season_timing.csv","02b240649e36533445690be9034469251659d0a2"),
    "cmip": ("cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"),
}
FEATURES = {
  "baseline": (),
  "SIC": ("sic_start_September_pct",),
  "SST_SSS": ("sst_start_September_c","sss_start_September"),
  "SIC_SST_SSS": ("sic_start_September_pct","sst_start_September_c","sss_start_September"),
}
MODELS = ("baseline","SIC","SST_SSS","SIC_SST_SSS")
MIN_TRAIN = 30
MIN_TRAIN_SITES = 5
PENALTY = {"species":5.,"site_species":8.,"year":5.,"climate":12.}

def frozen_csv(name):
    path, expected = INPUTS[name]
    raw = (SOURCE / path).read_bytes()
    sha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha != expected:
        raise ValueError("Frozen original input changed "+name+" "+sha)
    return pd.read_csv(SOURCE / path)

def check_unique(data, keys):
    if data.duplicated(keys).any():
        raise ValueError("Original repeated row at key "+"/".join(keys))

def val_is_true(x):
    return pd.notna(x) and bool(x)

def corr(a,b):
    a,b = np.asarray(a,float),np.asarray(b,float)
    if len(a)<3 or np.std(a)<1e-11 or np.std(b)<1e-11:
        return None
    return float(np.corrcoef(a,b)[0,1])

def residualize(frame,field,keys=("group","end_year")):
    dummy = []
    for name in keys:
        levels = sorted(frame[name].unique())
        dummy.extend((frame[name].to_numpy()==v).astype(float) for v in levels[1:])
    xx = np.column_stack([np.ones(len(frame))]+dummy)
    y = frame[field].to_numpy(float)
    return y - xx @ np.linalg.lstsq(xx,y,rcond=None)[0]

def fit_and_predict(train,test,model,groups):
    if train.empty or test.empty:
        raise ValueError("empty fold")
    def base(a):
        ss = a.species_id.to_numpy()
        grp = a.group.to_numpy()
        values = [np.ones(len(a)),(ss=="CHPE").astype(float),(ss=="GEPE").astype(float),
                  (a.end_year.to_numpy(float)-2000.)/10.]
        values.extend((grp==g).astype(float) for g in groups)
        return np.column_stack(values)
    x,xt = base(train),base(test)
    penalty = [0.,PENALTY["species"],PENALTY["species"],PENALTY["year"]]+[PENALTY["site_species"]]*len(groups)
    for f in FEATURES[model]:
        obs = train[f].to_numpy(float)
        center,sd=float(np.mean(obs)),max(float(np.std(obs)),1e-8)
        x=np.column_stack([x,(obs-center)/sd])
        xt=np.column_stack([xt,(test[f].to_numpy(float)-center)/sd])
        penalty.append(PENALTY["climate"])
    y=train.delta_log_nests.to_numpy(float)
    coef=np.linalg.solve(x.T@x+np.diag(penalty),x.T@y)
    return xt@coef

def holdouts(data,groups,strategy):
    out=[]
    for year in sorted(data.end_year.unique()):
        testing=data.loc[data.end_year==year]
        if testing.empty:
            continue
        sections = [testing] if strategy=="chronological" else [
            testing.loc[testing.cell_id==x] if strategy=="chronological_marine_cell_out" else testing.loc[testing.site_id==x]
            for x in sorted(testing.cell_id.unique() if strategy=="chronological_marine_cell_out" else testing.site_id.unique())
        ]
        for subset in sections:
            train=data.loc[data.end_year<year].copy()
            if strategy=="chronological_site_out":
                train=train.loc[train.site_id!=subset.site_id.iloc[0]]
            elif strategy=="chronological_marine_cell_out":
                train=train.loc[train.cell_id!=subset.cell_id.iloc[0]]
            if len(train)<MIN_TRAIN or train.site_id.nunique()<MIN_TRAIN_SITES:
                continue
            if int(train.end_year.max())>=int(year):
                raise ValueError("Future-year training leakage")
            fits={m:fit_and_predict(train,subset,m,groups) for m in MODELS}
            global_average=float(train.delta_log_nests.mean())
            for i, row in enumerate(subset.itertuples(index=False)):
                spec=train.loc[train.species_id==row.species_id,"delta_log_nests"]
                out.append({
                    "strategy":strategy,"site_id":row.site_id,"species_id":row.species_id,
                    "cell_id":row.cell_id,"end_year":year,
                    "training_interval_n":len(train),"training_site_n":train.site_id.nunique(),
                    "last_training_year":int(train.end_year.max()),
                    "target_log_nests_growth":float(row.delta_log_nests),
                    "predict_no_change":0.,
                    "predict_past_mean":global_average,
                    "predict_species_mean":float(spec.mean()) if len(spec) else global_average,
                    **{("predict_"+m):float(fits[m][i]) for m in MODELS},
                })
    return pd.DataFrame(out)

def score(data):
    out=[]
    for sp in ("ALL","ADPE","CHPE","GEPE"):
        a=data if sp=="ALL" else data.loc[data.species_id==sp]
        if not len(a):
            continue
        for m in ("no_change","past_mean","species_mean")+MODELS:
            diff=a["predict_"+m].to_numpy(float)-a.target_log_nests_growth.to_numpy(float)
            out.append({
              "strategy":a.strategy.iloc[0],"species":sp,"model":m,
              "intervals":len(a),"sites":a.site_id.nunique(),"marine_cells":a.cell_id.nunique(),
              "distinct_site_endyears":a[["site_id","end_year"]].drop_duplicates().shape[0],
              "mae":float(np.mean(np.abs(diff))),
              "rmse":float(np.sqrt(np.mean(diff*diff))),
              "mean_signed_error":float(np.mean(diff)),
            })
    return out

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    opath=OUT/"original_glorys_34sites_1993_2020_monthly.csv"
    if not opath.exists():
        raise ValueError("Missing newly acquired historical macro ocean")
    actual=hashlib.sha256(opath.read_bytes()).hexdigest()
    if actual!=MARINE_SHA256:
        raise ValueError("GLORYS new source does not match independently successful source SHA")
    ocean=pd.read_csv(opath)
    if len(ocean)!=3808 or ocean.site_id.nunique()!=34:
        raise ValueError("Macro ocean source size changed")
    bio=frozen_csv("bio")
    ice=frozen_csv("ice")
    grid=frozen_csv("grid")
    timing=frozen_csv("timing")
    cmip=frozen_csv("cmip")
    if len(bio)!=2999 or len(ice)!=9600:
        raise ValueError("Source cohort drift")
    macro=grid.loc[grid.cohort=="macro_40"]
    valid_sites=set(macro.loc[macro.grid_within_25km,"site_id"])
    if len(macro)!=40 or len(valid_sites)!=34:
        raise ValueError("Fixed marine-geo support has changed")
    check_unique(bio,["site_id","species_id","season","method"])
    check_unique(ocean,["site_id","year","month"])
    check_unique(ice,["site_id","year","month","inner_km"])
    check_unique(timing,["site_id","species_id","season","method"])
    assert set(ocean.site_id)==valid_sites
    sic9=ice.loc[(ice.month==9)&(ice.inner_km==0)&ice.complete_month].set_index(["site_id","year"])
    sea9=ocean.loc[ocean.month==9].set_index(["site_id","year"])
    tmap=timing.set_index(["site_id","species_id","season","method"])
    if set(timing.species_id)!={"ADPE"}:
        raise ValueError("Original timing audit has unexpectedly changed species scope")

    eligible=[]
    valid=bio.loc[bio.site_id.isin(set(macro.site_id))&
                  bio.species_id.isin(["ADPE","CHPE","GEPE"])&
                  bio.season.between(1991,2020)&bio["count"].notna()&
                  (bio["count"]>=0)&bio.method.ne("unknown")]
    for (site,sp), rows in valid.groupby(["site_id","species_id"]):
        methods=[]
        for method,one in rows.groupby("method"):
            one=one.sort_values("season")
            span=int(one.season.iloc[-1]-one.season.iloc[0])
            if len(one)>=4 and span>=10:
                methods.append((len(one),span,str(method),one))
        if not methods:
            continue
        methods.sort(key=lambda v:(-v[0],-v[1],v[2]))
        _,span,method,picked=methods[0]
        eligible.append((site,sp,method,picked))
    if len(eligible)!=54:
        raise ValueError("Previously fixed 54 long-series site×species count combinations drifted")
    records=[]
    for site,sp,method,one in eligible:
        rec=one.to_dict(orient="records")
        for left,right in zip(rec,rec[1:]):
            if int(right["season"])-int(left["season"])!=1:
                continue
            # Original confirmed positive-positive transitions: missing and zeros are never invented.
            if float(left["count"])<=0 or float(right["count"])<=0:
                continue
            x={
              "site_id":site,"species_id":sp,"region":str(left["region"]),
              "method":method,"group":site+"|"+sp,
              "start_year":int(left["season"]),"end_year":int(right["season"]),
              "n_start":float(left["count"]),"n_end":float(right["count"]),
              "delta_log_nests":float(np.log(float(right["count"])/float(left["count"]))),
              "within25km":site in valid_sites,
            }
            records.append(x)
    full=pd.DataFrame(records)
    if len(full)!=392:
        raise ValueError(f"Strict single-method positive-positive full cohort drift: {len(full)} vs 392")
    nearby=full.loc[full.within25km]
    if len(nearby)!=236:
        raise ValueError(f"Marine proximity support changed: {len(nearby)} vs 236")
    kept=[]
    for p in nearby.itertuples(index=False):
        key=(p.site_id,p.start_year)
        if key not in sea9.index or key not in sic9.index:
            continue
        marine=sea9.loc[key]
        si=sic9.loc[key]
        env={"sic_start_September_pct":float(si.sic_mean),
             "sst_start_September_c":float(marine.surface_potential_temperature_c),
             "sss_start_September":float(marine.surface_salinity)}
        if not np.all(np.isfinite(list(env.values()))):
            continue
        # Frozen month-support audit covers only ADPE (2011 onward).
        first=(p.site_id,p.species_id,p.start_year,p.method)
        second=(p.site_id,p.species_id,p.end_year,p.method)
        scoped=p.species_id=="ADPE" and first in tmap.index and second in tmap.index
        verified=bool(scoped and val_is_true(tmap.loc[first,"all_after_september"]) and val_is_true(tmap.loc[second,"all_after_september"]))
        cell=str(int(marine.grid_y))+":"+str(int(marine.grid_x))
        kept.append({**p._asdict(),**env,
             "cell_id":cell,"marine_grid_distance_km":float(marine.grid_distance_km),
             "month_audit_applicable":bool(scoped),
             "months_verified_after_september":verified})
    panel=pd.DataFrame(kept).sort_values(["end_year","site_id","species_id"]).reset_index(drop=True)
    if len(panel)!=216 or panel.site_id.nunique()!=26 or panel.group.nunique()!=39:
        raise ValueError("Unexpected 1993–2020 biological×marine macro support "+
                        str((len(panel),panel.site_id.nunique(),panel.group.nunique())))
    if panel.duplicated(["site_id","species_id","start_year","end_year"]).any():
        raise ValueError("Duplicated biological intervals")
    group_levels=sorted(panel.group.unique())
    panel.to_csv(OUT/"macro_original_breeding_ocean_intervals.csv",index=False)
    assoc=[]
    for species in ("ALL","ADPE","CHPE","GEPE"):
        subset=panel if species=="ALL" else panel.loc[panel.species_id==species]
        for field in ("sic_start_September_pct","sst_start_September_c","sss_start_September"):
            assoc.append({
              "species":species,"environment":field,"intervals":len(subset),
              "sites":subset.site_id.nunique(),"native_grid_cells":subset.cell_id.nunique(),
              "r_unadjusted":corr(subset[field],subset.delta_log_nests),
              "r_site_species_and_year_adjusted":corr(residualize(subset,field),residualize(subset,"delta_log_nests")),
              "interpretation":"exploratory_association_not_a_causal_effect",
            })
    pd.DataFrame(assoc).to_csv(OUT/"macro_historical_environment_correlations.csv",index=False)
    predictions=[]
    for strat in ("chronological","chronological_site_out","chronological_marine_cell_out"):
        q=holdouts(panel,group_levels,strat)
        if q.empty:
            raise ValueError("Insufficient conditional macro forecast support for "+strat)
        predictions.append(q)
    all_pred=pd.concat(predictions,ignore_index=True)
    all_pred.to_csv(OUT/"macro_all_temporal_holdout_predictions.csv",index=False)
    metrics=pd.DataFrame([r for q in predictions for r in score(q)])
    metrics.to_csv(OUT/"macro_holdout_metrics.csv",index=False)
    def get(st,m):
        a=metrics.loc[(metrics.strategy==st)&(metrics.species=="ALL")&(metrics.model==m)].iloc[0]
        return {"mae":float(a.mae),"rmse":float(a.rmse),"intervals":int(a.intervals),
                "sites":int(a.sites),"marine_cells":int(a.marine_cells)}
    cv={strat:{m:get(strat,m) for m in ("no_change","past_mean","species_mean")+MODELS}
        for strat in ("chronological","chronological_site_out","chronological_marine_cell_out")}
    sourceSites=sorted(set(panel.site_id))
    selected=cmip.loc[cmip.site_id.isin(sourceSites)&cmip.cohort.eq("macro_40")&
                      cmip.variable_id.isin(["siconc","tas","sos"])]
    if len(selected)!=len(sourceSites)*3*2*2*3:
        raise ValueError("26-site CMIP6 crosswalk not complete")
    climate=selected.groupby(["variable_id","experiment_id","period"],as_index=False).agg(
       sites=("site_id","nunique"),n_ocean_grid_or_land_rows=("change","size"),
       mean_change=("change","mean"),min_change=("change","min"),max_change=("change","max"))
    climate.to_csv(OUT/"macro_future_physical_climate_26sites.csv",index=False)
    # Pre-specified safety/transport gate: no outcome extrapolation without all.
    gate={
      "at_least_100_complete_original_intervals":len(panel)>=100,
      "at_least_15_biological_sites":panel.site_id.nunique()>=15,
      "at_least_30_verified_premeasurement_intervals_across_species":bool(panel.months_verified_after_september.sum()>=30 and panel.loc[panel.species_id!="ADPE","months_verified_after_september"].sum()>=10),
      "time_out_all_environment_better_than_baseline":cv["chronological"]["SIC_SST_SSS"]["mae"]<cv["chronological"]["baseline"]["mae"],
      "time_out_all_environment_better_than_SIC":cv["chronological"]["SIC_SST_SSS"]["mae"]<cv["chronological"]["SIC"]["mae"],
      "site_out_all_environment_better_than_baseline":cv["chronological_site_out"]["SIC_SST_SSS"]["mae"]<cv["chronological_site_out"]["baseline"]["mae"],
      "native_marine_cell_out_all_environment_better_than_baseline":cv["chronological_marine_cell_out"]["SIC_SST_SSS"]["mae"]<cv["chronological_marine_cell_out"]["baseline"]["mae"],
    }
    meta={
      "date":"2026-10-31","status":"original_three_species_macro_nest_growth_with_historical_seaice_and_glorys",
      "source":{name:sha for name,(_,sha) in INPUTS.items()}|{"macro_marine_csv_sha256":actual},
      "cohort":{
       "original_macro_sites":40,"marine_within25km_sites":34,
       "unmatched_far_marine_sites":sorted(set(macro.site_id)-valid_sites),
       "all_long_count_site_species":len(eligible),
       "strict_single_method_all_positive_positive_intervals":len(full),
       "strict_near_marine_intervals":len(nearby),
       "historical_1993_2020_complete_intervals":len(panel),
       "matched_site_species":panel.group.nunique(),"matched_site_codes":panel.site_id.nunique(),
       "matched_native_marine_cells":panel.cell_id.nunique(),
       "unique_site_start_years":panel[["site_id","start_year"]].drop_duplicates().shape[0],
       "species_intervals":{s:int(v) for s,v in panel.species_id.value_counts().items()},
       "eligible_2011on_ADPE_time_month_support":int(panel.month_audit_applicable.sum()),
       "verified_later_than_September_count_intervals":int(panel.months_verified_after_september.sum()),
       "timing_audit_scope":"existing dates audit covers ADPE only, 2011-2020; CHPE/GEPE date support unassessed",
      },
      "association":assoc,
      "prediction_metrics":cv,"model_specification":{
        "outcome":"log(nests_end / nests_start), known method positive-positive consecutive seasons",
        "features":"start-year September OSI near SIC and fixed GLORYS surface potential SST, salinity",
        "model_specs":FEATURES,"ridge_penalty":PENALTY,
        "min_earlier_training_intervals":MIN_TRAIN,"min_train_sites":MIN_TRAIN_SITES,
        "split":"training interval END-year strictly less than heldout END-year; optional exclude test site or native ocean grid",
        "missingness":"unknown count and unvisited sites never imputed as zero",
      },
      "future_physical_context_only":climate.to_dict("records"),
      "calibrated_future_nest_prediction_gate":gate,
      "calibrated_future_nest_prediction_permitted":all(gate.values()),
      "caveat":"Historical model/model-assimilation variables, same colony and native-grid dependence, missing timing for some species; no causal climate effect or calibrated 2050/2100 nest projection.",
    }
    (OUT/"macro_result.json").write_text(json.dumps(meta,indent=2,default=float)+"\n")
    summary={
      "cohort":meta["cohort"],
      "CV":cv,
      "associations":assoc,
      "gates":gate,
      "future_nesting_projection_allowed":meta["calibrated_future_nest_prediction_permitted"],
    }
    print("ORIGINAL MACRO BREEDING-OCEAN RESULT "+json.dumps(summary,default=float),flush=True)
    (OUT/"MACRO_REPORT_JA.md").write_text(
       "# 南極3種の繁殖数の長期マクロ解析：1993–2020年原海洋再解析の拡張\n\n"+
       f"元40地点・34近海洋地点のうち、54同一方法長期系列から正の巣数連続観測392区間、25km内236区間、1993–2020海洋一致 **{len(panel)}区間・{panel.site_id.nunique()}地点・{panel.cell_id.nunique()}海洋格子**。\n\n"+
       "## 時間順と未使用地点／海洋セルのMAE\n\n"+
       "| モデル | 年外 | 年外＋地点外 | 年外＋海洋格子外 |\n|---|---:|---:|---:|\n"+
       "".join(f"| {m} | {cv['chronological'][m]['mae']:.4f} | {cv['chronological_site_out'][m]['mae']:.4f} | {cv['chronological_marine_cell_out'][m]['mae']:.4f} |\n"
               for m in ("no_change","species_mean","baseline","SIC","SST_SSS","SIC_SST_SSS"))+
       "\n対象は元の単一方法で連続年・巣数正の繁殖記録。基準値と気候値はすべて学習期間内で計算。気候同化値は独立の野外因果測定ではない。\n"+
       f"元月監査対象はアデリー2011–2020のみ。9月以降計数の確証区間={int(panel.months_verified_after_september.sum())}、他種は未監査。\n"+
       f"**2050/2100年の巣数予測許可: {all(gate.values())}**。気候入力は物理モデル値として保存したが、生物応答係数の移植は不可。\n",
       encoding="utf-8")
if __name__=="__main__":
    main()
