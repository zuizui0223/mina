#!/usr/bin/env python3
"""V40: source-label probabilities for four UK-island invasive mammal taxa.

Estimates P(publisher documented status 1/2 | source attributes and original
status in 0/1/2), NOT detection-corrected actual predator occupancy. Fits
2014 UK RSPB islands (>10 hectares MLWS), 2017 Stanbury ESM5 original labels.
No JNCC seabird outcomes; no predator-free biological classifications.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, brier_score_loss, log_loss, roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import audit_jncc_predator_island_source_v33 as source

TAXA = ("American mink", "Brown rat", "House mouse", "Feral cat")
MODEL_GROUPS = 5
BOOTSTRAPS = 199
BOOT_SEED = 20261027
MIN_POS = 30
MIN_NEG = 30
MIN_FOLD_CLASS = 3
MIN_BOOT_VALID = 100
MIN_AREA_HA = 10.
ESM5_SHA = "3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5"
PROBABILITY_TARGET = (
    "P(Stanbury 2017 status is confirmed/probable among islands originally "
    "classified 0/1/2 | source measured 2014 geography/access). "
    "NOT calibrated true ecological occupancy."
)
FEATURES = (
    "log1p_low_tide_area_ha", "latitude", "longitude",
    "log1p_2014_human_population", "listed_ferry_connection",
)
COLS_G = slice(0, 3)
COLS_GH = slice(0, 5)
SOURCE_CODES = {"0", "1", "2", "3"}
PRED_COLUMN = {
    "American mink": "american_mink",
    "Brown rat": "brown_rat",
    "House mouse": "house_mouse",
    "Feral cat": "feral_cat",
}


def finite_float(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def listed_ferry(value) -> int:
    """Source-labeled ferry mention; not evidence of verified zero boat traffic."""
    val=str(value or "").strip().casefold()
    return int(val not in ("", "no", "none", "nil", "n/a", "unknown"))


def original_islands_and_taxa():
    ids, islands, srcmeta = source.fetch_rpsb_islands()
    if len(ids) != 9688 or len(islands) != 9688:
        raise ValueError("RSPB_9688_SOURCE_KEY_FRAME_CHANGED")
    raw = source.bounded_get(source.SUPPLEMENTS["ESM5"],source.MAX_SUPP_BYTES)
    sha = hashlib.sha256(raw).hexdigest()
    if sha != ESM5_SHA:
        raise ValueError("STANBURY_SOURCE_HASH_CHANGED")
    records=[]
    header, keys=source.sheet_rows(raw,islands,records)
    if len(records)!=9688 or len({r["lowid"] for r in records})!=9688:
        raise ValueError("STANBURY_9688_SOURCE_KEY_FRAME_CHANGED")
    if ids!={r["lowid"] for r in records}:
        raise ValueError("RSPB_STANBURY_LOWID_KEY_COVERAGE_CHANGED")
    labels={r["lowid"]:r["status_codes"] for r in records}
    return islands, labels, {
        "RSPB_source":source.RSPB_SERVICE,
        "RSPB_unique_source_islands":len(ids),
        "source_Stanbury_ESM5_original_SHA256":sha,
        "original_source_status_codes":{
            "0":"assumed_or_known_absent_combined",
            "1":"confirmed",
            "2":"probable",
            "3":"possible_or_incidental",
        },
        "source_RSPB_code_0_is_not_verified_survey_non_detection":True,
        "source_Stanbury_XLSX_source_columns":header["sheets"][0].get("predator_header_candidates", []),
        "original_source_census_years":[2014, 2017],
        "source_original_NBN_records_not_used_as_absence":True,
    }


def construct_domain(islands, labels):
    """Original RSPB area >10ha criterion, not modelled outcome selection."""
    out=[]
    for lowid in sorted(islands):
        m=islands[lowid]
        area=finite_float(m.get("low_tide_area_h"))
        if area is None or area<=MIN_AREA_HA:
            continue
        lat=finite_float(m.get("latitude"))
        lon=finite_float(m.get("longitude"))
        pop=finite_float(m.get("human_population"))
        if any(v is None for v in (lat,lon,pop)) or pop<0:
            raise ValueError("PRIMARY_ISLAND_DOMAIN_COVARIATE_MISSING")
        if not (48<=lat<=63.5 and -13.5<=lon<=3.5):
            raise ValueError("PRIMARY_ISLAND_OUTSIDE_RSPB_UK_GEOGRAPHY")
        status=labels[lowid]
        if not set(TAXA).issubset(status):
            raise ValueError("SOURCE_MISSING_PREDATOR_SPECIES")
        if any(str(status[t]).strip() not in SOURCE_CODES for t in TAXA):
            raise ValueError("SOURCE_PREDATOR_CODE_UNRECOGNIZED")
        out.append({
            "lowid":int(lowid),
            "latitude":lat,
            "longitude":lon,
            "area_ha":area,
            "population":pop,
            "ferry_listed":listed_ferry(m.get("ferry")),
            "group_1deg":f"{math.floor(lat)}:{math.floor(lon)}",
            "features":(
                math.log1p(area), lat, lon, math.log1p(pop),
                float(listed_ferry(m.get("ferry")))
            ),
            "source_status":{k:str(status[k]).strip() for k in TAXA},
        })
    if len(out)!=506 or len({x["lowid"] for x in out})!=506:
        raise ValueError("PRIMARY_STANBURY_GT10HA_506_SOURCE_COHORT_DRIFT")
    return out


def make_model():
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.,solver="lbfgs",max_iter=1000),
    )


def reliability(positive, predicted, bins=5):
    """Observed source-label fraction versus probability, not field occupancy."""
    order=np.argsort(predicted,kind="stable")
    slices=np.array_split(order,bins)
    rows=[]
    for i,idx in enumerate(slices):
        rows.append({
            "bin":i+1,"n":int(len(idx)),
            "mean_p_positive_source_label":float(predicted[idx].mean()),
            "actual_fraction_original_positive_source_labels":float(positive[idx].mean()),
            "expected_positive_source_labels":float(predicted[idx].sum()),
            "observed_positive_source_labels":int(positive[idx].sum()),
        })
    ece=sum(x["n"]*abs(x["actual_fraction_original_positive_source_labels"] -
                       x["mean_p_positive_source_label"]) for x in rows)/len(positive)
    return rows,float(ece)


def geographic_outer_cv(data, y, trained, taxon):
    """Outer geographic blocks only; no data-dependent group selection."""
    x=np.asarray([r["features"] for r in trained],dtype=np.float64)
    gr=np.asarray([r["group_1deg"] for r in trained],dtype=str)
    if len(set(gr))<MODEL_GROUPS or y.sum()<MIN_POS or (len(y)-y.sum())<MIN_NEG:
        return {
            "status":"STOP_ORIGINAL_PREDATOR_DOCUMENTED_LABEL_SUPPORT",
            "source_label_status":"NOT_VALIDATED",
            "heldout":None
        }
    folds=list(GroupKFold(n_splits=MODEL_GROUPS).split(x,y,groups=gr))
    if any(
        int(y[test].sum())<MIN_FOLD_CLASS or
        int(len(test)-y[test].sum())<MIN_FOLD_CLASS or
        len(set(y[train]))<2
        for train,test in folds
    ):
        return {
            "status":"STOP_SOURCE_SPATIAL_BLOCK_CLASS_IMBALANCE",
            "source_label_status":"NOT_VALIDATED",
            "fold_source_support":[
                {"test_islands":int(len(te)),"positive_source_labels":int(y[te].sum()),
                 "distinct_heldout_geographic_blocks":int(len(set(gr[te])))}
                for _,te in folds
            ],
            "heldout":None,
        }
    predicted={
        "M0_prevalence":np.zeros(len(y)),
        "G_geo":np.zeros(len(y)),
        "GH_geo_human_ferry":np.zeros(len(y)),
    }
    folds_report=[]
    for n,(train,test) in enumerate(folds,1):
        t=y[train]
        predicted["M0_prevalence"][test]=float(t.mean())
        for name,cols in [("G_geo",COLS_G),("GH_geo_human_ferry",COLS_GH)]:
            model=make_model()
            model.fit(x[train,cols],t)
            predicted[name][test]=model.predict_proba(x[test,cols])[:,1]
        folds_report.append({
            "fold":n,
            "test_islands":int(len(test)),
            "test_distinct_spatial_blocks":int(len(set(gr[test]))),
            "source_confirmed_or_probable":int(y[test].sum()),
            "source_code0_assumed_or_known_absent":int(len(test)-y[test].sum()),
            "Brier_M0":float(brier_score_loss(y[test],predicted["M0_prevalence"][test])),
            "Brier_G":float(brier_score_loss(y[test],predicted["G_geo"][test])),
            "Brier_GH":float(brier_score_loss(y[test],predicted["GH_geo_human_ferry"][test])),
        })
    scores={}
    for label,prob in predicted.items():
        rows,ece=reliability(y,prob)
        scores[label]={
            "geographic_out_of_fold_Brier":float(brier_score_loss(y,prob)),
            "geographic_out_of_fold_logloss":float(log_loss(y,prob,labels=[0,1])),
            "geographic_out_of_fold_ROC_AUC":float(roc_auc_score(y,prob)),
            "geographic_out_of_fold_average_precision":float(average_precision_score(y,prob)),
            "five_bin_source_label_expected_calibration_error":ece,
            "five_equal_count_reliability":rows,
            "probability_quantiles_05_50_95":[float(v) for v in np.quantile(prob,[.05,.5,.95])],
        }
    gain=scores["M0_prevalence"]["geographic_out_of_fold_Brier"]-scores["GH_geo_human_ferry"]["geographic_out_of_fold_Brier"]
    return {
        "status":"SPATIALLY_HELDOUT_DOCUMENTED_LABEL_PROBABILITY_ASSESSED",
        "source_label_status":(
            "SOURCE_LABEL_GEOGRAPHICALLY_PORTABLE_ONLY"
            if gain>0 else "RESEARCH_ONLY_NOT_GEOGRAPHICALLY_PORTABLE"
        ),
        "predeclared_5fold_geographic_blocks_degrees":1,
        "model_fixed_logistic_penalty_C":1.,
        "heldout":scores,
        "heldout_fold_support":folds_report,
        "Brier_gain_GH_over_original_label_prevalence_M0":float(gain),
        "Brier_gain_GH_over_G_only":float(
            scores["G_geo"]["geographic_out_of_fold_Brier"]-
            scores["GH_geo_human_ferry"]["geographic_out_of_fold_Brier"]
        ),
        "not_true_ecological_occupancy_probability":True,
    }


def geographic_bootstrap(trained, y, entire, rng, count=BOOTSTRAPS):
    """Model resampling uncertainty, NOT uncertainty of mammal true presence."""
    x=np.asarray([r["features"] for r in trained],dtype=float)
    pX=np.asarray([r["features"] for r in entire],dtype=float)
    group=np.asarray([r["group_1deg"] for r in trained],dtype=str)
    keys=sorted(set(group))
    bygroup={grp:np.flatnonzero(group==grp) for grp in keys}
    if count!=BOOTSTRAPS:
        raise ValueError("SOURCE_FROZEN_BOOTSTRAP_REPLICATES")
    pred=[]
    for _ in range(count):
        drawn=rng.choice(keys,size=len(keys),replace=True)
        indices=np.concatenate([bygroup[g] for g in drawn])
        if len(set(y[indices]))!=2:continue
        model=make_model().fit(x[indices,COLS_GH],y[indices])
        pred.append(model.predict_proba(pX[:,COLS_GH])[:,1])
    if len(pred)<MIN_BOOT_VALID:
        return None, {"bootstrap_valid_refits":len(pred),"status":"STOP_SOURCE_BLOCK_BOOTSTRAP_SUPPORT"}
    mat=np.stack(pred)
    return np.quantile(mat,[.05,.95],axis=0),{
        "bootstrap_valid_refits":len(pred),
        "bootstrap_attempts":count,
        "source_geographic_block_resampling_only":True,
        "intervals_are_not_credible_ranges_of_true_predator_occupancy":True,
        "status":"SOURCE_MODEL_PARAMETER_RESAMPLING_QUANTILES_AVAILABLE",
    }


def one_species(domain,taxon,rng):
    used=[r for r in domain if r["source_status"][taxon] in {"0","1","2"}]
    by_code=Counter(r["source_status"][taxon] for r in domain)
    y=np.array([int(r["source_status"][taxon] in {"1","2"}) for r in used],dtype=int)
    x=np.array([r["features"] for r in used],dtype=float)
    entireX=np.array([r["features"] for r in domain],dtype=float)
    cv=geographic_outer_cv(domain,y,used,taxon)
    if y.sum()<MIN_POS or len(y)-y.sum()<MIN_NEG:
        return {
            "species":taxon,
            "status":"STOP_TOO_FEW_ORIGINAL_SOURCE_LABELS",
            "source_labels_by_code":dict(by_code),
        },None
    model=make_model().fit(x[:,COLS_GH],y)
    pred=model.predict_proba(entireX[:,COLS_GH])[:,1]
    conf,bootstrap=geographic_bootstrap(used,y,domain,rng)
    per=[]
    for i,r in enumerate(domain):
        per.append({
            "lowid":r["lowid"],"species":taxon,
            "latitude":r["latitude"],"longitude":r["longitude"],
            "p_documented_positive":float(pred[i]),
            "model_bootstrap_p05":float(conf[0,i]) if conf is not None else None,
            "model_bootstrap_p95":float(conf[1,i]) if conf is not None else None,
            "status":cv["source_label_status"],
            "source_possible_code3_not_used_in_fit":r["source_status"][taxon]=="3",
        })
    return {
        "species":taxon,
        "training_original_source_islands":int(len(used)),
        "original_predator_status_counts":dict(by_code),
        "reported_positive_fraction_labeled_domain":float(y.mean()),
        "original_source_status_possible_code3_excluded":int(by_code["3"]),
        "fitted_logistic_GH_coefficient_signs_not_causal":{
            field:float(c) for field,c in zip(FEATURES,model[-1].coef_[0])
        },
        "model_validation":cv,
        "bootstrap":bootstrap,
        "full_sample_predicted_reported_label_p_quantiles_05_50_95":[float(v) for v in np.quantile(pred,[.05,.5,.95])],
        "modelled_target":PROBABILITY_TARGET,
    },per


def export_products(allsp,domain,outbase):
    base=Path(outbase)
    base.parent.mkdir(parents=True,exist_ok=True)
    long=[]
    geo=[]
    bysp={}
    for s,rows in allsp.items():
        if rows is None:continue
        bysp[s]={r["lowid"]:r for r in rows}
        long+=rows
    csvfile=base.with_name(base.name+"_PROBABILITIES.csv")
    fields=("lowid","species","latitude","longitude","p_documented_positive",
            "model_bootstrap_p05","model_bootstrap_p95","status",
            "source_possible_code3_not_used_in_fit")
    with csvfile.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(long)
    for island in domain:
        attr={
            "lowid":island["lowid"],
            "measurement":"Stanbury source-positive assessment likelihood, NOT true mammal occupancy",
            "source_cohort_low_tide_area_gt_10ha":True,
        }
        for taxon in TAXA:
            record=bysp.get(taxon,{}).get(island["lowid"])
            key=PRED_COLUMN[taxon]
            if record is None:
                attr[key+"_p_source_positive"]=None
                attr[key+"_CV_status"]="NO_MODEL"
                continue
            attr[key+"_p_source_positive"]=record["p_documented_positive"]
            attr[key+"_model_p05"]=record["model_bootstrap_p05"]
            attr[key+"_model_p95"]=record["model_bootstrap_p95"]
            attr[key+"_CV_status"]=record["status"]
        geo.append({
            "type":"Feature",
            "geometry":{"type":"Point","coordinates":[island["longitude"],island["latitude"]]},
            "properties":attr,
        })
    gjfile=base.with_name(base.name+"_MAP.geojson")
    gjfile.write_text(json.dumps({"type":"FeatureCollection","features":geo},
                                 ensure_ascii=False)+"\n",encoding="utf-8")
    return {"CSV":str(csvfile),"GEOJSON":str(gjfile),
            "CSV_source_island_x_species_rows":len(long),
            "GEOJSON_original_island_points":len(geo)}


def render_maps(domain, allsp, outbase):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return {"status":"MATPLOTLIB_NOT_INSTALLED"}
    files={}
    for sp,rows in allsp.items():
        if rows is None:continue
        plt.figure(figsize=(7,9))
        fig=plt.gcf();ax=plt.gca()
        sc=ax.scatter([r["longitude"] for r in rows],
                      [r["latitude"] for r in rows],
                      c=[r["p_documented_positive"] for r in rows],
                      s=21,cmap="viridis",vmin=0,vmax=1,linewidths=0,
                      alpha=.9)
        ax.set(xlim=(-13.5,3.5),ylim=(48,63.5),
               xlabel="Longitude (WGS84)",ylabel="Latitude (WGS84)")
        ax.set_aspect(1.0)
        ax.set_title(sp + "\nP(2017 source label confirmed/probable), NOT actual occupancy",
                     fontsize=11)
        plt.colorbar(sc,ax=ax,label="Source-positive assessment probability [0,1]",
                     shrink=.66)
        fig.text(.05,.025,"RSPB original low-tide area >10 ha, 506 islands; Stanbury 2017 codes 0/1/2/3",
                 fontsize=8)
        fig.tight_layout(rect=(0,.05,1,1))
        fn=Path(outbase).with_name(Path(outbase).name+"_"+PRED_COLUMN[sp]+".png")
        fig.savefig(fn,dpi=170)
        files[sp]=str(fn)
        plt.close(fig)
    return {"status":"SAVED","map_pngs":files}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--products-prefix",type=Path,required=True)
    args=p.parse_args()
    result={
        "status":"SOURCE_OR_PROBABILITY_MODEL_HOLD",
        "contract":"contracts/JNCC_UK_PREDATOR_SOURCE_PROBABILITY_SDM_V40.md",
        "source_status_probability_target":PROBABILITY_TARGET,
        "excludes_unmapped_source_islets_below_10_ha":True,
        "true_predator_occupancy_estimated":False,
        "JNCC_seabird_outcomes_read":0,
        "JNCC_predator_effect_fitted":False,
        "random_seed":BOOT_SEED,
        "taxa":TAXA,
    }
    try:
        source_islands,labels,source_report=original_islands_and_taxa()
        cohort=construct_domain(source_islands,labels)
        result["source"]=source_report
        result["island_primary_domain"]=len(cohort)
        results={};predictions={}
        rng=np.random.default_rng(BOOT_SEED)
        for taxon in TAXA:
            data,rows=one_species(cohort,taxon,rng)
            results[taxon]=data
            predictions[taxon]=rows
        result["models"]=results
        result["files"]=export_products(predictions,cohort,args.products_prefix)
        result["maps"]=render_maps(cohort,predictions,args.products_prefix)
        result["status"]="V40_ISLAND_PREDATOR_PUBLISHED_LABEL_PROBABILITY_MAP_COMPLETED"
    except Exception as exc:
        result["error"]=type(exc).__name__+": "+str(exc)[:650]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],"source_domain":result.get("island_primary_domain"),
        "species_validation":{
            sp:{"n":v.get("training_original_source_islands"),
                "status":v.get("model_validation",{}).get("source_label_status"),
                "positive":v.get("reported_positive_fraction_labeled_domain"),
                "Brier_gain":v.get("model_validation",{}).get(
                    "Brier_gain_GH_over_original_label_prevalence_M0"),
                "bootstrap_valid":v.get("bootstrap",{}).get("bootstrap_valid_refits"),
                "p_quantiles":v.get("full_sample_predicted_reported_label_p_quantiles_05_50_95")}
            for sp,v in result.get("models",{}).items()
        },
        "files":result.get("files"),"maps":result.get("maps"),
        "error":result.get("error"),
    },ensure_ascii=False))
    if result["status"]!="V40_ISLAND_PREDATOR_PUBLISHED_LABEL_PROBABILITY_MAP_COMPLETED":
        raise SystemExit(2)


if __name__=="__main__":
    main()
