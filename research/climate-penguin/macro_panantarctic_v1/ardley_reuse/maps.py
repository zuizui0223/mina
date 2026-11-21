"""Printed map comparison, not individual marked nests. Input: UBA Texte 30/2017 PDF."""
from pathlib import Path
import io,sys,hashlib
import numpy as np,pandas as pd,pymupdf
from PIL import Image
from scipy.ndimage import distance_transform_edt, minimum_filter, maximum_filter, affine_transform
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
import cv2
R=Path(__file__).resolve().parent
pdf=Path(sys.argv[1])
assert hashlib.sha256(pdf.read_bytes()).hexdigest()=="cdc78086b946ef5ed0c6f0a42fd12059b908cb26f2f80a8c1c41881ea1056af4"
doc=pymupdf.open(pdf)
def rgb(a,col):return np.all(a==col,axis=-1)
maps=[np.array(Image.open(io.BytesIO(doc.extract_image(i)["image"])).convert("RGB")) for i in (278,280,284)]
# Use only the common map, omit lower-left legend in all panels. Register coast/zone lines.
valid=np.ones((866,726),bool);valid[665:,:270]=False;valid[:4]=False;valid[:,:4]=False
lines=[(rgb(a,[0,0,0])&valid).astype(np.float32) for a in maps]
aligned=[];qa=[]
for i,(a,line) in enumerate(zip(maps,lines)):
    corr,warp=cv2.findTransformECC(lines[0],line,np.eye(2,3,dtype=np.float32),cv2.MOTION_AFFINE,
        (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,150,1e-8),None,5)
    b=cv2.warpAffine(a,warp,(726,866),flags=cv2.INTER_NEAREST|cv2.WARP_INVERSE_MAP)
    aligned.append(b);qa.append(dict(year=2013+i,correlation=corr,matrix=warp.tolist()))
pd.DataFrame(qa).to_json(R/"registration.json",orient="records",indent=2)
def classify(a):
    m=np.zeros(valid.shape,np.uint8)
    for k,col in enumerate([(255,0,0),(0,112,255),(56,168,0),(0,38,115)],1):m[rgb(a,col)&valid]=k
    return m
maps2=np.array([classify(a) for a in aligned])
# Comparable background is core land-colour in 2014, not water or an unvisited/unmapped island.
sand=rgb(aligned[1],[255,245,207])&valid
d14=distance_transform_edt(maps2[1]==0)
d13=distance_transform_edt(maps2[0]==0)
summary=[];detail=[]
for size in (4,8,16):
 for offset in (0,size//2):
    former=[];controls=[]
    for y in range(offset,866-size+1,size):
     for x in range(offset,726-size+1,size):
        sl=np.s_[y:y+size,x:x+size]
        if not np.all(sand[sl]) or d14[sl].min()<=1:continue
        was=maps2[0][sl];now=maps2[2][sl]
        rec=(y,x,int(np.isin(now,[1,2,3]).any()))
        if np.isin(was,[2,3]).sum()>=2:former.append(rec)
        elif not was.any() and rgb(aligned[0][sl],[255,245,207]).all() and d13[sl].min()>1:controls.append(rec)
    if not former:continue
    dist=cdist(np.array(former)[:,:2],np.array(controls)[:,:2])
    cost=np.where(dist<=39,dist,1e7) # about 50 m on the printed scale
    ij=zip(*linear_sum_assignment(cost))
    out=[(former[i],controls[j],dist[i,j]) for i,j in ij if dist[i,j]<=39]
    for a,b,di in out:detail.append(dict(size=size,offset=offset,y=a[0],x=a[1],control_y=b[0],control_x=b[1],G_2015=a[2],control_G_2015=b[2],distance_px=di))
    summary.append(dict(size=size,offset=offset,eligible_former=len(former),matched=len(out),former_G=sum(a[2] for a,b,di in out),control_G=sum(b[2] for a,b,di in out)))
pd.DataFrame(summary).to_csv(R/"map_contrasts.csv",index=False)
pd.DataFrame(detail).to_csv(R/"matched_map_cells.csv",index=False)
print(pd.DataFrame(summary))
for i,a in enumerate(maps2):
    pts=np.argwhere(a==4)
    print(2013+i,'Adelie-only core pixels',pts.tolist())
    if len(pts) and i<2:
        mask=np.isin(maps2[i+1],[1,2,3]);print('next G distance in pixels',distance_transform_edt(~mask)[a==4])
