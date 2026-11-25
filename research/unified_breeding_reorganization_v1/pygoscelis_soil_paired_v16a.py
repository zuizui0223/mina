"""V16a descriptive paired soil comparison on exact source site/date. No causal fit."""
import csv, hashlib, io, itertools, json, math, re, statistics, sys, zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
ZIP='6b364eeb628fd57b1221b472c715dbdc2d5bba4a6153193bfcdfd0362e3fc513'
PINS={'Methods.txt':'0a2430c1943387e5369159ea950774f2','Pygoscelis_metadata.csv':'b58d6e6b476c98afeb9f4e75f8f520fe','Pygoscelis_PP.csv':'fa57915e1d1253a6eeac36e70579ccf9'}
ORDER=['Pygoscelis adeliae','Pygoscelis antarcticus','Pygoscelis papua']
VARS=['CH (%)','pH','CO (%)','N-NH4 (mg/kg)','NO3-N (mg/kg)','P-PO4 (mg/kg)']
EXPECTED={'Biscoe Point':(0,2),'Kopaitic Island':(0,1,2),'Penguin Island':(0,1),'George Point':(1,2),'Hanna Point':(1,2)}
def sha(b):return hashlib.sha256(b).hexdigest()
def distance(a,b):
    x,y,u,v=map(math.radians,(*a,*b));h=math.sin((x-u)/2)**2+math.cos(x)*math.cos(u)*math.sin((y-v)/2)**2
    return 6371008.8*2*math.asin(math.sqrt(max(0,min(1,h))))
def parse(raw):
    a=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter=';'));assert len(a)==271
    assert all(not any(v.strip() for v in x.values()) for x in a if not x['Sample'].strip())
    b=[x for x in a if x['Sample'].strip()];assert len(b)==87 and len({x['Sample'] for x in b})==87
    return b
def run(path):
    b=path.read_bytes();assert sha(b)==ZIP
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        raw={k:z.read(k) for k in PINS}
        assert all(hashlib.md5(raw[k]).hexdigest()==v for k,v in PINS.items())
        meta=json.loads(z.read('metadata.json'));assert meta['doi']=='10.5281/zenodo.17742676' and meta['metadata']['license']['id']=='cc-by-4.0'
    m=parse(raw['Pygoscelis_metadata.csv']);y=parse(raw['Pygoscelis_PP.csv']);assert list(y[0])==['Sample',*VARS]
    d={x['Sample']:x for x in y};assert set(d)=={x['Sample'] for x in m}
    groups=defaultdict(list)
    for x in m:
        k=x['Sample'];assert re.fullmatch(r'[A-Z]+[123]',k);groups[k[:-1]].append(x)
    assert len(groups)==29
    bysite=defaultdict(dict);units=[]
    for k,rows in sorted(groups.items()):
        assert {x['Sample'][-1] for x in rows}==set('123') and len(rows)==3
        assert len({tuple((a,b) for a,b in x.items() if a!='Sample') for x in rows})==1
        x=rows[0];sp=ORDER.index(x['Penguin species']);site=x['Site'].strip();day=datetime.strptime(x['Date'],'%d-%m-%Y').date().isoformat();coords=(float(x['Latitude']),float(x['Longitude']));assert -90<=coords[0]<=90 and -180<=coords[1]<=180
        v={}
        for n in VARS:
            rawvals=[d[q['Sample']][n] for q in rows]
            vs=[float(z) for z in rawvals if z!='n.d.'];assert all(math.isfinite(z) and z>=0 for z in vs)
            v[n]=statistics.mean(vs) if len(vs)==3 else None
        assert sp not in bysite[site,day]
        a={'unit':k,'species':sp,'site':site,'date':day,'coords':coords,'mean':v};units.append(a);bysite[site,day][sp]=a
    assert Counter(u['species'] for u in units)=={0:12,1:6,2:11};assert len(bysite)==23
    mixed={(s,t):v for (s,t),v in bysite.items() if len(v)>1};assert {s:tuple(sorted(v)) for (s,t),v in mixed.items()}==EXPECTED
    pairs=[]
    for (s,t),v in sorted(mixed.items()):
        for i,j in itertools.combinations(sorted(v),2):
            a,b=v[i],v[j];res={}
            for n in VARS:
                u,w=a['mean'][n],b['mean'][n]
                res[n]={'earlier_species_mean':u,'later_species_mean':w,'difference':w-u if u is not None and w is not None else None,'ratio':w/u if n!='pH' and u is not None and w is not None and u>0 and w>0 else None}
            pairs.append({'site':s,'date':t,'pair':[i,j],'nominal_distance_m':distance(a['coords'],b['coords']),'values':res})
    assert len(pairs)==7
    summary=[]
    for pair in [(0,1),(0,2),(1,2)]:
        rows=[x for x in pairs if x['pair']==list(pair)];out={}
        for n in VARS:
            z=[x['values'][n] for x in rows if x['values'][n]['difference'] is not None];ds=[x['difference'] for x in z];rs=[x['ratio'] for x in z]
            out[n]={'n_complete_sites':len(z),'mean_difference':statistics.mean(ds) if ds else None,'min_difference':min(ds) if ds else None,'max_difference':max(ds) if ds else None,'positive':sum(v>0 for v in ds),'negative':sum(v<0 for v in ds),'zero':sum(v==0 for v in ds),'geomean_ratio':math.exp(statistics.mean(math.log(r) for r in rs)) if rs and all(r is not None for r in rs) else None}
        summary.append({'pair':list(pair),'sites':len(rows),'values':out})
    return {'status':'EXECUTED_DESCRIPTIVE_LOCAL_SOIL_CONTRASTS','source_doi':'10.5281/zenodo.17742676','zip_sha256':ZIP,'member_sha256':{k:sha(v) for k,v in raw.items()},'species_order':ORDER,'sample_rows':87,'groups':29,'site_dates':23,'mixed_site_dates':5,'n_non_numeric_by_field':{n:sum(q[n]=='n.d.' for q in y) for n in VARS},'n_complete_groups_by_field':{n:sum(q['mean'][n] is not None for q in units) for n in VARS},'pairs':pairs,'summary':summary,'limits':['Actual source 87 rows / 29 triplicates differs from described 84 / 28; no arbitrary row removal.','Exact trimmed source site and date only, not identical soils or shared colony footprint. Triplicates aggregated once.','Source n.d. preserved as missing/nonquantified, not zero; no reported detection limit used. Complete triplicate endpoints only.','Each contrast uses 2–3 sites; shared sites and contrasts are dependent. No significance or generalized species effect.','Concentrations and pH are soil properties, not deposition flux, plant response, historical change, or causal penguin effect.']}
if __name__=='__main__':
    out=run(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
