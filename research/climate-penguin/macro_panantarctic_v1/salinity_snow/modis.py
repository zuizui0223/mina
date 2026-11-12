"""Coarse MODIS timing check and same-colony join to archived January Sentinel NDVI."""
from acquire import R,O,roster,jobs
import gzip,json
from pathlib import Path
import pandas as pd,numpy as np

def write(frame,name):frame.to_csv(R/name,index=False,lineterminator="\n")
def decode(path):
    d=json.load(gzip.open(path));rows=[]
    items=pd.DataFrame(d["subset"]);items["v"]=items.data.str[0]
    for day,v in items.pivot(index="calendar_date",columns="band",values="v").iterrows():
        start=pd.Timestamp(day);doy=int(v.sur_refl_day_of_year)
        if not 1<=doy<=366:continue
        date=pd.Timestamp(start.year,1,1)+pd.Timedelta(days=doy-1)
        if not 0<=(date-start).days<=7:continue
        state=int(v.sur_refl_state_500m);qc=int(v.sur_refl_qc_500m)
        land=state!=65535 and (state>>3)&7==1
        clear=land and state&3==0 and state&4==0 and (state>>8)&3==0 and (state>>10)&1==0 and (state>>13)&1==0
        snow=(state>>12)&1; internal=(state>>15)&1
        valid=clear and snow==internal
        red,nir=int(v.sur_refl_b01),int(v.sur_refl_b02)
        ndvi=(nir-red)/(nir+red) if valid and snow==0 and qc&3<=1 and (qc>>2)&15==0 and (qc>>6)&15==0 and 0<min(red,nir) and max(red,nir)<=16000 else np.nan
        rows.append(dict(date=date,land=land,clear=clear,snow=snow if valid else np.nan,ndvi=ndvi))
    return rows
if __name__=="__main__":
    rows=[];daily=[]
    for a in roster().itertuples():
        site,y=a.site_id,a.summer
        files=list((R/"raw").glob(f"{site}_{y}_*.json.gz"))
        assert len(files)==3,(site,y,len(files))
        days=pd.DataFrame([r for p in files for r in decode(p)],columns=["date","land","clear","snow","ndvi"]).sort_values("date")
        daily.append(days.assign(site=site,summer=y)); valid=days.dropna(subset=["snow"])
        # Last observed snow and two clear, snow-free observations. January NDVI must follow both.
        s=valid[valid.snow==1];lo=hi=confirm=pd.NaT
        if len(s):
            last=s.date.max();free=valid[valid.date>last]
            if len(free)>=2 and (free.date.iloc[0]-last).days<=32 and (free.date.iloc[1]-free.date.iloc[0]).days<=32:
                lo=last;hi=free.date.iloc[0];confirm=free.date.iloc[1]
        jan1=pd.Timestamp(y,1,1)
        rows.append(dict(site=site,summer=y,cohort=a.cohort,days=len(days),land=int(days.land.sum()),valid=len(valid),
            snow_days=len(s),snow_last=lo,first_free=hi,confirmed=confirm,
            pre_jan=pd.notna(confirm) and confirm<jan1,
            midpoint_day=((lo+(hi-lo)/2)-jan1).total_seconds()/86400 if pd.notna(lo) else np.nan))
    annual=pd.DataFrame(rows);write(annual,"modis_seasons.csv");write(pd.concat(daily),"modis_daily.csv")
    pairs=pd.read_csv(O/"ndvi_vegetation_overlay_v1/pair_mapped_changes.csv").query("mask=='pixel_center'").copy()
    for col in ["first_year","last_year"]:
        a=annual.query("cohort=='sentinel'")[["site","summer","pre_jan","midpoint_day"]]
        pairs=pairs.merge(a.rename(columns=dict(site="site_id",summer=col,pre_jan=col+"_pre_jan",midpoint_day=col+"_mid")),on=["site_id",col],validate="many_to_one")
    pairs["supported"]=pairs.first_year_pre_jan & pairs.last_year_pre_jan & (pairs.mapped_common_pixels>0)
    write(pairs,"modis_sentinel_join.csv")
    print(annual.groupby("cohort").agg(n=("site","size"),sites=("site","nunique"),timed=("first_free","count"),pre=("pre_jan","sum")));print("matched",pairs.supported.sum())
