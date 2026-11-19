#!/usr/bin/env python3
"""V20 source-hashed three-island gentoo annual log-ratio comparison.

NOAA: original XLSX decoded with standard-library ZIP/XML, no generic
spreadsheet editing libraries. BAS: pinned original CSV. No raw pooled counts.
"""
import argparse
from collections import defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import audit_noaa_bas_independent_island_sources_v18 as source

NOAA_SHA="a57370f82adf82b53da11ce5d85dada1ae3f3750ef246312b59d0f168763eef4"
BAS_SHA="53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b"
HEAD=("YEAR","Copa_Adelie","Copa_Gentoo","Copa_Chinstrap","CapeShirreff_Chinstrap","CapeShirreff_Gentoo")
YEARS=set(range(1998,2010))|set(range(2011,2015))
SITES=("KingGeorge","Livingston","Signy")
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def parse_year(x):
    if x is None:return None
    s=str(x).strip()
    if re.fullmatch(r"(?:19|20)\d{2}",s):return int(s)
    m=re.fullmatch(r"((?:19|20)\d{2})\s*[-/]\s*(\d{2}|\d{4})",s)
    if m:
        y=int(m.group(1));n=int(m.group(2))
        return y if n in ((y+1)%100,y+1) else None
    return None

def numeric(x):
    if x is None or isinstance(x,bool):return None
    s=str(x).strip()
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)",s):return None
    v=float(s)
    return v if math.isfinite(v) else None

def colnum(s):
    m=re.fullmatch(r"([A-Z]+)\d+",s)
    if not m:raise ValueError("SCHEMA_STOP invalid NOAA cell address")
    n=0
    for c in m.group(1):n=26*n+ord(c)-64
    return n-1

def xlsx_values(raw):
    if not raw.startswith(b"PK"):raise ValueError("SOURCE_STOP NOAA XLSX not ZIP")
    with ZipFile(io.BytesIO(raw)) as z:
        if "xl/worksheets/sheet1.xml" not in z.namelist():
            raise ValueError("SCHEMA_STOP original NOAA worksheet missing")
        strings=[]
        if "xl/sharedStrings.xml" in z.namelist():
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings=["".join(t.text or "" for t in si.iter(NS+"t"))
                     for si in root.iter(NS+"si")]
        root=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        sheet=root.find(NS+"sheetData")
        if sheet is None:raise ValueError("SCHEMA_STOP no NOAA sheetData")
        rows=[]
        for r in sheet.findall(NS+"row"):
            d={}
            for cell in r.findall(NS+"c"):
                k=colnum(cell.attrib.get("r",""))
                typ=cell.attrib.get("t","n")
                value=cell.find(NS+"v")
                if typ=="s":
                    if value is None or value.text is None:raise ValueError("SCHEMA_STOP bad shared string")
                    idx=int(value.text)
                    if not 0<=idx<len(strings):raise ValueError("SCHEMA_STOP shared string index")
                    val=strings[idx]
                elif typ=="inlineStr":
                    val="".join(t.text or "" for t in cell.iter(NS+"t"))
                elif typ in ("n","str","b","e"):
                    val=value.text if value is not None else None
                else:raise ValueError("SCHEMA_STOP original NOAA cell type")
                d[k]=val
            if d:rows.append([d.get(k) for k in range(6)])
    if len(rows)!=39 or tuple(rows[0])!=HEAD:
        raise ValueError("SCHEMA_STOP original NOAA header or 38-year roster")
    return rows[1:]

def parse_noaa(raw):
    groups=defaultdict(list)
    for row in xlsx_values(raw):
        y=parse_year(row[0])
        if y is not None and 1977<=y<=2015:
            groups[y].append({name:numeric(row[i]) for i,name in enumerate(HEAD) if i})
    if len(groups)!=38 or any(len(g)!=1 for g in groups.values()):
        raise ValueError("SOURCE_STOP NOAA duplicate or absent source-year")
    return {y:g[0] for y,g in groups.items()}

def parse_bas(raw):
    try:txt=raw.decode("utf-8-sig")
    except UnicodeDecodeError:txt=raw.decode("latin-1")
    rdr=csv.DictReader(io.StringIO(txt))
    if rdr.fieldnames is None or not {"SEASON","TOTAL_NUMBER_OF_PAIRS"}<=set(rdr.fieldnames):
        raise ValueError("SCHEMA_STOP BAS original columns")
    groups=defaultdict(list);bad=[];row_count=0
    for row in rdr:
        row_count+=1
        y=parse_year(row.get("SEASON"))
        if y is None or not 1978<=y<=2020:
            bad.append(str(row.get("SEASON")));continue
        groups[y].append(numeric(row.get("TOTAL_NUMBER_OF_PAIRS")))
    if row_count!=43 or len(groups)!=42 or bad!=["1998-8895"]:
        raise ValueError("SOURCE_STOP BAS original year roster drift")
    if any(len(g)!=1 for g in groups.values()):raise ValueError("SOURCE_STOP BAS duplicated season")
    return {y:g[0] for y,g in groups.items()},bad

def pearson(x,y):
    if len(x)<3 or len(x)!=len(y):return None
    mx=sum(x)/len(x);my=sum(y)/len(y)
    vx=sum((a-mx)**2 for a in x);vy=sum((b-my)**2 for b in y)
    if vx<=1e-12 or vy<=1e-12:return None
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(vx*vy)

