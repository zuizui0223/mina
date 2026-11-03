"""Source-first retrieval audit for Dunn 2018 Signy mean hatching dates.

Expected public DOI 10.5285/274b49bd-40a4-4e5d-bd5f-69a1ba09d403.
Do not digitize published figure or infer raw nests from mean estimates.
No environmental associations until date units, original source grain and
source year coverage are established. This entry may be source-restricted.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path

DOI="10.5285/274b49bd-40a4-4e5d-bd5f-69a1ba09d403"
SOURCE="https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=274b49bd-40a4-4e5d-bd5f-69a1ba09d403&output=zip.tree"
def run(original,outdir):
    original,outdir=Path(original),Path(outdir)
    raw=original.read_bytes()
    if not zipfile.is_zipfile(original):
        raise ValueError("DOI entry did not return source archive ZIP: "+raw[:130].decode("utf-8","replace"))
    inventories=[]
    with zipfile.ZipFile(original) as z:
        for item in sorted(z.infolist(),key=lambda x:x.filename):
            if item.is_dir():continue
            name=item.filename
            ext=name.rsplit(".",1)[-1].lower() if "." in name else ""
            content=z.read(item)
            result={"path":name,"size_bytes":len(content),
                "original_file_sha256":hashlib.sha256(content).hexdigest(),
                "extension":ext}
            if ext in ("csv","tsv","txt"):
                enc=None; decoded=None
                for tryencoding in ("utf-8-sig","utf-8","cp1252","latin1"):
                    try:decoded=content.decode(tryencoding);enc=tryencoding;break
                    except UnicodeError:pass
                if decoded is None:raise ValueError("Cannot decode source "+name)
                result["encoding"]=enc
                result["first_3_source_lines"]=decoded.splitlines()[:3]
                rows=list(csv.reader(io.StringIO(decoded),delimiter="\t" if ext=="tsv" else ","))
                if rows:
                    result["columns"]=rows[0]
                    result["n_data_rows"]=max(0,len(rows)-1)
                    result["first_4_original_rows"]=rows[1:5]
            elif ext in ("xlsx","xls"):
                import pandas as pd
                xl=pd.ExcelFile(io.BytesIO(content))
                result["sheets"]={}
                for sheet in xl.sheet_names:
                    frame=pd.read_excel(xl,sheet_name=sheet)
                    result["sheets"][sheet]={"n_rows":len(frame),
                        "columns":list(map(str,frame.columns)),
                        "first_4_rows":frame.head(4).fillna("").astype(str).to_dict("records")}
            inventories.append(result)
    if not inventories:raise ValueError("Empty source ZIP")
    summary={"state":"original_public_source_structure_audited_not_yet_time_climate_response",
      "source_doi":DOI,"source_url":SOURCE,
      "original_zip_size":len(raw),"original_zip_sha256":hashlib.sha256(raw).hexdigest(),
      "n_files":len(inventories),"files":inventories,
      "existing_article_results_not_new":"Clewlow et al. 2019: both species ~1.02 days/degree C, mean gap ~27.89 days, shared response.",
      "limitations":["Published mean hatching dates may be model derived, not individual nest dates",
        "Colony A41->A39 and C69->C66 transitions must be kept as site changes",
        "No 1997/98, 1999/00 or 2010/11 nest observations per catalog",
        "Mean hatching and back-calculated laying must not be double-counted",
        "Do not convert camera settlement dates into laying date without direct ground truth",
        "No warming causal inference and no CMIP6 biological projection"]}
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"source_inventory.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"source_doi":DOI,"source_zip_sha256":summary["original_zip_sha256"],
        "files":inventories},ensure_ascii=False,indent=2))
    return summary
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();run(a.source,a.out)
