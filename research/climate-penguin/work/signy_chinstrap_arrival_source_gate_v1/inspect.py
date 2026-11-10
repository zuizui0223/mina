"""Source-first audit of BAS Signy chinstrap arrival-count archive.

No biological response, regression, or conversion of survey first date into
arrival phenology is permitted by this inventory. Original archive and CSV
hashes are recorded. Staff arrival and irregular 4-5 day sessions are key risks.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,io,json,re,zipfile
from pathlib import Path

ENTRY_ID="64a8291f-8c23-4e5d-9085-c36c8d83b09a"
DOI="10.5285/"+ENTRY_ID

def parse(raw):
 for enc in ("utf-8-sig","utf-8","cp1252"):
  try:
   text=raw.decode(enc)
   lines=list(csv.DictReader(io.StringIO(text)))
   if not lines:continue
   return lines,enc
  except (UnicodeError,csv.Error):
   continue
 raise ValueError("No usable original CSV decoding")
def year_from(value):
 if value is None:return None
 s=str(value)
 if re.fullmatch(r"\s*(?:19|20)\d{2}\s*[-/]\s*\d{2}\s*",s):return None  # seasonal range, not a unique census year
 years={int(v) for v in re.findall(r"(?<!\d)(?:19\d{2}|20\d{2})(?!\d)",s)}
 if len(years)==1:return next(iter(years))
 return None
def audit(original,out):
 original=Path(original)
 if not zipfile.is_zipfile(original):raise ValueError("BAS publisher download was not a ZIP")
 with zipfile.ZipFile(original) as z:
  csvs=sorted(f for f in z.namelist() if f.lower().endswith(".csv") and not f.startswith("__MACOSX/"))
  if not csvs or len(csvs)>20:raise ValueError("Unexpected original CSV archive")
  files=[]
  for file in csvs:
   raw=z.read(file)
   rows,enc=parse(raw)
   fields=list(rows[0])
   date_columns=[k for k in fields if any(x in k.lower() for x in ("date","season","year","session","count","arrival","number"))]
   summary={}
   for key in date_columns:
    values=[str(r.get(key,"")).strip() for r in rows]
    years=[year_from(x) for x in values]
    counts=collections.Counter(x for x in years if x is not None)
    summary[key]=dict(
       n_nonempty=sum(v.lower() not in ("","na","nan","none") for v in values),
       n_distinct=len(set(values)),
       year_coverage=sorted(counts),
       row_counts_by_detectable_year=dict(sorted(counts.items())),
       first_nonempty_examples=list(dict.fromkeys(v for v in values if v and v.lower() not in ("na","nan")))[:5])
   files.append(dict(file=file,sha256=hashlib.sha256(raw).hexdigest(),
     n_rows=len(rows),n_columns=len(fields),columns=fields,encoding=enc,
     date_and_count_column_audit=summary,
     note="This inventory does not infer first penguin arrival from the first available census."))
 result=dict(status="BAS_original_arrival_source_schema_only_NOT_phenology_response",
  publisher_url="https://ramadda.data.bas.ac.uk/repository/entry/show?entryid="+ENTRY_ID+"&output=zip.tree",
  source_doi=DOI,original_zip_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
  n_original_csv=len(files),files=files,
  limitations=["Counts start when research staff can reach the colony; missing early counts are left-censored",
    "Survey sessions vary between years and are usually separated by 4-5 days",
    "Do not interpret the first census date as an ecological first arrival",
    "Do not treat each penguin counted or each 4-day session as an independent climate-year",
    "This source has Chinstrap arrival only and cannot directly estimate a two-species temporal gap"])
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 (out/"source_inventory.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"n_original_csv":len(files),
  "file_overview":[{"name":x["file"],"rows":x["n_rows"],"columns":x["columns"]} for x in files]},
  ensure_ascii=False,indent=2))
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--original-zip",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);q=p.parse_args()
 audit(q.original_zip,q.out)
