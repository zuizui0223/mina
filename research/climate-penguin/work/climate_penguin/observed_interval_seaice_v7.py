"""V7: source-fixed Chinstrap/Gentoo observed intervals and preceding marine ice.

Endpoint state-change association, not annual count interpolation, independent
confirmation, climate attribution, local snow, or a competition estimate.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
INTERVAL_SHA='d8bd401224c83f07d767c325fc9ea0abd1a67f9ab7613fa2b40538474ac98d44'
V6_RESULT_SHA='9ab362853535e8bdbbc63cc83803d1e7636ec37eeab7d55d17151f27036360ff'
SITE_SHA='36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34'
OBS_PINS={
 'observations_p1.csv':'cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075',
 'observations_p2.csv':'c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3'}
MONTHS=(8,9,10,11)
CONTINENT_FID=17692
OUTCOMES={'chinstrap':'annualized_a_growth','gentoo':'annualized_b_growth',
          'relative':'annualized_log_ratio_change'}


def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_csv(p,rows):
    if not rows:raise ValueError('empty output table')
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def helper(name):
    spec=importlib.util.spec_from_file_location('v7_'+name,ROOT/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def prior_before(record,year):
    # Published calendar uncertainty remains an interval; do not default month.
    return helper('lagged_climate_v3').window_before(record,year)


def weights(rows,kind='duration'):
    gaps=np.asarray([float(r['gap']) for r in rows])
    if not np.isfinite(gaps).all() or np.any(gaps<=0):raise ValueError('invalid positive observation gap')
    if kind=='duration':return gaps
    if kind=='equal_land':
        if any(r.get('land_fid') is None for r in rows):raise ValueError('missing exact land ID')
        durations=defaultdict(float);members=defaultdict(set)
        for r in rows:
            durations[r['site_id']]+=float(r['gap']);members[r['land_fid']].add(r['site_id'])
        return np.asarray([float(r['gap'])/(durations[r['site_id']]*len(members[r['land_fid']])) for r in rows])
    raise ValueError('unsupported weighting')


def design(rows,mode):
    # A site intercept in annualized space is a site-specific linear log drift.
    sites=sorted({r['site_id'] for r in rows})
    cols=[np.asarray([float(r['site_id']==s) for r in rows]) for s in sites]
    if mode=='region_endpoint_year':
        for region in sorted({r['region'] for r in rows}):
            years=sorted({int(r[k]) for r in rows if r['region']==region for k in ('start','end')})
            for year in years[1:]:
                cols.append(np.asarray([((float(int(r['end'])==year)-float(int(r['start'])==year))/float(r['gap']))
                   if r['region']==region else 0. for r in rows]))
    elif mode!='site':raise ValueError('unsupported nuisance design')
    return np.column_stack(cols)


def fit(rows,mode,weighting='duration'):
    if not rows:return {'status':'EMPTY','n':0,'coefficients':{k:None for k in OUTCOMES}}
    w=weights(rows,weighting)
    x=np.asarray([float(r['x_ice_rate']) for r in rows])
    Y=np.column_stack([[float(r[field]) for r in rows] for field in OUTCOMES.values()])
    if not np.isfinite(x).all() or not np.isfinite(Y).all():raise ValueError('nonfinite model input')
    if not np.allclose(Y[:,2],Y[:,1]-Y[:,0],atol=1e-11,rtol=1e-11):
        raise ValueError('relative growth not identical to species difference')
    sw=np.sqrt(w);D=design(rows,mode);Z=D*sw[:,None];xx=x*sw;YY=Y*sw[:,None]
    X=np.column_stack((Z,xx));r0=int(np.linalg.matrix_rank(Z));r1=int(np.linalg.matrix_rank(X));df=len(rows)-r1
    rx=xx-Z@np.linalg.lstsq(Z,xx,rcond=None)[0]
    ry=YY-Z@np.linalg.lstsq(Z,YY,rcond=None)[0]
    den=float(rx@rx)
    algebraic=None
    if r1>r0 and den>1e-12:
        algebraic=(rx@ry)/den
        direct=np.linalg.lstsq(X,YY,rcond=None)[0][-1]
        if not np.allclose(algebraic,direct,atol=1e-8,rtol=1e-8):raise ValueError('FWL/direct coefficient disagreement')
    status='CLIMATE_COLLINEAR' if algebraic is None else ('SATURATED_NO_RESIDUAL_DF' if df<=0 else 'DESCRIPTIVE_ONLY')
    values={k:(float(algebraic[i]) if status=='DESCRIPTIVE_ONLY' else None) for i,k in enumerate(OUTCOMES)}
    info={s:float(sum(rx[i]**2 for i,r in enumerate(rows) if r['site_id']==s)) for s in sorted({r['site_id'] for r in rows})}
    error=float(algebraic[2]-(algebraic[1]-algebraic[0])) if algebraic is not None else None
    if error is not None and abs(error)>1e-9:raise ValueError('species coefficient decomposition failed')
    return dict(status=status,n=len(rows),sites=len(info),regions=len({r['region'] for r in rows}),
        land_units=len({r['land_fid'] for r in rows if r.get('land_fid') is not None}),
        mode=mode,weighting=weighting,nuisance_rank=r0,full_rank=r1,residual_df=df,
        coefficients=values,algebraic_coefficients_audit_only=None if algebraic is None else dict(zip(OUTCOMES,map(float,algebraic))),
        residual_x_ss=den,x_information_by_site=info,
        sites_with_nonzero_within_design_ice_information=sum(v>max(1e-12,den*1e-10) for v in info.values()),
        decomposition_error=error,p_values=None,confidence_intervals=None,
        unobserved_counts_interpolated=False,causal_effect_identified=False)


def deletion(rows,mode,weighting,field):
    outputs=[]
    for value in sorted({r[field] for r in rows},key=str):
        sub=[r for r in rows if r[field]!=value]
        z=fit(sub,mode,weighting)
        outputs.append(dict(omitted=str(value),status=z['status'],n=z['n'],coefficients=z['coefficients']))
    ranges={}
    for outcome in OUTCOMES:
        values=[z['coefficients'][outcome] for z in outputs if z['coefficients'][outcome] is not None]
        ranges[outcome]=[min(values),max(values)] if values else None
    return dict(refits=outputs,ranges_not_confidence_intervals=ranges)


def select(v6_dir,original_dir):
    source_file=v6_dir/'observed_species_intervals_v6.csv'
    geometry_file=v6_dir/'observed_species_intervals_v6_result.json'
    if sha(source_file)!=INTERVAL_SHA or sha(geometry_file)!=V6_RESULT_SHA:
        raise ValueError('V6 original interval or geography SHA mismatch')
    rawdir=original_dir/'source'
    if sha(rawdir/'sites.csv')!=SITE_SHA:raise ValueError('original registry drift')
    observations=[]
    for name,pin in OBS_PINS.items():
        if sha(rawdir/name)!=pin:raise ValueError('original observation source drift')
        observations+=read(rawdir/name)
    obs={r['id']:r for r in observations}
    if len(obs)!=len(observations):raise ValueError('duplicate observation ID')
    geography=json.loads(geometry_file.read_text())['geography']
    candidates=[r for r in read(source_file) if (r['species_a'],r['species_b'])==('CHPE','GEPE')]
    if len(candidates)!=79:raise ValueError('original CHPE/GEPE roster drift')
    keep=[];excluded=[];chronology=[]
    for raw in candidates:
        row=dict(raw);start,end=int(row['start']),int(row['end']);gap=int(row['gap'])
        if end-start!=gap or gap<=0:raise ValueError('bad original observation gap')
        if start-1<1979 or end-1>2020:
            excluded.append(dict(site_id=row['site_id'],start=start,end=end,reason='OUTSIDE_FIXED_PRODUCT_PRIOR_WINDOW'));continue
        failure=False
        for species in ('a','b'):
            for side in ('start','end'):
                rec=obs[row['source_'+species+'_'+side]]
                if not (rec['site_id']==row['site_id'] and rec['species_id']==row['species_'+species] and
                        int(rec['season'])==int(row[side]) and rec['type']=='nests' and
                        rec['citekey']==row['original_citekey'] and rec['vantage']==row['original_vantage']):
                    raise ValueError('original count identity/source mismatch')
                count=float(rec['count'].replace(',',''))
                if count<=0 or count!=float(row['n_'+species+'_'+side]):raise ValueError('original count changed')
                passed=prior_before(rec,int(row[side])-1)
                low,high,precision=helper('lagged_climate_v3').census_bounds(rec)
                chronology.append(dict(site_id=row['site_id'],start=start,end=end,species=rec['species_id'],
                   side=side,source_id=rec['id'],date_lower_bound=str(low),date_upper_bound=str(high),
                   source_precision=precision,prior_year=int(row[side])-1,prior_ends_before_lower_bound=passed,
                   source_date_field=rec['date'],imputed_census_date=False))
                failure|=not passed
        if failure:
            excluded.append(dict(site_id=row['site_id'],start=start,end=end,reason='PRIOR_WINDOW_NOT_CERTIFIED_BEFORE_COUNTS'));continue
        for key in ('annualized_a_growth','annualized_b_growth','annualized_log_ratio_change'):row[key]=float(row[key])
        ga=math.log(float(row['n_a_end'])/float(row['n_a_start']))/gap
        gb=math.log(float(row['n_b_end'])/float(row['n_b_start']))/gap
        if not (math.isclose(ga,row['annualized_a_growth'],abs_tol=1e-12) and
                math.isclose(gb,row['annualized_b_growth'],abs_tol=1e-12) and
                math.isclose(gb-ga,row['annualized_log_ratio_change'],abs_tol=1e-12)):
            raise ValueError('V6 counts/rates disagreement')
        g=geography[row['site_id']]
        land=g.get('original_land_fid') if g['category']=='EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON' and g.get('original_land_fid')!=CONTINENT_FID else None
        row.update(start=start,end=end,gap=gap,land_fid=land,source_land_status=g['category'])
        keep.append(row)
    if len(keep)!=78 or len({r['site_id'] for r in keep})!=19 or len({r['region'] for r in keep})!=3:
        raise ValueError('pre-exposure 78/19/3 source support changed')
    return keep,excluded,chronology,[r for r in read(rawdir/'sites.csv') if r['site_id'] in {x['site_id'] for x in keep}]


def join_monthly(rows,monthly):
    lookup={}
    for r in monthly:
        key=(r['site_id'],int(r['year']),int(r['month']))
        if key in lookup:raise ValueError('duplicate original site/month')
        lookup[key]=r
    out=[]
    for row in rows:
        states=[]
        for side in ('start','end'):
            values=[]
            for month in MONTHS:
                r=lookup.get((row['site_id'],int(row[side])-1,month))
                if r is None or str(r['complete_spatial_support']) not in ('True','true') or r['sic_percent_mean'] in ('',None):
                    raise ValueError('missing original monthly spatial support')
                value=float(r['sic_percent_mean'])
                if not math.isfinite(value) or not 0<=value<=100.001:raise ValueError('invalid SIC')
                values.append(value)
            states.append(sum(values)/4)
        out.append(dict(row,prior_sic_start_percent=states[0],prior_sic_end_percent=states[1],
                        delta_prior_sic_10pp=(states[1]-states[0])/10,
                        x_ice_rate=(states[1]-states[0])/(10*int(row['gap']))))
    return out


def describe(rows):
    counts=Counter();site_sum=defaultdict(lambda:np.zeros(4))
    for r in rows:
        a,b=r['annualized_a_growth'],r['annualized_b_growth']
        direction=('a_up' if a>0 else 'a_down' if a<0 else 'a_flat')+'_'+('b_up' if b>0 else 'b_down' if b<0 else 'b_flat')
        counts[direction]+=1
        site_sum[r['site_id']]+=np.array([a*r['gap'],b*r['gap'],(b-a)*r['gap'],r['gap']])
    summaries=[dict(site_id=s,gap_sum=float(z[3]),chinstrap_rate=float(z[0]/z[3]),
        gentoo_rate=float(z[1]/z[3]),relative_rate=float(z[2]/z[3])) for s,z in sorted(site_sum.items())]
    return dict(intervals=len(rows),sites=len(site_sum),regions=dict(Counter(r['region'] for r in rows)),
       gap_counts=dict(sorted(Counter(str(r['gap']) for r in rows).items())),
       species_direction_counts=dict(counts),relative_positive_intervals=sum(r['annualized_log_ratio_change']>0 for r in rows),
       relative_positive_and_b_decreasing=sum(r['annualized_log_ratio_change']>0 and r['annualized_b_growth']<0 for r in rows),
       site_summaries=summaries)


def main():
    p=argparse.ArgumentParser();p.add_argument('--v6-dir',required=True,type=Path)
    p.add_argument('--original-dir',required=True,type=Path);p.add_argument('--v4-cache',type=Path)
    p.add_argument('--out',required=True,type=Path);p.add_argument('--offline',action='store_true')
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    rows,excluded,chronology,sites=select(args.v6_dir,args.original_dir)
    write_csv(args.out/'source_78_interval_roster.csv',rows)
    write_csv(args.out/'source_exclusions.csv',excluded);write_csv(args.out/'source_calendar_bounds.csv',chronology)
    # Source code and tests import only numpy. Optional GIS/NetCDF loaded here.
    sys.path.insert(0,str(ROOT));import seaice_fixed_pairs_v4 as marine
    years=sorted({int(r[k])-1 for r in rows for k in ('start','end')})
    if len(years)!=35:raise ValueError('35 fixed source climate years changed')
    rawdir=args.out/'original_nc';rawdir.mkdir(exist_ok=True)
    manifest=args.out/'monthly_download_receipts.json'
    if args.offline:
        rec=json.loads(manifest.read_text());downloads=rec['files']
    else:
        jobs,catalogs=marine.discover(years,args.out)
        old={}
        if args.v4_cache:
            old={r['url']:r for r in json.loads((args.v4_cache/'monthly_download_receipts.json').read_text())['files']}
        def retrieve(job):
            y,m,url=job
            if url in old:
                r=old[url];path=args.v4_cache/'original_nc'/r['filename']
                if sha(path)!=r['sha256']:raise ValueError('cached original SHA mismatch')
                shutil.copyfile(path,rawdir/r['filename'])
                return dict(r,reused_source_run=40881769676)
            return marine.retrieve(job,rawdir)
        with ThreadPoolExecutor(max_workers=4) as pool:downloads=list(pool.map(retrieve,jobs))
        rec={'catalogs':catalogs,'files':downloads};manifest.write_text(json.dumps(rec,indent=2)+'\n')
    if len(downloads)!=140 or {(z['year'],z['month']) for z in downloads}!={(y,m) for y in years for m in MONTHS}:
        raise ValueError('required140 original months incomplete')
    monthly,pixels,ocean=marine.extract(downloads,sites,rawdir)
    write_csv(args.out/'original_19site_140month_seaice.csv',monthly)
    write_csv(args.out/'original_selected_marine_cells.csv',pixels)
    joined=join_monthly(rows,monthly);write_csv(args.out/'observed_78_intervals_seaice_v7.csv',joined)
    models={mode:fit(joined,mode) for mode in ('site','region_endpoint_year')}
    exact=[r for r in joined if r['land_fid'] is not None]
    land_models={mode:fit(exact,mode,'equal_land') for mode in models}
    sensitivity={mode:{field:deletion(joined,mode,'duration',field) for field in ('site_id','region')} for mode in models}
    land_sensitivity={mode:deletion(exact,mode,'equal_land','land_fid') for mode in models}
    result=dict(schema=1,status='POST_EXPLORATION_INTERVAL_SEAICE_SPECIES_DECOMPOSITION',
       source_interval_sha256=INTERVAL_SHA,source_geo_sha256=V6_RESULT_SHA,source_sites_sha256=SITE_SHA,
       source_nc_files=len(downloads),reused_v4_files=sum('reused_source_run' in x for x in downloads),
       source_climate_years=years,source_months=list(MONTHS),site_month_rows=len(monthly),
       source_exclusions=excluded,description=describe(joined),models=models,
       exact_land_description=describe(exact),exact_land_models=land_models,
       deletion_sensitivity_not_CI=sensitivity,land_deletion_sensitivity_not_CI=land_sensitivity,
       marine_support_overlap=marine.overlap_report(ocean),
       original_ocean_masks={s:sorted(mask) for s,mask in sorted(ocean.items())},
       source_quality_ranges={key:[min(z[key] for z in monthly),max(z[key] for z in monthly)] for key in ('n_ocean','n_valid','valid_fraction','n_interpolated','n_landspill','n_high_t2m','n_climatology_zero')},
       units='Change in log nests over observed interval per +10pp preceding SIC change, after site linear log drift; rate form has both sides divided by gap.',
       p_values=None,confidence_intervals=None,causal_effect_identified=False,
       limitations=['Fixed post-exploration 78 CHPE/GEPE intervals, not an independent replication of prior ADPE/GEPE results.',
         'Both species are present and positive at endpoints; absent years never imputed, same source dates not field-verified.',
         'Endpoint environmental state change is NOT mean environmental exposure during the entire interval.',
         'Weights assume process variance proportional to gap; survey error and variable census accuracy are not estimated.',
         'Singleton sites add geographic descriptions but no within-site exposure information.',
         'Current exact source land != independent historical nesting habitat; marine buffers share original pixels.',
         'Earlier than July1987 input sampling every48h versus later24h; monthly valid fraction not complete daily observation.',
         'Original OSI product uses ERA5 ancillary fields; no independent warming attribution.',
         'No measured local snow, coastal walking route, prey, migration, interspecies competition or causal population response.'])
    (args.out/'observed_interval_seaice_v7_result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('OBSERVED_INTERVAL_SEAICE_V7='+json.dumps(dict(status=result['status'],n=len(joined),sites=len(sites),
        files=len(downloads),models=models,land_models=land_models),allow_nan=False),flush=True)

if __name__=='__main__':main()
