// Source-pinned reproducible maximum-flow diagnostic. Node 18+.
// Usage: node spatial_source_offset.mjs original_three_decade_43_source_site_species.csv original_strict_paired_end_50_source_site_species.csv mapppd_unambiguous_site_seasons.csv > spatial_source_offset_result.json
import fs from 'node:fs';
import crypto from 'node:crypto';
function analyze(a,b,c){
 function parse(s){let rs=[],r=[],v="",q=false;for(let i=0;i<s.length;i++){const t=s[i];if(q){if(t==='"'&&s[i+1]==='"'){v+='"';i++}else if(t==='"')q=false;else v+=t;}else if(t==='"')q=true;else if(t===','){r.push(v);v=""}else if(t==='\n'){r.push(v.replace(/\r$/,""));if(r.length>1)rs.push(r);r=[];v=""}else v+=t}if(r.length||v){r.push(v);if(r.length>1)rs.push(r)}const h=rs.shift();return rs.map(r=>Object.fromEntries(h.map((k,i)=>[k,r[i]])))}
 const raw=parse(c);const A=parse(a),B=parse(b);
 const coords=new Map();for(const r of raw){const k=r.site_id+"|"+r.species_id;const x=[+r.latitude,+r.longitude];if(!x.every(Number.isFinite))continue;if(!coords.has(k))coords.set(k,[]);if(!coords.get(k).some(t=>t[0]===x[0]&&t[1]===x[1]))coords.get(k).push(x)}
 const key=r=>r.site_id+"|"+r.species;
 function canonical(r,three){const x=coords.get(key(r));if(x?.length!==1||Math.abs(x[0][0]-+r.latitude)>1e-5)throw Error("coordinate mismatch "+key(r));if(three&&Math.abs(x[0][1]-+r.longitude)>1e-5)throw Error("longitude mismatch");
 return {id:r.site_id,sp:r.species,reg:r.source_region,block:r.polar_250km_block,lat:x[0][0],lon:x[0][1],a:+r[three?"median_original_nest_count_0":"site_median_observed_nests_early"],b:+r[three?"median_original_nest_count_2":"site_median_observed_nests_late"]}}
 const X=A.map(r=>canonical(r,true)),Y=B.map(r=>canonical(r,false));if(X.length!==43||Y.length!==50)throw Error("roster drift");for(const x of X){const y=Y.find(t=>t.id===x.id&&t.sp===x.sp);if(!y||y.a!==x.a||y.b!==x.b)throw Error("subset drift "+x.id)}
 function dist(a,b){const r=Math.PI/180;const h=Math.sin((b.lat-a.lat)*r/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin((b.lon-a.lon)*r/2)**2;return 6371.0088*2*Math.asin(Math.sqrt(Math.min(1,h)))}
 const radii=[0,1,5,10,25,50,100,250,500,1000,Infinity];
 function flow(loss,gain,R,sameRegion=false){
 const L=loss.length,G=gain.length,n=L+G+2,src=n-2,tgt=n-1,cap=Array.from({length:n},()=>Array(n).fill(0));let totalL=loss.reduce((s,x)=>s+x.w,0),totalG=gain.reduce((s,x)=>s+x.w,0);
 for(let i=0;i<L;i++){cap[src][i]=loss[i].w;for(let j=0;j<G;j++)if((!sameRegion||loss[i].reg===gain[j].reg)&&dist(loss[i],gain[j])<=R+1e-8)cap[i][L+j]=Math.min(totalL,totalG);}
 for(let j=0;j<G;j++)cap[L+j][tgt]=gain[j].w;
 let F=0;const eps=1e-12*Math.max(1,totalL,totalG);
 for(;;){const par=Array(n).fill(-1);par[src]=src;const q=[src];for(let k=0;k<q.length&&par[tgt]<0;k++)for(let j=0;j<n;j++)if(par[j]<0&&cap[q[k]][j]>eps){par[j]=q[k];q.push(j)}
 if(par[tgt]<0)break;let f=Infinity;for(let j=tgt;j!==src;j=par[j])f=Math.min(f,cap[par[j]][j]);for(let j=tgt;j!==src;j=par[j]){cap[par[j]][j]-=f;cap[j][par[j]]+=f}F+=f}
 // Independent max-flow/min-cut check on residual reachability.
 const reach=new Set([src]),q=[src];for(let i=0;i<q.length;i++)for(let j=0;j<n;j++)if(!reach.has(j)&&cap[q[i]][j]>eps){reach.add(j);q.push(j)}
 let cut=0;for(let i=0;i<L;i++){if(!reach.has(i))cut+=loss[i].w;else for(let j=0;j<G;j++)if(!reach.has(L+j)&&(!sameRegion||loss[i].reg===gain[j].reg)&&dist(loss[i],gain[j])<=R+1e-8)cut+=Math.min(totalL,totalG)}
 for(let j=0;j<G;j++)if(reach.has(L+j))cut+=gain[j].w;
 if(Math.abs(cut-F)>1e-8*Math.max(1,totalL,totalG))throw Error("mincut check");
 return F}
 function calc(rows){const sa=rows.reduce((s,x)=>s+x.a,0),sb=rows.reduce((s,x)=>s+x.b,0);if(sa<=0||sb<=0)return null;
 const absolute=rows.map(x=>({...x,w:x.b-x.a})), relative=rows.map(x=>({...x,w:x.b/sb-x.a/sa}));const split=x=>[x.filter(t=>t.w<0).map(t=>({...t,w:-t.w})),x.filter(t=>t.w>0)];const [l,g]=split(absolute),[lr,gr]=split(relative);const sum=x=>x.reduce((s,t)=>s+t.w,0);const L=sum(l),G=sum(g),T=sum(lr);if(Math.abs(G-L-(sb-sa))>1e-7||Math.abs(T-sum(gr))>1e-9)throw Error("identity");
 const flows=radii.map(r=>({r:r===Infinity?"all":r,absolute: L?flow(l,g,r)/L:null,relative:T>1e-12?flow(lr,gr,r)/T:null}));
 for(let i=1;i<flows.length;i++)for(const k of ["absolute","relative"])if(flows[i][k]+1e-10<flows[i-1][k])throw Error("monotonic");
 if(L&&Math.abs(flows.at(-1).absolute-Math.min(1,G/L))>1e-9)throw Error("all-range identity");
 if(T>1e-12&&Math.abs(flows.at(-1).relative-1)>1e-9)throw Error("relative all-range identity");
 return {n:rows.length,regions:new Set(rows.map(x=>x.reg)).size,a:sa,b:sb,loss:L,gain:G,declining:l.length,growing:g.length,tv:T,flows,within_region_abs:L?flow(l,g,Infinity,true)/L:null,within_region_relative:T?flow(lr,gr,Infinity,true)/T:null}}
 const out=[];for(const [cohort,panel] of [["three_decade",X],["strict_end",Y]])for(const sp of ["ADPE","CHPE","GEPE"]){const z=panel.filter(x=>x.sp===sp),main=calc(z),loo=[];for(const unit of ["id","block","reg"])for(const v of new Set(z.map(x=>x[unit]))){const sub=calc(z.filter(x=>x[unit]!==v));if(sub)loo.push({unit,omitted:v,...sub})}out.push({cohort,species:sp,...main,loo})}
 return {rosters:{three_decade:X,strict_end:Y},out,design:"Exact fixed source panel 1991–2000 vs 2011–2020 medians. Absolute maximum loss offset by positive changes under great-circle radius; normalized share counterpart; max flow/min cut, no realized flux or dispersal."}
}
const args=process.argv.slice(2);if(args.length!==3)throw Error("three original CSV inputs required");const blobs=args.map(p=>fs.readFileSync(p));const expected=["a5ccb7a527605d28804ef389109f416bd6dea090","31f7915d34a4c3ced6a16ab6f18c933cf677403e","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"];for(let i=0;i<3;i++){const hash=crypto.createHash("sha1").update("blob "+blobs[i].length+"\0").update(blobs[i]).digest("hex");if(hash!==expected[i])throw Error("source git blob mismatch "+args[i]);}console.log(JSON.stringify(analyze(...blobs.map(b=>b.toString("utf8"))),null,2));