def pairwise(rows):
    if len(rows)<3:return None
    pairs={}
    for a,b in ((0,1),(0,2),(1,2)):
        first=[r["log_ratios"][SITES[a]] for r in rows]
        second=[r["log_ratios"][SITES[b]] for r in rows]
        v=pearson(first,second)
        if v is None:return None
        pairs[SITES[a]+"_vs_"+SITES[b]]=v
    return {"pairwise_pearson":pairs,"mean_pairwise_pearson":sum(pairs.values())/3}

def signs(rows):
    pure=[r for r in rows if all(abs(r["log_ratios"][s])>1e-12 for s in SITES)]
    same=sum(all(r["log_ratios"][s]>0 for s in SITES)
             or all(r["log_ratios"][s]<0 for s in SITES) for r in pure)
    return {"eligible_strict_nonzero_windows":len(pure),"three_way_same_sign_windows":same,
            "fraction_all_same_sign":same/len(pure) if pure else None}

def analyse(noaa,bas):
    common={y for y,r in noaa.items() if r["Copa_Gentoo"] is not None
            and r["CapeShirreff_Gentoo"] is not None and bas.get(y) is not None}
    if common!=YEARS:raise ValueError("COHORT_STOP source original V19 common years changed")
    vectors={}
    for y in sorted(common):
        three=(noaa[y]["Copa_Gentoo"],noaa[y]["CapeShirreff_Gentoo"],bas[y])
        if all(v is not None and v>0 and math.isfinite(v) for v in three):
            vectors[y]=three
    windows=[]
    for y in sorted(vectors):
        if y+1 in vectors:
            logs={s:math.log(b/a) for s,a,b in zip(SITES,vectors[y],vectors[y+1])}
            windows.append({"start_year":y,"log_ratios":logs})
    base={"source_original_matched_years":len(common),
          "source_matched_year_start_list":sorted(common),
          "strict_positive_three_island_years":len(vectors),
          "excluded_original_years_with_nonpositive_three_site_count":sorted(common-set(vectors)),
          "strict_three_island_yearly_change_windows":len(windows),
          "yearly_change_start_years":[w["start_year"] for w in windows],
          "source_raw_counts_pooled":False,
          "three_monitored_sites_are_not_whole_island_demographic_populations":True}
    if len(windows)<8:
        return {**base,"status":"HOLD_FEWER_THAN_EIGHT_TRIPLE_GROWTH_WINDOWS",
                "biological_descriptive_association_computed":False}
    main=pairwise(windows)
    if main is None:
        return {**base,"status":"HOLD_DEGENERATE_SOURCE_VARIANCE",
                "biological_descriptive_association_computed":False}
    loo=[pairwise(windows[:i]+windows[i+1:]) for i in range(len(windows))]
    loo=[x["mean_pairwise_pearson"] for x in loo if x is not None]
    phase={}
    for key,items in (("early_start_1998_2005",[r for r in windows if r["start_year"]<=2005]),
                      ("late_start_2006_2014",[r for r in windows if r["start_year"]>=2006])):
        phase[key]={"n_windows":len(items),**signs(items),
                    "mean_pairwise_pearson":(pairwise(items) or {}).get("mean_pairwise_pearson")}
    controls={}
    for name,g,c in (("Copacabana","Copa_Gentoo","Copa_Chinstrap"),
                     ("CapeShirreff","CapeShirreff_Gentoo","CapeShirreff_Chinstrap")):
        a=[];b=[]
        for y in sorted(common):
            if y+1 not in common:continue
            four=(noaa[y][g],noaa[y+1][g],noaa[y][c],noaa[y+1][c])
            if all(v is not None and v>0 and math.isfinite(v) for v in four):
                a.append(math.log(four[1]/four[0]))
                b.append(math.log(four[3]/four[2]))
        controls[name]={"n_windows":len(a),"gentoo_vs_chinstrap_growth_pearson":pearson(a,b)}
    return {**base,"status":"V20_EXPLORATORY_THREE_ISLAND_WITHIN_SOURCE_ANNUAL_GROWTH",
            "biological_descriptive_association_computed":True,
            "primary":{**main,**signs(windows)},
            "leave_one_window_out_mean_r_min_max":([min(loo),max(loo)] if loo else None),
            "early_late_source_sensitivity":phase,
            "same_NOAA_programme_cross_species_controls":controls,
            "original_source_derived_yearly_log_ratios":windows,
            "environmental_island_causation_supported":False,
            "general_antarctic_island_law_demonstrated":False,
            "scientific_decision":"DESCRIPTIVE_SYNCHRONY_ONLY_NOT_ISLAND_CAUSATION"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report={"status":"HOLD_SOURCE_OR_SCHEMA","biological_descriptive_association_computed":False}
    try:
        noa,qn=source.source_get(source.NOAA_URL,"noaa")
        bas,qb=source.source_get(source.BAS_URL,"bas")
        if qn["sha256"]!=NOAA_SHA or qb["sha256"]!=BAS_SHA:
            raise ValueError("SOURCE_STOP original verified SHA256 drift")
        n=parse_noaa(noa);b,bad=parse_bas(bas)
        report={"source_noaa_sha256":NOAA_SHA,"source_bas_sha256":BAS_SHA,
                "excluded_invalid_BAS_original_season":bad,
                "frozen_contract":"contracts/NOAA_BAS_GENTOO_GROWTH_SYNCHRONY_V20.md",
                **analyse(n,b)}
    except Exception as exc:
        report["error_type"]=type(exc).__name__;report["error"]=str(exc)[:700]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="original_source_derived_yearly_log_ratios"},ensure_ascii=False))
    if report["status"]=="HOLD_SOURCE_OR_SCHEMA":raise SystemExit(2)

if __name__=="__main__":main()
