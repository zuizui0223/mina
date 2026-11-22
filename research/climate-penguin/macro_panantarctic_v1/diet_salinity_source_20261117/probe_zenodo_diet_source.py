#!/usr/bin/env python3
"""Publisher-original Zenodo file-inventory gate. Metadata only; no biological effect claim."""
import argparse,hashlib,json,sys,urllib.request
from pathlib import Path
REC=17409948
URL=f"https://zenodo.org/api/records/{REC}"
HEADERS={"User-Agent":"mina-source-audit/0.1 (research provenance; zuizui0223/mina)","Accept":"application/json"}
def get_record():
    req=urllib.request.Request(URL,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=35) as resp:
        if resp.status!=200: raise RuntimeError(f"Unexpected HTTP {resp.status}")
        raw=resp.read(20_000_001)
        if len(raw)>20_000_000: raise RuntimeError("Metadata larger than cap")
    return json.loads(raw)
def normalize(record):
    if str(record.get("id"))!=str(REC): raise ValueError("Record ID mismatch")
    rows=[]
    for f in record.get("files",[]):
        links=f.get("links",{}) or {}
        rows.append({"key":f.get("key",""),"size_bytes":f.get("size"),
                     "checksum":f.get("checksum",""),
                     "has_content_link":bool(links.get("content") or links.get("self"))})
    return {"status":"ZENODO_METADATA_RETRIEVED_NO_DATA_DOWNLOADED",
            "record_id":REC,"doi":record.get("doi") or record.get("pids",{}).get("doi",{}).get("identifier"),
            "title":record.get("metadata",{}).get("title"),
            "access_status":record.get("metadata",{}).get("access_right") or record.get("access",{}).get("record"),
            "file_count":len(rows),"file_inventory":rows,
            "candidate_under50mb":[x["key"] for x in rows if x["has_content_link"] and isinstance(x["size_bytes"],int) and 0<x["size_bytes"]<=50_000_000],
            "ecological_inference":"NOT RUN: no diet values, same-site seasons, ocean-cell alignment or salinity effect"}
def verify_md5_bytes(raw,check):
    if not check.startswith("md5:"): return "NOT_MD5"
    if hashlib.md5(raw).hexdigest()!=check.split(":",1)[1].lower(): raise ValueError("Wrong publisher MD5")
    return "SOURCE_MD5_MATCH"
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);p.add_argument("--mock")
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    try:
        meta=json.loads(Path(a.mock).read_text()) if a.mock else get_record()
        result=normalize(meta)
    except Exception as e:
        result={"status":"ZENODO_METADATA_NOT_RETRIEVED","record_id":REC,
                "error":f"{type(e).__name__}: {str(e)[:600]}",
                "ecological_inference":"NOT RUN"}
    (out/"original_zenodo_17409948_source_receipt.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="file_inventory"},ensure_ascii=False))
    return 0 if result["status"]=="ZENODO_METADATA_RETRIEVED_NO_DATA_DOWNLOADED" else 2
if __name__=="__main__":sys.exit(main())
