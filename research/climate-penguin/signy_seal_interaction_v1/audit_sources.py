"""Original BAS archive inventory; no joint ecological outcomes."""
import argparse, csv, hashlib, io, json, sys, zipfile
from pathlib import Path
from openpyxl import load_workbook

IDS = {
    "seals":"8e910ac8-6f52-4548-bbcb-78474b559294",
    "ice":"0283c3e4-2164-4dfb-a066-0c49b816d7b6",
    "adelie":"daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
    "chinstrap":"d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9",
    "gentoo":"883c6b40-024e-41e8-9c3e-2668a44b5751",
}
def sha(b): return hashlib.sha256(b).hexdigest()
def inventory(path):
    raw=path.read_bytes()
    result={"archive_sha256":sha(raw),"archive_bytes":len(raw),"members":[]}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None: raise ValueError("corrupt member")
        if len(z.namelist())!=len(set(z.namelist())): raise ValueError("duplicate member name")
        for m in z.infolist():
            if m.is_dir(): continue
            data=z.read(m)
            row={"name":m.filename,"bytes":len(data),"sha256":sha(data)}
            ext=Path(m.filename).suffix.lower()
            if ext in (".csv",".tsv"):
                try:
                    for enc in ("utf-8-sig","cp1252"):
                        try: s=data.decode(enc); break
                        except UnicodeDecodeError: pass
                    try: dialect=csv.Sniffer().sniff(s[:8192],delimiters=",;\t")
                    except csv.Error: dialect="excel-tab" if ext==".tsv" else "excel"
                    rr=csv.reader(io.StringIO(s),dialect)
                    row["header"]=next(rr,[])
                    row["remaining_rows"]=sum(bool(r and any(x.strip() for x in r)) for r in rr)
                except Exception as e: row["schema_error"]=str(e)
            elif ext==".xlsx":
                try:
                    wb=load_workbook(io.BytesIO(data),read_only=True,data_only=True)
                    row["sheets"]=[{"name":ws.title,"header":[str(v) if v is not None else "" for v in next(ws.values,())],"max_row":ws.max_row} for ws in wb.worksheets]
                    wb.close()
                except Exception as e: row["schema_error"]=str(e)
            result["members"].append(row)
    result["has_table"]=any(("header" in r or "sheets" in r) and not r.get("schema_error") for r in result["members"])
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();r={}
    for name,id in IDS.items():
        path=a.source/(name+".zip")
        item={"doi":"10.5285/"+id}
        try: item.update(inventory(path));item["status"]="inventory_ok" if item["has_table"] else "no_readable_table"
        except Exception as e: item.update(status="blocked",error=str(e))
        r[name]=item
    ok=all(x["status"]=="inventory_ok" for x in r.values())
    report={"status":"SCHEMA_REVIEW_REQUIRED" if ok else "SOURCE_BLOCKED","sources":r,"numerical_join_executed":False}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v["status"] for k,v in r.items()}))
    return 0 if ok else 2
if __name__=="__main__": sys.exit(main())
