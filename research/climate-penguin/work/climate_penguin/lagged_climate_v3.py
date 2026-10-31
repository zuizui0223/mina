"""Fixed, year-bounded precensus lag versus concurrent temperature association.

Primary outcome: Gentoo minus Adelie annual change in log(1+nests).
Same frozen matched cohort, one predetermined Aug-Nov lag, no invented census
month. Exploratory covariation only: not causal warming, competition, or a test
of an immediate within-breeding-season mechanism.
"""
from __future__ import annotations
import argparse
import calendar
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
import numpy as np

PINS = {
    'cohort':'364933cd254fa9b0a542da92432e02ff61ff8e9a14548d73a8a568bc95140b3e',
    'observations_p1':'cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075',
    'observations_p2':'c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3',
    'era5':'f2bad55bc9b714351b8bc30031b1518eece43138f77d4047657a3e145911e9a6',
}
MONTHS=(8,9,10,11)
PRIMARY=('ADPE','GEPE')
TERMS=('delta_concurrent_AugNov_C','delta_prior_AugNov_C')


def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def census_bounds(record):
    """Return reported-date interval and precision, never an imputed census date."""
    def integer(key):
        raw=str(record.get(key,'')).strip()
        if not raw:return None
        number=float(raw)
        if not math.isfinite(number) or not number.is_integer():
            raise ValueError('invalid source calendar integer '+key)
        return int(number)
    y,m,d=integer('year'),integer('month'),integer('day')
    text=str(record.get('date','')).strip()
    if text:
        observed=date.fromisoformat(text)
        if any(value is not None and value!=correct for value,correct in
               ((y,observed.year),(m,observed.month),(d,observed.day))):
            raise ValueError('conflict between original date and calendar fields')
        return observed,observed,'day'
    if y is None:raise ValueError('source observation year absent')
    if m is None:
        if d is not None:raise ValueError('day without source month')
        return date(y,1,1),date(y,12,31),'year'
    if d is None:
        return date(y,m,1),date(y,m,calendar.monthrange(y,m)[1]),'month'
    observed=date(y,m,d)
    return observed,observed,'day'


def window_before(record, climate_year, last_month=11):
    low,_,_=census_bounds(record)
    end=date(climate_year,last_month,calendar.monthrange(climate_year,last_month)[1])
    return end<low


def monthly_index(rows):
    lookup={};site_grids={}
    for row in rows:
        site=row['site_id'];year=int(row['year']);month=int(row['month'])
        if month not in range(1,13):raise ValueError('invalid original month')
        key=(site,year,month)
        if key in lookup:raise ValueError('duplicate monthly source key')
        lat=float(row['returned_grid_latitude']);lon=float(row['returned_grid_longitude'])
        if not math.isfinite(lat) or not math.isfinite(lon):raise ValueError('nonfinite grid coordinate')
        grid=(lat,lon)
        if site in site_grids and site_grids[site]!=grid:raise ValueError('original grid changed across months')
        site_grids[site]=grid
        raw=row['air2m_mean_c']
        value=float(raw) if row['complete_month']=='True' and raw!='' else None
        if value is not None and (not math.isfinite(value) or not -100<value<50):
            raise ValueError('nonfinite or invalid original temperature')
        lookup[key]=(value,grid)
    return lookup


def seasonal_temp(lookup,site,year):
    values=[lookup.get((site,year,month),(None,None))[0] for month in MONTHS]
    return None if any(value is None for value in values) else float(sum(values)/len(values))


def equal_land_weights(rows):
    counts=Counter(row['site_id'] for row in rows);sites=defaultdict(set)
    for row in rows:sites[row['land_fid']].add(row['site_id'])
    if any(row['land_fid'] is None for row in rows):raise ValueError('missing exact mapped land')
    return [1/(counts[row['site_id']]*len(sites[row['land_fid']])) for row in rows]


