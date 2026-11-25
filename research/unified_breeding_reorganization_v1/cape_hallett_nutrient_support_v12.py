"""Read-only public-source support audit. No fitted plant response or inferred cell positions."""
from pathlib import Path
from collections import Counter, defaultdict
import sys, json, io, zipfile, hashlib, re, math, statistics
from artifact_tool import Blob, SpreadsheetFile
from pyproj import Transformer
from shapely.geometry import Polygon, Point
ZIP_SHA='38145b6acf43f6162b6f4a8b57c7bdf3a4c445597f09617e623f211d4a38ffeb'
INNER_SHA='46eef5d432515a20426a020baa588ce523d7d3169a4e4bf1b02d7031034ff764'
XLSX_SHA='25c573a356bec6df0ff81a0cdec6e8f99c579acc704f2988a3ca65ddd3280ad9'
# Official ASPA106 (2021) Table 3; zone rather than inferred exact plot.
CORNERS=[(170+14/60+4.012/3600,-(72+19/60+11.219/3600)),(170+13/60+58.341/3600,-(72+19/60+10.43/3600)),(170+13/60+51.901/3600,-(72+19/60+14.479/3600)),(170+13/60+57.338/3600,-(72+19/60+15.299/3600))]
T=Transformer.from_crs(4326,32759,always_xy=True)
ZONE=Polygon([T.transform(*p) for p in CORNERS]);assert ZONE.is_valid
num=lambda v:isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def coord(s):
    m=re.fullmatch(r'\s*(\d+)°\s*([\d.]+)[´′\']\s*S,\s*(\d+)°\s*([\d.]+)[´′\']\s*E\s*',s)
    if not m:raise ValueError('unknown coordinate '+s)
    a,b,c,d=map(float,m.groups());return c+d/60,-(a+b/60)
def geo(s):
    p=Point(T.transform(*coord(s)));return {'inside_zone':ZONE.covers(p),'distance_to_zone_m':ZONE.distance(p),'distance_to_zone_centroid_m':ZONE.centroid.distance(p)}
def read(path,outdir):
    b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==ZIP_SHA
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None;raw=z.read('original_source.zip')
    assert hashlib.sha256(raw).hexdigest()==INNER_SHA
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None; x=[n for n in z.namelist() if n.endswith('.xlsx')];assert len(x)==1;data=z.read(x[0])
    assert hashlib.sha256(data).hexdigest()==XLSX_SHA
    p=outdir/'nutrient_original.xlsx';p.write_bytes(data)
    return SpreadsheetFile.import_xlsx(Blob.load(str(p)))
