"""Fixed Signy diet test. See PLAN.md; raw archives remain outside git."""
import argparse, calendar, hashlib, importlib.util, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from netCDF4 import Dataset
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent

def save(d, name):
    d.to_csv(HERE / name, index=False, lineterminator='\n')

def stomachs(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith('signy_adelie_diet_summary.csv')]
        assert len(names) == 1
        raw = z.read(names[0])
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == 'ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d'
    d = pd.read_csv(io.BytesIO(raw))
    d['date'] = pd.to_datetime(d.DATE, format='%Y-%m-%d', errors='raise')
    d['season'] = d.date.dt.year - d.date.dt.month.le(4).astype(int)
    cols = ['FISH_MASS_g','CRUSTACEAN_MASS_g','CEPHALOPOD_MASS_g','OTHER_FOOD_MASS_g','TOTAL_MASS_g','EUPHAUSIA_SUPERBA_MASS_g']
    d[cols] = d[cols].apply(pd.to_numeric, errors='coerce')
    d['food'] = d[cols[:4]].sum(axis=1, min_count=4)
    d['krill_fraction'] = d.EUPHAUSIA_SUPERBA_MASS_g / d.food
    d['fish_fraction'] = d.FISH_MASS_g / d.food
    d['sampling_day'] = (d.date - pd.to_datetime(d.season.astype(str)+'-11-01')).dt.days
    tests = {
        'duplicate_key': d.duplicated(['DATE','RECORD_ID'],keep=False),
        'outside_season': ~d.date.dt.month.isin([11,12,1,2,3,4]),
        'missing_or_negative_mass': ~(d[cols].ge(0).all(axis=1)),
        'nonpositive_food_or_total': ~(d.food.gt(0)&d.TOTAL_MASS_g.gt(0)),
        'food_over_total': d.food.gt(d.TOTAL_MASS_g*1.05+.05),
        'krill_over_crustacean': d.EUPHAUSIA_SUPERBA_MASS_g.gt(d.CRUSTACEAN_MASS_g*1.05+.05),
        'invalid_fraction': ~(d.krill_fraction.between(0,1)&d.fish_fraction.between(0,1)),
    }
    flags=pd.DataFrame(tests,index=d.index)
    d['exclusion_reason']=flags.apply(lambda r:';'.join(r.index[r]),axis=1)
    save(d[['DATE','RECORD_ID','season','food','krill_fraction','fish_fraction','sampling_day','exclusion_reason']], 'stomach_audit.csv')
    rows=[]
    for year,g in d.groupby('season'):
        v=g[g.exclusion_reason.eq('')]
        rows.append(dict(season=int(year),n_raw=len(g),n_valid=len(v),first_date=g.DATE.min(),last_date=g.DATE.max(),sampling_day=v.sampling_day.mean(),krill_fraction=v.krill_fraction.mean(),fish_fraction=v.fish_fraction.mean(),krill_ratio_of_sums=v.EUPHAUSIA_SUPERBA_MASS_g.sum()/v.food.sum() if len(v) else np.nan))
    annual=pd.DataFrame(rows); save(annual,'signy_annual_diet.csv')
    assert annual.n_raw.sum()==len(d)
    return annual,dict(raw_rows=len(d),valid_rows=int(d.exclusion_reason.eq('').sum()),seasons=len(annual),first_sample=d.DATE.min(),last_sample=d.DATE.max(),source_sha256=sha,exclusions={k:int(v.sum()) for k,v in tests.items()})

def environment(path):
    helper=HERE.parent/'diet_salinity_source_20261117/extract_original_DEEPAA_100km_25km_source_20261119.py'
    spec=importlib.util.spec_from_file_location('native',helper); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert m.digest(path,'md5')==m.POLY_MD5
    # Signy A39 Gourlay GPS, BAS colony GPS dataset; diet only identifies Signy.
    sites=pd.DataFrame([['Signy',-60.731183,-45.58685],['Palmer',-64.7666667,-64.0666667],['Hope',-63.3952288,-56.9859742],['Stranger',-62.2616667,-58.6175]],columns=['site_id','colony_lat','colony_lon'])
    sites['source_region']='diet_locality';save(sites,'coordinates.csv')
    rows=[]
    with zipfile.ZipFile(path) as z:
        ll,mapping=m.native_map_manifest(z); lat,lon,mask=m.lonlat_grid(z,ll)
        members,geometry=m.original_native_pixel_sites(sites,lat,lon,mask);save(geometry,'geometry.csv')
        for year in range(2003,2020):
            days=[day for day in sorted(mapping) if int(day[:4])==year and int(day[5:7]) in m.MONTHS]
            for day in days:
                with Dataset('day.nc','r',memory=z.read(mapping[day])) as f:
                    a=np.ma.asarray(f.variables['Map'][:],dtype=float).filled(np.nan).ravel()
                for (site,radius),(idx,weights) in members.items():
                    pix=a[idx]; valid=np.isfinite(pix)&(pix!=-999)
                    v=pix[valid];w=weights[valid]
                    assert not ((v<0)&~np.isin(v,[-1,-2,-100])).any()
                    coastal=(v>0)&(v.astype(np.int64)%2==0)
                    rows.append(dict(site=site,radius_km=radius,date=day,season=year,month=int(day[5:7]),marine_pixels=int(valid.sum()),coastal_pixels=int(coastal.sum()),fraction=float(w[coastal].sum()/w.sum()) if w.sum()>0 else np.nan))
            print('processed winter',year,'maps',len(days),flush=True)
    d=pd.DataFrame(rows);save(d,'daily_environment.csv')
    monthly=d.groupby(['site','radius_km','season','month']).agg(n_days=('fraction','count'),fraction=('fraction','mean'),min_marine_pixels=('marine_pixels','min'),max_coastal_pixels=('coastal_pixels','max')).reset_index()
    monthly['coverage']=monthly.apply(lambda r:r.n_days/calendar.monthrange(int(r.season),int(r.month))[1],axis=1)
    save(monthly,'monthly_environment.csv')
    annual=[]
    for (site,radius,year),g in monthly.groupby(['site','radius_km','season']):
        ok=len(g)==5 and g.coverage.ge(.8).all()
        annual.append(dict(site=site,radius_km=radius,season=year,passes_coverage=ok,polynya_fraction=g.fraction.mean() if ok else np.nan,max_coastal_pixels=g.max_coastal_pixels.max(),min_coverage=g.coverage.min()))
    e=pd.DataFrame(annual);save(e,'annual_environment.csv');return e

