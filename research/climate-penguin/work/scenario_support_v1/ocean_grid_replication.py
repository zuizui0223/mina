"""Map frozen observation rows to exact shared GLORYS cells."""
from pathlib import Path
import hashlib,json
import pandas as pd
import numpy as np
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ocean_grid_replication_v1';out.mkdir(exist_ok=True)
sources=[root/'relationship_response_v1/cohort.csv',root/'climate_penguin/behavior_ocean_join.csv',root/'climate_penguin/ocean_grid_support.csv']
d=pd.read_csv(sources[0]);raw=pd.read_csv(sources[1]).set_index('source_row_1based');grid=pd.read_csv(sources[2]).set_index('location_id')
assert raw.index.is_unique and grid.index.is_unique
rows=[]
for r in d.itertuples():
    q=raw.loc[list(map(int,r.source_rows.split('|')))];g=grid.loc[q.location_id]
    cells=sorted(set(zip(g.grid_y.astype(int),g.grid_x.astype(int))))
    assert q.species.eq(r.species).all() and q.cam.eq(r.cam).all() and q.season_start_year.eq(r.year).all()
    assert np.isclose(q.ocean_m9_surface_salinity.mean()/.1,r.salt01)
    rows.append(dict(scope=r.scope,species=r.species,cam=r.cam,year=r.year,source_rows=r.source_rows,
        cells='|'.join(f'{y}:{x}' for y,x in cells),n_cells=len(cells),
        maximum_grid_distance_km=g.grid_distance_km.max(),salt01=r.salt01))
a=pd.DataFrame(rows);assert len(a)==len(d)
a.to_csv(out/'observation_cells.csv',index=False)
summary=[];shared=[]
for (scope,sp),g in a.groupby(['scope','species']):
    sites=g[['cam','cells']].drop_duplicates()
    assert not sites.cam.duplicated().any()
    grouped=sites.groupby('cells').cam.agg(list)
    for cells,cams in grouped.items():shared.append(dict(scope=scope,species=sp,cells=cells,sites=len(cams),camera_codes='|'.join(sorted(cams))))
    summary.append(dict(scope=scope,species=sp,observations=len(g),sites=g.cam.nunique(),cell_sets=g.cells.nunique(),
        multi_cell_observations=int(g.n_cells.gt(1).sum()),shared_cell_sets=int(grouped.map(len).gt(1).sum()),
        maximum_sites_sharing=int(grouped.map(len).max()),cell_years=len(g[['cells','year']].drop_duplicates())))
pd.DataFrame(summary).to_csv(out/'summary.csv',index=False);pd.DataFrame(shared).to_csv(out/'site_groups.csv',index=False)
# Exact single-cell shared exposures must agree within a cell-year, including across species.
checks=0
for key,g in a[a.n_cells.eq(1)].groupby(['scope','cells','year']):
    assert np.allclose(g.salt01,g.salt01.iloc[0],rtol=0,atol=1e-10)
    checks+=1
v=dict(passed=True,observation_rows=len(a),single_cell_year_checks=checks,
    hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    limits=['Cell sets are exact extraction identities, not independent ecological replicates',
            'Different cells can still share regional forcing and assimilation errors',
            'Camera code is the frozen geographic aggregation, not a count of individual cameras'])
(out/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(pd.DataFrame(summary).to_string(index=False))
