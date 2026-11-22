"""Independent January-only verification on archived 20 m Sentinel-2 pixel stacks."""
from itertools import combinations
import io,zipfile
import pandas as pd,numpy as np
from acquire import R,O
from modis import write
from land import med
def member(z,name):return np.load(io.BytesIO(z.read(name)),allow_pickle=False)
records=[];pairs=[]
annual=pd.read_csv(O/"vegetation_annual_ndvi_v1/annual_support.csv")
with zipfile.ZipFile(O/"vegetation_annual_pixels_v1/pixel_sources.zip") as z,zipfile.ZipFile(O/"vegetation_annual_ndvi_v1/ndvi_sources.zip") as nz,np.load(O/"ndvi_vegetation_overlay_v1/mapped_masks.npz") as mz:
    for site,t in annual.groupby("site_id"):
        mask=mz[site+"_pixel_center"];n=int(mask.sum());seasons={}
        for y in t.image_year:
            a=member(z,f"pixels/{site}_{y}.npz");v=member(nz,f"checked_arrays/{site}_{y}.npz")
            days=pd.to_datetime(a["dates"].astype(str)).day.to_numpy()
            snow=a["snow"][:,mask] & ~a["conflict"][:,mask];land=a["land"][:,mask] & ~a["conflict"][:,mask]
            vdays=pd.to_datetime(v["dates"].astype(str)).day.to_numpy();nd=v["daily_ndvi"][:,mask]
            lo=np.full(n,np.nan);hi=lo.copy();end=lo.copy();g=np.full_like(nd,np.nan)
            for i in range(n):
                ss=days[snow[:,i]]
                if not len(ss):continue
                free=days[(days>max(ss)) & land[:,i]]
                if len(free)<2:continue
                lo[i],hi[i],end[i]=max(ss),free[0],free[1]
                use=(vdays>end[i]) & (vdays>=16);g[use,i]=nd[use,i]
            records.append(dict(site=site,year=y,mapped_pixels=n,bracketed=np.isfinite(lo).sum(),later_2dates=(np.isfinite(g).sum(axis=0)>=2).sum()))
            seasons[y]=(lo,hi,vdays,g)
        for y1,y2 in combinations(sorted(seasons),2):
            a,b,days1,g1=seasons[y1];c,d,days2,g2=seasons[y2]
            # Each date used once in each year; compare near-calendar days after local clearance.
            pix=[];resolved=[]
            for i in range(n):
                x=np.flatnonzero(np.isfinite(g1[:,i]));w=np.flatnonzero(np.isfinite(g2[:,i]))
                if min(len(x),len(w))<2:continue
                from scipy.optimize import linear_sum_assignment
                dist=np.abs(days1[x,None]-days2[w]);r,j=linear_sum_assignment(np.where(dist<=3,dist,10000));ok=dist[r,j]<=3
                if ok.sum()<2:continue
                td=(c[i]+d[i]-a[i]-b[i])/2;green=np.median(g2[w[j[ok]],i]-g1[x[r[ok]],i])
                pix.append((td,green))
                if d[i]<a[i] or b[i]<c[i]:resolved.append((td,green))
            for key,arr in [("midpoint",pix),("resolved",resolved)]:
                pairs.append(dict(site=site,first=y1,last=y2,definition=key,pixels=len(arr),delta_days=med(np.array(arr)[:,0]) if arr else np.nan,delta_ndvi=med(np.array(arr)[:,1]) if arr else np.nan))
write(pd.DataFrame(records),"january_seasons.csv");write(pd.DataFrame(pairs),"january_pairs.csv")
print(pd.DataFrame(records).query("bracketed>0"));print(pd.DataFrame(pairs).query("pixels>0"))
