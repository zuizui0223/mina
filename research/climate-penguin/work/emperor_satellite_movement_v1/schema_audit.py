#!/usr/bin/env python3
"""Check whether original LaRue (2024) satellite and aerial records contain per-year colony positions.
Fetch byte-identical author XLSX inputs in CI; use Python standard ZIP/XML only.
This is a positional-data support audit, NOT a movement estimate.
"""
import csv, hashlib, io, json, re, urllib.request, zipfile, xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path

SHA="13f71112da43c1fd082273677757b41c550457ed"
SOURCES={
 "satellite":("empe_satellite_2023-05-25.xlsx","a964360e2cc9bc6303199e0971a4e7d40f793752",107208),
 "aerial":("empe_aerial_2023-05-25.xlsx","9458734d11a6e289a2bbecd423f5aba8b2d96bae",30944)
}
OUT=Path("research/climate-penguin/outputs/emperor_satellite_movement_v1")
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def original_bytes(name,sha,size):
 url="https://raw.githubusercontent.com/davidiles/EMPE_Global/"+SHA+"/data/"+name
 req=urllib.request.Request(url,headers={"User-Agent":"mina-colony-movement-source-audit/1.0"})
 with urllib.request.urlopen(req,timeout=50) as resp:
  data=resp.read()
 actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
 if actual!=sha or len(data)!=size:
  raise ValueError("Original author Git blob SHA or length differs: "+name+" "+actual)
 return data

def parse_worksheet(data):
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  files=set(z.namelist())
  shared=[]
  if "xl/sharedStrings.xml" in files:
   root=ET.fromstring(z.read("xl/sharedStrings.xml"))
   for si in root.findall(NS+"si"):
    shared.append("".join(t.text or "" for t in si.iter(NS+"t")))
  sheets=sorted(name for name in files if re.fullmatch("xl/worksheets/sheet[0-9]+[.]xml",name))
  if not sheets: raise ValueError("No worksheet XML in pinned file")
  for sh in sheets:
   root=ET.fromstring(z.read(sh))
   matrix=[]
   for row in root.iter(NS+"row"):
    vals={}
    for cell in row.findall(NS+"c"):
     address=cell.attrib.get("r","A")
     letters=re.match("[A-Z]+",address).group(0)
     col=0
     for letter in letters:col=col*26+ord(letter)-64
     value=cell.find(NS+"v")
     typ=cell.attrib.get("t","")
     if typ=="inlineStr":
      obj=cell.find(NS+"is")
      v="".join(x.text or "" for x in obj.iter(NS+"t")) if obj is not None else ""
     elif value is None:v=""
     elif typ=="s":v=shared[int(value.text)]
     else:v=value.text or ""
     vals[col-1]=v
    if vals:matrix.append([vals.get(i,"") for i in range(max(vals)+1)])
   if not matrix:continue
   cols=[str(x).strip() for x in matrix.pop(0)]
   if len(set(cols))!=len(cols):raise ValueError("Duplicate source headings")
   rows=[dict(zip(cols,row+[""]*(len(cols)-len(row)))) for row in matrix]
   yield sh,cols,rows

def audit(label,sh,cols,rows):
 candidates=lambda pattern:[k for k in cols if re.search(pattern,k,re.I)]
 years=candidates("year"),ids=candidates("site_id|colony_id"),lat=candidates("lat|northing"),lon=candidates("lon|long|easting")
 names=list(dict.fromkeys(years+ids+lat+lon+candidates("qual|area|month|day|pixel|presence|occ|image|img_")))
 site=ids[0] if ids else None
 year=next((x for x in years if x.lower() in ("year","img_year")),years[0] if years else None)
 grouped=defaultdict(list)
 if site and year:
  for r in rows:grouped[(r.get(site),r.get(year))].append(r)
 nonempty={k:sum(bool(str(r.get(k,"")).strip()) for r in rows) for k in names}
 summary={"input":label,"sheet":sh,"row_count":len(rows),"columns":cols,"year_fields":years,
  "site_fields":ids,"candidate_latitude_fields":lat,"candidate_longitude_fields":lon,
  "nonempty_relevant_columns":nonempty,"distinct_site_years":len(grouped),
  "per_year_n_site_year":dict(sorted(Counter(y for s,y in grouped).items(),key=lambda x:x[0])),
  "first_rows_selected": [{k:r.get(k,"") for k in names[:19]} for r in rows[:5]],
  "status":"potentially_has_observation_coordinates_validate_image_centroid" if year and site and lat and lon else "no_proven_observation_year_colony_coordinates"}
 print("EMPEROR ORIGINAL WORKBOOK SCHEMA "+json.dumps(summary,ensure_ascii=False),flush=True)
 return summary

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 report={"author_commit":SHA,"workbooks":{}}
 for label,(name,sha,size) in SOURCES.items():
  data=original_bytes(name,sha,size)
  (OUT/name).write_bytes(data)
  report["workbooks"][label]={"git_blob":sha,"bytes":len(data),"sheets":[audit(label,*t) for t in parse_worksheet(data)]}
 (OUT/"schema_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("EMPEROR MOVEMENT OBSERVATION-SUPPORT VERIFIED "+json.dumps({
  "author_sha":SHA,"workbooks":list(report["workbooks"]),"rows":{
    k:sum(x["row_count"] for x in v["sheets"]) for k,v in report["workbooks"].items()}}),flush=True)
if __name__=="__main__":main()
