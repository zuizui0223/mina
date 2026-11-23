#!/usr/bin/env python3
"""Public NIPR ADS Adélie annual census record availability; only anonymous official links.
No sign-in, credential bypass or fictional 2011–2022 records. Inspect what is actually public.
"""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,re,html.parser,datetime
O=Path("build/NIPR_ADS_Syowa_original_census_public")
O.mkdir(parents=True,exist_ok=True)
PAGES={
 "JARE62_2021_2022":"https://ads.nipr.ac.jp/data/meta/A20220304-002",
 "JARE66_2025":"https://ads.nipr.ac.jp/data/meta/A20260323-004",
 "search_list":"https://ads.nipr.ac.jp/data/search/list/1",
 "search_Adelie":"https://ads.nipr.ac.jp/data/search/list/1?query=Adelie",
 "search_penguin":"https://ads.nipr.ac.jp/data/search/list/1?keyword=penguin",
}
class Parse(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.src=[];self.data=""
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="a" and d.get("href"):self.links.append((d.get("href"),d.get("title","")))
        if tag=="script" and d.get("src"):self.src.append(d["src"])
    def handle_data(self,d): self.data+=" "+d[:5000]
def get(url,limit=4_000_000):
    q=urllib.request.Request(url,headers={"User-Agent":"NIPR-ADS-public-original-census-research-audit/1.0",
      "Accept":"text/html,application/json,application/octet-stream,*/*;q=0.8"})
    with urllib.request.urlopen(q,timeout=80) as r:
        b=r.read(limit+1)
        if len(b)>limit:raise ValueError("Exceeded source page size cap")
        return b,r.url,r.headers.get("Content-Type","")
def main():
    result={"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "purpose":"Unlinked official post-2010 Syowa breeding pair census source, count actual public seasons",
      "original_page_source_probes":{}}
    for name,url in PAGES.items():
        try:
            b,final,ctype=get(url)
            txt=b.decode("utf-8","replace");pp=Parse();pp.feed(txt)
            relevant=[{"url":urllib.parse.urljoin(final,href),"title":title} for href,title in pp.links
              if re.search(r"download|data|\\.csv|\\.zip|\\.txt|\\.pdf|A20\d{6}|metadata|api|application",href+" "+title,re.I)]
            scripts=[urllib.parse.urljoin(final,s) for s in pp.src]
            result["original_page_source_probes"][name]={
               "status":"FETCHED_OFFICIAL_PUBLIC_METADATA","source_url":url,"effective_url":final,
               "sha256":hashlib.sha256(b).hexdigest(),"page_bytes":len(b),
               "content_type":ctype,
               "dataset_IDs_in_html":sorted(set(re.findall(r"A20\d{6}-\d{3}",txt)))[:120],
               "near_penguin_terms":re.findall(r".{0,60}(?:Adelie|penguin|JARE|2021|2025|A20220304-002).{0,90}",txt,re.I)[:30],
               "relevant_hrefs":relevant[:90],"scripts":scripts[:30],
               "visible_text_sample":pp.data[:1600]}
            if name in ("JARE62_2021_2022","JARE66_2025"):
                (O/(name+"_source.html")).write_bytes(b)
            print("NIPR ADS",name,"FETCHED",len(b),"IDs",result["original_page_source_probes"][name]["dataset_IDs_in_html"][:20],
                    "scripts",scripts[:6],flush=True)
        except Exception as e:
            result["original_page_source_probes"][name]={"status":"NOT_RESOLVED","url":url,"error":repr(e)[:220]}
            print("NIPR ADS",name,"FAIL",repr(e)[:220],flush=True)
    (O/"NIPR_Syowa_ADS_public_metadata_manifest.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
if __name__=="__main__":main()
