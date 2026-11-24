"""Ross Sea primary-source receipt and old-panel inventory. No abundance outcomes emitted."""
from pathlib import Path
import csv, datetime as dt, hashlib, io, json, re, sys, zipfile
from collections import Counter
from urllib.parse import urlparse
import requests
from openpyxl import load_workbook
import fitz

OUT=Path("build/ross_sea_source_audit")
BASE="https://datastore.landcareresearch.co.nz"
DATASET="fb407798-f399-4875-81a0-51976b4c759c"
DOI="10.7931/kf06-x745"
SOURCES={
 "locations":("f82c5e1d-f04d-446d-9338-e9d0603360f8","colonylocations.xlsx"),
 "metadata":("e081bd92-4e27-44eb-8d5b-065906e97cc2","metadata_aerialsurveydata.pdf"),
 "counts":("5fd490e5-92c4-4f2c-a82e-c66db2320eb1","ross-sea-adelie-penguin-census-record_1981-2024.xlsx"),
}
LEGACY_PIN="add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a"
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(url,limit=30_000_000):
    if urlparse(url).scheme!="https" or urlparse(url).hostname!="datastore.landcareresearch.co.nz":
        raise ValueError("unexpected original URL")
    with requests.get(url,stream=True,timeout=(15,70)) as r:
        r.raise_for_status()
        chunks=[];n=0
        for c in r.iter_content(65536):
            n+=len(c)
            if n>limit:raise ValueError("bounded source intake")
            chunks.append(c)
        return b"".join(chunks),r.url
def yr(v):
    if isinstance(v,(dt.date,dt.datetime)):return v.year if 1981<=v.year<=2024 else None
    if isinstance(v,(float,int)) and not isinstance(v,bool) and int(v)==v and 1981<=v<=2024:return int(v)
    if isinstance(v,str):
        m=re.fullmatch(r"(19[89]\d|20[012]\d)(?:[-/](\d{2}|\d{4}))?",v.strip())
        if m:
            y=int(m[1]);return y if 1981<=y<=2024 else None
    return None
def nonblank(v):return v is not None and (not isinstance(v,str) or bool(v.strip()))
def safe_header(v):
    if not nonblank(v):return None
    if isinstance(v,str) and not re.fullmatch(r"[+\-]?\d+(?:[.,]\d+)?",v.strip()):return v[:180]
    if yr(v) is not None:return str(v)
    return "[numeric]"
def sheet_schema(ws,role):
    if ws.max_row*ws.max_column>2_000_000:raise ValueError("worksheet size bound")
    data=list(ws.values);n=len(data);w=ws.max_column
    # Candidate year axes only, not interpretation of count cells.
    row_years=[];col_years=[]
    for i,row in enumerate(data[:12],1):
        found=[(j+1,yr(v)) for j,v in enumerate(row) if yr(v) is not None]
        if len(found)>=5 and len(set(y for _,y in found))>=5:
            row_years.append({"row":i,"years_by_column":found})
    for j in range(min(12,w)):
        found=[(i+1,yr(row[j])) for i,row in enumerate(data) if yr(row[j]) is not None]
        if len(set(y for _,y in found))>=5:
            col_years.append({"column":j+1,"year_candidates":sorted(set(y for _,y in found)),"candidate_n":len(found)})
    # Header candidates are restricted to first rows; conceal arbitrary numbers.
    headers=[[safe_header(v) for v in row[:min(w,90)]] for row in data[:5]]
    out={"sheet":ws.title,"max_row":n,"max_column":w,"nonempty_rows":sum(any(nonblank(v) for v in r) for r in data),
         "header_candidates":headers,"candidate_year_rows":row_years,"candidate_year_columns":col_years}
    if role=="counts":
        # For each candidate wide year header, summarize presence only. Do not assign missing codes.
        for ax in row_years:
            years=[]
            for j,y in ax["years_by_column"]:
                col=[r[j-1] for r in data[ax["row"]:]]
                years.append({"year":y,"numeric_nonnegative_cells":sum(isinstance(v,(int,float)) and not isinstance(v,bool) and v>=0 for v in col),
                  "blank_cells":sum(not nonblank(v) for v in col),"other_cells":sum(nonblank(v) and not(isinstance(v,(int,float)) and not isinstance(v,bool) and v>=0) for v in col)})
            ax["candidate_presence_only"]=years
    return out
def inspect(name,b,role):
    if name.endswith(".xlsx"):
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            if z.testzip() is not None or "xl/workbook.xml" not in z.namelist():raise ValueError("not intact XLSX")
            if sum(x.file_size for x in z.infolist())>120_000_000:raise ValueError("expanded size bound")
        wb=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
        try:return {"workbook_crc_verified":True,"sheets":[sheet_schema(w,role) for w in wb]}
        finally:wb.close()
    if name.endswith(".pdf"):
        if not b.startswith(b"%PDF"):raise ValueError("not PDF")
        with fitz.open(stream=b,filetype="pdf") as doc:
            # Extract only lines relevant to structure and source semantics; not abundance tables.
            keys=re.compile(r"census|survey|count|estimate|colony|location|missing|blank|year|date|method|incubat|pair|nest|licen|quality|precision|code|photo",re.I)
            lines=[]
            for i,p in enumerate(doc):
                for x in p.get_text().splitlines():
                    if keys.search(x):lines.append([i+1,x[:500]])
            return {"pages":len(doc),"field_definition_text_candidates":lines[:150],"visual_verification":False}
    raise ValueError("unexpected format")
