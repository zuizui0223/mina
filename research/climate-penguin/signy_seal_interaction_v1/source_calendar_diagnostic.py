"""Inspect source conventions, never join penguin outcomes or change onset thresholds."""
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
import requests
from prepare_panel import read,PINS
DOI="10.5281/zenodo.15544181"
API="https://zenodo.org/api/records/15544181"
PAT=re.compile(r"advance|retreat|ice_days|persistence|day.of.year|yday|julian|yearday|Feb.?16|March.?15|\b410\b|\b411\b|iceyear|ice.year",re.I)
def sha(b): return hashlib.sha256(b).hexdigest()
def code_snippets(name,b):
    lines=b.decode("utf-8",errors="replace").splitlines()
    ix=set()
    for i,s in enumerate(lines):
        if PAT.search(s): ix.update(range(max(0,i-3),min(len(lines),i+4)))
    return {"name":name,"sha256":sha(b),"line_count":len(lines),"matching_context":[[i+1,lines[i][:1000]] for i in sorted(ix)[:800]]}
def code_audit(out):
    rec={"doi":DOI,"api":API,"status":"AUTHOR_CODE_UNAVAILABLE","files":[],"snippets":[]}
    try:
        r=requests.get(API,timeout=(15,45));r.raise_for_status();j=r.json()
        rec["title"]=j.get("metadata",{}).get("title")
        rec["record_doi"]=j.get("doi");rec["record_id"]=j.get("id")
        if str(j.get("id"))!="15544181" or not re.search(r"seal|Signy|Weddell",str(rec["title"]),re.I):
            raise ValueError("record identity/title not verified")
        (out/"zenodo_record.json").write_text(json.dumps(j,indent=2)+"\n")
        for f in j.get("files",[]):
            name=f["key"];size=f.get("size",0);item={"name":name,"size":size,"checksum":f.get("checksum")}
            rec["files"].append(item)
            if size>60_000_000 or not name.lower().endswith((".r",".rmd",".qmd",".zip",".txt")):continue
            url=f.get("links",{}).get("self")
            if not url or not url.startswith("https://zenodo.org/"):continue
            try:
                rr=requests.get(url,timeout=(15,60));rr.raise_for_status();b=rr.content
                item["download_sha256"]=sha(b)
                if item["checksum"] and item["checksum"].startswith("md5:") and hashlib.md5(b).hexdigest()!=item["checksum"][4:]:raise ValueError("checksum drift")
                if name.lower().endswith(".zip"):
                    with zipfile.ZipFile(io.BytesIO(b)) as z:
                        for info in z.infolist():
                            if info.file_size<=3_000_000 and info.filename.lower().endswith((".r",".rmd",".qmd",".txt")):
                                rec["snippets"].append(code_snippets(info.filename,z.read(info)))
                else:rec["snippets"].append(code_snippets(name,b))
            except Exception as e:item["error"]=str(e)
        rec["status"]="AUTHOR_CODE_RETRIEVED_REVIEW_REQUIRED" if rec["snippets"] else "AUTHOR_CODE_NO_RELEVANT_FILES"
    except Exception as e:rec["error"]=str(e)
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
