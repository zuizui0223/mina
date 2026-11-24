// Node 18+: node cross_species_source_offset.mjs SPATIAL_SOURCE_OFFSET_RESULT_20261124.json
import fs from 'node:fs';
import crypto from 'node:crypto';
function crossSpecies(src){
 const rows=src.rosters.strict_end.filter(x=>["South Shetland Islands","Central-west Antarctic Peninsula"].includes(x.reg));
 if(rows.length!==30)throw Error("roster drift");
 const radii=["same_site",1,5,10,25,50,100,250,500,"all"];
 const dist=(a,b)=>{const z=Math.PI/180,h=Math.sin((b.lat-a.lat)*z/2)**2+Math.cos(a.lat*z)*Math.cos(b.lat*z)*Math.sin((b.lon-a.lon)*z/2)**2;return 6371.0088*2*Math.asin(Math.sqrt(Math.min(1,h)))};
 function match(loss,gain,r,sameSpecies,localRegion){
 const L=loss.length,G=gain.length,N=L+G+2,S=N-2,T=N-1;
 const l=loss.reduce((s,t)=>s+t.w,0),g=gain.reduce((s,t)=>s+t.w,0),cap=Array.from({length:N},()=>Array(N).fill(0)),orig=Array.from({length:N},()=>Array(N).fill(0));
 const eligible=(a,b)=>(!sameSpecies||a.sp===b.sp)&&(!localRegion||a.reg===b.reg)&&(r==="same_site"?a.id===b.id:r==="all"||dist(a,b)<=r+1e-8);
 for(let i=0;i<L;i++){cap[S][i]=loss[i].w;for(let j=0;j<G;j++)if(eligible(loss[i],gain[j]))cap[i][L+j]=Math.min(l,g)}
 for(let j=0;j<G;j++)cap[L+j][T]=gain[j].w;
 for(let i=0;i<N;i++)orig[i]=cap[i].slice();
 let f=0,eps=1e-9;
 for(;;){const par=Array(N).fill(-1);par[S]=S;const Q=[S];for(let k=0;k<Q.length&&par[T]<0;k++)for(let j=0;j<N;j++)if(par[j]<0&&cap[Q[k]][j]>eps){par[j]=Q[k];Q.push(j)}
 if(par[T]<0)break;let d=Infinity;for(let j=T;j!==S;j=par[j])d=Math.min(d,cap[par[j]][j]);for(let j=T;j!==S;j=par[j]){cap[par[j]][j]-=d;cap[j][par[j]]+=d}f+=d}
 const reached=new Set([S]),q=[S];for(let k=0;k<q.length;k++)for(let j=0;j<N;j++)if(!reached.has(j)&&cap[q[k]][j]>eps){reached.add(j);q.push(j)}
 let cut=0;for(const i of reached)for(let j=0;j<N;j++)if(!reached.has(j))cut+=orig[i][j];
 if(Math.abs(f-cut)>1e-6)throw Error("cut");
 return f;
 }
 const result=[];
 function calc(rows,weight){let z=rows.map(x=>({...x,w:(x.b-x.a)*(x.sp==="GEPE"?weight:1)})),L=z.filter(x=>x.w<0).map(x=>({...x,w:-x.w})),G=z.filter(x=>x.w>0),l=L.reduce((s,t)=>s+t.w,0),g=G.reduce((s,t)=>s+t.w,0);if(l===0)return null;
 const out=radii.map(r=>({r,same_species:match(L,G,r,true,true)/l,any_species:match(L,G,r,false,true)/l,any_species_allow_cross_region:match(L,G,r,false,false)/l}));
 for(let i=0;i<out.length;i++){if(out[i].same_species>out[i].any_species+1e-10||out[i].any_species>out[i].any_species_allow_cross_region+1e-10)throw Error("nested constraint");if(i&&out[i-1].r!=="same_site"&&out[i].any_species<out[i-1].any_species-1e-10)throw Error("radius monotonic")}
 if(Math.abs(out.at(-1).any_species_allow_cross_region-Math.min(l,g)/l)>1e-8)throw Error("unbounded identity");
 return {n:rows.length,sites:new Set(rows.map(x=>x.id)).size,loss:l,gain:g,net:g-l,out}}
 for(let w of [0.5,1,2]){
 const full=calc(rows,w),subsets=[];
 for(const reg of new Set(rows.map(x=>x.reg)))subsets.push({reg,...calc(rows.filter(x=>x.reg===reg),w)});
 const loo=[];for(const unit of ["id","block","reg"])for(const omitted of new Set(rows.map(x=>x[unit]))){const x=calc(rows.filter(x=>x[unit]!==omitted),w);if(x)loo.push({unit,omitted,...x})}
 result.push({gentoo_weight:w,...full,regions:subsets,loo})
 }
 return {rows,results:result,scope:"Fixed two-region site-species roster, region-constrained max-flow; hypothetical equal or relative nests-as-source weights; no marine subsidy or migration estimate."};
}
const b=fs.readFileSync(process.argv[2]);if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!=='ebc6106cc7b8489af783e90c56a67e685dcfcdb6')throw Error('source blob mismatch');console.log(JSON.stringify(crossSpecies(JSON.parse(b.toString('utf8'))),null,2));
