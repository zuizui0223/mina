#!/usr/bin/env python3
"""Public original source discovery and acquisition for additional independent Adélie breeding censuses.
Signy (BAS), East Antarctica (PLOS and AADC), Ross aerial census (Landcare).
No model, no unverified time-series inference, no inclusion changes based on polynya signs.
"""
import datetime, hashlib, html.parser, json, re, urllib.request, urllib.parse
from pathlib import Path

OUT=Path("build/adelie_extra_census")
OUT.mkdir(parents=True,exist_ok=True)
class Links(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.current=None
    def handle_starttag(self,tag,attrs):
        if tag=="a":self.current={"href":dict(attrs).get("href",""),"text":""}
    def handle_data(self,v):
        if self.current is not None:self.current["text"]+=v
    def handle_endtag(self,tag):
        if tag=="a" and self.current is not None:self.links.append(self.current);self.current=None
def get(url,limit=8_000_000):
    q=urllib.request.Request(url,headers={
       "User-Agent":"Antarctic-ecology-independent-colony-source-audit/1.0 (https://github.com/zuizui0223/mina)",
       "Accept":"application/json,text/html,application/octet-stream;q=0.7,*/*;q=0.5"})
    with urllib.request.urlopen(q,timeout=105) as r:
        b=r.read(limit+1)
        if len(b)>limit:raise ValueError("EXCEEDED_REVIEW_SIZE_LIMIT")
        return b,r.url,r.headers.get("Content-Type","")
def attempt_download(url,name,max_size=8_000_000):
    try:
        body,actual,ctype=get(url,max_size)
        if body.lstrip().lower().startswith((b"<!doctype html",b"<html")) and not name.endswith(".html"):
            return {"status":"HTML_NOT_DATA","original_url":url,"actual_url":actual,
                    "bytes":len(body),"head":body[:200].decode("utf-8","replace")}
        p=OUT/name;p.write_bytes(body)
        return {"status":"ORIGINAL_FILE_DOWNLOADED","url":url,"resolved_url":actual,"bytes":len(body),
                "sha256":hashlib.sha256(body).hexdigest(),"file_name":name,
                "content_type":ctype,"first8":body[:8].hex()}
    except Exception as e:
        return {"status":"FAILED_SOURCE_DOWNLOAD","url":url,"error":str(e)[:350]}
def page(url,key):
    try:
        content,final,ctype=get(url,3_000_000)
        parser=Links();parser.feed(content.decode("utf-8","replace"))
        relevant=[]
        for a in parser.links:
            href=urllib.parse.urljoin(final,a["href"])
            if re.search(r"\\.csv|\\.xlsx?|\\.zip|download|census|adelie|penguin|breeding|entry|get\\?|api|data",href+" "+a["text"],re.I):
                relevant.append({"href":href,"text":a["text"].strip()[:90]})
        return {"status":"AVAILABLE","url":final,"sha256":hashlib.sha256(content).hexdigest(),
                "content_type":ctype,"links":relevant[:95],
                "text_markers":re.findall(r".{0,65}(?:Download|data access|CSV|\\.xlsx|\.zip|resource).{0,90}",content.decode("utf-8","replace"),re.I)[:28]}
    except Exception as e:
        return {"status":"UNAVAILABLE","error":str(e)[:300],"url":url}
def main():
    report={"audit_date":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "scope":"new independent colony counts and temporal comparability, no ecological modelling",
         "sources":{},"original_downloads":[]}
    ckan="https://datastore.landcareresearch.co.nz/api/3/action/resource_show?id=5fd490e5-92c4-4f2c-a82e-c66db2320eb1"
    try:
        b,u,t=get(ckan,600_000)
        j=json.loads(b)
        r=j["result"]
        meta={k:r.get(k) for k in ("id","name","url","format","size","hash","license_id","description","created","last_modified")}
        report["sources"]["landcare_ckan_resource"]={"status":"verified","meta":meta}
        if r.get("url"):
            report["original_downloads"].append(attempt_download(r["url"],"landcare_ross_aerial_1981_2024.xlsx",5_000_000))
    except Exception as e:
        report["sources"]["landcare_ckan_resource"]={"status":"NO_API_ACCESS","error":str(e)[:300]}
    report["sources"]["landcare_web"]=page("https://datastore.landcareresearch.co.nz/dataset/adelie-penguin-census-data/resource/5fd490e5-92c4-4f2c-a82e-c66db2320eb1","landcare")
    report["sources"]["bas_ramada"]=page("https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=daf2c4fd-c1e3-4e65-851f-d11f02c5b69d","bas")
    report["sources"]["bas_metadata"]=page("https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/01535","bas_meta")
    report["sources"]["aadc_occupancy"]=page("https://data.aad.gov.au/metadata/records/fulldisplay/AAS_4088_Adelie_Occupancy","aadc")
    report["sources"]["plos_east_article"]=page("https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0139877","plos")
    report["original_downloads"].append(attempt_download(
       "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0139877.s001&type=supplementary",
       "southwell2015_east_population_s001.doc",8_000_000))
    # A primary source may have discoverable small CSV downloads attached to BAS Ramadda.
    for entry in report["sources"]["bas_ramada"].get("links",[]):
        href=entry["href"]
        if href.lower().endswith(".csv") and len([d for d in report["original_downloads"] if d.get("file_name","").startswith("bas_")])<4:
            label=f"bas_signy_source_{len(report['original_downloads'])}.csv"
            report["original_downloads"].append(attempt_download(href,label,6_000_000))
    (OUT/"source_discovery_receipt.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str)+"\n")
    for k,v in report["sources"].items():
        print("SOURCE",k,v["status"],"links",len(v.get("links",[])))
        for link in v.get("links",[])[:20]:
            print("  LINK",link)
    for d in report["original_downloads"]:print("DOWNLOAD",d)
if __name__=="__main__":main()