def legacy(path):
    b=Path(path).read_bytes()
    if sha(b)!=LEGACY_PIN:raise ValueError("old panel digest mismatch")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:raise ValueError("old panel CRC")
        rows=list(csv.DictReader(io.StringIO(z.read("source_observed_2456.csv").decode("utf-8-sig"))))
    if len(rows)!=2456 or len({(r["site_id"],r["species"],r["season"]) for r in rows})!=2456:raise ValueError("old roster drift")
    q=[r for r in rows if r["species"]=="ADPE" and r["source_region"]=="Victoria Land"]
    if len(q)!=509 or len({r["site_id"] for r in q})!=50:raise ValueError("old region drift")
    sites={}
    for r in q:
        d=sites.setdefault(r["site_id"],{"site_id":r["site_id"],"site_name":r["site_name"],"latitude":r["latitude"],"longitude":r["longitude"],"years":[],"methods":set()})
        d["years"].append(int(r["season"]));d["methods"].add(r["original_survey_method"])
    for d in sites.values():d["years"].sort();d["methods"]=sorted(d["methods"])
    return {"archive_sha256":LEGACY_PIN,"n_selected_count_rows":2456,"region":"Victoria Land","ADPE_rows":len(q),"ADPE_sites":len(sites),
      "year_counts":dict(sorted(Counter(int(r["season"]) for r in q).items())),"sites":list(sites.values()),
      "scope":"Selected old archive only; absence from these keys does not establish a new independent event."}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r={"status":"SOURCE_SCHEMA_AUDIT_ONLY","doi":DOI,"dataset_id":DATASET,"files":{},"metadata":{},"legacy":None,"independence_established":False,"ecological_fit":False}
    try:r["legacy"]=legacy(sys.argv[1])
    except Exception as e:r["legacy_error"]=str(e)
    resources={}
    try:
        b,u=fetch(BASE+"/api/3/action/package_show?id="+DATASET,3_000_000)
        meta=json.loads(b)
        if not meta.get("success"):raise ValueError("CKAN response unsuccessful")
        m=meta["result"]
        if m.get("id")!=DATASET:raise ValueError("CKAN identity mismatch")
        resources={x["id"]:x for x in m.get("resources",[])}
        if not {v[0] for v in SOURCES.values()}<=set(resources):raise ValueError("CKAN resource identity mismatch")
        r["metadata"]={k:m.get(k) for k in ("id","title","license_id","license_title","metadata_modified","url","version","extras")}
        r["metadata"]["api_sha256"]=sha(b)
    except Exception as e:
        r["metadata_error"]=str(e)
        if "identity mismatch" in str(e):
            r["status"]="BLOCKED_SOURCE_IDENTITY"
            (OUT/"receipt.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n");print(json.dumps(r));return
    for role,(uid,name) in SOURCES.items():
        u=f"{BASE}/dataset/{DATASET}/resource/{uid}/download/{name}"
        d={"url":u,"resource_id":uid,"name":name};r["files"][role]=d
        try:
            b,ru=fetch(u);d.update(bytes=len(b),sha256=sha(b),resolved_url=ru)
            m=resources.get(uid,{})
            d["publisher_metadata"]={k:m.get(k) for k in ("size","hash","last_modified","format","name")}
            h=str(m.get("hash") or "").lower().strip()
            if re.fullmatch(r"[0-9a-f]{32}|[0-9a-f]{40}|[0-9a-f]{64}",h):
                alg={32:"md5",40:"sha1",64:"sha256"}[len(h)]
                if hashlib.new(alg,b).hexdigest()!=h:raise ValueError("publisher checksum mismatch")
                d["publisher_checksum_verified"]=True
            else:d["publisher_checksum_verified"]=False
            d["schema"]=inspect(name,b,role);d["acquired"]=True
        except Exception as e:d.update(acquired=False,error=str(e))
    r["status"]="PUBLISHER_FILES_ACQUIRED_SCHEMA_REVIEW_REQUIRED" if all(x.get("acquired") for x in r["files"].values()) else "PARTIAL_OR_BLOCKED_SOURCE"
    (OUT/"receipt.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":r["status"],"files":{k:{a:b for a,b in v.items() if a!="schema"} for k,v in r["files"].items()},"legacy":{"rows":r["legacy"]["ADPE_rows"],"sites":r["legacy"]["ADPE_sites"]} if r["legacy"] else None,"metadata_error":r.get("metadata_error"),"legacy_error":r.get("legacy_error"),"independence_established":False},ensure_ascii=False))
if __name__=="__main__":main()