def fit(rows,term,year_effect,weights=None):
    n=len(rows)
    if not n:return {'status':'EMPTY','coefficient':None,'n':0,'residual_df':None}
    x=np.asarray([float(row[term]) for row in rows]);y=np.asarray([float(row['relative_growth']) for row in rows])
    w=np.ones(n) if weights is None else np.asarray(weights,dtype=float)
    if len(w)!=n or not np.isfinite(w).all() or np.any(w<=0):raise ValueError('invalid weights')
    if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('nonfinite model input')
    columns=[np.ones(n)]
    for key in ('site_id','end_year') if year_effect else ('site_id',):
        levels=sorted({str(row[key]) for row in rows})
        columns += [np.array([float(str(row[key])==level) for row in rows]) for level in levels[1:]]
    D=np.column_stack(columns);sw=np.sqrt(w);Z=D*sw[:,None];X=np.column_stack((Z,x*sw))
    rank0=int(np.linalg.matrix_rank(Z));rank1=int(np.linalg.matrix_rank(X));df=n-rank1
    rx=x*sw-Z@np.linalg.lstsq(Z,x*sw,rcond=None)[0]
    ry=y*sw-Z@np.linalg.lstsq(Z,y*sw,rcond=None)[0]
    den=float(rx@rx);total=float(np.sum(w*(x-np.average(x,weights=w))**2))
    algebraic=float(np.linalg.lstsq(X,y*sw,rcond=None)[0][-1]) if rank1>rank0 and den>1e-10 else None
    if algebraic is not None:
        # Independent FWL residual calculation must agree with direct dummy fit.
        residualized=float(rx@ry/den)
        if not math.isclose(algebraic,residualized,rel_tol=1e-7,abs_tol=1e-9):
            raise ValueError('independent regression calculation mismatch')
    status='CLIMATE_COLLINEAR' if algebraic is None else ('SATURATED_NO_RESIDUAL_DF' if df<=0 else 'DESCRIPTIVE_ONLY')
    return dict(status=status,n=n,sites=len({r['site_id'] for r in rows}),
        years=len({r['end_year'] for r in rows}),regions=len({r.get('region','') for r in rows}),
        nuisance_rank=rank0,full_rank=rank1,residual_df=df,
        coefficient=algebraic if status=='DESCRIPTIVE_ONLY' else None,
        algebraic_coefficient_audit_only=algebraic,
        residual_climate_ss=den,remaining_climate_ss_fraction=den/total if total>1e-10 else None,
        p_value=None,confidence_interval=None,causal_warming_effect=False)


def leave_one(rows,term,year_effect,field):
    results=[]
    for value in sorted({r[field] for r in rows},key=str):
        sub=[r for r in rows if r[field]!=value]
        model=fit(sub,term,year_effect)
        results.append(dict(omitted=str(value),n=len(sub),coefficient=model['coefficient'],
                            status=model['status'],residual_df=model['residual_df']))
    good=[r['coefficient'] for r in results if r['coefficient'] is not None]
    return dict(refits=results,range_not_confidence_interval=[min(good),max(good)] if good else None,
                valid_refits=len(good))


