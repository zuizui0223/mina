"""Observed nest reweighting; frozen definitions in PLAN.md. No fitted biological model."""
import argparse, calendar, hashlib, importlib.util, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
WINDOWS={'long':((1993,2000),(2011,2020)), 'polynya':((2004,2010),(2013,2020))}

def save(d,name):
    d.to_csv(HERE/name,index=False,lineterminator='\n')

def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def prepare(root):
    paths={'counts':BASE/'outputs/source_observed_2456.csv',
           'atlas':BASE/'outputs/panantarctic_595_site_inventory.csv',
           'ice':root/'work/salinity42612067836/penguin-panantarctic-595site-original-1991-2020-monthly-ice/ice_595_outputs/original_595_site_months_120_source_QA.csv',
           'ocean':root/'work/salinity42958013800/penguin-original-595-colony-GLORYS12-1993-2020-18region-true-marine-months/all_original_eligible_colony_GLORYS12_1993_2020_AugNov_monthly.csv'}
    (HERE/'source_manifest.json').write_text(json.dumps({k:{'path':str(p.relative_to(root)),'sha256':digest(p)} for k,p in paths.items()},indent=2)+'\n',encoding='utf8',newline='\n')
    c=pd.read_csv(paths['counts']); atlas=pd.read_csv(paths['atlas'])
    assert len(c)==2456 and len(atlas)==595
    c=c[c.species.eq('ADPE')].copy()
    assert not c.duplicated(['site_id','season']).any()
    assert c.groupby('site_id').original_survey_method.nunique().max()==1
    assert c.observed_nest_count.ge(0).all()
    rosters=[];support=[]
    for label,windows in WINDOWS.items():
        panels=[]
        for j,(start,end) in enumerate(windows):
            g=c[c.season.between(start,end)].groupby('site_id').agg(n=('observed_nest_count','median'),n_years=('season','nunique'),years=('season',lambda x:';'.join(map(str,sorted(x)))))
            panels.append(g.add_suffix(str(j)))
        d=panels[0].join(panels[1],how='outer').reset_index()
        d['eligible_counts']=d.n_years0.ge(2)&d.n_years1.ge(2)
        d['comparison']=label;support.append(d)
        d=d[d.eligible_counts].merge(atlas[['site_id','source_region','latitude','longitude','polar_250km_fixed_grid_block']],on='site_id',validate='one_to_one')
        rosters.append(d)
    save(pd.concat(support),'census_support.csv')
    roster=pd.concat(rosters,ignore_index=True);save(roster,'count_rosters.csv')
    ids=set(roster.site_id)
    save(c[c.site_id.isin(ids)],'observed_counts_used.csv')
    ice=pd.read_csv(paths['ice']); ocean=pd.read_csv(paths['ocean'])
    for d in [ice,ocean]:
        assert not d.duplicated(['site_id','year','month']).any()
    ice=ice[ice.site_id.isin(ids)].copy(); ocean=ocean[ocean.site_id.isin(ids)].copy()
    assert set(ice.month)==set(ocean.month)=={8,9,10,11}
    ice['sic_pp']=ice.source_25km_buffer_mean_SIC_pct
    ice.loc[~ice.source_full_595_site_monthly_support.eq('OK'),'sic_pp']=np.nan
    ocean['salinity']=ocean.surface_GLORYS_salinity
    ocean['sst_C']=ocean.surface_GLORYS_thetao_C
    ocean['wet_cell']=ocean.source_original_wet_grid_y.astype(str)+':'+ocean.source_original_wet_grid_x.astype(str)
    assert ocean.groupby('site_id').wet_cell.nunique().max()==1
    valid=ocean.source_both_ocean_variables_valid.astype(str).str.lower().isin(['true','1'])
    ocean.loc[~valid,['salinity','sst_C']]=np.nan
    d=ice[['site_id','year','month','sic_pp']].merge(ocean[['site_id','year','month','salinity','sst_C','wet_cell']],on=['site_id','year','month'],how='outer',validate='one_to_one')
    rows=[]
    for (site,year),g in d.groupby(['site_id','year']):
        r={'site_id':site,'year':year,'wet_cell':g.wet_cell.dropna().iloc[0] if g.wet_cell.notna().any() else None}
        for v in ['sic_pp','salinity','sst_C']:
            r[v]=g[v].mean() if g[v].count()==4 else np.nan
        rows.append(r)
    annual=pd.DataFrame(rows);save(annual,'annual_ocean.csv')
    print(roster.groupby('comparison').agg(sites=('site_id','nunique'),regions=('source_region','nunique')).to_string(),flush=True)

