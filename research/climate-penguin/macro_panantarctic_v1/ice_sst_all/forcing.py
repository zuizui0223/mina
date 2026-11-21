from pathlib import Path
import sys,json
from concurrent.futures import ThreadPoolExecutor
import numpy as np,pandas as pd,dask
R=Path(__file__).resolve().parent
root=R.parents[1]
sys.path.insert(0,str(root/"work/cmip6_projection_v1"))
import extract
def main():
    extract.OUT=R/"forcing";extract.OUT.mkdir(exist_ok=True)
    extract.WORK=extract.OUT
    q=pd.read_csv(R.parent/"salinity_all/intervals.csv")
    coords=pd.read_csv(root/"outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv")
    sites=coords[coords.site_id.isin(q.site)][["site_id","latitude","longitude"]].drop_duplicates().copy()
    assert sites.site_id.is_unique and set(sites.site_id)==set(q.site)
    sites["location_id"]=sites.site_id;sites["cohort"]="repeated_co_census"
    selected=pd.concat([pd.read_csv(R/"tos_stores.csv"),pd.read_csv(root/"outputs/cmip6_projection_v1/selected_stores.csv").query("variable_id=='siconc'")])
    def run(job):
        source,var=job
        tab=extract.OUT/f"{source}_{var}.csv"
        if tab.exists():return
        rec,meta=extract.read_variable(source,var,selected,sites)
        pd.DataFrame(rec).to_csv(tab,index=False)
        tab.with_suffix(".json").write_text(json.dumps(meta,indent=2))
    with dask.config.set(scheduler="threads",num_workers=3),ThreadPoolExecutor(2) as pool:
        list(pool.map(run,list(selected[["source_id","variable_id"]].drop_duplicates().itertuples(index=False,name=None))))
if __name__=="__main__":main()
