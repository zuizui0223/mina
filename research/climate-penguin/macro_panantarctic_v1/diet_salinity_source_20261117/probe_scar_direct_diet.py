#!/usr/bin/env python3
"""SCAR Southern Ocean Diet Database source-file inventory and small sample schema.
One acquisition-only gate; no unverified diet observations or effects.
"""
import argparse,csv,hashlib,io,json,re,sys,urllib.request,zipfile
from pathlib import Path
REC=20047874
URL=f"https://zenodo.org/api/records/{REC}"
UA={"User-Agent":"mina-SCAR-diet-source-feasibility/0.1 (github.com/zuizui0223/mina)","Accept":"application/json"}
MAX_DOWNLOAD=40_000_000
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=75) as r:
        return json.load(r)
def inspect_csv(data,name):
    try:
        d=io.StringIO(data.decode("utf-8-sig"))
        reader=csv.reader(d)
        head=next(reader)
        small=[]
        for _,row in zip(range(5),reader):
            small.append([str(x)[:80] for x in row[:min(10,len(head))]])
        return {"file":name,"header":head[:120],"sample_first_ten_cells":small}
    except Exception as e:
        return {"file":name,"error":type(e).__name__+":"+str(e)[:300]}
def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    report={"record_id":REC,"source_api":URL,"provenance":"SCAR Southern Ocean Diet and Energetics Database https://diet.apps.aq/",
            "no_biological_effect_estimated":True}
    try:
        meta=get(URL)
        if str(meta.get("id"))!=str(REC):raise ValueError("Original Zenodo record ID mismatch")
        files=[]
        for f in meta.get("files",[]):
            files.append({"key":f.get("key"),"size":f.get("size"),"checksum":f.get("checksum"),
                "content_link":f.get("links",{}).get("content") or f.get("links",{}).get("self")})
        report.update({"status":"SCAR_ZENODO_METADATA_VERIFIED","title":meta.get("metadata",{}).get("title"),
            "doi":meta.get("doi"),"license":meta.get("metadata",{}).get("license"),
            "file_count":len(files),
            "files":[{k:v for k,v in f.items() if k!="content_link"} for f in files]})
        # Only one small, metadata-advertised original source file; never guess that its rows are penguin diets.
        eligible=[f for f in files if f["content_link"] and f["size"] and f["size"]<=MAX_DOWNLOAD and
                  str(f["key"]).lower().endswith((".csv",".zip",".xlsx"))]
        eligible=sorted(eligible,key=lambda f:(not any(x in str(f["key"]).lower() for x in ["diet","data"]),f["size"]))
        report["small_original_file_candidates"]=len(eligible)
        if eligible:
            f=eligible[0]
            req=urllib.request.Request(f["content_link"],headers=UA)
            with urllib.request.urlopen(req,timeout=180) as r: raw=r.read(MAX_DOWNLOAD+1)
            if len(raw)!=f["size"]:raise ValueError("Original source file byte count mismatch")
            check=str(f["checksum"])
            typ,_,val=check.partition(":")
            if typ in ("md5","sha256") and hashlib.new(typ,raw).hexdigest()!=val.lower():
                raise ValueError("Original Zenodo publisher checksum mismatch")
            report["single_small_original_checked_file"]={"key":f["key"],"bytes":len(raw),"checksum":check}
            name=str(f["key"]).lower()
            if name.endswith(".csv"):
                report["sample_schema"]=inspect_csv(raw,f["key"])
            elif name.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    if z.testzip() is not None:raise ValueError("Original ZIP failed integrity")
                    report["original_archive_member_names"]=[x.filename for x in z.infolist()[:100]]
                    report["original_archive_member_count"]=len(z.infolist())
                    report["original_csv_schema"]={}
                    for member in z.infolist():
                        if member.filename.lower().endswith(".csv"):
                            with z.open(member) as stream:
                                head=stream.readline(20000).decode("utf-8-sig").strip()
                                second=stream.readline(20000).decode("utf-8-sig").strip()
                            report["original_csv_schema"][member.filename]={
                                "source_file_size_bytes":member.file_size,
                                "header":next(csv.reader([head]),[]),
                                "first_row":next(csv.reader([second]),[])[:30]
                            }
            elif name.endswith(".xlsx"):
                import openpyxl
                book=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
                report["workbook_sheet_names"]=book.sheetnames
                report["sheet_schema"]={}
                for sheet in book.worksheets[:12]:
                    first=next(sheet.iter_rows(min_row=1,max_row=1,values_only=True),())
                    report["sheet_schema"][sheet.title]={"rows_estimate":sheet.max_row,
                        "cols_estimate":sheet.max_column,
                        "first_row":[str(x)[:150] for x in first[:80]]}
        else:
            report["source_file_status"]="No eligible <=40 MB CSV/XLSX/ZIP; inspect manifest manually before download."
    except Exception as e:
        report["status"]="SCAR_SOURCE_PROBE_BLOCKED"
        report["error"]=type(e).__name__+": "+str(e)[:800]
    (output/"scar_20047874_true_source_inventory.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    a=p.parse_args();r=run(a.out)
    sys.exit(0 if r["status"]=="SCAR_ZENODO_METADATA_VERIFIED" else 2)
