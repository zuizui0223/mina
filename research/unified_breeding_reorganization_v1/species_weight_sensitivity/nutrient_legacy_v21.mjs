// node nutrient_legacy_v21.mjs > summary.json
function run(){
 const soil={source:"Smykla et al. 2015 Table 1 p61",units:"mg/g",active:{n:5,N:13.86,P:8.028,Pav:.474,N_P_mean:2.01,N_sd:9.30,P_sd:5.470,Pav_sd:.120},relict:{n:5,N:9.56,P:15.650,Pav:.540,N_P_mean:.31,N_sd:11.99,P_sd:5.953,Pav_sd:.083},background:{n:6,N:.16,P:.873,Pav:.109,N_P_mean:.11,N_sd:.31,P_sd:.494,Pav_sd:.066}};
 const water={source:"Juchnowicz-Bierbasz and Rakusa-Suszczewski 2002 Table 3 p84",units:"mg element/L",stations:[["L1","background",1,32.34,4.60,12.99,1.87],["L2","background",5,103.08,79.52,55.14,1.22],["L3","relict",8,157.19,85.42,55.73,1.54],["L4","background",1,310.93,607.56,8.48,3.44],["L5","relict",7,134.18,6.17,551.97,1.97],["L6","relict",8,1559.87,40.12,349.85,1.03],["L7","background",8,3.67,38.79,26.14,.48],["L8","active",8,1063.43,140.16,3326.51,65.40]].map(([id,status,n,P,NO3,NH4,NO2])=>({id,status,n,P,NO3,NH4,NO2,DIN:NO3+NH4+NO2}))};
 const a=soil.active,b=soil.relict,c=soil.background;
 const ratios=Object.fromEntries(["N","P","Pav"].map(k=>[k,{relict_active:b[k]/a[k],relict_background:b[k]/c[k],active_background:a[k]/c[k],background_subtracted_relict_active:(a[k]>c[k]&&b[k]>c[k])?(b[k]-c[k])/(a[k]-c[k]):null}]));
 const soilresult={ratios,P_N_of_means:{active:a.P/a.N,relict:b.P/b.N,relative:(b.P/b.N)/(a.P/a.N)},published_mean_N_P:{active:a.N_P_mean,relict:b.N_P_mean,relative:b.N_P_mean/a.N_P_mean},Pav_P_of_means:{active:a.Pav/a.P,relict:b.Pav/b.P,relative:(b.Pav/b.P)/(a.Pav/a.P)}};
 const wactive=water.stations.find(x=>x.status==="active"),wrelict=water.stations.filter(x=>x.status==="relict"),wbackground=water.stations.filter(x=>x.status==="background");
 const mean=a=>a.reduce((s,x)=>s+x,0)/a.length,gmean=a=>Math.exp(mean(a.map(Math.log)));
 const relative=x=>({id:x.id,status:x.status,P_active_ratio:x.P/wactive.P,DIN_active_ratio:x.DIN/wactive.DIN,P_DIN:x.P/x.DIN,P_DIN_relative:(x.P/x.DIN)/(wactive.P/wactive.DIN)});
 const rel=water.stations.map(relative),r=rel.filter(x=>x.status==="relict");
 const waterresult={relative_stations:rel,relict_P_DIN_geomean_relative:gmean(r.map(x=>x.P_DIN_relative)),leave_one_relict_out:r.map((x,i)=>({excluded:x.id,geomean_relative:gmean(r.filter((_,j)=>i!==j).map(x=>x.P_DIN_relative))})),equal_station_means:Object.fromEntries([["active",[wactive]],["relict",wrelict],["background",wbackground]].map(([k,v])=>[k,{P:mean(v.map(x=>x.P)),DIN:mean(v.map(x=>x.DIN)),P_DIN_ratio_of_station_means:mean(v.map(x=>x.P))/mean(v.map(x=>x.DIN))}])),relict_above_active_P_DIN:r.filter(x=>x.P_DIN_relative>1).length};
 waterresult.relative_ratio_of_station_means=waterresult.equal_station_means.relict.P_DIN_ratio_of_station_means/waterresult.equal_station_means.active.P_DIN_ratio_of_station_means;
 if(Math.abs(soilresult.P_N_of_means.relative-ratios.P.relict_active/ratios.N.relict_active)>1e-12)throw Error("soil QA");
 for(const x of rel)if(Math.abs(x.P_DIN_relative-x.P_active_ratio/x.DIN_active_ratio)>1e-12)throw Error("water QA");
 return {status:"published_summary_synthesis_not_age_decay",soil,water,soilresult,waterresult,limits:"different measurement matrices, distinct sites, no repeated age or deposition rate, one active lysimeter station, no pooled effect, original web screenshots unavailable"};
}
console.log(JSON.stringify(run(),null,2));
