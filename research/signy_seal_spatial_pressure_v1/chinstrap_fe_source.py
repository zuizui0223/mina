"""Inventory exact publisher-original chinstrap Fe workbook. No ecological fit."""
import hashlib,io,json,zipfile
from pathlib import Path
import requests
from openpyxl import load_workbook
OUT=Path("build/chinstrap_fe_source")
URL="https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-023-37132-5/MediaObjects/41467_2023_37132_MOESM4_ESM.xlsx"
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r={"status":"SOURCE_BLOCKED","doi":"10.1038/s41467-023-37132-5","source_url":URL,"sample_level_fit":False,"signy_calibration":False}
    try:
        chunks=[];n=0
        with requests.get(URL,stream=True,timeout=(20,90)) as res:
            res.raise_for_status()
            r["resolved_url"]=res.url
            for c in res.iter_content(65536):
                n+=len(c)
                if n>10_000_000:raise ValueError("bounded source intake")
                chunks.append(c)
        b=b"".join(chunks)
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            if z.testzip() is not None or "xl/workbook.xml" not in z.namelist():raise ValueError("invalid workbook")
        r.update(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
        wb=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
        r["sheets"]=[]
        for ws in wb.worksheets:
            # Include textual schema/labels only, not concentration magnitudes.
            texts=[];nonempty=0
            for i,row in enumerate(ws.values,1):
                if any(v is not None for v in row):nonempty+=1
                for j,v in enumerate(row,1):
                    if isinstance(v,str) and v.strip():
                        texts.append([i,j,v[:250]])
            r["sheets"].append({"name":ws.title,"rows":ws.max_row,"columns":ws.max_column,"nonempty_rows":nonempty,"text_cells":texts[:300]})
        wb.close()
        r["status"]="ORIGINAL_WORKBOOK_ACQUIRED_SCHEMA_REVIEW_REQUIRED"
    except Exception as e:r["error"]=str(e)
    (OUT/"receipt.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in r.items() if k!="sheets"},ensure_ascii=False))
if __name__=="__main__":main()
