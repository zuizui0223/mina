#!/usr/bin/env python3
"""Second AADC original weighbridge source URL 5849: provenance only.

From official Australian Antarctic Division metadata for AAS_4086, browser
discovery shows both 5228 (technical document) and 5849 (second dataset link).
The latter was missed in V20-23 because NASA CMR/STAC advertised 5228 only.
Probe just original HTML/anchor labels and first 24KB of the three official
downloads using the V20 source-only parser. NEVER read wildlife tag IDs.

THIS DOES NOT establish that file 5849 is usable raw crossing data: a
specific original file label/manifest, actual file, technical codebook,
stable tag IDs and same-bird nesting observation remain outstanding.
"""
from __future__ import annotations
import argparse,json
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import build_opener, Request, HTTPSHandler
from urllib.parse import urlparse, urljoin
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import probe_bechervaise_original_rfid_vs_nest_resights_v20 as original

METADATA="https://data.aad.gov.au/metadata/records/AAS_4086_Weighbridge"
SOURCE_URLS={
    "AAS4086_TECHNICAL_GUIDE_5228":"https://data.aad.gov.au/eds/5228/download",
    "AAS4086_SECOND_OFFICIAL_LINK_5849":"https://data.aad.gov.au/eds/5849/download",
    "AAS4518_ORIGINAL_NEST_RESIGHTS_5516":"https://data.aad.gov.au/eds/5516/download"
}
FIRST_PAGE_LIMIT=240000

class PublisherLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.current=None
        self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag!="a":return
        attributes=dict(attrs)
        href=attributes.get("href","")
        if href:
            self.current={"url":urljoin(METADATA,href),"text":""}
    def handle_data(self,data):
        if self.current is not None:
            self.current["text"]+=data
    def handle_endtag(self,tag):
        if tag=="a" and self.current is not None:
            self.current["text"]=self.current["text"].strip()[:150]
            self.links.append(self.current)
            self.current=None

def original_publisher_data_anchors(html):
    parser=PublisherLinks()
    parser.feed(html)
    interest=set(SOURCE_URLS.values())
    candidates=[x for x in parser.links if x["url"] in interest]
    return {
        "source_metadata_html_anchors_observed":len(candidates),
        "metadata_ref_technical_5228":any(x["url"]==SOURCE_URLS["AAS4086_TECHNICAL_GUIDE_5228"] for x in candidates),
        "metadata_ref_additional_5849":any(x["url"]==SOURCE_URLS["AAS4086_SECOND_OFFICIAL_LINK_5849"] for x in candidates),
        "publisher_original_anchor_labels":candidates,
        "never_interpret_missing_static_HTML_anchor_as_absence_of_browser_link":True
    }

def get_source_metadata_links():
    out={"metadata_read_status":"HOLD_UNABLE_TO_READ_ORIGINAL_METADATA_HTML",
         "source_page":METADATA,
         "original_metadata_anchor_labels_verified":False}
    try:
        op=build_opener(HTTPSHandler(),original.SafeRedirect())
        with op.open(Request(METADATA,headers={
          "User-Agent":"Scientific archive source link inventory/1.0",
          "Accept":"text/html"}),timeout=16) as reply:
            if not original.official(reply.geturl()):
                raise ValueError("Redirect left original AADC HTTPS host")
            sample=reply.read(FIRST_PAGE_LIMIT+1)
        if len(sample)>FIRST_PAGE_LIMIT:
            raise ValueError("Official metadata over size cap")
        links=original_publisher_data_anchors(sample.decode("utf-8",errors="replace"))
        out.update(links)
        out["metadata_read_status"]="STATIC_PUBLISHER_META_ANCHOR_DISCOVERY_ONLY"
        out["original_metadata_anchor_labels_verified"]=links["metadata_ref_additional_5849"]
    except Exception as e:
        out["metadata_read_status"]="HOLD_ORIGINAL_METADATA_STATIC_RESPONSE"
        out["metadata_error_type"]=type(e).__name__
        out["metadata_error_message"]=str(e)[:180]
    return out

def source_report():
    links=get_source_metadata_links()
    probes={label:original.probe(url,label) for label,url in SOURCE_URLS.items()}
    raw=probes["AAS4086_SECOND_OFFICIAL_LINK_5849"]
    # A download returning a ZIP *prefix* is not proof of complete file
    # integrity, tag normalization or an animal-event table.
    raw_kind=raw.get("source_file_magic",{}).get("record_state","UNKNOWN")
    return {
        "status":"SECOND_AADC_ORIGINAL_LINK_FOUND_BUT_RAW_TAG_TO_EGG_IDENTIFICATION_HOLD",
        "source_record":"AAS_4086_Weighbridge",
        "source_metadata_page":METADATA,
        "metadata_links_probe":links,
        "source_only_download_probes":probes,
        "AAS4086_5849_additional_official_link_exists_in_browser_metadata":True,
        "AAS4086_5849_candidate_binary_signature_observed":raw_kind,
        "AAS4086_5849_confirmed_to_contain_real_weighbridge_tag_records":False,
        "AAS4086_5228_guide_not_the_same_as_5849_link":True,
        "AAS4518_5516_nest_resight_is_a_separate_archive":True,
        "no_source_penguin_tag_rows_opened":True,
        "no_email_or_download_credentials_submitted":True,
        "2019_published_gate_plus_nest_status_individual_link_PRIOR_ART":True,
        "2026_Ross_prebreeder_prospecting_and_out_of_colony_recruitment_PRIOR_ART":True,
        "new_postarrival_breeding_first_egg_effect":False,
        "cross_island_recolonization_cause_estimated":False,
        "Ecology_PR189_frozen":True,
        "USAP_PR142_frozen":True,
        "emperor_PR195_frozen":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=source_report()
    a.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("AADC_SOURCE_PAGE_LINKS",json.dumps(d["metadata_links_probe"],ensure_ascii=False)[:3000])
    for k,v in d["source_only_download_probes"].items():
        print("AADC_FILE",k,"RESULT",v["source_retrieval"],
              "HTML_OR_ARCHIVE",v.get("source_file_magic",{}).get("record_state"),
              "HTTP",v.get("http_status"),
              "ERROR",v.get("retrieval_error_short",""))
    print("AADC_5849_RAW_TAG_FILE_VERIFIED",False)
    print("NO_NEW_ARRIVAL_EGG_OR_INTERISLAND_PENGUIN_CAUSAL_EFFECT",True)

if __name__=="__main__":main()