def build_pairs(cohort,observations,monthly,geography):
    """Join source rows exactly; only exposure completeness can reduce the roster."""
    source=defaultdict(list)
    observation_ids=set()
    for r in observations:
        if r['id'] in observation_ids:raise ValueError('duplicate original observation ID')
        observation_ids.add(r['id'])
        if r['type']=='nests' and r['presence']=='1':
            source[(r['site_id'],r['species_id'],r['season'],r['citekey'],r['vantage'])].append(r)
    original={};groups=defaultdict(dict)
    for row in cohort:
        site,sp=row['site_id'],row['species_id'];start=int(row['start_year']);end=int(row['end_year'])
        if end!=start+1:raise ValueError('nonadjacent source pair')
        if sp in groups[site,start]:raise ValueError('duplicate cohort species')
        obs=[]
        for season,endpoint in ((start,'start'),(end,'end')):
            key=(site,sp,str(season),row['publisher_citekey'],row['publisher_vantage'])
            found=source.get(key,[])
            if len(found)!=1:raise ValueError('source identity not unique')
            record=found[0]
            if not math.isclose(float(record['count']),float(row['nests_'+endpoint]),abs_tol=1e-9):
                raise ValueError('source count mismatch')
            low,high,_=census_bounds(record)
            if low.year not in (season,season+1):raise ValueError('observation year inconsistent with season')
            obs.append(record)
        original[site,sp,start]=obs;groups[site,start][sp]=row
    lookup=monthly_index(monthly);all_pairs=[];matched=[];audit=[]
    for (site,start),members in sorted(groups.items()):
        if not all(sp in members for sp in PRIMARY):continue
        a,b=(members[sp] for sp in PRIMARY)
        if a['publisher_citekey']!=b['publisher_citekey'] or a['publisher_vantage']!=b['publisher_vantage']:continue
        if a['era5_grid_id']!=b['era5_grid_id']:raise ValueError('species grid conflict')
        end=start+1
        records=original[site,PRIMARY[0],start]+original[site,PRIMARY[1],start]
        prior_flags=[];current_flags=[];minimum_gaps=[];maximum_gaps=[]
        for record in records:
            season=int(record['season']);low,high,precision=census_bounds(record)
            current_end=date(season,11,30);prior_end=date(season-1,11,30)
            before=prior_end<low;prior_flags.append(before);current_flags.append(current_end<low)
            minimum_gaps.append((low-prior_end).days);maximum_gaps.append((high-prior_end).days)
            audit.append(dict(site_id=site,start_year=start,end_year=end,record_id=record['id'],
                species_id=record['species_id'],source_season=season,
                original_year=record.get('year',''),original_month=record.get('month',''),
                original_day=record.get('day',''),original_date=record.get('date',''),
                precision=precision,earliest_possible_count=low.isoformat(),latest_possible_count=high.isoformat(),
                these_bounds_are_not_assigned_survey_dates=True,
                prior_exposure_end=prior_end.isoformat(),prior_precedes_lower_bound=before,
                concurrent_exposure_end=current_end.isoformat(),concurrent_precedes_lower_bound=current_end<low))
        if not all(prior_flags):raise ValueError('prior window is not strictly before all source bounds')
        current=[seasonal_temp(lookup,site,y) for y in (start,end)]
        lagged=[seasonal_temp(lookup,site,y-1) for y in (start,end)]
        if any(v is None for v in current):raise ValueError('frozen current window lacks climate data')
        for member in (a,b):
            if not math.isclose(current[1]-current[0],float(member['delta_AugNov_ERA5_C']),abs_tol=1e-9):
                raise ValueError('concurrent ERA5 reconstruction mismatch')
        geo=geography[site]
        fid=geo['original_land_fid'] if geo['category']=='EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON' else None
        pair=dict(site_id=site,start_year=start,end_year=end,region=a['source_region'],
            land_fid=fid,grid=a['era5_grid_id'],pair='ADPE|GEPE',
            relative_growth=float(b['delta_log1p_nests'])-float(a['delta_log1p_nests']),
            delta_concurrent_AugNov_C=current[1]-current[0],
            delta_prior_AugNov_C=None if any(v is None for v in lagged) else lagged[1]-lagged[0],
            prior_precedes_all_source_bounds=True,concurrent_precedes_all_source_bounds=all(current_flags),
            all_four_full_calendar_months_known=all(census_bounds(r)[2]!='year' for r in records),
            original_record_ids=';'.join(r['id'] for r in records),
            prior_minimum_possible_gap_days=min(minimum_gaps),prior_maximum_possible_gap_days=max(maximum_gaps),
            inclusion_status='MISSING_PRIOR_CLIMATE' if any(v is None for v in lagged) else 'COMMON_SAMPLE')
        all_pairs.append(pair)
        if pair['inclusion_status']=='COMMON_SAMPLE':matched.append(pair)
    if len(all_pairs)!=45:raise ValueError('original primary 45-pair cohort changed')
    return all_pairs,matched,audit


