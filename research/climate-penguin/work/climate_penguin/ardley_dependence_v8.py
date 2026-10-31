"""V8: explain V7 Ardley influence with exact source-preserving decompositions.

Post-result diagnostic, not an independent confirmatory or causal climate test.
No re-selection of marine windows, lag, interval endpoints, species or outcome.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, statistics
from collections import defaultdict
from pathlib import Path

INPUT_SHA='e65555f37683bba97ede1712d6a943df09b7d0f02a85fe0c2a41d89cd72111d5'
RESULT_SHA='cdc73abd409789b0b488947fcb729b35efad92b2d70bc0ba10296f751b1a8982'
PINS={'sites.csv':'36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34',
      'observations_p1.csv':'cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075',
      'observations_p2.csv':'c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3'}
Y={'chinstrap':'annualized_a_growth','gentoo':'annualized_b_growth','relative':'annualized_log_ratio_change'}
FOCAL='ARDL'

def read(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,rows):
    if not rows:return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def _summarize(D,C,n):
    return {'n':n,'D':D,'C':C,'beta':{k:v/D if D>1e-12 else None for k,v in C.items()}}

def _components(rows,keys):
    groups=defaultdict(list)
    for r in rows:groups[tuple(str(r[k]) for k in keys)].append(r)
    out={}
    for key,part in sorted(groups.items()):
        w=[float(r['gap']) for r in part];sw=math.fsum(w)
        xx=[float(r['x_ice_rate']) for r in part]
        mx=math.fsum(a*b for a,b in zip(w,xx))/sw
        rx=[v-mx for v in xx];D=math.fsum(a*b*b for a,b in zip(w,rx));C={}
        for name,field in Y.items():
            yy=[float(r[field]) for r in part]
            my=math.fsum(a*b for a,b in zip(w,yy))/sw
            C[name]=math.fsum(a*b*(c-my) for a,b,c in zip(w,rx,yy))
        out['|'.join(key)]=_summarize(D,C,len(part))
    combined=_summarize(math.fsum(v['D'] for v in out.values()),
        {k:math.fsum(v['C'][k] for v in out.values()) for k in Y},len(rows))
    return combined,out

def partition(rows):
    seen=set()
    for r in rows:
        key=(r['site_id'],int(r['start']),int(r['end']))
        if key in seen:raise ValueError('duplicate original site/interval key')
        seen.add(key)
        gap=float(r['gap'])
        if gap<=0 or not math.isfinite(gap) or int(r['end'])-int(r['start'])!=gap:
            raise ValueError('invalid interval length')
        vals=[float(r[k]) for k in ('x_ice_rate',*Y.values())]
        if not all(math.isfinite(v) for v in vals):raise ValueError('nonfinite source input')
        if not math.isclose(vals[3],vals[2]-vals[1],abs_tol=1e-11,rel_tol=1e-11):
            raise ValueError('relative outcome differs from species difference')
    baseline,sites=_components(rows,('site_id',))
    within,strata=_components(rows,('site_id','original_citekey','original_vantage'))
    between=_summarize(baseline['D']-within['D'],
        {k:baseline['C'][k]-within['C'][k] for k in Y},len(rows))
    return {'baseline':baseline,'sites':sites,'within_source':within,'source_strata':strata,
            'between_source':between,'p_values':None,'confidence_intervals':None}

def one_nest_log_step(count):
    n=float(count)
    if not math.isfinite(n) or n<=0:raise ValueError('positive count required')
    return math.log1p(1/n)

def distance(a,b):
    p1,p2=map(math.radians,(float(a['latitude']),float(b['latitude'])))
    dp=p2-p1;dl=math.radians(float(b['longitude'])-float(a['longitude']))
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(h)))

def nearest_matched(rows,metadata,focal,min_pairs=3):
    roster=defaultdict(set)
    for r in rows:roster[r['site_id']].add((int(r['start']),int(r['end'])))
    if focal not in roster or focal not in metadata:raise ValueError('focal metadata absent')
    candidates=[]
    for s,keys in sorted(roster.items()):
        if s==focal:continue
        if s not in metadata:raise ValueError('orphan original site')
        shared=sorted(keys & roster[focal])
        candidates.append({'site_id':s,'distance_km':distance(metadata[focal],metadata[s]),
                           'n_exact_intervals':len(shared),'keys':shared})
    candidates.sort(key=lambda x:(x['distance_km'],x['site_id']))
    eligible=[c for c in candidates if c['n_exact_intervals']>=min_pairs]
    return {'selected_site':eligible[0]['site_id'] if eligible else None,
            'n_exact_intervals':eligible[0]['n_exact_intervals'] if eligible else 0,
            'metadata_selection_rule':'nearest original coordinate with >=3 exact start/end intervals; no response used',
            'candidates':candidates}

def count_summary(rows):
    out={}
    for s in ('a','b'):
        endpoint={}
        for r in rows:
            for side in ('start','end'):
                key=str(r['source_'+s+'_'+side]);n=float(r['n_'+s+'_'+side])
                if key in endpoint and endpoint[key]!=n:raise ValueError('count ID conflict')
                endpoint[key]=n
        ns=list(endpoint.values())
        out['chinstrap' if s=='a' else 'gentoo']={
          'unique_count_records':len(ns),'minimum':min(ns),'maximum':max(ns),
          'median':statistics.median(ns),
          'one_nest_log_step_range':[min(map(one_nest_log_step,ns)),max(map(one_nest_log_step,ns))],
          'actual_observation_error_measured':False}
    return out

def validate_original(rows,observations,metadata):
    if len(rows)!=78 or len({r['site_id'] for r in rows})!=19:raise ValueError('V7 roster changed')
    obs={r['id']:r for r in observations}
    if len(obs)!=5487 or len(metadata)!=729:raise ValueError('original source dimensions changed')
    for r in rows:
        if (r['species_a'],r['species_b'])!=('CHPE','GEPE'):raise ValueError('species changed')
        for s in ('a','b'):
            for side in ('start','end'):
                z=obs[str(r['source_'+s+'_'+side])]
                if not (z['site_id']==r['site_id'] and z['species_id']==r['species_'+s] and
                        int(z['season'])==int(r[side]) and z['citekey']==r['original_citekey'] and
                        z['vantage']==r['original_vantage'] and z['type']=='nests' and
                        float(z['count'].replace(',',''))==float(r['n_'+s+'_'+side])):
                    raise ValueError('original source record identity/count mismatch')
            growth=math.log(float(r['n_'+s+'_end'])/float(r['n_'+s+'_start']))/float(r['gap'])
            if not math.isclose(growth,float(r['annualized_'+s+'_growth']),abs_tol=1e-12):
                raise ValueError('original count growth mismatch')

# Factual transcription of official ASPA150(2009) Table2; None = printed blank, NOT zero.
ASPA150={1973:(18,1850),1980:(244,3809),1981:(141,2580),1983:(91,1656),
    1984:(110,3105),1985:(39,3522),1986:(None,3410),1994:(45,3772),1995:(49,2985),
    1996:(72,2974),1997:(33,3146),1998:(43,3349),1999:(34,3911),2000:(26,4472),
    2001:(22,4444),2002:(35,5131),2003:(29,4957),2004:(13,4798),2005:(9,4635)}

def primary_lineage(year,species):
    """Only explicit Table2 footnotes; no inference of a field census day."""
    year=int(year)
    if species not in ('CHPE','GEPE'):return None
    if 1994<=year<=2005:return 'INACH_Valencia_project'
    if year in (1973,1983):return 'Yanez_1984'
    if year==1980:return 'Trivelpiece_1987' if species=='CHPE' else 'Woehler_1993'
    if year==1981:return 'Bannasch_1983'
    if year==1984:return 'Peter_1998_2008' if species=='CHPE' else 'Woehler_1993'
    if year==1985:return 'Rauschert_1987'
    if year==1986:return None if species=='CHPE' else 'Woehler_1993'
    return None

def same_primary_project(row):
    if row['site_id']!=FOCAL or row['original_citekey']!='meeting2009management150':return False
    keys=[primary_lineage(row[side],sp) for side in ('start','end') for sp in ('CHPE','GEPE')]
    return None not in keys and len(set(keys))==1

def source_table_check(rows):
    unique={}
    for r in rows:
        if r['site_id']!=FOCAL or r['original_citekey']!='meeting2009management150':continue
        for s,sp in [('a','CHPE'),('b','GEPE')]:
            for side in ('start','end'):
                y=int(r[side]);n=float(r['n_'+s+'_'+side]);expected=ASPA150[y][0 if s=='a' else 1]
                unique[str(r['source_'+s+'_'+side])]={
                    'source_id':str(r['source_'+s+'_'+side]),'season':y,'species':sp,
                    'MAPPPD_count':n,'official_ASPA150_count':expected,'matches':expected==n}
    if not all(z['matches'] for z in unique.values()):raise ValueError('official table contradicts count')
    return sorted(unique.values(),key=lambda r:(r['season'],r['species']))

def analyze(rows,metadata):
    result=partition(rows);focal=[r for r in rows if r['site_id']==FOCAL]
    result['focal']=partition(focal)
    result['without_focal']=partition([r for r in rows if r['site_id']!=FOCAL])['baseline']
    result['focal_count_scales']=count_summary(focal)
    confirmed=[r for r in focal if same_primary_project(r)]
    result['focal_same_primary_project']={
        'selection':'Official Table2 primary-study/project notes match both taxa at both endpoints; post-source-audit subset',
        'partition':partition(confirmed)['baseline'],
        'keys':[[int(r['start']),int(r['end'])] for r in confirmed],
        'verified_same_field_day':False,
        'baseline_78_unchanged':True}
    result['focal_strata']={}
    for cite in sorted({r['original_citekey'] for r in focal}):
        sub=[r for r in focal if r['original_citekey']==cite]
        result['focal_strata'][cite]={
            'start':min(int(r['start']) for r in sub),'end':max(int(r['end']) for r in sub),
            'n_intervals':len(sub),'count_scales':count_summary(sub),'partition':partition(sub)['baseline'],
            'leave_one_interval_out_beta_not_CI':[
                dict(start=int(r['start']),end=int(r['end']),beta=partition(sub[:i]+sub[i+1:])['baseline']['beta'])
                for i,r in enumerate(sub)]}
    D=result['baseline']['D']
    for s,z in result['sites'].items():
        z['exposure_SS_share']=z['D']/D
        z['contribution_to_pooled_beta']={k:v/D for k,v in z['C'].items()}
    nearest=nearest_matched(rows,metadata,FOCAL)
    selected=nearest['selected_site'];matched=[]
    if selected:
        left={(int(r['start']),int(r['end'])):r for r in focal}
        right={(int(r['start']),int(r['end'])):r for r in rows if r['site_id']==selected}
        for key in sorted(left.keys()&right.keys()):
            a,b=left[key],right[key]
            matched.append({'start':key[0],'end':key[1],
                'neighbor_id':selected,'ardley_ice_rate':float(a['x_ice_rate']),
                'neighbor_ice_rate':float(b['x_ice_rate']),
                'ardley_relative_growth':float(a['annualized_log_ratio_change']),
                'neighbor_relative_growth':float(b['annualized_log_ratio_change']),
                'ardley_chinstrap_start':float(a['n_a_start']),'neighbor_chinstrap_start':float(b['n_a_start']),
                'ardley_gentoo_start':float(a['n_b_start']),'neighbor_gentoo_start':float(b['n_b_start']),
                'same_publisher_citation':a['original_citekey']==b['original_citekey'],
                'both_precise_dates_same':False})
        nearest['focal_same_intervals']=partition([left[k] for k in sorted(left.keys()&right.keys())])['baseline']
        nearest['neighbor_same_intervals']=partition([right[k] for k in sorted(left.keys()&right.keys())])['baseline']
        chosen=[right[k] for k in sorted(left.keys()&right.keys())]
        nearest['neighbor_count_scales']=count_summary(chosen)
        ax=[r['ardley_ice_rate'] for r in matched];bx=[r['neighbor_ice_rate'] for r in matched]
        ma,mb=statistics.mean(ax),statistics.mean(bx)
        da=math.fsum((v-ma)**2 for v in ax);db=math.fsum((v-mb)**2 for v in bx)
        nearest['same_interval_ice_rate_correlation']=math.fsum((a-ma)*(b-mb) for a,b in zip(ax,bx))/math.sqrt(da*db) if da*db>0 else None
        nearest['all_matched_citations_equal']=all(r['same_publisher_citation'] for r in matched)
    result['nearest_metadata_match']=nearest
    return result,matched

def main():
    p=argparse.ArgumentParser();p.add_argument('--v7-dir',type=Path,required=True)
    p.add_argument('--original-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    infile=args.v7_dir/'observed_78_intervals_seaice_v7.csv'
    resultfile=args.v7_dir/'observed_interval_seaice_v7_result.json'
    if sha(infile)!=INPUT_SHA or sha(resultfile)!=RESULT_SHA:raise ValueError('frozen V7 input SHA drift')
    source=args.original_dir/'source'
    for name,pin in PINS.items():
        if sha(source/name)!=pin:raise ValueError('original source SHA drift '+name)
    rows=read(infile);observations=read(source/'observations_p1.csv')+read(source/'observations_p2.csv')
    metadata={r['site_id']:r for r in read(source/'sites.csv')}
    validate_original(rows,observations,metadata)
    result,matched=analyze(rows,metadata)
    v7=json.loads(resultfile.read_text())
    for k in Y:
        if not math.isclose(result['baseline']['beta'][k],v7['models']['site']['coefficients'][k],abs_tol=1e-12):
            raise ValueError('V7 baseline model not reproduced')
    table=source_table_check(rows)
    report={'schema':1,'date':'2026-10-30','status':'POST_RESULT_ARDLEY_SOURCE_COUNT_AND_COVARIANCE_DIAGNOSIS',
        'input_sha256':{'V7_roster':sha(infile),'V7_result':sha(resultfile),**PINS},
        'baseline_roster_unchanged':True,'n':78,'result':result,
        'official_ASPA150_overlap_records':len(table),'official_ASPA150_all_overlap_counts_match':all(r['matches'] for r in table),
        'official_source_url':'https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/150.pdf',
        'official_HTML_replica':'https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000023459270',
        'table_verification_method':'Official PDF parsed text and official French HTML Table2 independently checked; PDF screenshot/download unavailable, not claimed visually verified.',
        'limits':['Ardley chosen after original influential-site result: explicit post-result diagnosis, not confirmation.',
            'Published citation is not primary field-study identity; ASPA150(2009) Table2 combines studies and species-specific source footnotes.',
            'Calendar period and published source are confounded; different source slopes cannot be assigned to method changes.',
            'Small colony and deterministic log sensitivity do not demonstrate observation error, demographic noise or a false climate relationship.',
            'No positive- or small-count threshold applied to rescue an effect. Original 78 rows remain baseline.',
            'Nearest site match uses only coordinates and exact interval availability; shared weather is not an experiment.',
            'Sea-ice product and lag remain unchanged; snow, prey, movement, detection error, competition and causal warming are not measured.']}
    write(args.out/'original_ASPA150_overlap_check_v8.csv',table)
    write(args.out/'exact_interval_neighbor_comparison_v8.csv',matched)
    write(args.out/'site_contributions_v8.csv',[
        dict(site_id=s,n=z['n'],D=z['D'],exposure_SS_share=z['exposure_SS_share'],
             **{f'C_{k}':v for k,v in z['C'].items()},
             **{f'beta_{k}':v for k,v in z['beta'].items()},
             **{f'pooled_beta_contribution_{k}':v for k,v in z['contribution_to_pooled_beta'].items()})
        for s,z in result['sites'].items()])
    (args.out/'ardley_dependence_v8_result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('ARDLEY_DEPENDENCE_V8='+json.dumps({'n':78,'baseline':result['baseline'],
        'focal':result['focal']['baseline'],'without_focal':result['without_focal'],
        'source_strata':result['focal']['source_strata'],'neighbor':result['nearest_metadata_match']['selected_site'],
        'official_source_matches':len(table)},allow_nan=False),flush=True)

if __name__=='__main__':main()
