"""Original MAPPPD same-site/year/source/method species growth contrasts.

Exploratory paired changes among already-present colonies. Not climate attribution,
competition, independent islands, extinction, or a rescue of the 216-test screen.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SPECIES = {'ADPE','CHPE','GEPE'}
CONTRASTS = [('ADPE','GEPE'),('CHPE','GEPE'),('ADPE','CHPE')]
UNKNOWN = {'','unknown','na','nan','none'}
SOURCES = {
 'release':'https://www.penguinmap.com/api/v1/release/?format=json',
 'sites':'https://www.penguinmap.com/api/v1/sites/?format=csv',
 'observations_p1':'https://www.penguinmap.com/api/v1/observations/?format=csv&page_size=5000&page=1',
 'observations_p2':'https://www.penguinmap.com/api/v1/observations/?format=csv&page_size=5000&page=2',
}
EXPECTED_SHA = {
 'release':'8f676f6498b1bc79708a67fb05d4ac8ee73249444e85402af87f6a3c64280a65',
 'sites':'36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34',
 'observations_p1':'cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075',
 'observations_p2':'c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3',
}

def numeric(value):
    try:
        x=float(str(value).replace(',','').strip())
    except (ValueError,TypeError): return None
    return x if math.isfinite(x) and 0<=x<1e10 else None

def source_month(row):
    try:
        y,m=int(row.get('year','')),int(row.get('month',''))
    except (ValueError,TypeError): return None
    return (y,m) if 1800<=y<=2026 and 1<=m<=12 else None

def annual_pairs(rows, sites):
    groups=defaultdict(list);ids=set();audit=Counter()
    for r in rows:
        if r['id'] in ids: raise ValueError('duplicate observation ID')
        ids.add(r['id'])
        if r['site_id'] not in sites: raise ValueError('orphan source site')
        try: year=int(r['season'])
        except (ValueError,TypeError): continue
        count=numeric(r.get('count'))
        if (r['species_id'] not in SPECIES or r['type']!='nests' or
            r['presence']!='1' or count is None or not 1890<=year<=2026): continue
        groups[r['site_id'],r['species_id'],year].append(r)
    audit['duplicate_site_species_seasons']=sum(len(v)>1 for v in groups.values())
    unique={k:v[0] for k,v in groups.items() if len(v)==1}
    annual=[]
    for (site,species,year),a in sorted(unique.items()):
        b=unique.get((site,species,year+1))
        if b is None: continue
        if a['citekey'].strip().lower() in UNKNOWN or a['citekey']!=b['citekey']:
            audit['source_changes_or_unknown']+=1;continue
        if a['vantage'].strip().lower() in UNKNOWN or a['vantage']!=b['vantage']:
            audit['method_changes_or_unknown']+=1;continue
        audit['matched_source_method_adjacent_pairs_before_positive_filter']+=1
        n0,n1=numeric(a['count']),numeric(b['count'])
        if n0<=0 or n1<=0:
            audit['nonpositive_pairs_excluded']+=1;continue
        annual.append(dict(site_id=site,species=species,region=sites[site]['region'],
          start=year,end=year+1,n_start=n0,n_end=n1,growth=math.log(n1/n0),
          citekey=a['citekey'],method=a['vantage'],source_id_start=a['id'],
          source_id_end=b['id'],calendar_start=source_month(a),calendar_end=source_month(b)))
    audit['positive_adjacent_pairs']=len(annual)
    return annual,dict(audit)

def direction(a,b):
    if a==0 or b==0:return 'one_or_both_unchanged'
    return ('a_up_' if a>0 else 'a_down_')+('b_up' if b>0 else 'b_down')

def match_species(annual,sp_a,sp_b):
    lookup={(x['site_id'],x['species'],x['start']):x for x in annual}
    if len(lookup)!=len(annual):raise ValueError('duplicate annual species pair')
    pairs=[];rejected=Counter()
    for a in annual:
        if a['species']!=sp_a:continue
        b=lookup.get((a['site_id'],sp_b,a['start']))
        if b is None:continue
        rejected['candidate_same_site_year']+=1
        if a['citekey']!=b['citekey']:
            rejected['different_source']+=1;continue
        if a['method']!=b['method']:
            rejected['different_method']+=1;continue
        known=bool(a['calendar_start'] is not None and a['calendar_end'] is not None
             and a['calendar_start']==b['calendar_start'] and a['calendar_end']==b['calendar_end'])
        pairs.append(dict(site_id=a['site_id'],region=a['region'],start=a['start'],end=a['end'],
          species_a=sp_a,species_b=sp_b,citekey=a['citekey'],method=a['method'],
          a_n_start=a['n_start'],a_n_end=a['n_end'],b_n_start=b['n_start'],b_n_end=b['n_end'],
          g_a=a['growth'],g_b=b['growth'],delta_log_ratio_b_over_a=b['growth']-a['growth'],
          direction=direction(a['growth'],b['growth']),same_known_calendar_months=known,
          source_a_start=a['source_id_start'],source_a_end=a['source_id_end'],
          source_b_start=b['source_id_start'],source_b_end=b['source_id_end']))
    return pairs,dict(rejected)

def summarize(rows):
    groups=defaultdict(list)
    for r in rows:groups[r['site_id']].append(r)
    site_stats=[]
    for site,rr in sorted(groups.items()):
        site_stats.append(dict(site_id=site,region=rr[0]['region'],n_intervals=len(rr),
          mean_delta=statistics.mean(r['delta_log_ratio_b_over_a'] for r in rr),
          fraction_b_outgrows_a=statistics.mean(r['delta_log_ratio_b_over_a']>0 for r in rr),
          mean_g_a=statistics.mean(r['g_a'] for r in rr),
          mean_g_b=statistics.mean(r['g_b'] for r in rr)))
    vals=[s['mean_delta'] for s in site_stats]
    by_region=defaultdict(list)
    for s in site_stats:by_region[s['region']].append(s['mean_delta'])
    loo=[statistics.mean(vals[:i]+vals[i+1:]) for i in range(len(vals))] if len(vals)>=3 else []
    return dict(n_intervals=len(rows),n_sites=len(groups),n_regions=len(by_region),
      n_distinct_start_years=len({r['start'] for r in rows}),
      equal_site_mean_log_ratio_change=statistics.mean(vals) if vals else None,
      median_site_mean_log_ratio_change=statistics.median(vals) if vals else None,
      site_weighted_fraction_b_outgrows_a=statistics.mean(s['fraction_b_outgrows_a'] for s in site_stats) if vals else None,
      site_weighted_mean_growth_a=statistics.mean(s['mean_g_a'] for s in site_stats) if vals else None,
      site_weighted_mean_growth_b=statistics.mean(s['mean_g_b'] for s in site_stats) if vals else None,
      raw_interval_direction_counts=dict(Counter(r['direction'] for r in rows)),
      sites_with_positive_mean_difference=sum(v>0 for v in vals),
      leave_one_site_out_mean_range=[min(loo),max(loo)] if loo else None,
      region_site_equal_means={k:statistics.mean(v) for k,v in sorted(by_region.items())},
      site_summaries=site_stats,causal_climate_or_competition_effect=False,
      inference='Descriptive observed-site contrast; no p value or inferential CI. Leave-one-site-out range is sensitivity, not confidence.')

def download_sources(folder):
    folder.mkdir(parents=True,exist_ok=True);raw={};receipts={}
    for key,url in SOURCES.items():
        req=urllib.request.Request(url,headers={'User-Agent':'mina-source-matched-species-growth/1.0'})
        with urllib.request.urlopen(req,timeout=90) as res: data=res.read(20_000_001)
        if not data or len(data)>20_000_000 or data.lstrip().startswith(b'<'):
            raise ValueError('invalid original source '+key)
        digest=hashlib.sha256(data).hexdigest()
        if digest!=EXPECTED_SHA[key]:raise ValueError('original source SHA drift '+key+': '+digest)
        (folder/(key+('.json' if key=='release' else '.csv'))).write_bytes(data)
        raw[key]=data;receipts[key]=dict(url=url,sha256=digest,bytes=len(data))
    return raw,receipts

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    raw,receipts=download_sources(args.out/'source')
    csvrows=lambda b:list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'),newline='')))
    release=json.loads(raw['release'])
    if release.get('version')!='5.0':raise ValueError('source version mismatch')
    s=csvrows(raw['sites']);obs=csvrows(raw['observations_p1'])+csvrows(raw['observations_p2'])
    if len(s)!=729 or len(obs)!=5487:raise ValueError('source scope drift')
    sites={r['site_id']:r for r in s}
    if len(sites)!=len(s):raise ValueError('duplicate source site')
    annual,audit=annual_pairs(obs,sites)
    report=dict(schema=1,status='exploratory_original_source_matched_species_growth',
      source_receipts=receipts,source_release=release,observation_columns=list(obs[0]),
      source_rows=len(obs),source_sites=len(sites),eligibility_audit=audit,
      positive_annual_panel=dict(n=len(annual),sites=len({r['site_id'] for r in annual}),
        regions=len({r['region'] for r in annual}),by_species=dict(Counter(r['species'] for r in annual))),
      primary_contrast='GEPE minus ADPE annual log nest-count change',contrasts={},
      limits=['Previously exposed dataset; exploratory, not independent confirmation.',
              'Known common citation and vantage do not guarantee identical field visits or detection.',
              'Positive endpoints only: excludes disappearance and establishment; conditional on observed persistence.',
              'Original site IDs are not verified physical islands; no new island mapping or snow exposure inferred.',
              'Relative change is not competition, replacement, dispersal, warming attribution or breeding success.',
              'Do not compare unmatched regional marginal trends as within-site contrasts.',
              'Existing 216 wild-cluster correction family remains unchanged.'])
    all_pairs=[]
    for a,b in CONTRASTS:
        paired,rejections=match_species(annual,a,b);all_pairs+=paired
        main_summary=summarize(paired)
        report['contrasts'][a+'__'+b]=dict(eligibility=rejections,all_source_matched=main_summary,
          known_calendar_months_only=summarize([r for r in paired if r['same_known_calendar_months']]),
          pre_2010=summarize([r for r in paired if r['start']<2010]),
          from_2010=summarize([r for r in paired if r['start']>=2010]))
    for name,rows in [('positive_annual_panel.csv',annual),('matched_species_annual_contrasts.csv',all_pairs)]:
        if rows:
            with (args.out/name).open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (args.out/'matched_species_growth_result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('MAPPPD_MATCHED_SPECIES_GROWTH_RESULT='+json.dumps(report,allow_nan=False),flush=True)

if __name__=='__main__':main()
