"""Same-summer descriptive support comparison; no causal or spatial overlay."""
import calendar,csv,datetime as dt,hashlib,io,json,re,zipfile
from pathlib import Path
from statistics import mean
from collections import defaultdict
import requests
import pandas as pd
from analyze import read,audit_year,metric,integer,selftest
OUT=Path("build/signy_matched_summer")
EARLY=(2010,2012,2013,2014)
LATE=(2016,2017,2018,2019,2020)
YEARS=EARLY+LATE
SOURCES={
 "seals":("8e910ac8-6f52-4548-bbcb-78474b559294","Signy_seal_annual_counts_by_area.csv","58f87d83afdd78f30daf5489f45f4221af30b1e413090c3d9a5493e602eacb3a"),
 "Adelie":("daf2c4fd-c1e3-4e65-851f-d11f02c5b69d","signy_adelie_breeding_success.csv","585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62"),
 "Chinstrap":("d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9","signy_chinstrap_breeding_success.csv","e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b"),
 "Gentoo":("883c6b40-024e-41e8-9c3e-2668a44b5751","signy_gentoo_breeding_success.csv","53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b")
}
ROSTER={"Adelie":["A2","A3","A4"],"Chinstrap":["C15","C16","C17","C79","C80"],"Gentoo":["SIGNY_SOURCE_AGGREGATE"]}
INCOMPLETE=re.compile(r"\b(not counted|not surveyed|incomplete|not visited|no count|missing data)\b",re.I)
def sha(b):return hashlib.sha256(b).hexdigest()
def get(sp):
    entry,suffix,pin=SOURCES[sp]
    u="https://ramadda.data.bas.ac.uk/repository/entry/show?entryid="+entry+"&output=zip.tree"
    with requests.get(u,timeout=(15,90),stream=True) as r:
        r.raise_for_status();chunks=[];n=0
        for c in r.iter_content(65536):
            n+=len(c)
            if n>10_000_000:raise ValueError("bounded intake")
            chunks.append(c)
    b=b"".join(chunks)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:raise ValueError("ZIP CRC")
        m=[p for p in z.namelist() if p.endswith("/"+suffix) or p==suffix]
        if len(m)!=1:raise ValueError("member identity")
        raw=z.read(m[0])
    if sha(raw)!=pin:raise ValueError("pinned member drift "+sp)
    return b,raw,{"doi":"10.5285/"+entry,"member":m[0],"csv_sha256":pin,"zip_sha256":sha(b)}
def season(s):
    m=re.fullmatch(r"(\d{4})\s*[-/]\s*(\d{2}|\d{4})",s)
    if not m:return None
    y=int(m[1]);return y if int(m[2])==(y+1 if len(m[2])==4 else (y+1)%100) else None
def parse_date(s):
    x=pd.to_datetime(s,dayfirst=not bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}",s)),errors="coerce")
    return x.date() if pd.notna(x) else None
