"""Unchanged44: region-shared versus local sea-ice covariation, exploratory only.

Uses orthogonal nested projection; no new lags, masks, p-values or causal effects.
Shared grid cells are deduplicated in descriptive fixed-region marine unions.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np

TERM = 'delta_prior_sic_10pp'
OUTCOME = 'relative_growth'
MODELS = {'site': ('site_id',), 'site_year': ('site_id','end_year'),
          'site_region_year': ('site_id','region_year')}
COMPONENT_NAMES = ('added_shared_year_space', 'added_region_year_space',
                   'within_region_year_space')
TOL = 1e-10
INPUT_SHA = {
    'fixed44_prior_seaice_pairs.csv':'a405141db916f53c9a852d24f722514bf0c545a56878ee2a73d9501230ede217',
    'original_selected_grid_cells.csv':'60751e5a2dc042e90d48c7e4c3a139e45849fe76369724efc1db326a6cb48576',
    'seaice_fixed44_v4_result.json':'6fbe873c2a0d92a5c27d90bd2ba2059b591db9e5e688492be362a17c0fe821d9',
}


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_source(source: Path) -> None:
    for name,digest in INPUT_SHA.items():
        if sha(Path(source)/name)!=digest:
            raise ValueError('original source SHA mismatch: '+name)


def read(path: Path) -> list[dict]:
    with Path(path).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError('empty output table')
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def label(row: dict, field: str) -> str:
    if field=='region_year':
        return str(row['region'])+'|'+str(row['end_year'])
    return str(row[field])


def design(rows: list[dict], effects: tuple[str,...]) -> np.ndarray:
    columns=[np.ones(len(rows))]
    for effect in effects:
        keys=sorted({label(r,effect) for r in rows})
        columns.extend(np.array([float(label(r,effect)==key) for r in rows])
                       for key in keys[1:])
    return np.column_stack(columns)


def residual(values: np.ndarray, matrix: np.ndarray) -> tuple[np.ndarray,int]:
    u,s,_=np.linalg.svd(matrix,full_matrices=False)
    threshold=max(matrix.shape)*np.finfo(float).eps*s[0] if len(s) else 0.
    rank=int(np.sum(s>threshold))
    q=u[:,:rank]
    return values-q@(q.T@values),rank


def fit(rows: list[dict], term: str, effects: tuple[str,...]) -> dict:
    if not rows:
        return {'status':'EMPTY','coefficient':None,'n':0}
    x=np.array([float(r[term]) for r in rows]);y=np.array([float(r[OUTCOME]) for r in rows])
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('nonfinite source predictor or response')
    z=design(rows,effects)
    r,rank=residual(np.column_stack([x,y]),z)
    rx,ry=r.T
    ss=float(rx@rx); cross=float(rx@ry)
    fullrank=int(np.linalg.matrix_rank(np.column_stack([z,x])))
    df=len(rows)-fullrank
    centered_ss=float((x-x.mean())@(x-x.mean()))
    result={'n':len(rows),'sites':len({r['site_id'] for r in rows}),
            'regions':len({r['region'] for r in rows}),
            'years':len({str(r['end_year']) for r in rows}),
            'nuisance_rank':rank,'full_rank':fullrank,'residual_df':df,
            'remaining_x_ss':ss,'remaining_x_fraction_of_centered':ss/centered_ss if centered_ss>TOL else None,
            'xy_crossproduct':cross,'coefficient':None,
            'p_value':None,'confidence_interval':None,'causal':False}
    if ss<=TOL*max(1.,centered_ss) or fullrank==rank:
        result['status']='NO_RESIDUAL_PREDICTOR'
    elif df<=0:
        result['status']='SATURATED_NO_RESIDUAL_DF'
        result['algebraic_coefficient_audit_only']=cross/ss
    else:
        result['status']='EXPLORATORY_DESCRIPTIVE_ONLY'
        result['coefficient']=cross/ss
    return result


def partition(rows: list[dict], term: str) -> dict:
    x=np.array([float(r[term]) for r in rows]);y=np.array([float(r[OUTCOME]) for r in rows])
    models={name:fit(rows,term,effects) for name,effects in MODELS.items()}
    residuals=[residual(np.column_stack([x,y]),design(rows,e))[0] for e in MODELS.values()]
    pieces=[residuals[0]-residuals[1],residuals[1]-residuals[2],residuals[2]]
    totalss=float(residuals[0][:,0]@residuals[0][:,0])
    totalxy=float(residuals[0][:,0]@residuals[0][:,1])
    comps=[]
    for name,part in zip(COMPONENT_NAMES,pieces,strict=True):
        px,py=part.T;ss=float(px@px);xy=float(px@py)
        comps.append({'component':name,'x_ss':ss,'xy_crossproduct':xy,
                      'fraction_of_site_residual_x_ss':ss/totalss if totalss>TOL else None,
                      'component_algebraic_slope':xy/ss if ss>TOL*max(1,totalss) else None,
                      'slope_contribution':xy/totalss if totalss>TOL else None,
                      'not_fraction_of_ecological_effect':True})
    cross=[]
    for i in range(3):
        for j in range(i+1,3):
            cross.extend(abs(float(pieces[i][:,a]@pieces[j][:,b])) for a in (0,1) for b in (0,1))
    assert np.allclose(sum(pieces),residuals[0],atol=1e-9)
    assert math.isclose(sum(c['x_ss'] for c in comps),totalss,rel_tol=1e-9,abs_tol=1e-9)
    assert math.isclose(sum(c['xy_crossproduct'] for c in comps),totalxy,rel_tol=1e-9,abs_tol=1e-9)
    rows_local=[{'site_id':r['site_id'],'region':r['region'],'end_year':r['end_year'],
                 'local_x_residual':float(rx),'local_y_residual':float(ry)}
                for r,(rx,ry) in zip(rows,residuals[2],strict=True)]
    return {'models':models,'orthogonal_components':comps,
            'site_residual_x_ss':totalss,'site_residual_xy':totalxy,
            'maximum_cross_component_dot_abs':max(cross,default=0),
            'local_residuals':rows_local}


def regional_union(cells: list[dict], site_regions: dict[str,str], require_full=True) -> tuple[list[dict],dict]:
    bygroup=defaultdict(dict);original_by_cell={};site_month_support=defaultdict(set)
    seen=set()
    for r in cells:
        site=r['site_id']
        if site not in site_regions:
            raise ValueError('unregistered source site')
        year,month,cell=int(r['year']),int(r['month']),int(r['flat_cell_index'])
        key=(site,year,month,cell)
        if key in seen:raise ValueError('duplicate source site cell')
        seen.add(key)
        if not r['flag']:
            raise ValueError('missing original flag')
        flag=int(r['flag'])
        if flag<0:raise ValueError('invalid original flag')
        if flag&3:continue
        if r['sic_percent'] in ('',None):
            raise ValueError('missing original ocean value')
        v=float(r['sic_percent']);lat=float(r['lat']);lon=float(r['lon'])
        if not all(math.isfinite(x) for x in (v,lat,lon)) or not 0<=v<=100.001:
            raise ValueError('missing or invalid original ocean value')
        value=(v,flag,lat,lon)
        globalkey=(year,month,cell)
        if globalkey in original_by_cell and value!=original_by_cell[globalkey]:
            raise ValueError('conflicting repeated original ocean cell')
        original_by_cell[globalkey]=value
        bygroup[(site_regions[site],year,month)][cell]=v
        site_month_support[(site,year,month)].add(cell)
    periods=sorted({(y,m) for _,y,m in bygroup})
    site_sets={}
    for site in site_regions:
        present=[site_month_support[(site,y,m)] for y,m in periods]
        if any(not p for p in present):raise ValueError('missing source site month')
        if any(p!=present[0] for p in present):raise ValueError('changing original ocean-cell support')
        site_sets[site]=present[0]
    if require_full:
        if len(periods)!=96 or len(cells)!=34272:
            raise ValueError('frozen source96 inventory changed')
    summary={};monthly=[]
    regions=sorted(set(site_regions.values()))
    for region in regions:
        sites=sorted(k for k,v in site_regions.items() if v==region)
        union=set().union(*(site_sets[s] for s in sites))
        summary[region]={'sites':sites,'n_unique_ocean_cells':len(union),
                         'fixed_ocean_cell_indices':sorted(union),
                         'sum_of_site_cell_counts':sum(len(site_sets[s]) for s in sites)}
        for y,m in periods:
            values=bygroup[(region,y,m)]
            if set(values)!=union:raise ValueError('regional fixed marine union incomplete')
            monthly.append({'region':region,'year':y,'month':m,
                            'n_unique_ocean_cells':len(values),
                            'sic_percent_mean':float(np.mean([values[k] for k in sorted(values)]))})
    return monthly,{'regions':summary,'periods':len(periods),
                    'original_source_cells_not_independent_sites':True}


def support(rows: list[dict]) -> dict:
    groups=defaultdict(list)
    for r in rows:groups[(r['region'],str(r['end_year']))].append(r)
    entries=[]
    for (region,year),part in sorted(groups.items()):
        x=[float(r[TERM]) for r in part]
        entries.append({'region':region,'end_year':year,'n_sites':len(part),
                        'sites':';'.join(sorted(r['site_id'] for r in part)),
                        'x_range_10pp':max(x)-min(x),
                        'same_year_local_x_contrast':len(part)>1 and max(x)-min(x)>TOL})
    return {'region_year_groups':len(groups),
            'singleton_region_year_groups':sum(len(v)==1 for v in groups.values()),
            'multi_site_region_year_groups':sum(len(v)>1 for v in groups.values()),
            'region_year_groups_with_nonzero_x_contrast':sum(e['same_year_local_x_contrast'] for e in entries),
            'rows':entries}


def leave_out(rows: list[dict], key: str, effects: tuple[str,...]) -> dict:
    refits=[]
    for value in sorted({str(r[key]) for r in rows}):
        subset=[r for r in rows if str(r[key])!=value]
        result=fit(subset,TERM,effects)
        refits.append({'omitted':value,**result})
    beta=[r['coefficient'] for r in refits if r['coefficient'] is not None]
    return {'refits':refits,'valid_refits':len(beta),
            'range_not_confidence_interval':[min(beta),max(beta)] if beta else None}


def run(source: Path,out: Path) -> dict:
    source=Path(source);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    verify_source(source)
    pair_path=source/'fixed44_prior_seaice_pairs.csv'
    cell_path=source/'original_selected_grid_cells.csv'
    prior_path=source/'seaice_fixed44_v4_result.json'
    pairs=read(pair_path);cells=read(cell_path);v4=json.loads(prior_path.read_text())
    if len(pairs)!=44 or len({r['site_id'] for r in pairs})!=7 or len({r['region'] for r in pairs})!=2:
        raise ValueError('original44 roster or original region labels changed')
    if len({(r['site_id'],r['start_year'],r['end_year']) for r in pairs})!=44:
        raise ValueError('duplicate source count comparison')
    for r in pairs:
        if int(r['end_year'])!=int(r['start_year'])+1 or r['prior_precedes_all_source_bounds']!='True':
            raise ValueError('original time order changed')
    regions={}
    for r in pairs:
        if r['site_id'] in regions and regions[r['site_id']]!=r['region']:
            raise ValueError('source site changed region')
        regions[r['site_id']]=r['region']
    union,geo=regional_union(cells,regions)
    seasonal=defaultdict(list)
    for r in union:seasonal[(r['region'],r['year'])].append(r)
    means={}
    for k,values in seasonal.items():
        if {z['month'] for z in values}!={8,9,10,11}:raise ValueError('incomplete fixed seasonal window')
        means[k]=float(np.mean([z['sic_percent_mean'] for z in values]))
    extended=[]
    for r in pairs:
        a=means[(r['region'],int(r['start_year'])-1)]
        b=means[(r['region'],int(r['end_year'])-1)]
        regional=(b-a)/10.
        extended.append(dict(r,delta_fixed_regional_union_10pp=regional,
                             delta_site_minus_regional_union_10pp=float(r[TERM])-regional))
    part=partition(pairs,TERM)
    for key,old in [('site','site_fixed'),('site_year','site_year_fixed')]:
        if not math.isclose(part['models'][key]['coefficient'],v4['models'][old]['coefficient'],abs_tol=1e-10):
            raise ValueError('old original V4 coefficient not recovered')
    regions_fit={k:fit([r for r in pairs if r['region']==k],TERM,('site_id',))
                 for k in sorted(set(regions.values()))}
    sensitivity={name:{key:leave_out(pairs,key,effects) for key in ('site_id','end_year')}
                 for name,effects in MODELS.items()}
    exact=[r for r in pairs if r['land_fid'] not in ('',None)]
    land={'n':len(exact),'land_features':len({r['land_fid'] for r in exact}),
          'same_subset_models':{n:fit(exact,TERM,e) for n,e in MODELS.items()},
          'land_deletion_not_CI':{n:leave_out(exact,'land_fid',e) for n,e in MODELS.items()}}
    local_rows=part.pop('local_residuals')
    local_info={}
    for region in sorted(set(regions.values())):
        chosen=[r for r in local_rows if r['region']==region]
        ss=sum(r['local_x_residual']**2 for r in chosen)
        local_info[region]={'original_rows':len(chosen),'local_predictor_ss':ss,
            'rows_with_nonzero_residual_contrast':sum(abs(r['local_x_residual'])>1e-8 for r in chosen),
            'range_residual_ice_difference_percentage_points':[min(r['local_x_residual'] for r in chosen)*10,max(r['local_x_residual'] for r in chosen)*10]}
    balance=support(pairs)
    group_rows=balance.pop('rows')
    result={'schema':1,'status':'POSTEXPLORATORY_REGIONAL_IDENTIFICATION_NOT_CAUSAL',
            'source_run_id':40881769676,
            'source_hashes':{p.name:sha(p) for p in (pair_path,cell_path,prior_path)},
            'n_unchanged_pairs':len(pairs),'response':'Gentoo minus Adelie annual change in log(1+nests)',
            'predictor':'preceding Aug-Nov SIC change /10 percentage points; original100km marine buffer',
            'partition':part,'region_separate_site_fixed':regions_fit,
            'group_support':balance,'fixed_marine_union':geo,'local_information_by_region':local_info,
            'deletion_sensitivity_not_CI':sensitivity,'same_exact_land_subset':land,
            'field_survey_months_imputed':False,'new_seaice_window_or_buffer_searched':False,
            'limits':['Original44 cohort was exposed before this diagnostic, not independent confirmation.',
                     'Only two named source regions; repeated site-years and source pixels are dependent.',
                     'Projection fractions measure sampled predictor information, not explained ecological change or causal mediation.',
                     'Region-by-year controls remove real regional environmental signals as well as confounding; estimand changes.',
                     '25km marine pixels within100km do not measure local nest snow, walking access, prey or species interaction.',
                     'Prior timing is conditional on original census year bounds; precise census dates remain mostly unresolved.',
                     'No p values, calibrated confidence intervals, warming attribution or new correction family.']}
    write(out/'fixed44_regional_exposure_diagnostics.csv',extended)
    write(out/'regional_unique_cell_monthly.csv',union)
    write(out/'original_region_year_support.csv',group_rows)
    write(out/'within_region_year_residuals.csv',local_rows)
    (out/'seaice_regional_v5_result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();result=run(args.source_dir,args.out)
    print('SEAICE_REGIONAL_V5='+json.dumps({k:v for k,v in result.items() if k not in ('deletion_sensitivity_not_CI','same_exact_land_subset')},ensure_ascii=False))

if __name__=='__main__':main()
