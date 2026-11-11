from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import gzip,json,time,sys
import pandas as pd
import requests
R=Path(__file__).resolve().parent
O=R.parents[1]/"outputs"
S=R.parent/"space_for_time"
def roster():
    counts=pd.read_csv(next(S.glob("observed_2species*.csv")))
    a=pd.DataFrame([(s,y+1,"penguin") for s in sorted(set(counts.site_id)) for y in range(2011,2021)],columns=["site_id","summer","cohort"])
    b=pd.read_csv(O/"vegetation_annual_ndvi_v1/annual_support.csv")[["site_id","image_year"]].rename(columns={"image_year":"summer"}).assign(cohort="sentinel")
    return pd.concat([a,b],ignore_index=True)
def jobs():
    coords=pd.read_csv(O/"vegetation_response_v1/site_species_cohort.csv")
    macro=pd.read_csv(O/"sic_spatial_coherence_macro40_v1/macro40_site_coordinates.csv")
    coords=pd.concat([macro,coords]).drop_duplicates("site_id").set_index("site_id")
    for r in roster().itertuples():
        c=coords.loc[r.site_id]
        for year,lo,hi in [(r.summer-1,273,345),(r.summer-1,353,361),(r.summer,1,73)]:
            yield (r.site_id,r.summer,float(c.latitude),float(c.longitude),f"A{year}{lo:03}",f"A{year}{hi:03}")
def fetch(j):
    site,summer,lat,lon,start,end=j
    cache=R/"raw"/f"{site}_{summer}_{start}.json.gz"
    if cache.exists():return
    for attempt in range(4):
        try:
            response=requests.get("https://modis.ornl.gov/rst/api/v1/MOD09A1/subset",params=dict(latitude=lat,longitude=lon,startDate=start,endDate=end,kmAboveBelow=0,kmLeftRight=0),timeout=75)
            response.raise_for_status()
            d=response.json()
            assert d["ncols"]==d["nrows"]==1 and d["subset"]
            cache.write_bytes(gzip.compress(response.content,mtime=0))
            return
        except Exception as e:
            err=str(e)
            time.sleep(2**attempt)
    print(site,start,err,flush=True)
if __name__=="__main__":
    (R/"raw").mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=12) as ex:list(ex.map(fetch,jobs()))
