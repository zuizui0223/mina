#!/usr/bin/env python3
"""V41 post-result RSPB-archipelago-heldout V40 source-label SDM stress test.

Post V40 and openly NOT confirmatory. Same four taxa, same >10 ha source
cohort, same Ridge C=1 logistic, same input covariates and label semantics.
No seabird response or true predator occupancy.
"""
from __future__ import annotations
import argparse,json,math
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import brier_score_loss, roc_auc_score, log_loss

import map_jncc_uk_island_predator_sdm_v40 as v40


def original_group(meta):
    raw = str(meta.get("group") or "").strip().lower().replace("_"," ")
    if raw and raw not in {"none","n/a","unknown"}:
        return "RSPB_GROUP:"+raw
    country=str(meta.get("country") or "").strip().lower().replace("_"," ")
    coast=str(meta.get("coast") or "").strip().lower().replace("_"," ")
    if not (country and coast):
        raise ValueError("SOURCE_ORIGINAL_ARCHIPELAGO_MISSING_AND_NO_REGION_FALLBACK")
    return "RSPB_REGION_FALLBACK:"+country+":"+coast


def group_cv(cohort,taxon,island_metadata):
    source=[r for r in cohort if r["source_status"][taxon] in {"0","1","2"}]
    y=np.array([int(r["source_status"][taxon] in {"1","2"}) for r in source],dtype=int)
    x=np.array([r["features"] for r in source],dtype=float)
    groups=np.array([original_group(island_metadata[r["lowid"]]) for r in source],dtype=str)
    gcounts=Counter(groups)
    out={
        "species":taxon,
        "training_source_islands":len(source),
        "source_label_positives":int(y.sum()),
        "source_combined_assumed_or_known_absence_0":int(len(y)-y.sum()),
        "original_RSPB_geographic_groups":len(gcounts),
        "largest_original_RSPB_group_n":int(max(gcounts.values())) if gcounts else 0,
        "largest_original_RSPB_group_fraction":float(max(gcounts.values())/len(y)) if gcounts else None,
        "fivefold_grouping":"original RSPB group_ with frozen region fallback",
        "target":"original Stanbury 2017 positive status 1/2 versus 0; NOT true occupancy",
        "V40_predicted_probability_maps_untouched":True,
    }
    if len(gcounts)<5 or y.sum()<30 or len(y)-y.sum()<30:
        out["status"]="SOURCE_GROUP_SUPPORT_STOP"
        return out
    splits=list(GroupKFold(n_splits=5).split(x,y,groups=groups))
    preds={label:np.zeros(len(y)) for label in ("M0","G","GH")}
    fold_data=[]
    all_test_support=True
    for n,(train,test) in enumerate(splits,1):
        train_y=y[train]
        if len(set(train_y))!=2:
            out["status"]="TRAIN_FOLD_ONE_SOURCE_CLASS_STOP"
            return out
        srcp=float(train_y.mean())
        preds["M0"][test]=srcp
        for label,cols in (("G",v40.COLS_G),("GH",v40.COLS_GH)):
            model=v40.make_model().fit(x[train,cols],train_y)
            preds[label][test]=model.predict_proba(x[test,cols])[:,1]
        positive=int(y[test].sum())
        source0=int(len(test)-positive)
        if positive<3 or source0<3: all_test_support=False
        fold_data.append({
            "fold":n,
            "original_heldout_islands":len(test),
            "original_heldout_RSPB_groups":len(set(groups[test])),
            "original_source_positive_status_1_or_2":positive,
            "original_source_reference_code0_not_field_absence":source0,
            "Brier_M0":float(brier_score_loss(y[test],preds["M0"][test])),
            "Brier_G":float(brier_score_loss(y[test],preds["G"][test])),
            "Brier_GH":float(brier_score_loss(y[test],preds["GH"][test])),
        })
    calib={}
    for label,p in preds.items():
        bins,ece=v40.reliability(y,p)
        calib[label]={
            "source_label_pooled_Brier":float(brier_score_loss(y,p)),
            "source_label_pooled_logloss":float(log_loss(y,p,labels=[0,1])),
            "source_label_pooled_AUC":float(roc_auc_score(y,p)),
            "five_source_label_reliability_bins":bins,
            "source_label_ECE":float(ece),
        }
    pooled_gain=calib["M0"]["source_label_pooled_Brier"]-calib["GH"]["source_label_pooled_Brier"]
    equalfold_gain=float(np.mean([r["Brier_M0"]-r["Brier_GH"] for r in fold_data]))
    out.update({
        "original_archipelago_fold_support_pass":all_test_support,
        "test_source_counts":fold_data,
        "scores":calib,
        "pooled_Brier_gain_GH_vs_M0":float(pooled_gain),
        "equal_original_group_fold_Brier_gain_GH_vs_M0":equalfold_gain,
        "transportability_gate":bool(all_test_support and pooled_gain>0 and equalfold_gain>0),
        "status":(
            "SOURCE_ARCHIPELAGO_LABEL_TRANSPORT_SUPPORT_PASS"
            if all_test_support and pooled_gain>0 and equalfold_gain>0
            else "SOURCE_ARCHIPELAGO_PREDICTIVE_TRANSPORTABILITY_NOT_SUPPORTED"
        ),
        "source0_is_assumed_or_known_absence_NOT_verified_surveillance_zero":True,
        "group_heldout_source_status_prediction_is_not_true_predator_occupancy":True,
    })
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    receipt={
        "status":"V41_SOURCE_HOLD_NO_NEW_PREDATOR_OCCUPANCY_CLAIM",
        "post_result_robustness_not_confirmation":True,
        "V40_source_probabilities_unchanged":True,
        "JNCC_original_bird_responses_read":0,
        "source_V36_predator_refuge_H2_still_STOP":True,
        "contract":"contracts/JNCC_PREDATOR_SDM_ARCHIPELAGO_STRESS_V41.md",
    }
    try:
        island_data,raw_status,source_qa=v40.original_islands_and_taxa()
        cohort=v40.construct_domain(island_data,raw_status)
        result={t:group_cv(cohort,t,island_data) for t in v40.TAXA}
        receipt.update({
            "status":"V41_PREDATOR_ORIGINAL_ARCHIPELAGO_SPATIAL_TRANSFER_AUDITED",
            "original_506_island_domain":len(cohort),
            "original_RSPB_Stanbury":source_qa,
            "species":result,
        })
    except Exception as exc:
        receipt["error"]=type(exc).__name__+": "+str(exc)[:600]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":receipt["status"],
        "N":receipt.get("original_506_island_domain"),
        "species":{
            t:{
                "status":v["status"],
                "n":v.get("training_source_islands"),
                "p_source":v.get("source_label_positives"),
                "num_groups":v.get("original_RSPB_geographic_groups"),
                "largest_group_fraction":v.get("largest_original_RSPB_group_fraction"),
                "all_fold_supported":v.get("original_archipelago_fold_support_pass"),
                "fold_positive_n":[r["original_source_positive_status_1_or_2"] for r in v.get("test_source_counts",[])],
                "pooled_Brier_gain":v.get("pooled_Brier_gain_GH_vs_M0"),
                "fold_equal_gain":v.get("equal_original_group_fold_Brier_gain_GH_vs_M0"),
                "source_label_ECE":v.get("scores",{}).get("GH",{}).get("source_label_ECE"),
            }
            for t,v in receipt.get("species",{}).items()
        },
        "error":receipt.get("error"),
    },ensure_ascii=False))
    if receipt["status"]!="V41_PREDATOR_ORIGINAL_ARCHIPELAGO_SPATIAL_TRANSFER_AUDITED":
        raise SystemExit(2)


if __name__=="__main__":
    main()
