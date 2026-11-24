"""Pre-outcome source mapping and deterministic execution gate for frozen V1."""
import argparse,csv,datetime as dt,hashlib,io,json,re,statistics,sys,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/climate_penguin"))
from signy_trispecies_stage_source_v1 import source_extract
from analyze import run

PINS={"seals":"58f87d83afdd78f30daf5489f45f4221af30b1e413090c3d9a5493e602eacb3a","ice":"b04bbb3bc593c67c070b18497acb6f96d52cbed6914952d814741c30206b5835"}
def digest(b): return hashlib.sha256(b).hexdigest()
def read(path,suffix,kind):
    with zipfile.ZipFile(path) as z:
        names=[x for x in z.namelist() if x.endswith(suffix)]
        if len(names)!=1: raise ValueError("ambiguous original file")
        raw=z.read(names[0])
    if digest(raw)!=PINS[kind]: raise ValueError("source digest drift")
    rows=list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
    i=next(i for i,r in enumerate(rows) if r and r[0].strip()=="Year")
    if any(len(r)!=len(rows[i]) for r in rows[i+1:] if any(v.strip() for v in r)): raise ValueError("ragged source")
    return [dict(zip(rows[i],map(str.strip,r))) for r in rows[i+1:] if any(v.strip() for v in r)]
def num(s):
    try:
        v=float(s.replace(",",""))
        return v if v>=0 and v<float("inf") else None
    except (ValueError,AttributeError): return None
def seal_gate(rows):
    by=defaultdict(list)
    for r in rows: by[int(r["Year"])].append(r)
    result={}; audit={}
    for y,rr in sorted(by.items()):
        if not 1997<=y<=2020: continue
        zone=defaultdict(list); bad=[]; specials=[]; duplicates=[]
        months=sorted({r["Month"].upper() for r in rr if r["Month"]})
        for r in rr:
            z=r["Zone"]; a=r["Area"]; v=num(r["Number_of_fur_seals"])
            if z not in "123456" or len(z)!=1 or not a or re.search(r"\b(total|subtotal|sum|all zones|whole island)\b",a,re.I):
                specials.append({"zone":z,"area":a,"has_count":v is not None,"comments":r["Comments"]})
                # Do not silently mix totals with components.
                continue
            if v is None or v%1: bad.append({"zone":z,"area":a,"comments":r["Comments"]})
            zone[z].append((a,v))
        for z,rs in zone.items():
            names=Counter(re.sub(r"\s+"," ",a.casefold()) for a,v in rs)
            duplicates.extend([{"zone":z,"area":a,"n":n} for a,n in names.items() if n>1])
        reason=[]
        if set(zone)!=set("123456"): reason.append("six_zones_not_complete")
        if set(months)-{"FEB"}: reason.append("non_feb_month")
        if not months: reason.append("no_explicit_feb_month")
        if bad: reason.append("missing_or_invalid_count")
        if duplicates: reason.append("duplicate_area_within_zone")
        if specials: reason.append("aggregate_or_unlabelled_rows_require_review")
        audit[str(y)]={"rows":len(rr),"months":months,"zones":{z:len(rs) for z,rs in zone.items()},
                       "zone_area_labels":{z:[a for a,v in rs] for z,rs in zone.items()},
                       "missing":bad,"duplicates":duplicates,"specials":specials,"reasons":reason}
        if not reason: result[y]=int(sum(v for rs in zone.values() for a,v in rs))
    return result,audit

