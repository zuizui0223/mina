from pathlib import Path
import sys,numpy as np,pandas as pd
R=Path(__file__).resolve().parent
def run(ice_file,ocean_file):
    ice=pd.read_csv(ice_file).query("site_id=='ARDL' and source_full_595_site_monthly_support=='OK'")
    ocean=pd.read_csv(ocean_file).query("site_id=='ARDL' and source_both_ocean_variables_valid")
    x=ice.merge(ocean,on=["site_id","year","month"],validate="one_to_one");assert (x.groupby("year").month.nunique()==4).all()
    env=x.groupby("year").agg(ice=("source_25km_buffer_mean_SIC_pct","mean"),sst=("surface_GLORYS_thetao_C","mean"))
    counts=pd.read_csv(R.parent/"salinity_snow/expanded_panel.csv").query("site_id=='ARDL' and species_pair=='ADPE__GEPE'").set_index("year")
    p=env.join(counts[["GEPE","ADPE"]]);p["extent_map"]=p.index.isin([1993,2003,2004,2005,2012,2013,2014,2015])
    p["composition_map_checked"]=p.index.isin(range(2012,2016))
    p["dec_G"]=pd.Series({2013:6187,2014:6464,2015:5726});p["dec_A"]=pd.Series({2013:429,2014:512,2015:381})
    p.to_csv(R/"annual_overlap.csv",lineterminator="\n")
    # A counts-only demographic baseline: one-year log net growth, trained only on earlier completed transitions.
    # Climate model uses preceding season levels available at origin; no future forcing required.
    rows=[]
    for sp in ["GEPE","ADPE"]:
        t=p[["ice","sst",sp]].copy();t["next"]=p[sp].shift(-1);t=t.dropna();t["growth"]=np.log(t["next"]/t[sp])
        for yr,r in t.iterrows():
            h=t[t.index<yr]
            if len(h)<6:continue
            X=np.column_stack([np.ones(len(h)),h.ice,h.sst]);assert np.linalg.matrix_rank(X)==3
            b=np.linalg.lstsq(X,h.growth,rcond=None)[0]
            rows.append(dict(species=sp,start=yr,n_train=len(h),observed=r["next"],persist=r[sp],drift=r[sp]*np.exp(h.growth.mean()),climate=r[sp]*np.exp(np.dot([1,r.ice,r.sst],b))))
    f=pd.DataFrame(rows);f.to_csv(R/"net_growth_hindcast.csv",index=False,lineterminator="\n")
    print(p[p.extent_map].round(2));print(f.groupby("species").apply(lambda g:(g[["persist","drift","climate"]].sub(g.observed,axis=0)).abs().mean(),include_groups=False));print(f.groupby("species").size())
if __name__=="__main__":run(*sys.argv[1:])
