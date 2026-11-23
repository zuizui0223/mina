#!/usr/bin/env python3
"""Acquire original official Duffy2024 Figshare files and live MAPPPD v5 all-count CSV.
Audit-only: inspect physical and census data grain, not biological coefficients.
"""
from __future__ import annotations
import csv,hashlib,io,json,os,re,urllib.request,zipfile,datetime
from pathlib import Path
import pandas as pd

FILES={
 "duffy_data.zip":("https://ndownloader.figshare.com/files/43527807",41946,"e578281f0116c88235fe5aa536c34b3f"),
 "duffy_results.zip":("https://ndownloader.figshare.com/files/43527810",18510306,"4f31340b7a16bcf5ca9e9a029acc2799"),
 "duffy_Rmd.Rmd":("https://ndownloader.figshare.com/files/43527798",15593,"f2fb0042d4112f1228cade1a72e0a694"),
 "duffy_methods.html":("https://ndownloader.figshare.com/files/43527795",673161,"eb50ed419738925abd9c8767996ddfa0"),
}
COUNTS="https://penguinmap.com/mapppd/DownloadAll"
def fetch(url,path,size_cap=60_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"Antarctic-Open-Data-Research/1.0","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=130) as response, path.open("wb") as out:
        n=0
        for b in iter(lambda:response.read(1024*1024),b""):
            out.write(b);n+=len(b)
            if n>size_cap:raise ValueError(f"Size cap exceeded: {url}")
    return n
def md5(path):
    h=hashlib.md5()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(2**20),b""):h.update(b)
    return h.hexdigest()
def zip_manifest(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None, "Zip CRC invalid"
        records=[]
        for v in z.infolist():
            entry={"path":v.filename,"uncompressed_bytes":v.file_size,"compressed_bytes":v.compress_size}
            if not v.is_dir() and v.file_size<1_000_000 and v.filename.lower().endswith((".csv",".tsv")):
                try:
                    f=pd.read_csv(io.BytesIO(z.read(v.filename)),sep=None,engine="python")
                    entry["rows"]=len(f);entry["columns"]=list(map(str,f.columns))[:35]
                    entry["first2"]=f.head(2).where(pd.notnull(f.head(2)),None).to_dict("records")
                except Exception as e:entry["csv_parse_problem"]=str(e)[:160]
            records.append(entry)
    return records
def main():
    root=Path("build/polynya44_data");root.mkdir(parents=True,exist_ok=True)
    raw=root/"raw";raw.mkdir(exist_ok=True)
    report={"timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "origin":"Duffy 2024 Figshare 24768654; MAPPPD v5 2026",
            "not_a_biological_test":True}
    for name,(url,size,expected_md5) in FILES.items():
        p=raw/name;n=fetch(url,p)
        h=md5(p)
        if size!=n or h!=expected_md5:raise ValueError(f"Author file identity changed {name}: expected {size}/{expected_md5}, actual {n}/{h}")
        entry={"source":url,"size":n,"md5":h,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
        if name.endswith(".zip"):entry["members"]=zip_manifest(p)
        report[name]=entry
        print("DUFFY VERIFIED",name,n,"members",len(entry.get("members",[])))
        if name.endswith(".zip"):print(" DUFFY MEMBER NAMES:",[v["path"] for v in entry["members"]][:110])
    p=raw/"mapppd_v5_all_counts.csv"
    n=fetch(COUNTS,p)
    if p.read_bytes()[:1000].lstrip().lower().startswith((b"<!doctype",b"<html")):
        raise ValueError("Official MAPPPD All counts returned HTML instead of CSV")
    df=pd.read_csv(p,low_memory=False)
    if len(df)<1000:raise ValueError(f"Too few original MAPPPD census records {len(df)}")
    record={"source":COUNTS,"bytes":n,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "rows":len(df),"columns":list(map(str,df.columns)),
            "first3":df.head(3).where(pd.notnull(df.head(3)),None).astype(str).to_dict("records"),
            "interesting_column_value_counts":{}}
    for col in df:
        if re.search(r"species|count.?type|method|unit|penguin|season|year|source|status|quality|estimate|breeding|census|site",str(col),re.I):
            uniq=df[col].nunique(dropna=True)
            if uniq<=40:record["interesting_column_value_counts"][str(col)]=df[col].value_counts(dropna=False).head(30).astype(int).to_dict()
            else:record["interesting_column_value_counts"][str(col)]={"nunique":int(uniq),"nulls":int(df[col].isna().sum()),"examples":df[col].dropna().astype(str).head(6).tolist()}
    report["mapppd_v5_original_counts"]=record
    (root/"raw_source_identity_and_schema.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str)+"\n")
    print("MAPPPD VERIFIED",len(df),"rows",n,"bytes","COLUMNS",df.columns.tolist())
    print("MAPPPD metadata",json.dumps(record["interesting_column_value_counts"],default=str)[:7000])
if __name__=="__main__":main()
