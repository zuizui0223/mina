# Ardley published breeding map: visible-symbol zone audit

Executed locally 2026-11-24. The publisher PDF of Braun, Grämer & Peter (2025), DOI 10.60810/openumwelt-7664, [official report](https://www.umweltbundesamt.de/system/files/medien/11850/publikationen/63_2025_texte.pdf), 255 pages, SHA256 7c53635e6799c1eafca006e9293baa336288689afc2f1d405c802f832069b8b9. Initial source workflow 45389357453 downloaded the PDF but failed a brittle author/page assertion (second URL 404). Repaired workflow 45390508988 verified the exact same publisher bytes, found the unique section/caption at page index 61 (printed p.62), and recovered [artifact 14919110826](https://github.com/zuizui0223/mina/actions/runs/45390508988/artifacts/14919110826), SHA256 81e03fddcbe2f9d16df37d9f3f226b0a58946498d5ccd56aa119bd91b87813e5. Web PDF screenshot failed cache miss; original embedded raster and rendered page obtained and raster visually inspected locally. Figure has ONE 1123×793 embedded indexed image and no map polygon vector paths (two page-level black paths only). Extracted raster SHA256 1bced935f47291ca34355ef49353e5a7da5a29d4a22ba13eb29891616df2f2a3. Figure legend identifies green 2017/18 breeding groups, blue 2023/24 groups, red latest zonation, orange old zonation. No hidden early breeding polygon geometry recovered.

## Visible symbols, not occupied-area estimates

2023/24 red boundary (RGB 168,56,0) dilated four pixels, flood-filled seven disjoint interiors from visually checked zone-label seeds. Exclude boundary and exterior. Exact legend RGB green (85,255,0) and blue (0,112,255); broad color range and 4–8 px boundary dilation sensitivity (10 settings). All exact pixel counts separately verified against RGB histograms. No pixel-to-square-metre conversion, georeferencing, group count estimate, original-area ratio, pixel transition table, or plant overlay authorized: blue can occlude old green and the survey methods differ.

| Zone | Interior pixels | Visible green | Visible blue | % of total retained blue |
|---|---:|---:|---:|---:|
|1|28704|229|464|5.65509|
|2|27079|50|546|6.65448|
|3|32198|176|1983|24.16819|
|4|25948|150|0|0|
|5|44788|78|2165|26.38635|
|6|14651|132|217|2.64473|
|7|59238|114|2830|34.49116|
|Total||929|8205|100|

At every tested setting Zone 4 has 150 retained green and 0 blue pixels; Zone 7 has 2761–2830 retained blue pixels. Latest Zone 7 has the largest visible blue count, robust to the stated mask choices. This numerically corroborates the published spatial description, NOT an independent field study. Original report identifies moss deterioration in southern newly/larger gentoo groups; that observation is from the authors, not our new estimate. No inferred actual historic area loss/gain from overplotted colors.

## New open-data inventory

Original official Zenodo API catalogue for [10.5281/zenodo.14503437](https://doi.org/10.5281/zenodo.14503437), related article DOI 10.1016/j.ecolind.2024.113011; [run 45390637302](https://github.com/zuizui0223/mina/actions/runs/45390637302), artifact 14919200348. Catalogue SHA256 75dd2bbe0cb6f866d0cddc0839da6b357f8850880682583ba3f01950700c1775. Publisher metadata says CC BY 4.0, collection 2013–2018, parts of colonies on Ardley, King George, Nelson or Deception islands, aerial imagery and shapefiles. Single ZIP `Dataset distinguish breeding penguins drone imagery.zip`, 4109917595 bytes, MD5 62bb5a89ca7f5f06e54b74e26bf5de5d. Catalogue only, not downloaded due size; it does not cover 2023/24. Full survey extents unknown. Thus the original two-season transition GIS still unavailable. Do not substitute study-subset shape files for full-island occupied extent. Request actual 2017/18 and 2023/24 breeding group polygons and comparable botanical observations from monitoring authors. No publication/merge. No restricted AADC material used.

Local reproducibility bundle `ardley_visible_breeding_zone_audit_20261124.zip` SHA256 09676c127ed5447f0402a5fb10704513ff1e5b3e99fbbbb9ae20c7220d685fe5, with exact executed script, all 70 zone rows, ten sensitivity rows, source receipt, and analysis README. Below is the core calculation from that executed script (same numeric code; introductory docstring omitted). Download the verified source artifact from GitHub, save code as audit_visible_figure.py, then run `python audit_visible_figure.py github-actions-artifact-14919110826.zip results`.

```python
import argparse, csv, hashlib, json, zipfile, io
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import fitz
from collections import Counter
p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True)
h=hashlib.sha256(a.artifact.read_bytes()).hexdigest();assert h=='81e03fddcbe2f9d16df37d9f3f226b0a58946498d5ccd56aa119bd91b87813e5'
with zipfile.ZipFile(a.artifact) as z:
    meta=json.loads(z.read('receipt.json'));assert meta['sha256']=='7c53635e6799c1eafca006e9293baa336288689afc2f1d405c802f832069b8b9' and meta['page_index']==61 and meta['status']=='verified_figure_page'
    doc=fitz.open(stream=z.read('figure6_page.pdf'),filetype='pdf')
    page=doc[0]; imgs=page.get_images(full=True);assert len(imgs)==1
    raw=doc.extract_image(imgs[0][0])['image'];im=Image.open(io.BytesIO(raw)).convert('RGB')
assert im.size==(1123,793)
A=np.array(im).astype(np.int16);r,g,b=A.transpose(2,0,1)
red=(r==168)&(g==56)&(b==0); red[610:,:429]=False
seeds={1:(503,75),2:(657,165),3:(806,199),4:(481,374),5:(683,453),6:(896,431),7:(558,532)}
colors={'exact':((r==85)&(g==255)&(b==0),(r==0)&(g==112)&(b==255)), 'broad':((r>=45)&(r<=125)&(g>=230)&(b<=30),(r<=30)&(g>=70)&(g<=155)&(b>=220))}
rows=[];check=[]
for d in [4,5,6,7,8]:
    lab,_=ndi.label(~ndi.binary_dilation(red,iterations=d))
    ids=[lab[y,x] for x,y in seeds.values()];assert len(set(ids))==7 and 0 not in ids and lab[0,0] not in ids
    for method,(old,new) in colors.items():
        counts=[]
        for z,(x,y) in seeds.items():
            m=lab==lab[y,x];o=int((m&old).sum());n=int((m&new).sum());area=int(m.sum())
            if method=='exact':
                hst=Counter(map(tuple,A[m]));assert (o,n)==(hst[(85,255,0)],hst[(0,112,255)])
            counts.append((z,area,o,n))
        so=sum(x[2] for x in counts);sn=sum(x[3] for x in counts)
        for z,area,o,n in counts:rows.append(dict(margin_px=d,color_rule=method,zone=z,interior_pixels=area,visible_2017_18_green_px=o,visible_2023_24_blue_px=n,share_visible_old_pct=100*o/so,share_visible_new_pct=100*n/sn,blue_fraction_of_visible_colors_pct=100*n/(o+n) if o+n else None))
        assert sum(x[1] for x in counts)==int(np.isin(lab,ids).sum())
        check.append(dict(margin_px=d,color_rule=method,total_old=so,total_new=sn,zone4_old=counts[3][2],zone4_new=counts[3][3],zone7_old=counts[6][2],zone7_new=counts[6][3]))
with (a.out/'visible_zone_pixels.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (a.out/'sensitivity.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(check[0]));w.writeheader();w.writerows(check)
receipt={'source_report_sha256':meta['sha256'],'source_artifact_sha256':hashlib.sha256(a.artifact.read_bytes()).hexdigest(),'extracted_image_sha256':hashlib.sha256(raw).hexdigest(),'native_size':im.size,'primary':{'margin_px':4,'color_rule':'exact'},'verification':'exact counts independently verified with RGB histogram; disjoint 7 components, no exterior component; sensitivity to red line dilation and color thresholds','limit':'Visible symbol pixels in overlaid raster only. Cannot infer original polygon area, true transitions, change in number of groups or geographic location of individual pixels. No plant observations.'}
(a.out/'audit_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps([x for x in rows if x['margin_px']==4 and x['color_rule']=='exact'],indent=2));print(json.dumps(check))
```
