"""Inspect source conventions, never join penguin outcomes or change onset thresholds."""
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
import requests
from prepare_panel import read,PINS
DOI="10.5281/zenodo.15544182"
API="https://zenodo.org/api/records/15544182"
# Version-specific record, verified against the publisher's landing page.
CONCEPT_DOI="10.5281/zenodo.15544181"
FILES={"getDay.R":"be753a71556c0344c109135cb2557cd6","ice_variables_Signy.r":"3754f64588feab4436e21851547b15c9","iceGam.R":"cd297909dfeceec25d6a047e2ad13903","iceVariables.csv":"ed47049fed0250658a69042e293022e5","icevars.R":"d402e6c98c0d5301d6e37424108e5f0c"}
PAT=re.compile(r"advance|retreat|ice_days|persistence|day.of.year|yday|julian|yearday|Feb.?16|March.?15|\b410\b|\b411\b|iceyear|ice.year",re.I)
def sha(b): return hashlib.sha256(b).hexdigest()
def code_snippets(name,b):
    lines=b.decode("utf-8",errors="replace").splitlines()
    ix=set()
    for i,s in enumerate(lines):
        if PAT.search(s): ix.update(range(max(0,i-3),min(len(lines),i+4)))
    return {"name":name,"sha256":sha(b),"line_count":len(lines),"matching_context":[[i+1,lines[i][:1000]] for i in sorted(ix)[:800]]}
def code_audit(out):
    rec={"doi":DOI,"concept_doi":CONCEPT_DOI,"api":API,"status":"AUTHOR_CODE_UNAVAILABLE","files":[],"snippets":[]}
    # The original DOI is a concept DOI; the versioned record is 15544182.
    # Pin file names and MD5 checksums independently published on its landing page.
    try:
        r=requests.get(API,timeout=(15,30));r.raise_for_status();j=r.json()
        rec["title"]=j.get("metadata",{}).get("title")
        rec["record_doi"]=j.get("doi");rec["record_id"]=j.get("id")
        if str(j.get("id"))!="15544182" or rec["record_doi"]!=DOI or not re.search(r"seal|Signy|Weddell",str(rec["title"]),re.I):
            raise ValueError("versioned record identity/title not verified")
        (out/"zenodo_record.json").write_text(json.dumps(j,indent=2)+"\n")
        rec["api_identity_verified"]=True
    except Exception as e:
        rec["api_identity_verified"]=False
        rec["api_error"]=str(e)
    source=out/"author_original"
    source.mkdir(exist_ok=True)
    for name,md5 in FILES.items():
        urls=[f"https://zenodo.org/records/15544182/files/{name}?download=1",f"{API}/files/{name}/content"]
        item={"name":name,"expected_md5":md5,"attempts":[]}
        rec["files"].append(item)
        for url in urls:
            try:
                rr=requests.get(url,timeout=(15,35));rr.raise_for_status();b=rr.content
                if hashlib.md5(b).hexdigest()!=md5:raise ValueError("published file checksum mismatch")
                (source/name).write_bytes(b)
                item.update(url=url,sha256=sha(b),bytes=len(b),verified=True)
                if name.lower().endswith(".r"):rec["snippets"].append(code_snippets(name,b))
                else:
                    rows=list(csv.reader(io.StringIO(b.decode("utf-8-sig"))))
                    rec["author_csv_header"]=rows[0]
                    rec["author_csv_rows"]=len(rows)-1
                    rec["author_csv_2013"]=[row for row in rows[1:] if "2013" in row]
                break
            except Exception as e:item["attempts"].append({"url":url,"error":str(e)})
    complete=all(x.get("verified") for x in rec["files"])
    rec["status"]="AUTHOR_CODE_AND_TABLE_VERIFIED_REVIEW_REQUIRED" if complete else "AUTHOR_CODE_PARTIAL_OR_UNAVAILABLE"
    return rec
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    # Only the open environmental table, not penguin or seal numerical outcomes.
    rows=read(a.source/"ice.zip","Signy_sea_ice_variables.csv","ice")
    with zipfile.ZipFile(a.source/"ice.zip") as z:
        n=[x for x in z.namelist() if x.endswith("Signy_sea_ice_variables.csv")][0];b=z.read(n)
    assert sha(b)==PINS["ice"]
    (a.out/"original_bas_ice.csv").write_bytes(b)
    rec={"status":"SOURCE_DIAGNOSTIC_ONLY","original_sha256":sha(b),"year_count":len(rows),
         "row_2013":[r for r in rows if r["Year"]=="2013"],"onset_outside_46_411":[r for r in rows if float(r["advance [a]"])!=0 and not 46<=float(r["advance [a]"])<=411],
         "all_year_ice_events":[{k:r[k] for k in ("Year","advance [a]","retreat [b]","ice_days [c]","persistence [d]")} for r in rows],
         "calendar_metadata_conflict":"embedded CSV cites March 15; BAS web lineage and Dunn 2025 say February 16; do not guess offset or recode",
         "author_code":code_audit(a.out),"joint_numerical_outcomes_opened":False}
    (a.out/"calendar_diagnostic.json").write_text(json.dumps(rec,indent=2)+"\n")
    print(json.dumps({k:v for k,v in rec.items() if k not in ("author_code","all_year_ice_events")}))
    print(json.dumps({k:v for k,v in rec["author_code"].items() if k!="snippets"}))
if __name__=="__main__":main()
