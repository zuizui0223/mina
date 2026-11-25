"""Acquire exact published spectral library and describe source schema only."""
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from openpyxl import load_workbook
BASE="https://datashare.ed.ac.uk"
ITEM="8140387f-ae94-4ab0-a7ea-bd0339c748ea"
API=BASE+"/server/api/core/items/"+ITEM
DOI="10.7488/ds/7720"
def digest(b,kind="sha256"):return hashlib.new(kind,b).hexdigest()
def get(url,limit=30_000_000):
    if urlparse(url).scheme!="https" or urlparse(url).hostname not in ("datashare.ed.ac.uk","www.datashare.ed.ac.uk"):raise ValueError("unexpected source URL")
    with requests.get(url,timeout=(15,90),stream=True) as r:
        r.raise_for_status()
        chunks=[];n=0
        for c in r.iter_content(1<<20):
            n+=len(c)
            if n>limit:raise ValueError("bounded intake exceeded")
            chunks.append(c)
        return b"".join(chunks)
def js(url):
    return json.loads(get(url,4_000_000))
def link(x,name):
    u=x["_links"][name]["href"]
    return urljoin(BASE,u.split("{")[0])
def collection(url,key):
    seen=set()
    for _ in range(20):
        if url in seen:raise ValueError("pagination cycle")
        seen.add(url)
        j=js(url)
        for o in j.get("_embedded",{}).get(key,[]):yield o
        nxt=j.get("_links",{}).get("next",{}).get("href")
        if not nxt:return
        url=urljoin(BASE,nxt)
    raise ValueError("pagination bound exceeded")
TOKENS=re.compile(r"species|taxon|genus|group|class|sample|specimen|individual|replicate|locality|site|location|date|hydration|wet|dry|wavelength|reflectance",re.I)
TAXA=re.compile(r"prasiola|deschampsia|colobanthus|sanionia|andreaea|polytrich|moss|lichen|algae|alga|bryophyte|rock",re.I)
def csv_schema(b):
    for enc in ("utf-8-sig","cp1252"):
        try:s=b.decode(enc,errors="strict");break
        except UnicodeDecodeError:continue
    try:d=csv.Sniffer().sniff(s[:8192],delimiters=",;\t")
    except csv.Error:d="excel"
    rr=csv.reader(io.StringIO(s),d)
    h=next(rr,[])
    return {"header":h[:180],"header_columns":len(h),"rows":sum(1 for r in rr if r and any(x.strip() for x in r)),"candidate_metadata_columns":[x for x in h if TOKENS.search(x)][:80],"encoding":enc}
def inventory(name,b,depth=0):
    r={"name":name,"bytes":len(b),"sha256":digest(b),"candidate_name_labels":TAXA.findall(name)}
    ext=Path(name).suffix.lower()
    try:
        if ext in (".csv",".tsv"):r["table"]=csv_schema(b)
        elif ext in (".xlsx",".xlsm"):
            w=load_workbook(io.BytesIO(b),read_only=True,data_only=True);r["sheets"]=[]
            for s in w:
                h=[str(x) for x in next(s.values,())]
                r["sheets"].append({"name":s.title,"rows":s.max_row,"columns":s.max_column,"header":h[:180],"candidate_metadata_columns":[x for x in h if TOKENS.search(x)][:80]})
            w.close()
        elif ext==".zip" and depth<2:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                if z.testzip() is not None or sum(x.file_size for x in z.infolist())>180_000_000:raise ValueError("ZIP integrity/size")
                r["members"]=[inventory(x.filename,z.read(x),depth+1) for x in z.infolist() if not x.is_dir()]
        elif ext in (".txt",".md") and "readme" in name.lower():
            for enc in ("utf-8-sig","cp1252"):
                try:
                    s=b.decode(enc,errors="strict");break
                except UnicodeDecodeError:continue
            r["readme_lines"]=len(s.splitlines())
            r["metadata_context"]=[[i+1,x[:800]] for i,x in enumerate(s.splitlines()) if TOKENS.search(x) or TAXA.search(x)][:150]
        elif ext==".txt":r["text_lines"]=len(b.splitlines())
    except Exception as e:r["inspection_error"]=str(e)
    return r
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    r={"status":"SOURCE_BLOCKED","doi":DOI,"item":ITEM,"api":API,"files":[],"classifier_fitted":False,"ecological_join_executed":False}
    try:
        j=js(API);meta=j.get("metadata",{})
        identifiers=[v.get("value","") for k,vs in meta.items() if k.startswith("dc.identifier") for v in vs]
        r["identity"]={"uuid":j.get("uuid"),"name":j.get("name"),"handle":j.get("handle"),"identifiers":identifiers}
        if j.get("uuid")!=ITEM or DOI not in " ".join(identifiers).lower() or "spectral library" not in str(j.get("name","")).lower():raise ValueError("publisher identity mismatch")
        for bundle in collection(link(j,"bundles"),"bundles"):
            if bundle.get("name")!="ORIGINAL":continue
            for bit in collection(link(bundle,"bitstreams"),"bitstreams"):
                name=bit.get("name","");record={"name":name,"uuid":bit.get("uuid"),"size":bit.get("sizeBytes"),"publisher_checksum":bit.get("checkSum")};r["files"].append(record)
                try:
                    b=get(link(bit,"content"));check=bit.get("checkSum") or {}
                    if record["size"] is not None and len(b)!=record["size"]:raise ValueError("byte count mismatch")
                    if check.get("value"):
                        algo=str(check.get("checkSumAlgorithm","")).lower().replace("-","")
                        if digest(b,algo).lower()!=str(check["value"]).lower():raise ValueError("publisher checksum mismatch")
                    else:raise ValueError("publisher checksum unavailable")
                    record.update(verified=True,inventory=inventory(name,b))
                except Exception as e:record.update(verified=False,error=str(e))
        if not r["files"]:raise ValueError("no original bitstreams")
        r["status"]="PUBLISHER_SOURCE_INVENTORIED_REVIEW_REQUIRED" if all(f.get("verified") for f in r["files"]) else "PARTIAL_SOURCE_BLOCKED"
    except Exception as e:r["error"]=str(e)
    (a.out/"spectral_source_receipt.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":r["status"],"identity":r.get("identity"),"files":[{k:v for k,v in f.items() if k!="inventory"} for f in r["files"]],"error":r.get("error")},ensure_ascii=False))
if __name__=="__main__":main()
