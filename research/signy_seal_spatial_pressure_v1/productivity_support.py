"""BCO-DMO productivity × native winter-polynya support audit only, no response fit.
Usage: python productivity_support.py /path/to/artifact_directory output.json
"""
import csv, hashlib, io, json, math, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
PINS={14935924098:'fbeeffce21a8323f8f9afa75986b6d3cc05d7d66053ee872a43a39d7251b0e06',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'}
RAW_PIN='1f1f7c0b6aeb4d9f4ae5288edea9b668666fcbc25bfa93c607229ec9d317c6e3'
SPECIES={'Pygoscelis adeliae':'ADPE','Pygoscelis antarcticus':'CHPE','Pygoscelis papua':'GEPE'}
YEARS=set(range(2004,2011))|set(range(2013,2021))
# 5-km radius for listing possible atlas locations ONLY (no automatic match).
RADIUS_KM=5.0
# Direct nominal candidates from prior source names, not colony footprint proof.
NOMINAL={'Cape Shirreff':'SHIR','Pointe Geologie':'PGEO'}

def read(root,i,member,raw_pin=None):
    b=(root/f'github-actions-artifact-{i}.zip').read_bytes()
    assert hashlib.sha256(b).hexdigest()==PINS[i], i
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        raw=z.read(member)
    if raw_pin:assert hashlib.sha256(raw).hexdigest()==raw_pin
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
def value(s):
    try:
        v=float(s);return v if math.isfinite(v) else None
    except (TypeError,ValueError):return None
def distance(lat,lon,r):
    a,b,c,d=map(math.radians,[lat,lon,float(r['latitude']),float(r['longitude'])]);t=math.sin((a-c)/2)**2+math.cos(a)*math.cos(c)*math.sin((b-d)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(max(0,min(1,t))))
def run(root):
    b=read(root,14935924098,'985565_v1_global_seabird_breeding_success.csv',RAW_PIN)
    a=read(root,13669533413,'panantarctic_595_site_inventory.csv')
    n=read(root,13669533413,'source_observed_2456.csv')
    p=read(root,14926710177,'winter_595.csv')
    m=read(root,13829236358,'original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv')
    assert (len(b),len(a),len(n),len(p),len(m))==(6602,595,2456,21420,16464)
    assert len({x['site_id'] for x in a})==595
    assert len({(r['site_id'],r['species'],r['season']) for r in n})==2456
    assert len({(x['site_id'],x['radius_km'],x['season']) for x in p})==21420
    assert len({(r['site_id'],r['year']) for r in m})==16464
    P=defaultdict(set); M=defaultdict(set); N=defaultdict(set)
    for r in p:
        y=int(r['season']); assert 2003<=y<=2020
        pv=value(r['direct_DEEPAA_coastal_polynya_fraction'])
        if y not in YEARS:
            assert pv is None and value(r['n_valid_months']) is None
            continue
        assert value(r['n_valid_months'])==5 and pv is not None and 0<=pv<=1
        if r['radius_km'] in ('100','100.0'):P[r['site_id']].add(y)
    assert len(P)==595 and all(v==YEARS for v in P.values())
    for r in m:
        if int(r['original_source_4_GLORYS_months'])==4 and int(r['original_source_4_OSISAF_months'])==4 and all(value(r[k]) is not None for k in ('mean_source_SIC_pp','mean_GLORYS_salinity','mean_GLORYS_thetao_C')):M[r['site_id']].add(int(r['year']))
    assert len(M)==588 and all(v==set(range(1993,2021)) for v in M.values())
    for r in n:N[r['site_id'],r['species']].add(int(r['season']))
    q=[r for r in b if r['ScientificName_accepted'] in SPECIES]
    assert len(q)==494 and len({(r['site'],r['ScientificName_accepted'],r['year']) for r in q})==494
    groups=defaultdict(list)
    for r in q:groups[r['site'],SPECIES[r['ScientificName_accepted']]].append(r)
    rows=[]
    for (site,sp),g in sorted(groups.items()):
        coords={(float(r['latitude']),float(r['longitude'])) for r in g};assert len(coords)==1
        lat,lon=next(iter(coords));valid={int(r['year']) for r in g if value(r['breeding_success']) is not None and value(r['breeding_success'])>=0}
        yr={int(r['year']) for r in g};assert len(yr)==len(g)
        outside=lat>-60
        near=[] if outside else sorted([(distance(lat,lon,r),r) for r in a if distance(lat,lon,r)<=RADIUS_KM],key=lambda z:(z[0],z[1]['site_id']))
        cand=[]
        for dist,r in near:
            k=r['site_id'];hy=valid&P[k]&M[k];ny=hy&N[k,sp]
            cand.append({'site_id':k,'site_name':r['site_name'],'region':r['source_region'],'distance_km':dist,'nominal_name_candidate':NOMINAL.get(site)==k,'winter_and_hydro_years':sorted(hy),'winter_hydro_and_observed_nest_years':sorted(ny),'n_winter_hydro_years':len(hy),'n_joint_nest_years':len(ny)})
        rec={'site':site,'species':sp,'latitude':lat,'longitude':lon,'n_source_rows':len(g),'n_valid_productivity_years':len(valid),'missing_or_invalid_productivity_years':sorted(yr-valid),'first_year':min(yr),'last_year':max(yr),'n_valid_sample_size_records':sum(value(r['n']) is not None and value(r['n'])>0 for r in g),'outside_native_antarctic_domain':outside,'valid_productivity_in_frozen_winter_years':sorted(valid&YEARS),'n_candidates_within_5km':len(cand),'candidate_coverage':cand,'independent_event_lineage_verified':False,'spatial_footprint_verified':False}
        rows.append(rec)
    antarctic=[x for x in rows if not x['outside_native_antarctic_domain']]
    out={'status':'STRUCTURAL_RESPONSE_BRIDGE_AUDIT_ONLY','publisher_doi':'10.26008/1912/bco-dmo.985565.1','input_artifact_sha256':PINS,'raw_csv_sha256':RAW_PIN,'winter_years':sorted(YEARS),'all_pygoscelis_rows':len(q),'all_species_site_series':len(rows),'all_named_sites':len({x['site'] for x in rows}),'antarctic_rows':sum(x['n_source_rows'] for x in antarctic),'antarctic_valid_productivity_rows':sum(x['n_valid_productivity_years'] for x in antarctic),'antarctic_series':len(antarctic),'antarctic_named_sites':len({x['site'] for x in antarctic}),'antarctic_series_with_10plus_candidate_winter_years':sum(any(c['n_winter_hydro_years']>=10 for c in x['candidate_coverage']) for x in antarctic),'antarctic_series_with_10plus_candidate_joint_nest_years':sum(any(c['n_joint_nest_years']>=10 for c in x['candidate_coverage']) for x in antarctic),'site_series':rows,'limitations':['No response magnitude, trend or ecological coefficient fitted.','BCO-DMO year is austral breeding season start (publisher metadata).','5-km proximity is candidate coverage only, not an accepted site crosswalk.','Productivity is offspring per nesting female; not abundance or annual survival.','BAS/NOAA monitoring may overlap; no per-row original source ID.','Subantarctic observations excluded from native Antarctic polynya domain; no zero fill.','MAPPPD nesting and productivity survey footprints may differ, even for nominal names.'],'ecological_fit':False,'independence_established':False}
    return out
if __name__=='__main__':
    r=run(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='site_series'},ensure_ascii=False,indent=2))
    for x in r['site_series']:
        if not x['outside_native_antarctic_domain']:
            print(x['site'],x['species'], 'years',len(x['valid_productivity_in_frozen_winter_years']), 'candidates',[(c['site_id'],round(c['distance_km'],3),c['n_winter_hydro_years'],c['n_joint_nest_years']) for c in x['candidate_coverage']])
