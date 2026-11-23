#!/usr/bin/env python3
"""Source-only fallback Syowa 2004–2010: native 6.25km original DEEP-AA winters.
This intentionally does not infer NSIDC SIC when provider returns HTTP 403.
"""
from __future__ import annotations
import argparse,calendar,datetime,hashlib,json,math
from pathlib import Path
import numpy as np,pandas as pd
from extract_syowa_2004_2010_DEEPAA_NSIDC import get_metadata,deepaa

def main():
    p=argparse.ArgumentParser()
    for name in ("counts","coords","deepaa","out"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    geo,original,metadata=get_metadata(a)
    daily,n_days=deepaa(a,geo)
    monthly=daily.groupby(["site_source_round_id","season","month"],as_index=False).agg(
        coastal=("coastal_fraction","mean"),all_open=("total_open_fraction","mean"),
        observed_days=("coastal_fraction","count"),native_days=("date","nunique"))
    monthly["min_days"]=monthly.apply(lambda r:math.ceil(.8*calendar.monthrange(int(r.season),int(r.month))[1]),axis=1)
    monthly["adequate"]=monthly.observed_days>=monthly.min_days
    if not (len(monthly)==7*7*5 and monthly.adequate.all()):
        raise ValueError("SYOWA DEEP-AA source missing complete months")
    annual=monthly.groupby(["site_source_round_id","season"],as_index=False).agg(
        coastal=("coastal","mean"),all_open=("all_open","mean"),n_months=("adequate","sum"))
    if not (len(annual)==49 and annual.n_months.eq(5).all()):
        raise ValueError("SYOWA seven sites and seven winter years not complete")
    yearly=annual.groupby("season",as_index=False).agg(
        coastal_frac=("coastal","mean"),all_open_frac=("all_open","mean"),
        contributing_source_rounded_centers=("site_source_round_id","nunique"))
    if not yearly.contributing_source_rounded_centers.eq(7).all():
        raise ValueError("Not all seven independent rounded coordinates contribute")
    result=original.merge(yearly,on="season",validate="one_to_one")
    result["coastal_percent"]=result.coastal_frac*100
    result["all_open_percent"]=result.all_open_frac*100
    result["year_span_is_only_six_elapsed_years"]=True
    result.to_csv(out/"Syowa_Southwell_original_7year_DEEPAA_coastal_and_breeding_pairs_UNFIT.csv",index=False)
    annual.to_csv(out/"Syowa_7_geocoded_sites_original_DEEPAA_2004_2010.csv",index=False)
    monthly.to_csv(out/"Syowa_original_DEEPAA_monthly_7geocoded_2004_2010.csv",index=False)
    v={"status":"SUCCESS_SEVEN_OBSERVED_YEAR_DEEPAA_ORIGINAL_SOURCE_ONLY_NSIC_UNAVAILABLE",
      "original_source":"Southwell 2015 PLOS S1, DOI https://doi.org/10.1371/journal.pone.0139877.s001",
      "total_original_nominal_sites":8,
      "unique_original_rounding_centers":7,
      "original_years":list(range(2004,2011)),
      "number_of_source_polynya_days":n_days,
      "n_valid_source_geo_years":49,
      "coastal_mean_pct":float(result.coastal_percent.mean()),
      "coastal_sd_pctpoints":float(result.coastal_percent.std(ddof=1)),
      "coastal_all_zero_winters":int((result.coastal_percent==0).sum()),
      "breeding_pair_original_years":7,
      "raw_breeding_pair_series_present_but_not_fitted":True,
      "NSIDC_continuous_SIC_not_present":True,
      "why_no_NSIDC":"External ERDDAP returned HTTP 403 to official monthly query on the previous verified run; no alternative data imputed",
      "meets_8year_count_span_eligibility":False,
      "qualifying_8th_independent_block":False,
      "interpretation":"source-only physical variability, not an adjusted demographic result"}
    (out/"Syowa_DEEPAA_SOURCE_ONLY_BLOCK_NO_GO.json").write_text(json.dumps(v,indent=2)+"\n")
    print(json.dumps(v,indent=2))
if __name__=="__main__":main()
