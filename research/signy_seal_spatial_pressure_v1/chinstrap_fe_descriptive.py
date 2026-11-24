"""Pinned publisher workbook: descriptive Fe concentrations by collection substrate."""
import hashlib, io, json, math, re, zipfile
from pathlib import Path
from statistics import mean, median, stdev
import requests
from openpyxl import load_workbook

URL="https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-37132-5/MediaObjects/41467_2023_37132_MOESM4_ESM.xlsx"
PIN="6d323fa9bd473722ac1bbd2e209367a5dd998490411afb8c776782ea5622a508"
OUT=Path("build/chinstrap_fe_descriptive")
LABELS={"Directly on the ground":"SOIL","On the ice ground":"ICE","On the new guano collector":"TRAP"}
EXPECTED={"SOIL":12,"ICE":6,"TRAP":5}
def acquire():
    with requests.get(URL,stream=True,timeout=(20,90)) as r:
        r.raise_for_status()
        chunks=[]; n=0
        for c in r.iter_content(65536):
            n+=len(c)
            if n>1000000: raise ValueError("bounded intake")
            chunks.append(c)
    b=b"".join(chunks)
    if hashlib.sha256(b).hexdigest()!=PIN: raise ValueError("source SHA256 mismatch")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None: raise ValueError("ZIP CRC")
    return b

def date_from_id(key, group):
    if key=="VC.210208_SOIL": return "2021-02-08"
    m=re.fullmatch(r"VC\.G(?:T)?(\d{2})(\d{2})_\d+_(SOIL|ICE|TRAP)",key)
    if not m or m.group(3)!=group: raise ValueError("unexpected date or substrate code: "+key)
    return "2021-"+m.group(1)+"-"+m.group(2)

def describe(v):
    if not v: raise ValueError("empty group")
    return {"n":len(v),"mean_mg_g":mean(v),"median_mg_g":median(v),"sd_between_samples_mg_g":stdev(v) if len(v)>1 else None,"min_mg_g":min(v),"max_mg_g":max(v)}

def run(b):
    wb=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    if wb.sheetnames!=["Hoja1"]: raise ValueError("unexpected sheet")
    it=iter(wb["Hoja1"].values)
    h=list(next(it))
    if h!=["Sample ID","Fe (µg/g dw)","SD","Species","Collection","Locality","Colony"]: raise ValueError("header mismatch")
    rows=[]; ids=set()
    for key,fe,sd,sp,label,loc,col in it:
        if key in ids or sp!="Pygoscelis antarcticus" or loc!="Antarctica - Deception Island" or col!="Vapour Col" or label not in LABELS: raise ValueError("identity/label mismatch")
        if not isinstance(fe,(int,float)) or not math.isfinite(fe) or fe<=0: raise ValueError("invalid Fe")
        ids.add(key); group=LABELS[label]
        rows.append({"id":key,"group":group,"date_inferred_from_id":date_from_id(key,group),"fe_mg_g":fe/1000})
    wb.close()
    groups={k:[r for r in rows if r["group"]==k] for k in EXPECTED}
    if len(rows)!=23 or {k:len(v) for k,v in groups.items()}!=EXPECTED: raise ValueError("fixed count mismatch")
    def vals(rs):return [r["fe_mg_g"] for r in rs]
    result={"all":describe(vals(rows)),"groups":{},"contrasts":{},"common_dates":{}}
    for k,g in groups.items():
        byday={d:describe(vals([r for r in g if r["date_inferred_from_id"]==d])) for d in sorted({r["date_inferred_from_id"] for r in g})}
        result["groups"][k]={"sample_weighted":describe(vals(g)),"by_inferred_date":byday,"equal_date_weight_mean_mg_g":mean(v["mean_mg_g"] for v in byday.values())}
    for k in ("SOIL","ICE"):
        a,t=groups[k],groups["TRAP"]
        am,tm=mean(vals(a)),mean(vals(t))
        rr=[]
        for i in range(len(a)):rr.append(mean(vals(a[:i]+a[i+1:]))/tm)
        for i in range(len(t)):rr.append(am/mean(vals(t[:i]+t[i+1:])))
        common=sorted(set(result["groups"][k]["by_inferred_date"])&set(result["groups"]["TRAP"]["by_inferred_date"]))
        day_ratios=[]
        for d in common:
            x=result["groups"][k]["by_inferred_date"][d];y=result["groups"]["TRAP"]["by_inferred_date"][d]
            day_ratios.append({"date":d,"comparison_n":x["n"],"trap_n":y["n"],"ratio":x["mean_mg_g"]/y["mean_mg_g"],"difference_mg_g":x["mean_mg_g"]-y["mean_mg_g"]})
        result["contrasts"][k+"_vs_TRAP"]={"ratio_of_sample_means":am/tm,"difference_mg_g":am-tm,"leave_one_sample_out_ratio_range":[min(rr),max(rr)],"common_date_descriptive_contrasts":day_ratios}
    for d in sorted(set.intersection(*(set(g["by_inferred_date"]) for g in result["groups"].values()))):
        result["common_dates"][d]={k:g["by_inferred_date"][d] for k,g in result["groups"].items()}
    # Do not weight by the source SD: it is not verified independent biological variance.
    return {"status":"DESCRIPTIVE_SINGLE_COLONY_SUBSTRATE_AUDIT","source_sha256":PIN,"n_samples":23,"n_colonies":1,"n_species":1,"date_note":"Month/day parsed from sample IDs; year from study. Dates are not a separate original column.","scope":"Descriptive collection-method contrast; not contamination mass or causal substrate effect. No seasonal flux or Signy calibration.","results":result}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r=run(acquire())
    (OUT/"result.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,ensure_ascii=False))

if __name__=="__main__":main()
