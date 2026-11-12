"""Summarise actual support, matched biological changes and same-site terrestrial comparisons."""
import pandas as pd
import numpy as np
from acquire import R
def save(d,f):d.to_csv(R/f,index=False,lineterminator="\n")
def main():
    m=pd.read_csv(R/"expanded_marine_matches.csv").query("scope=='site' and annual and cal==5")
    summaries=[]
    for pair,t in m.groupby("pair"):
        mag=t.difference;site=t.groupby("high_site").difference.mean()
        years=set(t.high_start)|set(t.high_end)|set(t.low_start)|set(t.low_end)
        summaries.append(dict(pair=pair,sites=len(site),pairs=len(t),years=len(years),first=min(years),last=max(years),
            higher=(mag>0).sum(),equal=(mag==0).sum(),lower=(mag<0).sum(),mean=mag.mean(),median=mag.median(),
            equal_site_mean=site.mean(),leave_one_site_min=min(mag[t.high_site!=s].mean() for s in site.index),
            leave_one_site_max=max(mag[t.high_site!=s].mean() for s in site.index)))
    save(pd.DataFrame(summaries),"marine_summary.csv")
    st=pd.read_csv(R/"sentinel_seasons.csv")
    pairs=pd.read_csv(R/"sentinel_pairs.csv")
    result=[]
    for kind,t in pairs.groupby("definition"):
        for minpix in [1,5,20]:
            for annual in [False,True]:
                q=t[t.pixels>=minpix];q=q[q["last"]==q["first"]+1] if annual else q
                ndays=q.delta_days;ndvi=q.delta_ndvi
                result.append(dict(definition=kind,min_pixels=minpix,annual_only=annual,pairs=len(q),sites=q.site.nunique(),
                    distinct_summers=len(set(q["first"])|set(q["last"])),site_summers=len(set(zip(q.site,q["first"]))|set(zip(q.site,q["last"]))),
                    earlier_greener_or_later_browner=((ndays*ndvi)<0).sum(),
                    opposite=((ndays*ndvi)>0).sum(),ties=((ndays*ndvi)==0).sum(),
                    spearman=ndays.corr(ndvi,method="spearman") if len(q)>=3 and ndays.nunique()>1 and ndvi.nunique()>1 else np.nan))
    save(pd.DataFrame(result),"land_summary.csv")
    # Exact same summer year at both endpoints of a marine interval.
    q=pairs.query("definition=='resolved' and pixels>0")
    co=pd.read_csv(R/"expanded_marine_intervals.csv")
    co=co[co.ice<0].assign(first=lambda t:t.start+1,last=lambda t:t.end+1)
    save(q.merge(co,on=["site","first","last"]),"same_season_land_ocean.csv")
if __name__=="__main__":main()
