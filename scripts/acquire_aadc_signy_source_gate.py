#!/usr/bin/env python3
"""Fetch field-original BAS Signy and Australian Mawson/Bechervaise public datasets.
Metadata and table inventory only, no fitted response or source rewriting.
"""
import datetime,hashlib,html.parser,json,re,urllib.request,urllib.error,urllib.parse,zipfile,io
from pathlib import Path
O=Path("build/adelie_new_region_sources");O.mkdir(parents=True,exist_ok=True)
SOURCES={
 "aadc_mawson_1991_2019":"https://data.aad.gov.au/eds/5516/download",
 "aadc_bechervaise_1990_2005":"https://data.aad.gov.au/eds/1356/download",
 "bas_signy_entry_json":"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=daf2c4fd-c1e3-4e65-851f-d11f02c5b69d&output=json",
 "bas_signy_entry_xml":"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=daf2c4fd-c1e3-4e65-851f-d11f02c5b69d&output=xml.xmlentry",
 "bas_signy_entry_zip":"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=daf2c4fd-c1e3-4e65-851f-d11f02c5b69d&output=zip.zipgroup",
 "bas_signy_file_get":"https://ramadda.data.bas.ac.uk/repository/entry/get?entryid=daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
 "polarbytes_signy_mirror":"https://polarbytes.umk.edu.my/adelie",
 "aadc_windmill_meta":"https://data.aad.gov.au/metadata/records/AAS_4518_AAS_Reproductive_Success_Windmill_Islands",
}
def get(url,cap):
    request=urllib.request.Request(url,headers={"User-Agent":"Antarctic-breeding-original-source-availability-audit/1.0",
      "Accept":"application/json,text/html,application/zip,application/octet-stream,*/*;q=0.5"})
    with urllib.request.urlopen(request,timeout=115) as response:
        final=response.url;headers=response.headers
        content=bytearray()
        for b in iter(lambda:response.read(1024*512),b""):
            content.extend(b)
            if len(content)>cap:raise ValueError("HARD_SOURCE_SIZE_CAP_EXCEEDED")
    return bytes(content),final,dict(headers.items())
def zinventory(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        out=[]
        for f in z.infolist():
            out.append({"name":f.filename,"size":f.file_size,"compressed":f.compress_size,
                        "candidate_tabular":f.filename.lower().endswith((".csv",".tsv",".xlsx",".xls",".txt"))})
        return out
class H(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            d=dict(attrs)
            if d.get("href"):self.links.append(d["href"])
def main():
    report={"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "source_policy":"Only official original files or mirror explicitly labelled; no double-counting with MAPPPD",
       "sources":{}}
    for name,url in SOURCES.items():
        try:
            b,final,headers=get(url,85_000_000 if name.startswith("aadc_") else 25_000_000)
            contenttype=headers.get("Content-Type","")
            item={"status":"fetched","url":url,"final_url":final,"bytes":len(b),
               "content_type":contenttype,"sha256":hashlib.sha256(b).hexdigest(),"head_hex":b[:12].hex()}
            if zipfile.is_zipfile(io.BytesIO(b)):
                item["zip_members"]=zinventory(b)
            elif b.startswith((b"{",b"[")):
                try:
                    obj=json.loads(b);item["json_top_keys"]=list(obj)[:25] if isinstance(obj,dict) else ["LIST"]
                    item["json_text_sample"]=str(obj)[:1500]
                except Exception: pass
            elif b.lstrip().lower().startswith((b"<html",b"<!doctype",b"<?xml")):
                page=b.decode("utf-8","replace");p=H();p.feed(page)
                links=[urllib.parse.urljoin(final,x) for x in p.links]
                item["links"]=[x for x in links if re.search(r"\\.csv|\\.xlsx?|\\.zip|/get\\?|download|entryid|data",x,re.I)][:60]
                item["dataset_csv_occurrences"]=page.lower().count(".csv")
                item["dataset_xlsx_occurrences"]=page.lower().count(".xlsx")
                item["data_file_regexes"]=re.findall(r"[^<>\"' ]+\\.csv",page,re.I)[:30]
                item["html_text_regex"]=re.findall(r".{0,95}(?:Download|CSV|Data|File|Resource).{0,100}",page,re.I)[:20]
            # Do not publish raw binary if abnormally huge; store only archived audited names.
            item["retained_original"]=None
            if len(b)<=22_000_000 and (zipfile.is_zipfile(io.BytesIO(b)) or
                b.startswith((b"CDF",b"\xd0\xcf\x11\xe0",b"PK\x03\x04")) or
                name=="polarbytes_signy_mirror"):
                ext=(".zip" if zipfile.is_zipfile(io.BytesIO(b)) else
                     ".html" if name=="polarbytes_signy_mirror" else ".dat")
                path=O/(name+ext);path.write_bytes(b)
                item["retained_original"]=path.name
            report["sources"][name]=item
            print("SOURCE",name,item["status"],item["bytes"],item.get("content_type"),"original?",item["retained_original"],flush=True)
            if "zip_members" in item:
                print(" MEMBERS",[(x["name"],x["size"]) for x in item["zip_members"][:35]],flush=True)
        except Exception as e:
            report["sources"][name]={"status":"failed","url":url,"error":repr(e)[:350]}
            print("SOURCE FAILED",name,repr(e)[:300],flush=True)
    (O/"original_sources_and_access_receipt.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
