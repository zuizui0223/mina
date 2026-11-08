#!/usr/bin/env python3
"""Probe provider-listed PUBLIC raw Ross penguin data discovery routes.

Does NOT bypass USAP-DC reCAPTCHA, test hidden download API endpoints, use
personal accounts, or fetch raw individual-level data from an unlisted source.
Only already-advertised PointBlue official public raw-data S3 entry.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode
import json,xml.etree.ElementTree as ET,hashlib,csv,io

OUT=Path(__file__).resolve().parent/"outputs"
OUT.mkdir(parents=True,exist_ok=True)
LISTING="https://deju-penguinscience.s3.us-east-2.amazonaws.com/"
POINTBLUE="https://data.pointblue.org/apps/penguin_science/"
PUBLIC_LANDING="http://deju-penguinscience.s3-website.us-east-2.amazonaws.com/index.html?path=AllData%2F"
KNOWN={
 "band_resighting_1997-2021.csv":"aaae6ddad6d12081b5a68466794438a2",
 "band_inv_1994-2021.csv":"3da33defa4decc82b6e317c7fa9f9044"}
MAX_CONTENT=35*1024*1024
class Hrefs(HTMLParser):
 def __init__(self):
  super().__init__();self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  if tag=="a":
   u=dict(attrs).get("href")
   if u:self.hrefs.append(u)

def fetch(url,limit=1024*1024):
 try:
  with urlopen(Request(url,headers={"User-Agent":"mina-Ross-Adelie-source-discovery/1.0 (scientific open-data metadata audit)"}),timeout=20) as response:
   length=response.headers.get("Content-Length")
   body=response.read(limit+1)
   return {"status":response.status,"final_url":response.geturl(),
     "content_type":response.headers.get("Content-Type",""),
     "content_length_header":length,"body":body,"truncated":len(body)>limit}
 except HTTPError as err:
  return {"status":int(err.code),"error":"HTTP error; public route unavailable","body":b""}
 except Exception as e:
  return {"status":None,"error":type(e).__name__+": "+str(e)[:150],"body":b""}

def clean(d):
 return {k:v for k,v in d.items() if k!="body"}
def main():
 routes={}
 for label,url in (("official_pointblue_landing",POINTBLUE),
                   ("official_pointblue_raw_repository_landing",PUBLIC_LANDING),
                   ("official_pointblue_public_read_object_https",LISTING+"index.html?path=AllData%2F"),
                   ("public_s3_listing_for_advertised_AllData",
                    LISTING+"?"+urlencode({"list-type":"2","prefix":"AllData/","max-keys":"1000"}))):
  obj=fetch(url,2*1024*1024)
  routes[label]=clean(obj)
  print("PUBLIC_PROVIDER_ROUTE="+json.dumps({"name":label,**routes[label]}),flush=True)
  if label=="official_pointblue_landing" and obj["status"]==200:
   p=Hrefs();p.feed(obj["body"].decode("utf-8",errors="replace"))
   routes[label]["public_links"]=[x for x in p.hrefs if "penguin" in x.lower() or "s3" in x.lower()][:20]
  if label=="official_pointblue_raw_repository_landing" and obj["status"]==200:
   p=Hrefs();p.feed(obj["body"].decode("utf-8",errors="replace"))
   routes[label]["public_links"]=[x for x in p.hrefs if "AllData" in x or x.endswith(".js")][:40]
   routes[label]["page_contains_AllData"]=b"AllData" in obj["body"]
  if label=="public_s3_listing_for_advertised_AllData" and obj["status"]==200:
   try:
    parsed=ET.fromstring(obj["body"])
    ns="{http://s3.amazonaws.com/doc/2006-03-01/}"
    keys=[z.text for z in parsed.findall(f".//{ns}Key") if z.text]
    routes[label]["n_public_keys_first_page"]=len(keys)
    routes[label]["is_truncated"]=parsed.findtext(f".//{ns}IsTruncated")
    routes[label]["first_30_public_keys"]=keys[:30]
    routes[label]["possible_band_resight_public_keys"]=[x for x in keys
      if any(z in x.lower() for z in ("band","resight","resighting","inventory"))][:40]
   except Exception as err:
    routes[label]["parse_error"]=str(err)[:200]
 discovered=routes.get("public_s3_listing_for_advertised_AllData",{}).get("possible_band_resight_public_keys",[])
 exact=[x for x in discovered if Path(x).name in KNOWN]
 matched_files=[]
 if exact:
  for name in exact[:3]:
   # Exact publication-named object on the *explicitly public* PointBlue S3
   # route. It is not an undocumented workaround to the USAP-DC CAPTCHA.
   u=LISTING+name
   o=fetch(u,MAX_CONTENT)
   record={"object_key":name,**clean(o)}
   if o["status"]==200 and not o["truncated"]:
    md5=hashlib.md5(o["body"]).hexdigest()
    record["bytes_verified"]=len(o["body"])
    record["MD5_original_USAP_expected"]=KNOWN[Path(name).name]
    record["MD5_measured"]=md5
    record["exact_USAP_file_verification"]=md5==KNOWN[Path(name).name]
    record["SHA256"]=hashlib.sha256(o["body"]).hexdigest()
    if md5==KNOWN[Path(name).name]:
     line=o["body"].splitlines()[0].decode("utf-8-sig",errors="replace")
     cols=next(csv.reader(io.StringIO(line)))
     record["raw_original_columns"]=cols
   matched_files.append(record)
 result={
  "status":"ORIGINAL_BYTES_VERIFIED" if any(z.get("exact_USAP_file_verification") for z in matched_files)
        else "SOURCE_ACCESS_HOLD_OR_ONLY_PUBLIC_METADATA",
  "original_doi_resights":"10.15784/601444",
  "original_doi_banding":"10.15784/601443",
  "publication_listed_file_md5":KNOWN,
  "provider_public_route_receipts":routes,
  "matched_provider_file_records":matched_files,
  "source_access_notice":"USAP-DC publication page indicates reCAPTCHA for downloads; no CAPTCHA or access control was bypassed.",
  "biological_gate":"NO_INDIVIDUAL_MOVEMENT_VERIFIED_WITHOUT_RAW_ID_DATE_PLACE_BREEDING_FIELDS"}
 (OUT/"public_source_access_receipt.json").write_text(json.dumps(result,indent=2)+"\n")
 print("ROSS_RESIGHT_ACCESS_GATE="+json.dumps({k:result[k] for k in ("status","original_doi_resights","original_doi_banding","source_access_notice","biological_gate")}),flush=True)
if __name__=="__main__":
 main()
