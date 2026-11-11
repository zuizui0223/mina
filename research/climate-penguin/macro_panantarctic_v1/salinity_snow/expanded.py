"""Join complete Aug-Nov original ocean and satellite months with actual co-censuses."""
from acquire import R
import pandas as pd,sys
from pathlib import Path
def build(glorys,osi):
    g=pd.read_csv(glorys);i=pd.read_csv(osi)
    assert len(g)==65856 and len(i)==71400
    assert g.source_both_ocean_variables_valid.all() and max(g.source_geodesic_wet_cell_distance_km)<=25
    keys=["site_id","source_region","year","month"]
    m=g.merge(i.query("source_full_595_site_monthly_support=='OK'"),on=keys,validate="one_to_one")
    season=m.groupby(keys[:3],as_index=False).agg(n=("month","nunique"),source_SIC_pp=("source_25km_buffer_mean_SIC_pct","mean"),source_glorys_salinity=("surface_GLORYS_salinity","mean"),source_glorys_thetao_C=("surface_GLORYS_thetao_C","mean")).query("n==4")
    c=pd.read_csv(R.parent/"outputs/source_observed_2456.csv"); assert len(c)==2456
    t=c.pivot(index=["site_id","source_region","season"],columns="species",values="observed_nest_count").reset_index().rename(columns={"season":"year"})
    rows=[]
    for species in ["ADPE","CHPE"]:
        b=t.dropna(subset=["GEPE",species]).copy();b["total"]=b.GEPE+b[species]
        b=b[b.total>0].merge(season,on=keys[:3],validate="one_to_one")
        b["share"]=100*b.GEPE/b.total;b["species_pair"]=species+"__GEPE"
        rows.append(b)
    out=pd.concat(rows).sort_values(["species_pair","site_id","year"])
    out.to_csv(R/"expanded_panel.csv",index=False,lineterminator="\n")
    print(out.groupby("species_pair").agg(rows=("year","size"),sites=("site_id","nunique"),regions=("source_region","nunique"),years=("year","nunique")))
if __name__=="__main__":build(*sys.argv[1:])