def fit(d,e):
    joined=d.merge(e[e.site.eq('Signy')&e.radius_km.eq(100)],on='season',how='left',validate='one_to_one');save(joined,'signy_matched.csv')
    g=joined[joined.n_valid.ge(5)].dropna(subset=['polynya_fraction','krill_fraction','sampling_day']).copy()
    result={'n_matched_seasons':len(g),'years':g.season.tolist(),'exposure_min':float(g.polynya_fraction.min()) if len(g) else None,'exposure_max':float(g.polynya_fraction.max()) if len(g) else None}
    if len(g)<8 or g.polynya_fraction.nunique()<2:
        result['verdict']='NOT_ESTIMABLE_INSUFFICIENT_EXPOSURE_OR_YEARS';return result
    x=g[['polynya_fraction','sampling_day','season']].copy();x=x-x.mean();x=sm.add_constant(x)
    if np.linalg.matrix_rank(x)<4:
        result['verdict']='NOT_ESTIMABLE_RANK_DEFICIENT';return result
    model=sm.OLS(g.krill_fraction,x).fit(cov_type='HAC',cov_kwds={'maxlags':1},use_t=True)
    result.update(verdict='ESTIMATED_ASSOCIATION_NOT_CAUSAL',coefficient=float(model.params['polynya_fraction']),ci95=model.conf_int().loc['polynya_fraction'].tolist(),p=float(model.pvalues['polynya_fraction']))
    (HERE/'main_model.txt').write_text('\n'.join(line.rstrip() for line in model.summary().as_text().splitlines())+'\n',encoding='utf-8',newline='\n')
    return result

def sensitivity(d,e):
    rows=[];loo=[]
    for radius in [100,25]:
        g=d.merge(e[e.site.eq('Signy')&e.radius_km.eq(radius)],on='season',validate='one_to_one')
        g=g[g.n_valid.ge(5)].dropna(subset=['polynya_fraction','krill_fraction','sampling_day'])
        for response in ['krill_fraction','fish_fraction','krill_ratio_of_sums']:
            for adjusted in [True,False]:
                cols=['polynya_fraction','sampling_day','season'] if adjusted else ['polynya_fraction']
                x=sm.add_constant(g[cols]-g[cols].mean())
                if len(g)<8 or np.linalg.matrix_rank(x)<len(cols)+1:continue
                f=sm.OLS(g[response],x).fit(cov_type='HAC',cov_kwds={'maxlags':1},use_t=True)
                rows.append(dict(radius_km=radius,response=response,adjusted=adjusted,n=len(g),beta=f.params['polynya_fraction'],lower=f.conf_int().loc['polynya_fraction',0],upper=f.conf_int().loc['polynya_fraction',1],p=f.pvalues['polynya_fraction']))
        if radius==100:
            for year in g.season:
                sub=g[g.season.ne(year)];x=sm.add_constant(sub[['polynya_fraction','sampling_day','season']]-sub[['polynya_fraction','sampling_day','season']].mean())
                f=sm.OLS(sub.krill_fraction,x).fit()
                loo.append(dict(omitted_season=int(year),beta=f.params['polynya_fraction']))
    save(pd.DataFrame(rows),'sensitivity_models.csv');save(pd.DataFrame(loo),'leave_one_season_out.csv')
    support=e.groupby(['site','radius_km']).agg(years=('polynya_fraction','count'),exposure_min=('polynya_fraction','min'),exposure_max=('polynya_fraction','max')).reset_index();save(support,'environment_support.csv')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--diet-zip',type=Path,required=True);p.add_argument('--deepaa-zip',type=Path);p.add_argument('--reuse-environment',action='store_true');a=p.parse_args()
    d,audit=stomachs(a.diet_zip)
    if a.deepaa_zip or a.reuse_environment:
        e=pd.read_csv(HERE/'annual_environment.csv') if a.reuse_environment else environment(a.deepaa_zip)
        audit['main_test']=fit(d,e)
        sensitivity(d,e)
    (HERE/'result.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(audit,indent=2))
