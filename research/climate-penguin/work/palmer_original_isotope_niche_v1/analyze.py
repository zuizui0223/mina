"""Independent Palmer nesting-island isotope audit, not a warming response.

Gorman et al. 2014 original data via palmerpenguins. The isotope signature
during egg laying is NOT Signy chick-rearing stomach fish wet-mass.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"outputs"
RAW_SHA="ba99fbd527f0bb983b3d9615ef5c81a5917ab7d9"
LOC_SHA="1c5214ab355d3d2e19bc33e5de4693fa21f38731"
ICE_SHA="4fcea71c2d8b1069b6ad143f6522061ed434daf5"
ISLANDS={"Biscoe":(-64-48/60,-63-46/60),"Dream":(-64-43/60,-64-13/60),
         "Torgersen":(-64-46/60,-64-4/60)}
SEXES=("FEMALE","MALE")
def get(path,sha):
    path=Path(path)
    raw=path.read_bytes()
    found=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if found!=sha:raise ValueError("Frozen source blob changed "+str(path))
    with path.open(newline="",encoding="utf-8-sig") as fh:return list(csv.DictReader(fh))
def mean(x):return sum(x)/len(x)
def numeric(x):
    try:return float(x) if math.isfinite(float(x)) else None
    except (TypeError,ValueError):return None
def dist(a,b):
    a,b,c,d=map(math.radians,(a[0],a[1],b[0],b[1]))
    x=math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 12742*math.asin(min(1,math.sqrt(x)))
def diskoverlap(d,r=100):
    if d>=2*r:return 0.
    return (2*r*r*math.acos(d/(2*r))-.5*d*math.sqrt(4*r*r-d*d))/(math.pi*r*r)
def save(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as fh:
        out=csv.DictWriter(fh,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
def run(rawpath,out):
    orig=get(rawpath,RAW_SHA)
    if len(orig)!=344:raise ValueError("Original 344 rows changed")
    isotopes=[]; sexknown=[]
    for row in orig:
        year=int(row["Date Egg"][:4])
        if year!=2000+int(row["studyName"][3:5]) or year not in (2007,2008,2009):
            raise ValueError("Season year mismatch")
        if row["Stage"]!="Adult, 1 Egg Stage":raise ValueError("Breeding stage mismatch")
        sp=row["Species"].split()[0]; island=row["Island"]
        if sp not in ("Adelie","Chinstrap","Gentoo") or island not in ISLANDS:raise ValueError("Species/island mismatch")
        n,c=numeric(row["Delta 15 N (o/oo)"]),numeric(row["Delta 13 C (o/oo)"])
        if n is None or c is None:continue
        value=dict(species=sp,island=island,year=year,sex=row["Sex"],delta15n=n,delta13c=c,
                   egg_date=row["Date Egg"])
        isotopes.append(value)
        if value["sex"] in SEXES:sexknown.append(value)
    if (len(isotopes),len(sexknown))!=(330,324):raise ValueError("Original isotope/sex coverage changed")
    groups=defaultdict(list)
    for x in sexknown:groups[(x["island"],x["year"],x["species"])].append(x)
    if len(groups)!=15:raise ValueError("Expected 15 island-year-species groups")
    centers=[]
    for (island,year,sp),a in sorted(groups.items()):
        centers.append(dict(island=island,year=year,species=sp,n=len(a),
             male=sum(x["sex"]=="MALE" for x in a),female=sum(x["sex"]=="FEMALE" for x in a),
             n15_permil=mean([x["delta15n"] for x in a]),
             c13_permil=mean([x["delta13c"] for x in a]),
             median_egg_doy=statistics.median(datetime.date.fromisoformat(x["egg_date"]).timetuple().tm_yday for x in a)))
    contrasts=[]
    for island,sp in (("Biscoe","Gentoo"),("Dream","Chinstrap")):
        for year in (2007,2008,2009):
            a,b=groups[(island,year,"Adelie")],groups[(island,year,sp)]
            per={}
            for sex in SEXES:
                aa=[x for x in a if x["sex"]==sex];bb=[x for x in b if x["sex"]==sex]
                if min(len(aa),len(bb))<5:raise ValueError("Insufficient sex-specific sample")
                per[sex]=(mean([x["delta15n"] for x in bb])-mean([x["delta15n"] for x in aa]),
                          mean([x["delta13c"] for x in bb])-mean([x["delta13c"] for x in aa]))
            contrasts.append(dict(island=island,year=year,reference="Adelie",compared=sp,
              n_ad=len(a),n_other=len(b),
              n15_difference=mean([x["delta15n"] for x in b])-mean([x["delta15n"] for x in a]),
              c13_difference=mean([x["delta13c"] for x in b])-mean([x["delta13c"] for x in a]),
              sexbalanced_n15_difference=mean([per[s][0] for s in SEXES]),
              sexbalanced_c13_difference=mean([per[s][1] for s in SEXES]),
              male_n15_difference=per["MALE"][0],female_n15_difference=per["FEMALE"][0],
              median_egg_date_gap_days=statistics.median(datetime.date.fromisoformat(x["egg_date"]).toordinal() for x in b)-
                                       statistics.median(datetime.date.fromisoformat(x["egg_date"]).toordinal() for x in a)))
    macro=[r for r in get(ROOT/"climate_penguin/daily_ice_locations.csv",LOC_SHA) if r["cohort"]=="macro_40"]
    ice=get(ROOT/"climate_penguin/macro_monthly_seaice_1991_2020.csv",ICE_SHA)
    if len(macro)!=40 or len(ice)!=9600:raise ValueError("Source physical geography drift")
    im={}
    for r in ice:
        if r["inner_km"]!="0" or r["complete_month"]!="True":continue
        key=(r["site_id"],int(r["year"]),int(r["month"]))
        if key in im:raise ValueError("Duplicate satellite observation")
        im[key]=float(r["sic_mean"])
    proxies=[];islandToSite={}
    for island,coords in ISLANDS.items():
        km,site=min((dist(coords,(float(r["latitude"]),float(r["longitude"]))),r["site_id"]) for r in macro)
        if km>10:raise ValueError("Marine proxy >10km")
        islandToSite[island]=site
        for year in (2007,2008,2009):
            s=[im[(site,year,m)] for m in (8,9,10,11)]
            proxies.append(dict(island=island,year=year,source_site=site,loc_distance_km=km,
                  source_nearshore_september_sic_pct=s[1],source_aug_nov_sic_pct=mean(s)))
    if islandToSite!={"Biscoe":"BISC","Dream":"LITC","Torgersen":"LITC"}:
        raise ValueError("Marine proxy support changed")
    bs=[v for v in contrasts if v["island"]=="Biscoe"]
    ds=[v for v in contrasts if v["island"]=="Dream"]
    if not(all(x["sexbalanced_n15_difference"]<0 for x in bs) and
        ds[0]["sexbalanced_n15_difference"]<0 and all(x["sexbalanced_n15_difference"]>0 for x in ds[1:])):
        raise ValueError("Original isotope year contrast changed")
    if not(all(x["sexbalanced_c13_difference"]<0 for x in bs) and
            all(x["sexbalanced_c13_difference"]>0 for x in ds)):
        raise ValueError("Original carbon isotope signs changed")
    bas=[("Biscoe","Dream"),("Biscoe","Torgersen"),("Dream","Torgersen")]
    summary={"n_original_records":len(orig),"n_two_isotopes":len(isotopes),
      "n_two_isotopes_and_sex":len(sexknown),"n_species_island_year":len(centers),
      "n_same_island_year_pairs":len(contrasts),"n_islands":3,"n_distinct_nearshore_SIC_proxy_codes":len(set(islandToSite.values())),
      "marine_proxy_by_island":islandToSite,
      "theoretical_full_100km_circle_overlap":{a+"_"+b:diskoverlap(dist(ISLANDS[a],ISLANDS[b])) for a,b in bas},
      "signy_ice_to_stomach_fish_gap_independently_replicated":False,
      "palmer_isotope_proxy_is_stomach_fish_fraction":False,
      "source_git_blob_SHA":RAW_SHA,"climate_location_SHA":LOC_SHA,"satellite_ice_SHA":ICE_SHA,
      "units":"RBC delta15N/delta13C per mil, egg-stage, not consumed prey biomass",
      "scope":"Original published Gorman 2014 data; exploratory same-island and same-year species differences, not a newly discovered climatic effect",
      "caveat":"Only 3 seasons, only 2 paired islands, species pair confounded with island, same broad nearshore SIC reference reused for Dream/Torgersen"}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    save(out/"isotope_centroids.csv",centers)
    save(out/"isotope_within_island_pair_year.csv",contrasts)
    save(out/"island_sic_proxy_support.csv",proxies)
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    z=p.parse_args();print(json.dumps(run(z.source,z.out),ensure_ascii=False))
