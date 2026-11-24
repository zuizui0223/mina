"""Source schema and structural support only. No cross-source numerical merge."""
import argparse,csv,hashlib,io,json,re,sys,zipfile
from collections import Counter
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
from signy_trispecies_stage_source_v1 import source_extract

def describe(path, suffix, pin):
    with zipfile.ZipFile(path) as z:
        names=[n for n in z.namelist() if n.endswith(suffix)]
        if len(names)!=1: raise ValueError(f"Expected one {suffix}: {names}")
        data=z.read(names[0])
    if hashlib.sha256(data).hexdigest()!=pin: raise ValueError("source member drift")
    # BAS CSV begins with comment metadata. Preserve metadata and inspect actual header.
    s=data.decode("utf-8-sig",errors="strict")
    rows=list(csv.reader(io.StringIO(s)))
    i=0; meta=[]
    while i<len(rows) and (not any(x.strip() for x in rows[i]) or rows[i][0].lstrip().startswith("#")):
        meta.append(rows[i]);i+=1
    if i==len(rows): raise ValueError("no header")
    h=[v.strip() for v in rows[i]]
    body=[r for r in rows[i+1:] if any(v.strip() for v in r)]
    out={"member":names[0],"sha256":pin,"metadata_rows":meta,"header":h,"data_rows":len(body),
         "row_widths":dict(Counter(map(len,body))),"column_structure":[]}
    for j,name in enumerate(h):
        vals=[r[j].strip() for r in body if len(r)>j and r[j].strip()]
        # Only display design labels (not counts, outcomes, environmental magnitudes).
        label=bool(re.search(r"year|season|date|month|day|area|zone|species|sex|age|class|region|site|location|type|variable|parameter|unit|survey|period",name,re.I))
        if re.search(r"duration|ice|count|number|extent|area\s*\(|km2|percent|concentration|retreat|advance|persistence|value",name,re.I):
            label=False
        u=sorted(set(vals))
        out["column_structure"].append({"name":name,"nonempty":len(vals),"unique":len(u),
           "design_labels":u[:120] if label and len(u)<=120 else None})
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    o={"status":"STRUCTURAL_REVIEW_ONLY","numerical_join_executed":False}
    o["seals"]=describe(a.source/"seals.zip","Signy_seal_annual_counts_by_area.csv","58f87d83afdd78f30daf5489f45f4221af30b1e413090c3d9a5493e602eacb3a")
    o["ice"]=describe(a.source/"ice.zip","Signy_sea_ice_variables.csv","b04bbb3bc593c67c070b18497acb6f96d52cbed6914952d814741c30206b5835")
    by={}
    for species in ["Adelie","Chinstrap","Gentoo"]:
        r,_,m=source_extract(species,a.source/(species.lower()+".zip"))
        valid=[v for v in r if v["reported_chicks_per_pair"] is not None and v["nest_before_chicks"]]
        years=sorted(set(v["season_start"] for v in valid))
        by[species]={"sha256":m["selected_csv_sha256"],"eligible_years":years,
                     "eligible_by_year":{str(y):sorted(v["colony"] for v in valid if v["season_start"]==y) for y in years},
                     "chick_dates_by_year":{str(y):sorted(set(v["chick_count_date"] for v in valid if v["season_start"]==y)) for y in years},
                     "source_colony_labels":sorted(set(v["colony"] for v in r))}
    common=sorted(set.intersection(*(set(v["eligible_years"]) for v in by.values())))
    for sp,v in by.items():
        v["fixed_literal_labels_on_penguin_common_years"]=sorted(set.intersection(*(set(v["eligible_by_year"][str(y)]) for y in common))) if common else []
    o["penguins"]=by;o["penguin_common_years_before_environment_gate"]=common
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2)+"\n")
    print(json.dumps(o,ensure_ascii=False))
if __name__=="__main__": main()