def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    seals,sa=seal_gate(read(a.source/"seals.zip","Signy_seal_annual_counts_by_area.csv","seals"))
    ice={}
    for r in read(a.source/"ice.zip","Signy_sea_ice_variables.csv","ice"):
        y=int(r["Year"])
        if y in ice: raise ValueError("duplicate ice year")
        ice[y]=(num(r["ice_days [c]"]),num(r["retreat [b]"]))
    # Official BAS online lineage: annual window begins Feb 16 of year 1.
    # Use only winter intervals ending before the earliest measured chick stage;
    # no relabeling to previous/next year to increase support.
    groups={};sources={}
    for sp in ("Adelie","Chinstrap","Gentoo"):
        rr,_,m=source_extract(sp,a.source/(sp.lower()+".zip"))
        sources[sp]=m
        by=defaultdict(dict)
        for r in rr:
            if r["reported_chicks_per_pair"] is not None and r["nest_before_chicks"]:
                by[r["season_start"]][r["colony"]]=r
        groups[sp]=by
    common=sorted(set.intersection(*(set(g) for g in groups.values())))
    candidates=[y for y in common if y+1 in seals and y in ice]
    time_audit={};eligible=[]
    for y in candidates:
        n,ret=ice[y]
        endpoint=min(dt.date.fromisoformat(r["chick_count_date"]) for g in groups.values() for r in g[y].values())
        # source calendar day 1 = Jan 1 of year 1; extended DOY into year 2.
        end=dt.date(y,1,1)+dt.timedelta(days=int(ret)-1) if ret is not None and ret>0 and ret%1==0 and ret<=411 else None
        ok=n is not None and n<=366 and ((n==0 and ret==0) or (end is not None and end<endpoint))
        time_audit[str(y)]={"earliest_chick_date":str(endpoint),"ice_retreat_date":str(end) if end else None,"pre_endpoint_ice":bool(ok)}
        if ok: eligible.append(y)
    roster={sp:sorted(set.intersection(*(set(g[y]) for y in eligible))) if eligible else [] for sp,g in groups.items()}
    roster_ok=len(roster["Adelie"])>=3 and len(roster["Chinstrap"])>=3 and roster["Gentoo"]==["SIGNY_SOURCE_AGGREGATE"] and all(re.fullmatch(r"[AC]\d+",k) for sp in ("Adelie","Chinstrap") for k in roster[sp])
    receipt={"status":"SUPPORT_REVIEW","seals_annual_structure":sa,"ice_calendar_source":"https://data.bas.ac.uk/full-record.php?id=GB%2FNERC%2FBAS%2FPDC%2F02065",
             "source_pins":PINS,"penguin_sources":sources,"penguin_common_years":common,
             "seal_eligible_years":sorted(seals),"common_before_ice_timing":candidates,"ice_timing":time_audit,
             "eligible_years":eligible,"fixed_roster":roster,"roster_ok":roster_ok,
             "minimum_years":20,"minimum_calendar_blocks":6,"numerical_join_executed":False}
    # Exact schema and structural mapping reviewed; keep primary blocked if support
    # falls short. No post hoc choice of alternative ice year, roster or thresholds.
    if len(eligible)>=20 and len({(y-1996)//4 for y in eligible})>=6 and roster_ok:
        panel=[]
        for y in eligible:
            row={"season_start":y,"fur_seals_feb":seals[y+1],"antecedent_ice_days":ice[y][0]}
            for sp,g in groups.items():
                row[sp.lower()]=statistics.median(g[y][k]["reported_chicks_per_pair"] for k in roster[sp])
            panel.append(row)
        df=pd.DataFrame(panel)
        dest=a.out/"panel.csv";df.to_csv(dest,index=False)
        receipt.update(status="REVIEWED_SOURCE_CALENDAR_ROSTER_PASS",panel_sha256=digest(dest.read_bytes()),numerical_join_executed=True)
        try:
            results=run(df);results["panel_sha256"]=receipt["panel_sha256"]
            (a.out/"result.json").write_text(json.dumps(results,indent=2)+"\n")
        except ValueError as exc:
            receipt.update(status="MODEL_GATE_BLOCKED",model_error=str(exc))
    else: receipt["status"]="FROZEN_SUPPORT_GATE_BLOCKED"
    (a.out/"panel_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:receipt[k] for k in ("status","seal_eligible_years","common_before_ice_timing","eligible_years","fixed_roster","numerical_join_executed")}))
if __name__=="__main__": main()
