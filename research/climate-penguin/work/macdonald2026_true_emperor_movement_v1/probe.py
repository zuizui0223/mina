#!/usr/bin/env python3
"""Retrieve UK PDC Macdonald et al (2026) *actual tracking* shapefiles.

Explore documented RAMADDA entry DOI only. No 50-colony movement imputation.
A first-pass source transport and ZIP/file schema audit, with SHA256 receipt.
"""
import hashlib,html.parser,json,urllib.request,urllib.parse,zipfile,io
from pathlib import Path

DATA_DOI="10.5285/e1e00e5d-fc4c-4948-9e00-8d02e8b359d9"
ID="e1e00e5d-fc4c-4948-9e00-8d02e8b359d9"
ROOT="https://ramadda.data.bas.ac.uk/repository/entry/show?entryid="+ID
OUT=Path("research/climate-penguin/outputs/macdonald2026_true_emperor_movement_v1")
MAX=75_000_000

class Links(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  if tag in ("a","link"):
   d=dict(attrs)
   if "href" in d:self.urls.append((d["href"],d.get("title","")))

def take(label,url,limit):
 row={"source":label,"url":url}
 try:
  request=urllib.request.Request(url,headers={"User-Agent":"mina-independent-antarctic-ecology-research/1.0","Accept":"*/*"})
  with urllib.request.urlopen(request,timeout=55) as r:
   row.update({"http_code":r.status,"final_url":r.url,"content_type":r.headers.get("Content-Type"),"header_length":r.headers.get("Content-Length")})
   data=r.read(limit+1)
  row["read_length"]=len(data)
  row["truncated"]=len(data)>limit
  row["sha256_of_read"]=hashlib.sha256(data).hexdigest() if not row["truncated"] else None
  row["first_250_bytes"]=data[:250].decode("utf-8","replace")
  if not row["truncated"]:
   if zipfile.is_zipfile(io.BytesIO(data)):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
     row["zip_members"]=[{"path":f.filename,"bytes":f.file_size,"compressed_bytes":f.compress_size} for f in z.infolist() if not f.is_dir()]
     row["zip_total_uncompressed_bytes"]=sum(f["bytes"] for f in row["zip_members"])
    (OUT/(label+".zip")).write_bytes(data)
   elif "html" in (row["content_type"] or "").lower():
    parser=Links();parser.feed(data.decode("utf-8","replace"))
    row["links_related_to_entry_or_data"]=[{"url":urllib.parse.urljoin(r.url,h),"title":t} for h,t in parser.urls if any(k in h.lower() for k in ("get?","zip","02155","e1e00","download","shp","csv"))][:80]
    (OUT/(label+".html")).write_bytes(data)
   elif len(data)<1_000_000:
    (OUT/(label+".txt")).write_bytes(data)
 except Exception as err:
  row["error"]=type(err).__name__+": "+str(err)
 print("MACDONALD2026 POLAR DATA SOURCE PROBE "+json.dumps(row),flush=True)
 return row

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 result={"source_doi":DATA_DOI,"source_dataset_title":"Year-round estimates of penguin colony locations at Atka Bay, Coulman Island and Cape Washington, 2017–2024",
 "source_reference":"Macdonald et al. (2026), UK Polar Data Centre", "probes":[]}
 for label,url,lim in [
  ("metadata_HTML",ROOT,3_000_000),
  ("metadata_CSV",ROOT+"&output=default.csv",3_000_000),
  ("dataset_zip",ROOT+"&output=zip.tree",MAX),
  ("data_bas_record","https://data.bas.ac.uk/records/"+ID+".html",3_000_000)
 ]:
  result["probes"].append(take(label,url,lim))
 (OUT/"source_access_audit.json").write_text(json.dumps(result,indent=2)+"\n")
 result["usable_archive"]=any(p.get("zip_members") for p in result["probes"])
 print("MACDONALD2026 COLONY TRACKING ACCESS RESULT "+json.dumps({"doi":DATA_DOI,"usable_zip":result["usable_archive"],"errors":{p["source"]:p.get("error") for p in result["probes"]},"zip_files":[x["path"] for p in result["probes"] for x in p.get("zip_members",[])][:200]}),flush=True)
if __name__=="__main__":main()
