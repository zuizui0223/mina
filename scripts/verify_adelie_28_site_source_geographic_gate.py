#!/usr/bin/env python3
"""Replicate the original 146->102 spatial ->99 observed GLORYS match, and exact 28-site exclusions.
Never reads isotope response or refits the biological model.
"""
import argparse,hashlib,json,zipfile
from io import BytesIO
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree

def read(archive,member):
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None, "Input ZIP CRC failed"
        return pd.read_csv(BytesIO(z.read(member)),low_memory=False)
def main(a):
    r=read(a.centroids,"source_site_projected_centroids.csv")
    land=read(a.centroids,"source_site_season_landsat_coverage.csv")
    atlas=read(a.atlas,"panantarctic_595_site_inventory.csv")
    marine=read(a.marine,"all_original_18region_1993_2020_real_joint_marine_3var_site_year.csv")
    ori=read(a.author,"published_author_site_level_support_2004_2010.csv")
    frozen=read(a.pinned_sites,"113_to_85_verified_site_catalogue.csv")
    nov=read(a.novfeb,"original_892_matched_site_season_NovFeb_GLORYS.csv")
    assert (len(r),len(land),len(atlas),len(marine),len(ori),len(frozen),len(nov))==(146,1410,595,16464,583,113,892)
    x,y=Transformer.from_crs(4326,3031,always_xy=True).transform(atlas.longitude,atlas.latitude)
    dd,ix=cKDTree(np.column_stack((x,y))).query(r[["easting","northing"]].to_numpy(),k=2)
    r["nearest_id"]=atlas.site_id.to_numpy()[ix[:,0]]
    r["distance_m"]=dd[:,0]
    r["second_nearest_distance_m"]=dd[:,1]
    r["id_ok"]=r.site_id.eq(r.nearest_id)
    r["distance_ok"]=r.distance_m<=2000
    r["second_ok"]=r.second_nearest_distance_m>2000
    r["strict_geo_ok"]=r.id_ok&r.distance_ok&r.second_ok
    assert int(r.strict_geo_ok.sum())==102
    r["marine_1997_roster_ok"]=r.site_id.isin(set(marine.loc[marine.year.eq(1997),"site_id"]))
    r["combined_ok"]=r.strict_geo_ok&r.marine_1997_roster_ok
    assert int(r.combined_ok.sum())==100
    eligible=land.loc[land.site_id.isin(r.loc[r.combined_ok,"site_id"])&land.season.between(1993,2013)]
    assert (len(eligible),eligible.site_id.nunique())==(892,99)
    keys=["site_id","season"]
    assert set(map(tuple,eligible[keys].itertuples(index=False,name=None)))==set(map(tuple,nov[keys].itertuples(index=False,name=None)))
    sites=ori.groupby("site_id",as_index=False).agg(
      n_site_years=("season","nunique"),n_pixels=("n_pixels","sum"),region=("region","first"))
    sites=sites.merge(r.drop(columns=["easting","northing"]),on="site_id",validate="one_to_one")
    sites=sites.merge(frozen[["site_id","included"]],on="site_id",validate="one_to_one")
    sites["first_failed_rule"]=np.select(
      [~sites.id_ok,sites.id_ok&~sites.distance_ok,
       sites.id_ok&sites.distance_ok&~sites.second_ok,
       sites.strict_geo_ok&~sites.marine_1997_roster_ok,sites.combined_ok],
      ["nearest_mapppd_site_id_mismatch","matching_site_over_2km",
       "second_mapppd_site_within_2km","absent_from_frozen_1997_marine_site_roster",
       "passed_geo_and_marine_site_roster"],default="UNCLASSIFIED")
    assert "UNCLASSIFIED" not in set(sites.first_failed_rule)
    assert (sites.included==sites.combined_ok).all()
    assert (len(sites),int(sites.included.sum()),int(sites.loc[~sites.included,"n_site_years"].sum()))==(113,85,144)
    summary=sites.groupby(["included","first_failed_rule"]).agg(
      sites=("site_id","nunique"),site_years=("n_site_years","sum")).reset_index()
    exp={"nearest_mapppd_site_id_mismatch":(8,42),"matching_site_over_2km":(6,33),
         "second_mapppd_site_within_2km":(12,58),"absent_from_frozen_1997_marine_site_roster":(2,11)}
    for k,(n,m) in exp.items():
        z=summary.loc[(~summary.included)&summary.first_failed_rule.eq(k)]
        assert len(z)==1 and (int(z.sites.iloc[0]),int(z.site_years.iloc[0]))==(n,m)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    sites.to_csv(out/"original113_site_geographic_gate.csv",index=False)
    summary.to_csv(out/"exact_28_site_exclusion_reasons.csv",index=False)
    regional=sites.groupby("region").agg(n_sites=("site_id","size"),retained_sites=("included","sum"),
      n_source_years=("n_site_years","sum"),retained_years=("n_site_years",
      lambda z:int(z[sites.loc[z.index,"included"]].sum()))).reset_index()
    regional["excluded_years"]=regional.n_source_years-regional.retained_years
    regional["excluded_sites"]=regional.n_sites-regional.retained_sites
    regional.to_csv(out/"source_region_selection_imbalance.csv",index=False)
    receipt={"status":"PASS_28_EXCLUDED_SITES_GEOGRAPHY_GATE_REPRODUCED",
      "source_original_583_113":{"site_years":583,"sites":113},
      "source_146_to_102_to_100_to_99":{"centroids":146,"strict_geographic_match":102,
      "with_1997_marine_roster":100,"with_1993_2013_survey_seasons":99,"survey_site_years":892},
      "main_439_85":{"retained_sites":85,"retained_site_years":439},
      "excluded_sites":28,"excluded_site_years":144,
      "first_failure_categories":{k:{"sites":n,"site_years":m} for k,(n,m) in exp.items()},
      "not_identified":"True physical explanation for a bad match (versus product/coordinate definitions) is unresolved",
      "interpretation":"Sequential dataset-eligibility filter, not biological disappearance, diet sensitivity or treatment"}
    (out/"exact_28_site_geo_gate_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ["centroids","atlas","marine","author","pinned_sites","novfeb","out"]:
        p.add_argument("--"+arg.replace("_","-"),dest=arg,required=True)
    main(p.parse_args())
