#!/usr/bin/env python3
"""Frozen source-column audit: does the 583 -> 439 loss occur entirely at the site inventory?
No Y values or model-fitting involved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

EXPECTED_GEO_BLOB = "5662badeedd43bc8e2dacbfdfc157f8d4fdf9a69"
EXPECTED_MATCHED_BLOB = "66184a09576297aea12f408fffc524185a3671f2"

def blob_sha(file):
    b = Path(file).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original-source",required=True)
    p.add_argument("--matched-860",required=True)
    p.add_argument("--geography",required=True)
    p.add_argument("--output",required=True)
    a = p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    assert blob_sha(a.matched_860)==EXPECTED_MATCHED_BLOB, "matched source changed"
    assert blob_sha(a.geography)==EXPECTED_GEO_BLOB, "geography source changed"
    raw=pd.read_csv(a.original_source)
    matched=pd.read_csv(a.matched_860)
    geo=pd.read_csv(a.geography)
    assert (len(raw),raw.site_id.nunique())==(583,113)
    assert (len(matched),matched.site_id.nunique())==(860,88)
    assert not raw.duplicated(["site_id","season"]).any()
    assert not matched.duplicated(["site_id","season"]).any()
    region_col="region"
    keys=["site_id","season"]
    frozen=matched.loc[matched.season.between(2004,2010),keys]
    assert (len(frozen),frozen.site_id.nunique())==(439,85)
    geo=geo[geo.radius_km.eq(100)].copy()
    assert geo.site_id.nunique()==88 and not geo.site_id.duplicated().any()
    source_sites=set(raw.site_id)
    geocoded_sites=set(geo.site_id)
    matched_sites=set(frozen.site_id)
    excluded_sites=source_sites-matched_sites
    assert len(excluded_sites)==28
    assert excluded_sites==source_sites-geocoded_sites,"Excluded sites not precisely accounted by geography table"
    assert matched_sites==(source_sites&geocoded_sites),"Geography overlap not exactly frozen site set"
    assert len(geocoded_sites-source_sites)==3
    m=raw.merge(frozen.assign(retained=True),on=keys,how="left",validate="one_to_one")
    m["retained"]=m.retained.fillna(False).astype(bool)
    assert int(m.retained.sum())==439
    assert int((~m.retained).sum())==144
    assert int(m.groupby("site_id").retained.nunique().max())==1,"Partially excluded site exists"
    m["in_pinned_geography"]=m.site_id.isin(geocoded_sites)
    assert bool((m.retained==m.in_pinned_geography).all())
    m.sort_values(keys).to_csv(out/"583_to_439_verified_site_inventory_keys.csv",index=False)
    sites=m.groupby(["site_id",region_col],as_index=False).agg(n_source_siteyears=("season","size"),
                                                               included=("retained","first"))
    sites["in_pinned_geography"]=sites.site_id.isin(geocoded_sites)
    sites.sort_values(["included","region","site_id"]).to_csv(out/"113_to_85_verified_site_catalogue.csv",index=False)
    report={
       "status":"PASS_SITE_INVENTORY_EXACTLY_EXPLAINS_144_ROW_LOSS",
       "source_rows":len(raw),"source_sites":len(source_sites),
       "matched_2004_2010_rows":len(frozen),"matched_sites":len(matched_sites),
       "excluded_source_sites":len(excluded_sites),"excluded_source_siteyears":int((~m.retained).sum()),
       "partial_sites_excluded":0,
       "all_28_excluded_sites_absent_from_pinned_88_site_geography":True,
       "geography_sites_total":len(geocoded_sites),
       "geography_sites_no_2004_2010_original_source":len(geocoded_sites-source_sites),
       "selected_year_loss_within_85_retained_sites":0,
       "causal_reason_for_geography_omission":"NOT_IDENTIFIED (could include site catalogue identity, coordinate QA, or marine wet-cell selection)",
       "region_exclusion_counts":sites.loc[~sites.included].groupby("region").agg(sites=("site_id","size"),
         site_years=("n_source_siteyears","sum")).to_dict("index"),
       "verified_sources":{"geography_git_blob":EXPECTED_GEO_BLOB,"matched860_git_blob":EXPECTED_MATCHED_BLOB}
    }
    (out/"site_inventory_exclusion_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