def write_csv(path,rows):
    with Path(path).open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    ap=argparse.ArgumentParser()
    for arg in ('cohort','observations-p1','observations-p2','era5','land-result','out'):
        ap.add_argument('--'+arg,required=True,type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    for name,expected in PINS.items():
        if sha(getattr(args,name))!=expected:raise ValueError('source SHA mismatch: '+name)
    cohort=read_csv(args.cohort);obs=read_csv(args.observations_p1)+read_csv(args.observations_p2)
    monthly=read_csv(args.era5);geography=json.loads(args.land_result.read_text())['geography']
    if len(cohort)!=381 or len(obs)!=5487 or len(monthly)!=14400:raise ValueError('source rows changed')
    original,common,audit=build_pairs(cohort,obs,monthly,geography)
    if len(common)<3:raise ValueError('no supported common comparison')
    exact=[r for r in common if r['land_fid'] is not None]
    models={};sensitivity={};spatial={}
    for term in TERMS:
        models[term]={};sensitivity[term]={};spatial[term]={}
        for year,label in ((False,'site_fixed'),(True,'site_year_fixed')):
            models[term][label]=fit(common,term,year)
            sensitivity[term][label]={field:leave_one(common,term,year,field) for field in ('end_year','grid')}
            spatial[term][label]=dict(exact_sample=fit(exact,term,year),
                same_sample_equal_land_weight=fit(exact,term,year,equal_land_weights(exact)),
                leave_one_land=leave_one(exact,term,year,'land_fid'))
    unique_records={r['record_id']:r for r in audit}
    eligible_keys={(r['site_id'],r['start_year']) for r in common}
    common_audit=[r for r in audit if (r['site_id'],r['start_year']) in eligible_keys]
    report=dict(schema=3,status='POSTEXPLORATORY_FIXED_LAG_SOURCE_YEAR_BOUNDED_NOT_CAUSAL',
        primary='GEPE minus ADPE annual change in log(1+nests)',
        lag_definition='For each breeding-season label s use mean Aug-Nov of s-1; compare exposure at the two count endpoints.',
        chronology_assumption='Published observation year/date fields bound actual census timing; source calendar accuracy is not independently field-verified.',
        n_original_pairs=len(original),n_common_pairs=len(common),
        common_sites=len({r['site_id'] for r in common}),common_grids=len({r['grid'] for r in common}),
        common_regions=len({r['region'] for r in common}),common_years=len({r['end_year'] for r in common}),
        excluded_pairs=[r for r in original if r['inclusion_status']!='COMMON_SAMPLE'],
        chronology=dict(original_unique_records=len(unique_records),
            original_unique_record_precision=dict(Counter(r['precision'] for r in unique_records.values())),
            original_all_four_months_known=sum(r['all_four_full_calendar_months_known'] for r in original),
            common_prior_before_every_original_bound=all(r['prior_precedes_all_source_bounds'] for r in common),
            common_prior_min_possible_gap_days=min(r['prior_minimum_possible_gap_days'] for r in common),
            common_prior_max_possible_gap_days=max(r['prior_maximum_possible_gap_days'] for r in common),
            common_current_before_all_counts=sum(r['concurrent_precedes_all_source_bounds'] for r in common),
            date_fields_not_imputed=True),
        same_sample_models=models,year_grid_deletion=sensitivity,
        exact_land_common_sample=dict(n=len(exact),sites=len({r['site_id'] for r in exact}),land_ids=len({r['land_fid'] for r in exact})),
        mapped_land_sensitivity=spatial,
        source_sha256={**{name:sha(getattr(args,name)) for name in PINS},'land_result':sha(args.land_result)},
        source_runs={'counts381':40868420083,'raw_observations':40868828790,'ERA5':40856645581,'land':40869812618},
        limitations=['Fixed lag changes the biological estimand; it is not a temporal repair of the original contemporaneous coefficient.',
          'Observed-year bounds do not prove the publisher dates are field-validated; uncertain dates remain intervals.',
          'Positive endpoints and an Adelie-selected climate roster condition the sample; no establishment or extinction analysis.',
          'Small number of sites, current mapped land units, original survey lineage and incomplete detection controls.',
          'No causal anthropogenic warming, direct competition, movement, snow or sea-ice mediator is identified.',
          'Deletion ranges are not confidence intervals; no p-values; original 216-test family unchanged.',
          'Lag/diagnostics chosen after prior analysis; not a prospective confirmation.'])
    write_csv(args.out/'lagged_primary_45_roster.csv',original)
    write_csv(args.out/'lagged_primary_common_pairs.csv',common)
    write_csv(args.out/'original_record_chronology_bounds.csv',audit)
    (args.out/'lagged_climate_v3_result.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('n_original_pairs','n_common_pairs','common_sites','common_grids','chronology','same_sample_models')},ensure_ascii=False))

if __name__=='__main__':main()
