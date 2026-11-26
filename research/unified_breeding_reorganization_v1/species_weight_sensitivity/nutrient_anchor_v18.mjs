// node nutrient_anchor_v18.mjs RESULT_20261126.json > result.json
import fs from 'node:fs';
function run(v){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const rates={ADPE:{d:132,p:60821,sd:1904,pop:846,published:574},GEPE:{d:153,p:102816,sd:3089,pop:8858,published:11775}};
 const mass=84.5/1000;
 const kg=(s,c)=>mass*rates[s].d*c/1e6;
 const p=Object.fromEntries(Object.entries(rates).map(([s,o])=>[s,{...o,kg_adult:kg(s,o.p),kg_nest:2*kg(s,o.p),reconstructed_total:kg(s,o.p)*o.pop,kg_nest_low:2*kg(s,o.p-o.sd),kg_nest_high:2*kg(s,o.p+o.sd)}]));
 for(const r of Object.values(p))assert(Math.abs(r.reconstructed_total-r.published)<1,"source rounding");
 const n={CHPE:0.106,GEPE:0.079};
 const add=a=>a.reduce((x,y)=>x+y,0), weighted=(a,w)=>add(a.map((x,i)=>x*w[i])), pct=(a,b)=>a>0?(b-a)/a*100:null;
 function compare(x,kind){const sp=x.species, w=sp.map(s=>kind==="P"?p[s].kg_nest:n[s]);const a=weighted(x.n0,w),b=weighted(x.n1,w);const d=b-a,net=add(x.n1)-add(x.n0);assert(net===x.net,"net");const base={site:x.site,family:x.family,start:x.first_year,end:x.last_year,n0:x.n0,n1:x.n1,count_change:net,count_pct:pct(add(x.n0),add(x.n1)),weighted_pct:pct(a,b),sign_mismatch:Math.sign(d)!==Math.sign(net),weighted_delta:d,weights:w};
 if(kind==="P"){const corners=sp.map(s=>[p[s].kg_nest_low,p[s].kg_nest_high]);const results=corners[0].flatMap(u=>corners[1].map(z=>{const w=[u,z];return {delta:weighted(x.n1,w)-weighted(x.n0,w),pct:pct(weighted(x.n0,w),weighted(x.n1,w))}}));return {...base,scope:x.site==="ARDL"?"same_named_island_scenario":"unvalidated_transfer_scenario",kg_p_early:a,kg_p_late:b,corner_delta_range:[Math.min(...results.map(q=>q.delta)),Math.max(...results.map(q=>q.delta))],corner_pct_range:[Math.min(...results.map(q=>q.pct)),Math.max(...results.map(q=>q.pct))],all_corners_same_count_sign:results.every(q=>Math.sign(q.delta)===Math.sign(net))}}
 const n0=add(x.n0),n1=add(x.n1),ch=x.d[sp.indexOf("CHPE")],ge=x.d[sp.indexOf("GEPE")];
 return {...base,hypothetical_early_n_percent:n0?100*a/n0:null,hypothetical_late_n_percent:n1?100*b/n1:null,hypothetical_mixed_n_pp:n0&&n1?100*(b/n1-a/n0):null,gentoo_chinstrap_dry_mass_break_even:ch<0&&ge>0?-ch/ge*n.CHPE/n.GEPE:null}
 }
 const outputs={};for(const [kind,f] of [["P","ADPE__GEPE"],["N","CHPE__GEPE"]]){outputs[kind]={};for(const k of ["endpoints","adjacent_years"]){const rows=v[k].filter(x=>x.family===f).map(x=>compare(x,kind));outputs[kind][k]={rows,n:rows.length,mismatches:rows.filter(x=>x.sign_mismatch).length,weighted_pct_values:rows.map(x=>x.weighted_pct),corner_sign_robust:kind==="P"?rows.filter(x=>x.all_corners_same_count_sign).length:null,mix_n_declines:kind==="N"?rows.filter(x=>x.hypothetical_mixed_n_pp<0).length:null}}}
 assert(outputs.P.endpoints.n===6&&outputs.P.adjacent_years.n===45&&outputs.N.endpoints.n===9&&outputs.N.adjacent_years.n===42,"rosters");
 return {status:"conditional literature scenarios; actual flux and vegetation response not measured",P_source:p,P_weight_ratio:p.GEPE.kg_nest/p.ADPE.kg_nest,N_source:n,N_concentration_ratio:n.GEPE/n.CHPE,ADPE_ardley_to_ross:60821/22911,ADPE_ardley_to_vestfold:60821/27624,outputs}
}
console.log(JSON.stringify(run(JSON.parse(fs.readFileSync(process.argv[2],'utf8'))),null,2));