def polynya(path):
    from netCDF4 import Dataset
    helper=BASE/'diet_salinity_source_20261117/extract_original_DEEPAA_100km_25km_source_20261119.py'
    spec=importlib.util.spec_from_file_location('native',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert digest(path)==m.POLY_SHA256
    manifest=json.loads((HERE/'source_manifest.json').read_text(encoding='utf8'))
    manifest['deepaa']={'filename':path.name,'sha256':m.POLY_SHA256,'url':'https://zenodo.org/records/13358042','product':'SIC60_6.25km_20d.zip'}
    (HERE/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
    d=pd.read_csv(HERE/'count_rosters.csv');d=d[d.comparison.eq('polynya')]
    sites=d[['site_id','source_region','latitude','longitude']].rename(columns={'latitude':'colony_lat','longitude':'colony_lon'})
    rows=[]
    with zipfile.ZipFile(path) as z:
        ll,mapping=m.native_map_manifest(z);lat,lon,mask=m.lonlat_grid(z,ll)
        members,geometry=m.original_native_pixel_sites(sites,lat,lon,mask);save(geometry,'polynya_geometry.csv')
        for year in list(range(2004,2011))+list(range(2013,2021)):
            days=[s for s in sorted(mapping) if int(s[:4])==year and int(s[5:7]) in m.MONTHS]
            for day in days:
                with Dataset('day.nc','r',memory=z.read(mapping[day])) as f:
                    a=np.ma.asarray(f.variables['Map'][:],dtype=float).filled(np.nan).ravel()
                for (site,radius),(idx,w) in members.items():
                    pix=a[idx];valid=np.isfinite(pix)&(pix!=-999)
                    v=pix[valid];weights=w[valid]
                    assert not ((v<0)&~np.isin(v,[-1,-2,-100])).any()
                    coastal=(v>0)&(v.astype(np.int64)%2==0)
                    rows.append(dict(site_id=site,radius=radius,year=year,month=int(day[5:7]),fraction=weights[coastal].sum()/weights.sum() if weights.sum()>0 else np.nan))
            print('polynya winter',year,'maps',len(days),flush=True)
    monthly=pd.DataFrame(rows).groupby(['site_id','radius','year','month']).fraction.agg(['count','mean']).reset_index()
    monthly['coverage']=monthly.apply(lambda r:r['count']/calendar.monthrange(int(r.year),int(r.month))[1],axis=1)
    save(monthly,'monthly_polynya.csv')
    annual=[]
    for (site,radius,year),g in monthly.groupby(['site_id','radius','year']):
        annual.append(dict(site_id=site,radius=radius,year=year,polynya_pp=100*g['mean'].mean() if len(g)==5 and g.coverage.ge(.8).all() else np.nan))
    save(pd.DataFrame(annual),'annual_polynya.csv')

def decompose(d,v):
    w0=d.n0.to_numpy()/d.n0.sum();w1=d.n1.to_numpy()/d.n1.sum()
    e0=d[v+'0'].to_numpy();e1=d[v+'1'].to_numpy()
    local=float(np.sum((w0+w1)/2*(e1-e0)))
    redistribution=float(np.sum((w1-w0)*(e0+e1)/2))
    total=float(np.sum(w1*e1)-np.sum(w0*e0))
    assert abs(local+redistribution-total)<1e-10
    return dict(variable=v,early=float(w0@e0),late=float(w1@e1),total=total,local=local,redistribution=redistribution,south_shift_km=float(111.195*((w0-w1)@d.latitude.to_numpy())),sites=len(d),regions=d.source_region.nunique(),cells=d.wet_cell.nunique())

def analyze():
    roster=pd.read_csv(HERE/'count_rosters.csv');annual=pd.read_csv(HERE/'annual_ocean.csv')
    results=[];omissions=[];matched=[];support=[];diagnostics=[]
    for label,windows in WINDOWS.items():
        radii=[100,25] if label=='polynya' else [0]
        for radius in radii:
            e=annual.copy();variables=['sic_pp','salinity','sst_C']
            if radius:
                p=pd.read_csv(HERE/'annual_polynya.csv');p=p[p.radius.eq(radius)]
                e=e.merge(p[['site_id','year','polynya_pp']],on=['site_id','year'],how='left',validate='one_to_one');variables+=['polynya_pp']
            d=roster[roster.comparison.eq(label)].copy()
            for j,(start,end) in enumerate(windows):
                g=e[e.year.between(start,end)].groupby('site_id')
                means=g[variables].mean();counts=g[variables].count()
                means=means.where(counts.eq(end-start+1)).add_suffix(str(j))
                d=d.merge(means,on='site_id',how='left',validate='one_to_one')
            d=d.merge(annual[['site_id','wet_cell']].dropna().drop_duplicates(),on='site_id',how='left',validate='one_to_one')
            needed=[v+str(j) for v in variables for j in [0,1]]
            d['missing_environment']=d[needed].apply(lambda r:';'.join(r.index[r.isna()]),axis=1)
            d['radius']=radius;support.append(d)
            # Support audit only: quantify how the complete-ocean gate changes the
            # sea-ice/latitude comparison. Not a substitute salinity estimate.
            for v in ['sic_pp']+(['polynya_pp'] if radius else []):
                q=d.dropna(subset=[v+'0',v+'1'])
                diagnostics.append(dict(comparison=label,radius=radius,**decompose(q,v)))
            d=d[d.missing_environment.eq('')].copy();matched.append(d)
            assert len(d)>=3 and d.n0.sum()>0 and d.n1.sum()>0
            for v in variables:
                results.append(dict(comparison=label,radius=radius,**decompose(d,v)))
                for unit in ['site_id','source_region','wet_cell','polar_250km_fixed_grid_block']:
                    for omitted in d[unit].unique():
                        sub=d[d[unit].ne(omitted)]
                        if len(sub)>=3 and sub.n0.sum()>0 and sub.n1.sum()>0:
                            omissions.append(dict(comparison=label,radius=radius,unit=unit,omitted=omitted,**decompose(sub,v)))
    save(pd.concat(support),'matched_support.csv');save(pd.concat(matched),'matched_rosters.csv')
    out=pd.DataFrame(results);save(out,'decomposition.csv');save(pd.DataFrame(omissions),'omissions.csv')
    save(pd.DataFrame(diagnostics),'parent_roster_support_diagnostic.csv')
    print(out.to_string(index=False))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,4,figsize=(13,6))
    units={'sic_pp':'Sea ice (percentage points)','salinity':'Surface salinity (PSU)','sst_C':'Surface temperature (C)','polynya_pp':'Coastal polynya (percentage points)'}
    for row,label in enumerate(WINDOWS):
        for col,(v,title) in enumerate(units.items()):
            ax=axes[row,col];g=out[(out.comparison==label)&out.radius.isin([0,100])&(out.variable==v)]
            if g.empty:ax.axis('off');continue
            r=g.iloc[0];ax.bar(['Local','Redistribution','Net'],[r.local,r.redistribution,r.total],color=['#2878a0','#e69f00','#555555']);ax.axhline(0,color='black',linewidth=.7)
            ax.set_title(title,fontsize=10);ax.tick_params(axis='x',rotation=20)
            if col==0:ax.set_ylabel(f'{WINDOWS[label][0]} to {WINDOWS[label][1]}\n{r.sites} sites')
    fig.suptitle('Observed nest-weighted environmental change; fixed roster within each comparison')
    fig.tight_layout();fig.savefig(HERE/'decomposition.png',dpi=180);plt.close(fig)

def tests():
    d=pd.DataFrame(dict(n0=[1.,3.],n1=[3.,1.],latitude=[-60.,-70.],source_region=['a','b'],wet_cell=['x','y'],x0=[2.,8.],x1=[3.,9.]))
    r=decompose(d,'x');assert np.isclose(r['local'],1) and np.isclose(r['redistribution'],-3)
    q=d.copy();q.n1=q.n0;assert abs(decompose(q,'x')['redistribution'])<1e-12
    q=d.copy();q.x1=q.x0;assert abs(decompose(q,'x')['local'])<1e-12
    assert decompose(d.iloc[::-1],'x')==r
    print('PASS decomposition identity, constant weights/environment, order invariance')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path);p.add_argument('--deepaa',type=Path);p.add_argument('--analyze',action='store_true');a=p.parse_args()
    tests()
    if a.root:prepare(a.root)
    if a.deepaa:polynya(a.deepaa)
    if a.analyze:analyze()
