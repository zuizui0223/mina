"""V11: later nest composition without reusing chick-output baseline counts.

A fixed t+2 to t+5 source comparison; not offspring recruitment or a forecast.
Source bridges are labelled exact count agreements, not field validation.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, statistics, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recorded_chick_output_v9 as v9

STAGE_SHA='3b3637c545ba3b804895ff406907fa50f51b95d765b554184368688ea4a4b557'
START_OFFSET=2
END_OFFSET=5
PRIMARY='CHPE|GEPE'

def truth(x):
    if isinstance(x,bool): return x
    if str(x) not in ('True','False'): raise ValueError('invalid stored boolean')
    return x=='True'

def source_index(rows):
    seen=set();index=defaultdict(list)
    for r in rows:
        rid=str(r['id'])
        if rid in seen: raise ValueError('duplicate observation ID: '+rid)
        seen.add(rid)
        if r.get('type')!='nests' or r.get('species_id') not in {'ADPE','CHPE','GEPE'}: continue
        cite=str(r.get('citekey','')).strip(); vantage=str(r.get('vantage','')).strip()
        if cite.lower() in v9.UNKNOWN or vantage.lower() in v9.UNKNOWN: continue
        try: season=int(r['season'])
        except (ValueError,TypeError): continue
        # Form duplicate groups before filtering numeric values.
        index[r['site_id'],r['species_id'],season,cite,vantage].append(r)
    return dict(index)

def one(index,site,sp,year,cite,vantage):
    r=index.get((site,sp,year,cite,vantage),[])
    if len(r)!=1 or v9.number(r[0].get('count')) is None: return None
    return r[0]

def metrics(baseline,early,late):
    na,nb=float(baseline['nest_count_a']),float(baseline['nest_count_b'])
    ca,cb=float(baseline['chick_count_a']),float(baseline['chick_count_b'])
    if min(na,nb)<=0 or min(ca,cb)<0: raise ValueError('invalid baseline count')
    e=[v9.number(r['count']) for r in early]; l=[v9.number(r['count']) for r in late]
    if not all(math.isfinite(n) and n>=0 for n in e+l): raise ValueError('invalid later count')
    ns=nb/(na+nb);cs=cb/(ca+cb) if ca+cb else None
    ps=e[1]/sum(e) if sum(e) else None; pe=l[1]/sum(l) if sum(l) else None
    growth=(pe-ps)/(END_OFFSET-START_OFFSET) if pe is not None and ps is not None else None
    loggrowth=(math.log(l[1]/l[0])-math.log(e[1]/e[0]))/(END_OFFSET-START_OFFSET) if min(e+l)>0 else None
    shift=cs-ns if cs is not None else None
    sign=None if shift is None or growth is None or shift==0 or growth==0 else shift*growth>0
    return dict(baseline_nest_share=ns,baseline_chick_share=cs,baseline_share_shift=shift,
        baseline_output_a=ca/na,baseline_output_b=cb/nb,
        future_start_count_a=e[0],future_start_count_b=e[1],
        future_end_count_a=l[0],future_end_count_b=l[1],
        future_share_early=ps,future_share_late=pe,future_share_change_per_year=growth,
        future_log_ratio_change_per_year=loggrowth,directional_concordance=sign,
        undefined_future_composition=ps is None or pe is None)

def followup(b,index):
    t=int(b['season_start']);site=b['site_id'];sp=(b['species_a'],b['species_b'])
    start,end=t+START_OFFSET,t+END_OFFSET;vantage=b['vantage'];original=b['citekey']
    out=dict(site_id=site,site_name=b.get('site_name',''),region=b['region'],pair=b['pair'],
        season_start=t,future_start=start,future_end=end,baseline_citekey=original,vantage=vantage,
        baseline_stage_ordered=truth(b['both_stages_ordered']),
        baseline_same_full_dates=truth(b['same_full_dates_across_species']),
        current_mapped_nonmainland_land=truth(b['current_mapped_nonmainland_land']),
        exact_source_land_fid=b.get('exact_source_land_fid'),
        status='no_qualified_future_source',source_candidate_audit=[],
        identical_field_protocol_verified=False,recruitment_identified=False)
    if truth(b.get('ambiguous_site_season_pair',False)):
        out['status']='ambiguous_baseline_source';return out
    source_candidates=sorted({k[3] for k in index if k[0]==site and k[4]==vantage and k[2] in (start,end)})
    eligible=[]
    for cite in source_candidates:
        a=[one(index,site,s,start,cite,vantage) for s in sp]
        z=[one(index,site,s,end,cite,vantage) for s in sp]
        reason=None; bridge_ids=[]
        if any(x is None for x in a+z): reason='incomplete_or_duplicated_endpoint_records'
        elif cite!=original:
            bridge=[one(index,site,s,t,cite,vantage) for s in sp]
            if any(x is None for x in bridge): reason='baseline_bridge_missing_or_duplicated'
            elif [v9.number(x['count']) for x in bridge]!=[float(b['nest_count_a']),float(b['nest_count_b'])]:
                reason='baseline_count_disagreement'
            else: bridge_ids=[str(x['id']) for x in bridge]
        out['source_candidate_audit'].append(dict(citekey=cite,reason=reason or 'eligible_by_provenance',
              baseline_bridge_ids=bridge_ids))
        if reason is None: eligible.append((cite,a,z,bridge_ids))
    same=[x for x in eligible if x[0]==original]
    if same: selected=same[0]
    elif len(eligible)==1: selected=eligible[0]
    elif len(eligible)>1:
        out['status']='ambiguous_future_source';return out
    else:return out
    cite,a,z,bridge_ids=selected
    out.update(future_citekey=cite,source_link='same_citation' if cite==original else 'baseline_count_agreement_bridge',
        bridge_count_record_ids=bridge_ids)
    baseids={str(b[f'{stage}_source_id_{suffix}']) for stage in ('nest','chick') for suffix in ('a','b')}
    futureids={str(x['id']) for x in a+z}
    if len(futureids)!=4 or baseids&futureids:
        out['status']='shared_baseline_future_count_ids';return out
    try:
        cb=[date.fromisoformat(str(b['chick_date_upper_'+s])) for s in ('a','b')]
        ab=[v9.calendar_bounds(x) for x in a];zb=[v9.calendar_bounds(x) for x in z]
        ordered=(all(x[0] is not None and x[1] is not None for x in ab+zb)
             and max(cb)<min(x[0] for x in ab) and max(x[1] for x in ab)<min(x[0] for x in zb))
    except (ValueError,TypeError): ordered=False
    if not ordered:
        out['status']='chronology_unresolved_or_reversed';return out
    out.update(status='accepted',no_shared_count_ids=True,all_future_counts_after_chicks=True,
        future_early_source_id_a=str(a[0]['id']),future_early_source_id_b=str(a[1]['id']),
        future_late_source_id_a=str(z[0]['id']),future_late_source_id_b=str(z[1]['id']),
        chick_latest_possible_date=max(cb).isoformat(),
        future_early_earliest_possible_date=min(x[0] for x in ab).isoformat(),
        future_early_latest_possible_date=max(x[1] for x in ab).isoformat(),
        future_late_earliest_possible_date=min(x[0] for x in zb).isoformat(),
        **metrics(b,a,z))
    return out

def disjoint_windows(rows):
    selected=[];last={}
    for r in sorted(rows,key=lambda x:(x['site_id'],x['pair'],int(x['future_start']),int(x['future_end']),int(x['season_start']))):
        key=r['site_id'],r['pair']
        if int(r['future_start'])>last.get(key,-10**9):
            selected.append(r);last[key]=int(r['future_end'])
    return selected

def mean(values):
    values=[x for x in values if x is not None]
    return statistics.mean(values) if values else None

def summarize(rows):
    groups=defaultdict(list)
    for r in rows: groups[r['site_id']].append(r)
    ss=[]
    for site,part in sorted(groups.items()):
        ss.append(dict(site_id=site,region=part[0]['region'],n=len(part),
          baseline_seasons=[int(r['season_start']) for r in part],
          mean_stage_share_shift=mean([r['baseline_share_shift'] for r in part]),
          mean_future_share_change_per_year=mean([r['future_share_change_per_year'] for r in part]),
          concordant=sum(r['directional_concordance'] is True for r in part),
          discordant=sum(r['directional_concordance'] is False for r in part),
          tie_or_undefined=sum(r['directional_concordance'] is None for r in part)))
    regions=sorted({r['region'] for r in rows})
    return dict(n_links=len(rows),n_sites=len(groups),regions=regions,
       n_mapped_current_nonmainland_lands=len({str(r['exact_source_land_fid']) for r in rows if r['current_mapped_nonmainland_land']}),
       same_citation_links=sum(r['source_link']=='same_citation' for r in rows),
       count_agreement_bridge_links=sum(r['source_link']!='same_citation' for r in rows),
       concordant=sum(r['directional_concordance'] is True for r in rows),
       discordant=sum(r['directional_concordance'] is False for r in rows),
       tie_or_undefined=sum(r['directional_concordance'] is None for r in rows),
       positive_stage_direction_n=sum(r['baseline_share_shift'] is not None and r['baseline_share_shift']>0 for r in rows),
       positive_future_direction_n=sum(r['future_share_change_per_year'] is not None and r['future_share_change_per_year']>0 for r in rows),
       constant_positive_direction_concordant_n=sum(r['future_share_change_per_year'] is not None and r['future_share_change_per_year']>0 for r in rows),
       stage_direction_uniform_nonzero=bool(rows) and (
          all(r['baseline_share_shift'] is not None and r['baseline_share_shift']>0 for r in rows) or
          all(r['baseline_share_shift'] is not None and r['baseline_share_shift']<0 for r in rows)),
       row_mean_stage_share_shift=mean([r['baseline_share_shift'] for r in rows]),
       row_mean_future_share_change_per_year=mean([r['future_share_change_per_year'] for r in rows]),
       equal_site_mean_stage_share_shift=mean([r['mean_stage_share_shift'] for r in ss]),
       equal_site_mean_future_share_change_per_year=mean([r['mean_future_share_change_per_year'] for r in ss]),
       site_summaries=ss,multi_region_generality_supported=len(groups)>=3 and len(regions)>=2,
       p_value=None,recruitment_identified=False)

def write_rows(path,rows):
    # Preserve reasons for every unlinked baseline; JSON arrays remain inspectable.
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original-dir',required=True,type=Path)
    ap.add_argument('--v10-dir',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    src=args.original_dir/'source' if (args.original_dir/'source').is_dir() else args.original_dir
    for name,pin in v9.PINS.items():
        if v9.digest(src/name)!=pin:raise ValueError('original source SHA drift: '+name)
    stagefile=args.v10_dir/'stage_species_composition_v10.csv'
    if v9.digest(stagefile)!=STAGE_SHA:raise ValueError('V10 baseline SHA changed')
    raw=v9.read_csv(src/'observations_p1.csv')+v9.read_csv(src/'observations_p2.csv')
    if len(raw)!=5487:raise ValueError('source record count changed')
    baseline=v9.read_csv(stagefile)
    if len(baseline)!=75:raise ValueError('V10 baseline source contrast roster changed')
    original={str(r['id']):r for r in raw}
    for b in baseline:
        for suffix in ('a','b'):
            for stage in ('nest','chick'):
                o=original[b[f'{stage}_source_id_{suffix}']]
                if (o['site_id']!=b['site_id'] or o['species_id']!=b[f'species_{suffix}']
                    or int(o['season'])!=int(b['season_start']) or o['citekey']!=b['citekey']
                    or o['vantage']!=b['vantage'] or v9.number(o['count'])!=float(b[f'{stage}_count_{suffix}'])):
                    raise ValueError('V10 baseline original-record identity mismatch')
    idx=source_index(raw);ledger=[followup(b,idx) for b in baseline]
    accepted=[r for r in ledger if r['status']=='accepted'];reports={}
    for pair in ('CHPE|GEPE','ADPE|GEPE','ADPE|CHPE'):
        all_rows=[r for r in accepted if r['pair']==pair]
        ordered=[r for r in all_rows if r['baseline_stage_ordered']]
        groups={
          'ordered_same_citation_primary':[r for r in ordered if r['source_link']=='same_citation'],
          'ordered_including_count_agreement_bridges':ordered,
          'ordered_same_full_dates':[r for r in ordered if r['baseline_same_full_dates']],
          'all_stage_timing_diagnostic':all_rows}
        reports[pair]={k:dict(all_windows=summarize(p),nonoverlapping_windows=summarize(disjoint_windows(p))) for k,p in groups.items()}
    result=dict(schema=1,status='POST_EXPLORATION_STAGE_TO_LATER_COUNTS_NOT_RECRUITMENT_OR_FORECAST',
       primary_species_pair=PRIMARY,fixed_future_offsets=[START_OFFSET,END_OFFSET],
       original_source_sha256=v9.PINS,baseline_stage_SHA256=STAGE_SHA,
       baseline_contrasts=len(baseline),accepted_links=len(accepted),
       eligibility_statuses=dict(Counter(r['status'] for r in ledger)),contrasts=reports,
       limits=[
         'Only future endpoints t+2 and t+5; missing observations never interpolated.',
         'Baseline and future outcome share no original count IDs or count denominators.',
         'Exact baseline count agreement between sources does not verify same field scope or effort.',
         'Repeated overlapping future periods are not independent ecological trials.',
         'Recorded chicks are not tracked individuals, certified fledglings or successful recruits.',
         'Earlier adults, immigration/emigration, breeding propensity and other cohorts remain unmeasured.',
         'The fixed follow-through window is not assumed to equal a species recruitment age.',
         'No inference about warming, sea-ice, causal competition or population growth mechanisms.',
         'Original V1--V10, prior 216 multiplicity correction and frozen papers unchanged.'])
    write_rows(args.out/'stage_future_eligibility_v11.csv',ledger)
    write_rows(args.out/'stage_future_accepted_v11.csv',accepted)
    (args.out/'stage_followthrough_v11_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('STAGE_FOLLOWTHROUGH_V11='+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)
if __name__=='__main__':main()