def penguin(sp,raw):
    for enc in ("utf-8-sig","latin-1"):
        try:txt=raw.decode(enc);break
        except UnicodeDecodeError:pass
    it=csv.reader(io.StringIO(txt));h=[v.strip() for v in next(it)]
    needed={"SEASON","TOTAL_NUMBER_OF_PAIRS","TOTAL_NUMBER_OF_CHICKS","DATE_PAIR_COUNT","DATE_CHICK_COUNT","COMMENTS"}
    if sp!="Gentoo":needed.add("COLONY")
    if not needed<=set(h) or len(h)!=len(set(h)):raise ValueError("schema "+sp)
    values={};dates={};repairs={"overflow_comment_rows":0,"short_rows_padded":0}
    for row in it:
        if not any(v.strip() for v in row):continue
        if len(row)>len(h):
            if h[-1]!="COMMENTS":raise ValueError("unexpected ragged row")
            row=row[:len(h)-1]+[",".join(row[len(h)-1:])]
            repairs["overflow_comment_rows"]+=1
        if len(row)<len(h):
            row+=[""]*(len(h)-len(row));repairs["short_rows_padded"]+=1
        r=dict(zip(h,map(str.strip,row)))
        y=season(r["SEASON"])
        if y is None or y+1 not in YEARS:continue
        col=r["COLONY"] if sp!="Gentoo" else "SIGNY_SOURCE_AGGREGATE"
        if col not in ROSTER[sp]:continue
        k=(y+1,col)
        if k in values:raise ValueError("duplicate "+str(k))
        a=integer(r["TOTAL_NUMBER_OF_PAIRS"]);b=integer(r["TOTAL_NUMBER_OF_CHICKS"])
        nd,cd=parse_date(r["DATE_PAIR_COUNT"]),parse_date(r["DATE_CHICK_COUNT"])
        if a is None or a<1 or b is None or not(nd and cd and dt.date(y,9,1)<=nd<cd<=dt.date(y+1,2,calendar.monthrange(y+1,2)[1])) or INCOMPLETE.search(r["COMMENTS"]):raise ValueError("invalid target row "+str((sp,k)))
        values[k]=a;dates[str(k)]={"pair_date":str(nd),"chick_date":str(cd)}
    if set(values)!={(y,c) for y in YEARS for c in ROSTER[sp]}:raise ValueError("fixed coverage "+sp)
    return {y:[values[y,c] for c in ROSTER[sp]] for y in YEARS},{"repairs":repairs,"dates":dates}
def contrast(panel,spatial):
    annual={}
    for y in YEARS:
        x=panel[y];n=sum(x)
        if spatial and n<2:raise ValueError("low total")
        annual[y]={"counts":x,"total":n}
        if spatial:
            h,eff=metric(x);annual[y].update(H=h,effective_fraction=eff/len(x))
    def stat(a,b):
        am,bm=mean(annual[y]["total"] for y in a),mean(annual[y]["total"] for y in b)
        out={"early_mean_count":am,"late_mean_count":bm,"count_ratio":bm/am}
        if spatial:
            for key in ("H","effective_fraction"):
                va,vb=mean(annual[y][key] for y in a),mean(annual[y][key] for y in b)
                out.update({"early_"+key:va,"late_"+key:vb,"delta_"+key:vb-va})
        return out
    r=stat(EARLY,LATE)
    variants=[stat(tuple(y for y in EARLY if y!=k),LATE) for k in EARLY]+[stat(EARLY,tuple(y for y in LATE if y!=k)) for k in LATE]
    r["loo_ranges"]={k:[min(v[k] for v in variants),max(v[k] for v in variants)] for k in ("count_ratio","delta_H","delta_effective_fraction") if k in r}
    r["annual"]=annual;return r
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r={"status":"BLOCKED_SUPPORT_OR_SOURCE","early_february_years":EARLY,"late_february_years":LATE,"source_receipts":{},"rosters":ROSTER,"independent_islands":1,"causal_model":False}
    try:
        selftest()
        b,raw,meta=get("seals");r["source_receipts"]["seals"]=meta
        path=OUT/"seals.source.zip";path.write_bytes(b)
        rows,_=read(path);path.unlink()
        by=defaultdict(list)
        for row in rows:by[int(row["Year"])].append(row)
        panel={sp:{} for sp in ("fur","elephant","weddell")}
        for y in YEARS:
            audit,c=audit_year(by[y],y)
            if not audit["eligible"]:raise ValueError("seal audit "+str(audit))
            for sp in panel:
                if sp not in c:raise ValueError("seal species support")
                panel[sp][y]=c[sp]
        r["penguin_structure"]={}
        for sp in ROSTER:
            b,raw,meta=get(sp);r["source_receipts"][sp]=meta
            panel[sp],r["penguin_structure"][sp]=penguin(sp,raw)
        r["results"]={sp:contrast(v,sp!="Gentoo") for sp,v in panel.items()}
        r["status"]="MATCHED_SUMMER_DESCRIPTIVE_ONLY"
    except Exception as e:r["error"]=str(e)
    (OUT/"result.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({k:v for k,v in r.items() if k!="penguin_structure"},ensure_ascii=False))
if __name__=="__main__":main()
