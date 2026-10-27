#!/usr/bin/env python3
"""V34: source-only 2014 island predator *reported-status* niche screen.

NO seabird abundance, composition E, 1998/2021 state or survey absences read.
A label of 0 in Stanbury ESM5 mixes known/assumed absence and is NOT proof of
surveyed absence. Outputs are models of published status/reporting, never
detection-adjusted ecological occupancy probabilities.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, re, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.base import clone

import audit_jncc_predator_island_source_v33 as source

ESM5_SHA = "3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5"
PREDATORS = ("American mink", "Brown rat")
SOURCE_STATUSES = ("0", "1", "2", "3")
FIXED_FEATURES = ("log1p_high_tide_area_ha", "log1p_resident_population", "any_ferry_service")
AREA_BINS_HA = ((0, .1), (.1, 1), (1, 10), (10, 100), (100, 1000), (1000, float("inf")))
MIN_CLASSIFIED_POSITIVES = 30
MIN_DISTINCT_GROUPS = 5
MIN_FOLD_BOTH_CLASSES = 3

def source_islands() -> dict[int,dict]:
    meta = source.official_json("", {"f":"json"})
    fields = {f["name"] for f in meta.get("fields",[])}
    required = {"FID","lowid","name","mhwsarea_h","mlwsarea_h","population","ferry","group_","country"}
    if not required.issubset(fields):
        raise ValueError("SOURCE_SCHEMA missing source island predictors")
    count = int(source.official_json("/query",{
        "where":"1=1","returnCountOnly":"true","f":"json"
    })["count"])
    if count != 9688:
        raise ValueError("SOURCE_FRAME_CHANGED expected 9688")
    result={}
    for offset in range(0,count,1000):
        obj=source.official_json("/query",{
          "where":"1=1","outFields":"FID,lowid,name,mhwsarea_h,mlwsarea_h,population,ferry,group_,country,coast",
          "returnGeometry":"true","outSR":4326,"orderByFields":"FID ASC",
          "resultOffset":offset,"resultRecordCount":min(1000,count-offset),"f":"json"
        })
        rows=obj.get("features",[])
        if len(rows)!=min(1000,count-offset):
            raise ValueError("SOURCE_PAGE_INVALID")
        for row in rows:
            a=row["attributes"]
            key=source.to_integral_key(a.get("lowid"))
            if key is None or key in result:
                raise ValueError("SOURCE_LOWID_MISSING_OR_DUPLICATE")
            loc=row.get("geometry") or {}
            if not (isinstance(loc.get("x"),(int,float))
                    and isinstance(loc.get("y"),(int,float))
                    and -180<=loc["x"]<=180 and -90<=loc["y"]<=90):
                raise ValueError("SOURCE_RSPB_COORDINATE_MISSING")
            result[key]={
                "lon":float(loc["x"]),"lat":float(loc["y"]),
                "name":str(a.get("name") or "").strip().lower().replace("_"," "),
                "area_ha":a.get("mhwsarea_h"),
                "mlws_area_ha":a.get("mlwsarea_h"),
                "population":a.get("population"),
                "ferry":str(a.get("ferry") or "").strip().lower(),
                "group":str(a.get("group_") or "").strip().lower(),
                "country":str(a.get("country") or "").strip().lower(),
                "coast":str(a.get("coast") or "").strip().lower(),
            }
    if len(result)!=9688:
        raise ValueError("SOURCE_FRAME_JOIN_COUNT")
    return result

def excel_index(c:str)->int:
    letters=re.match(r"([A-Z]+)",c)
    if letters is None:
        raise ValueError("invalid cell coordinate")
    n=0
    for t in letters.group(1):n=n*26+ord(t)-64
    return n-1

def load_original_ESM5(raw:bytes) -> tuple[dict[int,dict],dict]:
    if hashlib.sha256(raw).hexdigest()!=ESM5_SHA:
        raise ValueError("SOURCE_ESM5_SHA_CHANGED")
    if not raw.startswith(b"PK"):
        raise ValueError("SOURCE_ESM5_NOT_XLSX")
    result={}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        infos=z.infolist()
        if len(infos)>150 or sum(i.file_size for i in infos)>45_000_000:
            raise ValueError("SOURCE_ESM5_ZIP_LIMIT")
        ss=ET.fromstring(z.read("xl/sharedStrings.xml"))
        strings=["".join(x.text or "" for x in si.findall(".//x:t",source.NS))
                 for si in ss.findall("x:si",source.NS)]
        root=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows=[]
        for element in root.findall(".//x:sheetData/x:row", source.NS):
            cells={}
            for c in element.findall("x:c",source.NS):
                pos=excel_index(c.attrib.get("r",""))
                v=c.find("x:v",source.NS)
                if v is None:
                    inline=c.find("x:is",source.NS)
                    if inline is None:continue
                    rawvalue="".join(x.text or "" for x in inline.findall(".//x:t",source.NS))
                elif c.attrib.get("t")=="s":
                    rawvalue=strings[int(v.text)]
                else:
                    rawvalue=str(v.text or "")
                cells[pos]=rawvalue
            if cells:rows.append(cells)
    if len(rows)!=9690:
        raise ValueError("SOURCE_ESM5_ROW_COUNT_CHANGED")
    first,second=rows[:2]
    if (first.get(1,"").strip().lower()!="island"
       or second.get(12,"").strip().lower()!="american mink"
       or second.get(14,"").strip().lower()!="brown rat"):
        raise ValueError("SOURCE_ESM5_TWO_ROW_SCHEMA_CHANGED")
    predator_cols={}
    for col,txt in second.items():
        if str(txt).strip() in PREDATORS: predator_cols[str(txt).strip()]=col
    if set(predator_cols)!=set(PREDATORS):
        raise ValueError("SOURCE_ESM5_PREDATOR_FIELDS_MISSING")
    for rawrow in rows[2:]:
        lowid=source.to_integral_key(rawrow.get(0))
        if lowid is None or lowid in result:raise ValueError("SOURCE_ESM5_BAD_LOWID")
        statuses={}
        for name,col in predator_cols.items():
            val=str(rawrow.get(col,"")).strip()
            if val not in SOURCE_STATUSES:
                raise ValueError("SOURCE_ESM5_UNSUPPORTED_LITERAL_STATUS "+name+":"+repr(val))
            statuses[name]=val
        result[lowid]={
            "name":str(rawrow.get(1,"")).strip().lower(),
            "statuses":statuses,
        }
    if len(result)!=9688:
        raise ValueError("SOURCE_ESM5_CARDINALITY")
    return result,{
        "status_legend":str(first.get(12,""))[:1000],
        "n":len(result),
        "predator_cols":predator_cols,
        "sha256":hashlib.sha256(raw).hexdigest(),
        "original_period":"Stanbury original 2017 archive; source locations labelled as 2014 RSPB",
    }

def norm_name(s):
    return re.sub(r"[^a-z0-9]","",str(s).lower())

def generate_cohort(isl,esm):
    if set(isl)!=set(esm):
        raise ValueError("LOWID_JOIN_NOT_EXACT")
    rows=[]
    names_matching=0
    failed=[]
    for key in sorted(isl):
        a=isl[key];b=esm[key]
        if norm_name(a["name"])==norm_name(b["name"]):
            names_matching+=1
        elif len(failed)<12:
            failed.append({"lowid":key,"island_RSPB":a["name"],"island_Stanbury":b["name"]})
        area=a["area_ha"]
        mlws=a["mlws_area_ha"]
        pop=a["population"]
        if area is None or not math.isfinite(float(area)) or float(area)<0:
            raise ValueError("SOURCE_AREA_INCOMPLETE")
        if mlws is None or not math.isfinite(float(mlws)) or float(mlws)<0:
            raise ValueError("SOURCE_LOW_TIDE_AREA_INCOMPLETE")
        if pop is None or not math.isfinite(float(pop)) or float(pop)<0:
            raise ValueError("SOURCE_POP_INCOMPLETE")
        # 'group_' is an original RSPB named archipelago, used ONLY for
        # held-out validation. Missing group gets coarse source region.
        grp=a["group"].strip()
        if not grp or grp==" ":
            grp="region:"+a["country"]+":"+a["coast"]
        ferry=a["ferry"] not in (""," ","none","no","nil","n/a")
        rows.append({
            "lowid":key,"area_ha":float(area),"mlws_area_ha":float(mlws),"population":float(pop),
            "ferry":ferry,"group":grp,"status":b["statuses"],
        })
    return rows,{
        "island_n":len(rows),"exact_original_lowid_overlap_n":len(rows),
        "literal_island_name_agreement_n":names_matching,
        "literal_island_name_agreement_fraction":names_matching/len(rows),
        "source_mismatching_names_first_12_non_sensitive":failed,
        "separate_original_metadata_sources_joined_by_lowid_not_name":True,
        "source_island_centroids_not_demonstrated_nest_coordinates":True,
        "source_status_0_is_assumed_or_known_absent_combination":True,
    }

def tabulate(rows:list[dict])->dict:
    bins=[]
    for low,hi in AREA_BINS_HA:
        cand=[r for r in rows if low<=r["area_ha"]<hi]
        bins.append({
            "area_ha_min_inclusive":low,
            "area_ha_max_exclusive":hi if math.isfinite(hi) else None,
            "n":len(cand),
            "by_predator":{
                pred:{
                    "literal_status_counts":dict(Counter(r["status"][pred] for r in cand)),
                    "fraction_source_confirmed_or_probable":
                        sum(r["status"][pred] in {"1","2"} for r in cand)/len(cand) if cand else None
                }
                for pred in PREDATORS
            }
        })
    over10=[r for r in rows if r["area_ha"]>10]
    low_tide_over10=[r for r in rows if r["mlws_area_ha"]>10]
    def status_fraction(records, species):
        return sum(r["status"][species] in {"1","2"} for r in records)/len(records) if records else None
    return {
        "overall_source_islands":len(rows),
        "original_islands_over_10_ha":len(over10),
        "original_islands_over_10ha_low_tide_area":len(low_tide_over10),
        "publisher_reported_506_islands_over10ha_used_only_for_source_denominator_audit":True,
        "over10ha_denominator_tide_definitions_are_distinct":True,
        "area_bins":bins,
        "confirmed_or_probable_fraction_over10ha":{
            p:sum(r["status"][p] in {"1","2"} for r in over10)/len(over10) if over10 else None
            for p in PREDATORS
        },
        "original_low_tide_over10ha_reported_status":{
            p:{"literal_status_counts":dict(Counter(r["status"][p] for r in low_tide_over10)),
               "confirmed_or_probable_fraction":status_fraction(low_tide_over10,p)}
            for p in PREDATORS
        },
        "original_source_reported_0_not_surveyed_absence":True,
    }

def fit_reported_status(rows:list[dict],predator:str,mode:str)->dict:
    if mode not in ("confirmed_only","confirmed_or_probable"):
        raise ValueError("UNEXPECTED_RESPONSE_MODE")
    y=np.array([
        int(r["status"][predator]=="1")
        if mode=="confirmed_only"
        else int(r["status"][predator] in {"1","2"})
        for r in rows
    ],dtype=np.int8)
    x=np.array([
        [np.log1p(r["area_ha"]),np.log1p(r["population"]),float(r["ferry"])]
        for r in rows
    ],dtype=float)
    group=np.array([r["group"] for r in rows])
    ng=len(set(group))
    prevalence=float(y.mean())
    ans={
       "predator":predator,"reported_label":mode,
       "n_original_islands":len(y),
       "original_islands_with_target_report_status":int(y.sum()),
       "reported_status_fraction":prevalence,
       "original_geographic_group_count":ng,
       "largest_geographic_group_fraction":max(Counter(group).values())/len(group),
       "class_0_definition":"REMAINDER_OF_REPORTED_STATUSES_NOT_SURVEYED_ABSENCE",
       "model_does_not_return_real_predator_occupancy_probability":True,
       "features":FIXED_FEATURES,
       "cross_validation":"GroupKFold held-out RSPB original island archipelago group",
    }
    if (ng<MIN_DISTINCT_GROUPS or y.sum()<MIN_CLASSIFIED_POSITIVES
          or (len(y)-y.sum())<MIN_CLASSIFIED_POSITIVES):
        ans["status"]="STOP_SOURCE_LABEL_SUPPORT"
        return ans
    fold_results=[]
    cv=GroupKFold(n_splits=5)
    for split,(train,test) in enumerate(cv.split(x,y,group)):
        if y[train].min()==y[train].max():
            ans["status"]="STOP_TRAIN_FOLD_SINGLE_CLASS"
            return ans
        base=float(y[train].mean())
        estimator=make_pipeline(StandardScaler(),
                                LogisticRegression(solver="lbfgs",C=1.0,
                                                   max_iter=1500))
        estimator.fit(x[train],y[train])
        prob=estimator.predict_proba(x[test])[:,1]
        fold_results.append({
            "fold":split+1,
            "held_out_archipelago_count":len(set(group[test])),
            "test_islands":len(test),
            "test_source_positive":int(y[test].sum()),
            "baseline_Brier":float(brier_score_loss(y[test],np.full(len(test),base))),
            "model_Brier":float(brier_score_loss(y[test],prob)),
            "AUC_if_both_test_classes":float(roc_auc_score(y[test],prob))
                 if 0<y[test].sum()<len(test) else None,
        })
    equal_fold_gain=float(np.mean([f["baseline_Brier"]-f["model_Brier"] for f in fold_results]))
    if sum(f["AUC_if_both_test_classes"] is not None for f in fold_results)<MIN_FOLD_BOTH_CLASSES:
        ans["status"]="STOP_UNBALANCED_SPATIAL_FOLDS"
        ans["folds"]=fold_results
        return ans
    final=make_pipeline(StandardScaler(),LogisticRegression(solver="lbfgs",C=1.0,max_iter=1500))
    final.fit(x,y)
    ans.update({
       "status":"SOURCE_REPORTED_STATUS_NICHE_FIT_DESCRIPTIVE_NOT_OCCUPANCY",
       "equal_fold_Brier_gain":equal_fold_gain,
       "heldout_fold_Brier_better_count":sum(f["model_Brier"]<f["baseline_Brier"] for f in fold_results),
       "folds":fold_results,
       "standardized_feature_coefficients":{
           n:float(v) for n,v in zip(FIXED_FEATURES,final[-1].coef_[0])
       },
       "feature_coefficients_are_reporting_associations_not_invasion_or_predation_causes":True,
    })
    return ans

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    receipt={
        "status":"UNEXECUTED_SOURCE_ACCESS",
        "source_original":"RSPB UK Islands 2014 + Stanbury 2017 ESM5",
        "source_predator_ESM5_SHA256_pinned":ESM5_SHA,
        "external_JNCC_bird_count_cells_read":0,
        "JNCC_predator_effect_fitted":False,
        "island_status_is_predator_detections_not_verifiable_surveyed_absences":True,
        "independent_breeding_niche_absence_observed":False,
    }
    try:
        islands=source_islands()
        original_raw=source.bounded_get(source.SUPPLEMENTS["ESM5"],source.MAX_SUPP_BYTES)
        esim,raw_meta=load_original_ESM5(original_raw)
        cohort,identity=generate_cohort(islands,esim)
        receipt["original_predator_data"]=raw_meta
        receipt["source_key_identity"]=identity
        receipt["area_stratified_literal_predator_status"]=tabulate(cohort)
        receipt["source_only_models"]=[
            fit_reported_status(cohort,p,mode) for p in PREDATORS
            for mode in ("confirmed_only","confirmed_or_probable")
        ]
        receipt["status"]="SOURCE_ONLY_PREDATOR_REPORTED_STATUS_MODEL_COMPLETE"
    except Exception as exc:
        receipt["status"]="SOURCE_OR_SCHEMA_HOLD_NO_PREDATOR_EFFECT"
        receipt["source_failure"]=type(exc).__name__+": "+str(exc)[:350]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]!="SOURCE_ONLY_PREDATOR_REPORTED_STATUS_MODEL_COMPLETE":
        raise SystemExit(2)

if __name__=="__main__":main()
