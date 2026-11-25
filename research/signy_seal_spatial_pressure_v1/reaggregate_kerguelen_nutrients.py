"""Reproduce descriptive P/Fe concentration ratios from published xlsx files.
The input files are from https://github.com/Lola-san/Agazella.nutrient.release.Ker.
Requires openpyxl. No flux, Signy weight or independent-animal inference.
"""
import argparse, hashlib, json, math
from pathlib import Path
from statistics import mean, median
from openpyxl import load_workbook

PINS = {
    "res_compo_scats.xlsx": "f68fff27dcf408170c5ffe626db4eff92c49f65d",
    "data_scats.xlsx": "adef3decc6c154b055d81062e9f7539eff1c894b",
}
def read(path, sheet):
    data = path.read_bytes()
    blob = hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
    if blob != PINS[path.name]:
        raise ValueError(f"original Git blob mismatch: {path.name}")
    wb=load_workbook(path, read_only=True, data_only=True)
    rows=iter(wb[sheet].values)
    h=next(rows)
    out=[dict(zip(h,r)) for r in rows if r[0] is not None]
    wb.close()
    if len(out)!=60 or len({r["Code_sample"] for r in out})!=60:
        raise ValueError("sample count/identity mismatch")
    return {r["Code_sample"]:r for r in out}
def summary(rows):
    def group(site):
        g=[r for r in rows if r["site"]==site]
        return {"n":len(g),"flagged_pup":sum(r["pup"]==1 for r in g),
            "P":mean(r["P"] for r in g),"Fe":mean(r["Fe"] for r in g),
            "P_median":median(r["P"] for r in g),"Fe_median":median(r["Fe"] for r in g),
            "median_P_over_Fe":median(r["P"]/r["Fe"] for r in g)}
    a,b=group("Cap Noir"),group("Pointe Suzanne")
    ratio={k:a[k]/b[k] for k in ("P","Fe")}
    return {"CN":a,"PS":b,"CN_over_PS":ratio,
        "equal_total_output_CN_to_PS_dry_feces_mass_ratio":{k:1/v for k,v in ratio.items()},
        "ratio_of_concentration_ratios":ratio["P"]/ratio["Fe"]}
def run(root):
    c=read(root/"res_compo_scats.xlsx","résultats compilés")
    m=read(root/"data_scats.xlsx","data")
    if set(c)!=set(m): raise ValueError("unjoined sample IDs")
    rows=[]
    for key,v in c.items():
        s=m[key]
        if s["site"] not in ("Cap Noir","Pointe Suzanne"):
            raise ValueError("unexpected site")
        if not all(isinstance(v[k],(float,int)) and math.isfinite(v[k]) and v[k]>0 for k in ("P","Fe")):
            raise ValueError("nonquantitative primary element")
        if key!="CN12":
            rows.append({"site":s["site"],"pup":s["pup_suspicion"],"P":v["P"],"Fe":v["Fe"]})
    if len(rows)!=59: raise ValueError("published exclusion mismatch")
    main=summary(rows)
    variants=[summary(rows[:i]+rows[i+1:]) for i in range(len(rows))]
    rr={k:[min(v["CN_over_PS"][k] for v in variants),max(v["CN_over_PS"][k] for v in variants)] for k in ("P","Fe")}
    return {"main":main,"exclude_flagged_or_nonzero_pup_suspicion":summary([r for r in rows if r["pup"]==0]),
            "leave_one_scat_out_concentration_ratio_ranges":rr,
            "dry_mass_ratio_robust_opposite_rank_interval":[1/min(rr["Fe"][0],main["CN_over_PS"]["Fe"]),1/max(rr["P"][1],main["CN_over_PS"]["P"])]}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source_dir",type=Path);p.add_argument("out",type=Path)
    a=p.parse_args()
    a.out.write_text(json.dumps(run(a.source_dir),indent=2)+"\n")
