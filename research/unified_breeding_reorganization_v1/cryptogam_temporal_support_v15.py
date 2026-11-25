"""Read-only support audit: no ecological response model or inferred exposure."""
import io, json, math, sys, zipfile, hashlib
from pathlib import Path
from collections import Counter, defaultdict
from artifact_tool import Blob, SpreadsheetFile
ZIP_SHA='4799038f0fc80e6084bd6ec48854df069616cb32f8127ee498939ee04e89a4b5'
RELEASE_SHA='f68651176d46d585a7e1a255c0c68a705df954b76d71df7395bb8413fb21ef80'
XLSX_SHA='4528c80317f7f85642f70530ab9df0c3ace59c1c32f7ab94643edfc5711adb2c'
NUM=lambda x:isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def sha(x):return hashlib.sha256(x).hexdigest()
def coord(r):return (r[5],r[6])
def distance(a,b):
    lat,lon,la,lo=map(math.radians,(*a,*b));h=math.sin((lat-la)/2)**2+math.cos(lat)*math.cos(la)*math.sin((lon-lo)/2)**2
    return 6371008.8*2*math.asin(math.sqrt(max(0,min(1,h))))
def run(path,out):
    b=path.read_bytes();assert sha(b)==ZIP_SHA
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        md=json.loads(z.read('metadata.json'));assert md['doi']=='10.5281/zenodo.17112197' and md['metadata']['license']['id']=='cc-by-4.0'
        raw=z.read('How-the-small-host-the-small-v1.0.0.zip')
    assert sha(raw)==RELEASE_SHA and hashlib.md5(raw).hexdigest()=='91a307c56a14aa2a216501e759640275'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        names=[k for k in z.namelist() if k.endswith('.xlsx')];assert len(names)==1
        data=z.read(names[0])
    assert sha(data)==XLSX_SHA
    out.mkdir(parents=True,exist_ok=True);p=out/'original.xlsx';p.write_bytes(data)
    w=SpreadsheetFile.import_xlsx(Blob.load(str(p)))
    m=w.worksheets.get_item('Metadata').get_range('A1:C28').values
    a=w.worksheets.get_item('Data').get_range('A1:Z1324').values
    h,r=a[0],a[1:];assert len(r)==1323 and len(h)==26 and all(x[0] for x in r)
    assert h[:11]==['Sample_name','Year','Moss_Lichen_species','MossLichenVascular','Geography','Lat','Lon','N','Dry_weight','FMC','WHC']
    assert all(NUM(x[5]) and NUM(x[6]) and -90<=x[5]<=90 and -180<=x[6]<=180 for x in r)
    ids=Counter(x[0] for x in r);compound=Counter((x[4],x[1],x[0]) for x in r)
    campaign=[];host=[]
    for g in sorted({x[4] for x in r}):
        early=[x for x in r if x[4]==g and x[1]<=2017];recent=[x for x in r if x[4]==g and x[1]>=2023]
        ec={coord(x) for x in early};rc={coord(x) for x in recent}
        hs=sorted({x[2] for x in early}&{x[2] for x in recent})
        campaign.append({'region':g,'early_rows':len(early),'recent_rows':len(recent),'early_coordinate_count':len(ec),'recent_coordinate_count':len(rc),'exact_shared_coordinates':len(ec&rc),'shared_host_species':hs})
        for sp in hs:
            e=[x for x in early if x[2]==sp];l=[x for x in recent if x[2]==sp]
            ce={coord(x) for x in e};cl={coord(x) for x in l}
            nearest={c:min(distance(c,q) for q in ce) for c in cl}
            host.append({'region':g,'host':sp,'early_rows':len(e),'recent_rows':len(l),'early_distinct_coordinates':len(ce),'recent_distinct_coordinates':len(cl),'exact_shared_coordinates':len(ce&cl),'nearest_distance_m':min(nearest.values()),'recent_sample_rows_with_old_host_within_m':{str(t):sum(nearest[coord(x)]<=t for x in l) for t in [25,100,250]},'recent_distinct_coordinates_with_old_host_within_m':{str(t):sum(v<=t for v in nearest.values()) for t in [25,100,250]}})
    ret={'status':'NEW_ORIGINAL_SOURCE_VERIFIED_TEMPORAL_ANIMAL_PLANT_GATE_FAILED','doi':md['doi'],'license':md['metadata']['license']['id'],'source_pins':{'outer_zip':ZIP_SHA,'release_zip':RELEASE_SHA,'xlsx':XLSX_SHA},'rows':len(r),'columns':h,'unique_sample_names':len(ids),'sample_names_with_multiple_rows':sum(v>1 for v in ids.values()),'unique_region_year_sample_keys':len(compound),'repeated_region_year_sample_keys':sum(v>1 for v in compound.values()),'exact_duplicate_rows':len(r)-len({tuple(x) for x in r}),'host_type_counts':dict(Counter(x[3] for x in r)),'region_year_counts':[{'region':g,'year':y,'rows':n,'distinct_coordinates':len({coord(x) for x in r if (x[4],x[1])==(g,y)})} for (g,y),n in sorted(Counter((x[4],x[1]) for x in r).items())],'numeric_support':{h[i]:{'numeric':sum(NUM(x[i]) for x in r),'non_numeric':dict(Counter(str(x[i]) for x in r if not NUM(x[i])))} for i in range(5,26)},'campaigns':campaign,'host_support':host,'metadata_variables':[{'name':x[1],'description':x[2]} for x in m[2:] if x[1]],'explicit_local_animal_exposure_field':False,'same_plot_verified':False,'ecological_model_fitted':False,'limitations':['Early=all 2013–2017 rows and recent=2023–2024 rows as literal year labels, not independently verified new-sample provenance. Signy 2023 has 230 rows versus 210 newly collected samples reported in paper. No arbitrary selection of 210 rows.','Coordinates are nominal sample positions. Proximity radii 25/100/250m are diagnostics only, not a temporal plot crosswalk. No nearest-neighbor outcome matching.','Sample_name is not globally unique; even geography/year/name is not unique. No deduplication or treating repeated IDs as longitudinal samples.','Non-numeric #N/A is missing, not zero; no outcome values summarized.','No explicit animal-influence, transect identifier, repeat-plot ID or exact sampling date; host samples are not vegetation-cover measurements. No inference of penguin effects or plant changes.']}
    assert sum(z['exact_shared_coordinates'] for z in campaign)==0 and len(host)==7
    return ret
if __name__=='__main__':
    result=run(Path(sys.argv[1]),Path(sys.argv[2]));(Path(sys.argv[2])/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
