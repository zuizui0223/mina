"""Frozen exploratory winter/lead-winter contrast; stage gates precede outcome fit."""
import argparse, calendar, hashlib, importlib.util, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t
import statsmodels.api as sm

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
P='direct_DEEPAA_coastal_polynya_fraction'
Y='predicted_d15N_season_day_equal'
CONTROLS=['mean_doy_centered','mean_doy_sq','GLORYS_NovFeb_thetao_C','author_SIC_150km_NovFeb_center_approx_fraction','GLORYS_NovFeb_salinity']

def save(d,name): d.to_csv(HERE/name,index=False,lineterminator='\n')
def write(d,name): (HERE/name).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
def member(path,name,**kw):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return pd.read_csv(io.BytesIO(z.read(name)),**kw)
def native():
    path=BASE/'diet_salinity_source_20261117/extract_original_DEEPAA_100km_25km_source_20261119.py'
    s=importlib.util.spec_from_file_location('native',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def source(root):
    from netCDF4 import Dataset
    cache=root/'work/polynya_temporal_review'
    paths={'physical':cache/'14539723210.zip','image_days':cache/'14326122826.zip','isotope':cache/'14328755565.zip','deepaa':root/'work/signy_polynya_full/deepaa_verified.zip'}
    hashes={k:digest(p) for k,p in paths.items()}
    assert hashes['isotope']=='dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205'
    m=native();assert hashes['deepaa']==m.POLY_SHA256
    write({k:dict(path=str(v.relative_to(root)),sha256=hashes[k]) for k,v in paths.items()},'source_manifest.json')
    ph=member(paths['physical'],'source_original_860_site_seasons_true_DEEPAA100km_no_optical_Y.csv')
    ph=ph[ph[P].notna()].copy();assert len(ph)==439
    days=member(paths['image_days'],'source_d15N_proxy_site_season_day.csv',usecols=['site_id','season','year','month','day','n_original_pixels'])
    days=days.merge(ph[['site_id','season']],on=['site_id','season'],validate='many_to_one')
    assert not days.duplicated(['site_id','season','year','month','day']).any()
    days['date']=pd.to_datetime(days[['year','month','day']])
    days['winter_end']=pd.to_datetime(days.season.astype(str)+'-10-31')
    days['summer_end']=pd.to_datetime((days.season+1).astype(str)+'-03-01')
    days['lead_start']=pd.to_datetime((days.season+1).astype(str)+'-06-01')
    days['temporal_order_ok']=(days.date>days.winter_end)&(days.date<days.summer_end)&(days.date<days.lead_start)
    days['gap_days_to_lead']=(days.lead_start-days.date).dt.days
    save(days,'image_date_audit.csv')
    timing=days.groupby(['site_id','season']).agg(first_date=('date','min'),last_date=('date','max'),n_image_days=('date','size'),temporal_order_ok=('temporal_order_ok','all'),min_gap_days=('gap_days_to_lead','min')).reset_index()
    support=ph.merge(timing,on=['site_id','season'],how='left',validate='one_to_one')
    assert len(support)==439 and support.temporal_order_ok.eq(True).all()
    geo=member(paths['physical'],'source_original_88_site_polynya_25km_100km_native_grid_geography.csv')
    sites=geo[geo.radius_km.eq(100)&geo.site_id.isin(ph.site_id)][['site_id','source_region','colony_lat','colony_lon']]
    assert len(sites)==85
    rows=[]
    with zipfile.ZipFile(paths['deepaa']) as z:
        ll,mapping=m.native_map_manifest(z);lat,lon,mask=m.lonlat_grid(z,ll)
        members,geometry=m.original_native_pixel_sites(sites,lat,lon,mask)
        members={k:v for k,v in members.items() if k[1]==100};save(geometry[geometry.radius_km.eq(100)],'geometry.csv')
        coverage=m.valid_daily_days(mapping,range(2004,2012));write(coverage,'winter_source_coverage.json')
        for year in range(2004,2012):
            if not coverage[year]: continue
            selected=[day for day in sorted(mapping) if int(day[:4])==year and int(day[5:7]) in m.MONTHS]
            for day in selected:
                with Dataset('day.nc','r',memory=z.read(mapping[day])) as f:
                    a=np.ma.asarray(f.variables['Map'][:],dtype=float).filled(np.nan)
                assert a.shape==(1264,1328);a=a.ravel()
                for (site,_),(idx,weights) in members.items():
                    pix=a[idx];valid=np.isfinite(pix)&(pix!=-999)
                    v=pix[valid];w=weights[valid]
                    assert not ((v<0)&~np.isin(v,[-1,-2,-100])).any()
                    coastal=(v>0)&(v.astype(np.int64)%2==0)
                    rows.append(dict(site_id=site,year=year,month=int(day[5:7]),fraction=w[coastal].sum()/w.sum() if w.sum()>0 else np.nan,marine_pixels=int(valid.sum())))
            print('native winter',year,'maps',len(selected),flush=True)
    monthly=pd.DataFrame(rows).groupby(['site_id','year','month']).agg(n_days=('fraction','count'),fraction=('fraction','mean'),min_marine_pixels=('marine_pixels','min')).reset_index()
    monthly['coverage']=monthly.apply(lambda r:r.n_days/calendar.monthrange(int(r.year),int(r.month))[1],axis=1)
    save(monthly,'monthly_polynya.csv')
    annual=[]
    for (site,year),g in monthly.groupby(['site_id','year']):
        annual.append(dict(site_id=site,year=year,fraction=g.fraction.mean() if len(g)==5 and g.coverage.ge(.8).all() else np.nan))
    annual=pd.DataFrame(annual);save(annual,'annual_polynya.csv')
    now=annual.rename(columns={'year':'season','fraction':'P0'})
    future=annual.rename(columns={'year':'season','fraction':'P1'});future.season-=1
    support=support.merge(now,on=['site_id','season'],how='left',validate='one_to_one').merge(future,on=['site_id','season'],how='left',validate='one_to_one')
    assert np.allclose(support.P0,support[P],atol=1e-12)
    support['eligible']=support[['P0','P1']].notna().all(axis=1)&support.temporal_order_ok
    support['exclusion_reason']=np.where(support.eligible,'','next_winter_unavailable')
    save(support,'support_before_outcome.csv')
    eligible=support[support.eligible]
    audit=dict(original_rows=len(support),eligible_rows=len(eligible),sites=eligible.site_id.nunique(),regions=eligible.source_region.nunique(),winters=eligible.season.nunique(),all_image_dates_ordered=bool(support.temporal_order_ok.all()),min_gap_days=int(support.min_gap_days.min()),P0_reconstruction_max_abs=float(abs(support.P0-support[P]).max()),years=eligible.groupby('season').size().to_dict())
    audit['passes_support']=bool(audit['sites']>=30 and audit['regions']>=6 and audit['winters']>=4 and audit['all_image_dates_ordered'])
    write(audit,'support_audit.json');print(json.dumps(audit,indent=2),flush=True)

def residualize(v,d):
    a=np.asarray(v,dtype=float).copy()
    if a.ndim==1:a=a[:,None]
    for _ in range(3000):
        before=a.copy()
        a-=pd.DataFrame(a).groupby(d.site_id.to_numpy()).transform('mean').to_numpy()
        a-=pd.DataFrame(a).groupby(d.region_year.to_numpy()).transform('mean').to_numpy()
        if np.max(abs(a-before))<1e-10:break
    else:raise ValueError('FE projection did not converge')
    return a

def fit(d,features):
    cols=CONTROLS+features
    x=residualize(d[cols],d);y=residualize(d[Y],d).ravel()
    assert np.linalg.matrix_rank(x)==len(cols)
    f=sm.OLS(y,x).fit(cov_type='cluster',cov_kwds={'groups':d.source_region.to_numpy()})
    g=d.source_region.nunique();critical=t.ppf(.975,g-1)
    rows=[]
    for p in features:
        i=cols.index(p);b=float(f.params[i]*.1);se=float(f.bse[i]*.1)
        rows.append(dict(term=p,beta_per_10pp=b,se=se,lower=b-critical*se,upper=b+critical*se))
    if len(features)==2:
        v=np.zeros(len(cols));v[-2:]=[.1,-.1]
        b=float(v@f.params);se=float(np.sqrt(v@f.cov_params()@v))
        rows.append(dict(term='P0_minus_P1',beta_per_10pp=b,se=se,lower=b-critical*se,upper=b+critical*se))
    return rows,x,f

def outcome(root):
    audit=json.loads((HERE/'support_audit.json').read_text());assert audit['passes_support']
    support=pd.read_csv(HERE/'support_before_outcome.csv');support=support[support.eligible]
    path=root/'work/polynya_temporal_review/14328755565.zip'
    manifest=json.loads((HERE/'source_manifest.json').read_text());assert digest(path)==manifest['isotope']['sha256']
    iso=member(path,'matched_860_original_isotope_ocean_ice_site_seasons.csv')
    d=iso.merge(support[['site_id','season','P0','P1','n_image_days']],on=['site_id','season'],validate='one_to_one')
    assert len(d)==audit['eligible_rows'] and d.n_observed_days.eq(d.n_image_days).all()
    assert np.isfinite(d[[Y,'P0','P1']+CONTROLS]).all().all()
    d['region_year']=d.source_region+'__'+d.season.astype(str)
    save(d,'matched_analysis.csv')
    x=residualize(d[CONTROLS+['P0','P1']],d)
    c=x[:,:len(CONTROLS)];pr=x[:,-2:]-c@np.linalg.lstsq(c,x[:,-2:],rcond=None)[0]
    corr=float(np.corrcoef(pr.T)[0,1]);std=x.std(axis=0)
    diag=dict(residual_correlation=corr,P0_residual_std=float(pr[:,0].std()),P1_residual_std=float(pr[:,1].std()),rank=int(np.linalg.matrix_rank(x)),columns=x.shape[1],standardized_condition_number=float(np.linalg.cond(x/std)))
    diag['identifiable']=bool(diag['rank']==diag['columns'] and min(diag['P0_residual_std'],diag['P1_residual_std'])>1e-8 and abs(corr)<.95)
    write(diag,'identification.json')
    if not diag['identifiable']:
        write(dict(verdict='NOT_IDENTIFIABLE',chlorophyll='NOT_RUN_FROZEN_GATE'),'verdict.json');return
    results=[]
    for name,features in [('Mnow',['P0']),('Mlead',['P1']),('Mjoint',['P0','P1'])]:
        rows,_,_=fit(d,features)
        results.extend(dict(model=name,n=len(d),regions=d.source_region.nunique(),**r) for r in rows)
    result=pd.DataFrame(results);save(result,'coefficients.csv')
    omit=[]
    for region in sorted(d.source_region.unique()):
        sub=d[d.source_region.ne(region)].copy()
        try:
            rows,_,_=fit(sub,['P0','P1'])
            omit.extend(dict(omitted_region=region,n=len(sub),status='OK',**r) for r in rows)
        except (AssertionError,ValueError):
            omit.append(dict(omitted_region=region,n=len(sub),status='NOT_IDENTIFIABLE'))
    omission=pd.DataFrame(omit);save(omission,'region_omissions.csv')
    main=result[result.model.eq('Mjoint')].set_index('term')
    robust=bool(omission.status.eq('OK').all() and omission[omission.term.isin(['P0','P0_minus_P1'])].beta_per_10pp.lt(0).all())
    passed=bool(main.loc['P0','upper']<0 and main.loc['P0_minus_P1','upper']<0 and robust)
    write(dict(verdict='TIME_SPECIFICITY_SUPPORTED' if passed else 'TIME_SPECIFICITY_NOT_ESTABLISHED',chlorophyll='NEXT_STAGE_REQUIRED' if passed else 'NOT_RUN_FROZEN_GATE',joint_P0_upper=float(main.loc['P0','upper']),contrast_upper=float(main.loc['P0_minus_P1','upper']),all_region_omission_signs_negative=robust),'verdict.json')
    print(result.to_string(index=False));print((HERE/'verdict.json').read_text())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--stage',choices=['source','outcome'],required=True);a=p.parse_args()
    (source if a.stage=='source' else outcome)(a.root)