def run(path,outdir):
    outdir.mkdir(parents=True,exist_ok=True);w=read(path,outdir)
    rows=w.worksheets.get_item('Sheet1').get_range('A1:F219').values
    assert rows[13][:3]==['Sample No','Species','Location ']
    current=None;chem=[];stations={};other=[]
    for i,r in enumerate(rows[14:],15):
        if r[0] is None and isinstance(r[1],str) and isinstance(r[2],str) and re.match(r'^Sites? \d',r[1]):
            k=re.match(r'^Sites? (\d+(?:-\d+)?):',r[1]).group(1);current=(k,r[1].strip(),r[2]);g=geo(r[2]);stations[k]=g;continue
        if current and isinstance(r[1],str) and any(num(x) for x in r[3:]):
            k,label,c=current
            if r[1].strip() in ('Xanthomendosa borealis','Usnea sphacelata','Umbilicaria decussata','Umbilicaria deccusata'):
                chem.append({'site':k,'label':label,'species':{'Umbilicaria deccusata':'Umbilicaria decussata'}.get(r[1].strip(),r[1].strip()),'n':r[3] if num(r[3]) else None,'p':r[4] if num(r[4]) else None,'d15n':r[5] if num(r[5]) else None})
            else:other.append(r[1].strip())
    assert len(chem)==140
    counts=Counter((r['site'],r['species']) for r in chem);ln=sorted({r['site'] for r in chem});lc={k:stations[k] for k in ln}
    nh=w.worksheets.get_item('Sheet4').get_range('A1:S18').values
    periods=[(2,'2004-12-08/14'),(5,'2005-01-08/24'),(8,'2005-12-26/2006-01-10'),(12,'2006-01-11/17'),(16,'2006-01-17/23')]
    ar=[]
    for r in nh[4:15]:
        assert isinstance(r[0],str) and isinstance(r[1],str)
        k=re.match(r'^Site (\d+):',r[0]).group(1);g=geo(r[1]); pr={}
        for j,name in periods:
            values=[v for v in r[j:j+3] if num(v)]
            if values:pr[name]={'replicates':len(values),'mean_ug_m3':statistics.mean(values)}
        ar.append({'site':k,**g,'periods':pr})
    assert len(ar)==11
    aids={a['site'] for a in ar};both=sorted(aids&set(ln))
    groups=[]
    for (k,s),n in sorted(counts.items()):
        v=[r for r in chem if r['site']==k and r['species']==s];d=[r['d15n'] for r in v if r['d15n'] is not None];nv=[r['n'] for r in v if r['n'] is not None];pv=[r['p'] for r in v if r['p'] is not None]
        groups.append({'site':k,'species':s,'n_records':n,'n_delta15N':len(d),'mean_delta15N':statistics.mean(d) if d else None,'mean_percent_N':statistics.mean(nv) if nv else None,'mean_percent_P':statistics.mean(pv) if pv else None,**lc[k]})
    out={'status':'PUBLIC_NUTRIENT_SOURCE_VERIFIED_NO_EXACT_PLOT_MEASUREMENT','source_doi':'10.5285/eba81a75-2e49-4063-92c8-97c26f300ce5','source_paper_doi':'10.1007/s10533-014-0042-7','zip_sha256':ZIP_SHA,'inner_sha256':INNER_SHA,'xlsx_sha256':XLSX_SHA,'lichen_chemistry':{'records':len(chem),'species_counts':dict(Counter(r['species'] for r in chem)),'site_count':len(ln),'species_site_groups':len(groups),'sites_inside_restricted_zone':sum(x['inside_zone'] for x in lc.values()),'closest_site_to_zone_m':min(x['distance_to_zone_m'] for x in lc.values()),'groups':groups},'ammonia':{'site_count':len(ar),'observed_site_periods':sum(len(x['periods']) for x in ar),'replicate_measurements':sum(y['replicates'] for x in ar for y in x['periods'].values()),'sites_inside_restricted_zone':sum(x['inside_zone'] for x in ar),'closest_site_to_zone_m':min(x['distance_to_zone_m'] for x in ar),'sites':ar},'same_literal_site_ids_chemistry_and_ammonia':both,'other_chemistry_labels':dict(Counter(other)),'limits':['Original workbook literal Umbilicaria deccusata mapped to Umbilicaria decussata using source paper species label; no numeric values changed. Xanthomendosa borealis retained as literal workbook spelling.','Same literal station ID is not proof of simultaneous observations or shared specimen. Locations rounded to 0.01 arc-minute and describe stations, not every specimen footprint.','No station inside official restricted zone; no assignment of an exact measurement to vegetation grid.','Original 2004-06 source demonstrates a spatial nutrient pathway in published study; not our new biological effect or a temporal exposure series.','Ammonia height note at Sheet4 row 18 is retained as source caveat: some entries are 2.5m and not comparable without formatting/measurement review. No regression or mixing model fit.']}
    return out
if __name__=='__main__':
    r=run(Path(sys.argv[1]),Path(sys.argv[2]));(Path(sys.argv[2])/'nutrient_support.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:({a:b for a,b in v.items() if a not in ('groups','sites')} if isinstance(v,dict) else v) for k,v in r.items()},ensure_ascii=False))
