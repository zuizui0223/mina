"""Match earlier/later snow clearance and subsequent NDVI on identical mapped pixels."""
import json,warnings
from itertools import combinations
import pandas as pd,numpy as np
from optical import sites,F,R
from modis import write
def med(a,axis=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore",RuntimeWarning)
        return np.nanmedian(a,axis=axis)
def season(site,y):
    mask=np.load(F/(site+"_mask.npy")).astype(bool);n=mask.sum()
    origin=pd.Timestamp(y-1,10,1)
    rows=sorted([r for f in F.glob(f"{site}_{y}_*_series.json") for r in json.loads(f.read_text())],key=lambda r:r["date"])
    assert len({r["date"] for r in rows})==len(rows)
    days=[];states=[];late=[]
    for r in rows:
        a=np.load(F/f"{site}_{r['id']}.npz");dt=pd.Timestamp(r["date"]);day=(dt-origin).days
        s=a["scl"][mask];days.append(day);states.append(s)
        if "red" in a:
            red=a["red"][mask];nir=a["nir"][mask]
            ok=np.isin(s,[4,5]) & (red>0) & (nir>0); k=(dt.month-1)*2+int(dt.day>15)
            v=np.full(n,np.nan);v[ok]=(nir[ok]-red[ok])/(nir[ok]+red[ok]);late.append((k,day,v))
    lo=np.full(n,np.nan);hi=lo.copy();conf=lo.copy()
    s=np.array(states).reshape(len(days),n);days=np.array(days)
    for i in range(n):
        spring=days<(pd.Timestamp(y,2,1)-origin).days
        snowy=days[(s[:,i]==11)&spring]
        if not len(snowy):continue
        free=days[(days>snowy[-1]) & spring & np.isin(s[:,i],[4,5])]
        if len(free)>=2 and free[0]-snowy[-1]<=32 and free[1]-free[0]<=32:
            lo[i],hi[i],conf[i]=snowy[-1],free[0],free[1]
    nd=np.full((6,n),np.nan)
    for k in range(6):
        v=[np.where(day>conf,values,np.nan) for idx,day,values in late if idx==k]
        if v and n:nd[k]=med(np.stack(v),axis=0)
    return lo,hi,nd,dict(site=site,summer=y,scenes=len(rows),mapped_pixels=n,bracketed=int(np.isfinite(lo).sum()),
        one_later=int((np.isfinite(nd[2:]).sum(axis=0)>=1).sum()),two_later=int((np.isfinite(nd[2:]).sum(axis=0)>=2).sum()),
        one_later_jan_mar=int((np.isfinite(nd).sum(axis=0)>=1).sum()),two_later_jan_mar=int((np.isfinite(nd).sum(axis=0)>=2).sum()),
        median_lower_day=med(lo) if n else np.nan,median_upper_day=med(hi) if n else np.nan)
if __name__=="__main__":
    out=[];records=[];pix=[]
    for site in sites:
        seasons={}
        for year in range(2018,2026):
            l,h,nd,rec=season(site,year);seasons[year]=(l,h,nd);out.append(rec)
        for a,b in combinations(seasons,2):
            al,ah,an=seasons[a];bl,bh,bn=seasons[b]
            allbins=np.isfinite(an)&np.isfinite(bn)
            use=allbins.copy();use[:2]=False
            keep=use.sum(axis=0)>=2
            snow=((bl+bh)-(al+ah))/2;green=med(np.where(use,bn-an,np.nan),axis=0)
            clear_order=(bh<al)|(ah<bl)
            for i in np.flatnonzero(keep):
                pix.append(dict(site=site,first=a,last=b,mask_index=i,first_last_snow=al[i],first_free=ah[i],
                    last_last_snow=bl[i],last_free=bh[i],delta_days=snow[i],delta_ndvi=green[i],resolved=clear_order[i],
                    common_bins=use[:,i].sum()))
            for label,k in [("midpoint",keep),("resolved",keep&clear_order),("single_bin_feb_mar",use.any(axis=0)),("single_bin_jan_mar",allbins.any(axis=0))]:
                if label=="single_bin_jan_mar":green=med(np.where(allbins,bn-an,np.nan),axis=0)
                records.append(dict(site=site,first=a,last=b,definition=label,pixels=k.sum(),
                    delta_days=med(snow[k]) if k.any() else np.nan,delta_ndvi=med(green[k]) if k.any() else np.nan))
    write(pd.DataFrame(out),"sentinel_seasons.csv");write(pd.DataFrame(records),"sentinel_pairs.csv")
    write(pd.DataFrame(pix,columns=["site","first","last","mask_index","first_last_snow","first_free","last_last_snow","last_free","delta_days","delta_ndvi","resolved","common_bins"]),"sentinel_pixels.csv")
    print(pd.DataFrame(out).groupby("site").sum(numeric_only=True)[["scenes","bracketed","two_later"]])
    print(pd.DataFrame(records).query("pixels>0"))
