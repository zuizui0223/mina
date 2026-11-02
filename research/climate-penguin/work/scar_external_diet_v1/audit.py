"""Source-grain audit of 2023 SCAR GloBI pinned diet mirror, no effect fishing."""
import argparse,csv,hashlib,json,math,re,collections
from pathlib import Path
BLOB="418c4495ad27fe2f62e96305525019fd2fee905f"
COMMIT="1856664248be16b9dcee9ba56d2b23d87f3d9cd1"
def valid(v):return v is not None and str(v).strip().lower() not in ("","na","nan","null","unknown")
def num(v):
    try:return float(v) if math.isfinite(float(v)) else None
    except (TypeError,ValueError):return None
def species(r):
    s=" ".join(str(r.get(k,"")) for k in ("predator_name","predator_name_original","predator_group","predator_common_name")).lower()
    for val,sp in (("pygoscelis adeliae","Adelie"),("pygoscelis antarcticus","Chinstrap"),("pygoscelis papua","Gentoo"),
                   ("adélie","Adelie"),("adelie","Adelie"),("chinstrap","Chinstrap"),("gentoo","Gentoo")):
        if val in s:return sp
    return None
def year(r):
    found=[]
    for k,v in r.items():
        if k.lower() in ("year","year_start","sample_year","sampling_year","date","date_start","date_end","sample_date","start_date","end_date") and valid(v):
            found.extend(int(x) for x in re.findall(r"(?<!\d)(?:18\d{2}|19\d{2}|20\d{2})(?!\d)",str(v)))
    return found[0] if found and len(set(found))==1 else None
def group(r):
    s=" ".join(str(r.get(k,"")) for k in ("prey_name","prey_group","prey_group_soki","prey_worms_class","prey_worms_phylum")).lower()
    if any(x in s for x in ("actinopterygii","fish","teleost","myctophi","nototheni","channichthy","osteichth")):return "fish"
    if any(x in s for x in ("crustacea","euphausi","krill","amphipod","copepod","mysid")):return "crustacean"
    return None
def save(path,rows,keys):
    with path.open("w",newline="",encoding="utf8") as h:
        w=csv.DictWriter(h,fieldnames=keys);w.writeheader();w.writerows(rows)
def main(source,out):
    b=source.read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
    if sha!=BLOB:raise ValueError("source blob drift: "+sha)
    data=csv.DictReader(b.decode("utf-8-sig").splitlines())
    fields=data.fieldnames
    if "fraction_diet_by_weight" not in fields:raise ValueError("weight measure not in original schema")
    n=0;target=[];format_counts=collections.Counter()
    locfields=[k for k in fields if any(z in k.lower() for z in ("site","location","island","latitude","longitude"))]
    for r in data:
        n+=1;sp=species(r)
        if not sp:continue
        mass=num(r.get("fraction_diet_by_weight"))
        loc="|".join(str(r.get(k,"")).strip() for k in locfields if valid(r.get(k)))
        f=group(r)
        id=str(r.get("predator_sample_id","")).strip()
        key=str(r.get("source_id","")).strip()
        typ="weight" if mass is not None else "occurrence" if num(r.get("fraction_occurrence")) is not None else "other"
        format_counts[typ]+=1
        target.append(dict(species=sp,source_id=key,year=year(r),location=loc,
                           prey=f,mass_fraction=mass,sample=id,format=typ))
    G=collections.defaultdict(list)
    for r in target:G[(r["source_id"],r["species"],r["year"],r["location"])].append(r)
    panels=[]
    for (source_id,sp,y,loc),a in sorted(G.items(),key=lambda kv:str(kv[0])):
        panels.append(dict(source_id=source_id,species=sp,year=y,location=loc[:250],
            n_diet_rows=len(a),n_weight=sum(t["mass_fraction"] is not None for t in a),
            n_fish_weight=sum(t["prey"]=="fish" and t["mass_fraction"] is not None for t in a),
            n_crust_weight=sum(t["prey"]=="crustacean" and t["mass_fraction"] is not None for t in a),
            n_sample_ids=len({t["sample"] for t in a if valid(t["sample"])}),
            n_weight_gt_one=sum(t["mass_fraction"] is not None and t["mass_fraction"]>1 for t in a)))
    pair=collections.defaultdict(set)
    for p in panels:
        if p["year"] is not None and p["n_fish_weight"] and p["n_crust_weight"]:
            pair[(p["source_id"],p["year"],p["location"])].add(p["species"])
    same=[dict(source_id=k[0],year=k[1],location=k[2],species=",".join(sorted(v)),n_species=len(v))
          for k,v in pair.items() if len(v)>=2]
    sums=collections.defaultdict(list)
    for p in panels:sums[p["source_id"]].append(p)
    source_rows=[]
    for sid,a in sorted(sums.items()):
        source_rows.append(dict(source_id=sid,species=",".join(sorted({x["species"] for x in a})),
            n_years=len({x["year"] for x in a if x["year"] is not None}),
            years=";".join(str(y) for y in sorted({x["year"] for x in a if x["year"] is not None})),
            n_site_species_year=len(a),n_rows=sum(x["n_diet_rows"] for x in a),
            n_fish_weight=sum(x["n_fish_weight"] for x in a),
            n_crust_weight=sum(x["n_crust_weight"] for x in a),
            n_sample_ids=sum(x["n_sample_ids"] for x in a)))
    out.mkdir(parents=True,exist_ok=True)
    save(out/"source_support.csv",source_rows,list(source_rows[0]))
    save(out/"site_species_year_support.csv",panels,list(panels[0]))
    save(out/"possible_species_pairs.csv",same,["source_id","year","location","species","n_species"])
    results=dict(status="support_only_not_validated_signy_replication",original_rows=n,
        source_git_blob=sha,source_sha256=hashlib.sha256(b).hexdigest(),source_commit=COMMIT,
        original_zenodo="10.5281/zenodo.7796465",focal_species_rows=len(target),
        focal_by_species=dict(collections.Counter(x["species"] for x in target)),
        fields=fields,location_fields=locfields,measure_types=dict(format_counts),
        n_source_ids=len(source_rows),n_source_species_site_year=len(panels),
        n_sources_with_at_least_three_years=sum(x["n_years"]>=3 for x in source_rows),
        n_potential_pair_years=len(same),candidate_pairs=same[:40],
        limitations=["the source is 2023 mirror; 2026 table identity not confirmed",
        "a prey record is not an independent stomach","missing fish/crust rows are not zero",
        "fraction of diet by weight is not necessarily individual-stomach wet mass",
        "stage, site, source, season, sample grain and multi-year support must pass before any climate model"])
    (out/"summary.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:results[k] for k in ("original_rows","focal_species_rows","n_source_ids","n_potential_pair_years","n_sources_with_at_least_three_years")}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--diet",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();main(a.diet,a.out)
