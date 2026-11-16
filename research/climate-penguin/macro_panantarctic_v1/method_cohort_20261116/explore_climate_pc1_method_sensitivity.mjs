#!/usr/bin/env node
/**
 * Exploratory PC1 slope sensitivity to survey-method cohort definition.
 * Static site-mean marine PC1 does NOT identify an annual warming effect.
 * All intervals are fixed-250km-block RESAMPLING QUANTILES, not population CIs.
 * The externally reported 265 series is not recreated and never transported.
 */
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

const OBS='research/climate-penguin/outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv';
const PC='research/climate-penguin/macro_panantarctic_v1/source_audit_20261115/source_cohort_climate_support_588_sites.csv';
const SHA_OBS='fc134e364cf38699fa7611d7dee5fbbbcb370c0a';
const SHA_PC='9b382f84e06f25317c801eb1b611563d8929e71f';
const COHORTS=['per_year_known_method','most_frequent_method','strict_single_shared_method','any_shared_method','no_shared_method'];
const K=['PC1','early_log_n','early_years_log','late_years_log'];
const INTER=['PC1','method_disjoint','PC1_x_method_disjoint',...K.slice(1)];
const DRAWS=2000,SEED=20261116;
const blob = x=>createHash('sha1').update(Buffer.from('blob '+x.length+'\0')).update(x).digest('hex');
function csvParse(s) {
  const rows=[];let row=[],tok='',q=false;
  for(let i=0;i<s.length;i++){const c=s[i];
    if(q){if(c==='"'&&s[i+1]==='"'){tok+='"';i++;}else if(c==='"')q=false;else tok+=c;}
    else if(c==='"')q=true;else if(c===','){row.push(tok);tok='';}
    else if(c==='\n'){row.push(tok.replace(/\r$/,''));rows.push(row);row=[];tok='';}
    else tok+=c;}
  assert(!q);
  if(row.length||tok){row.push(tok);rows.push(row);}
  const h=rows.shift();assert(rows.every(r=>r.length===h.length));
  return rows.map(r=>Object.fromEntries(h.map((k,i)=>[k,r[i]])));
}
const med=v=>{const a=v.slice().sort((a,b)=>a-b),k=a.length>>1;return a.length%2?a[k]:(a[k-1]+a[k])/2;};
function solve(M,b) {
  const n=b.length,A=M.map((x,i)=>[...x,b[i]]);
  for(let c=0;c<n;c++) {
    let j=c;for(let i=c+1;i<n;i++)if(Math.abs(A[i][c])>Math.abs(A[j][c]))j=i;
    if(Math.abs(A[j][c])<1e-11)return null;
    [A[j],A[c]]=[A[c],A[j]];const z=A[c][c];
    for(let k=c;k<=n;k++)A[c][k]/=z;
    for(let i=0;i<n;i++)if(i!==c){const d=A[i][c];for(let k=c;k<=n;k++)A[i][k]-=d*A[c][k];}
  }
  return A.map(r=>r[n]);
}
function fit(rows,mode='plain') {
  const vars=mode==='plain'?K:INTER;
  if(rows.length<35||new Set(rows.map(x=>x.block)).size<5)return null;
  const d=vars.length,XX=Array.from({length:d},()=>Array(d).fill(0)),Xy=Array(d).fill(0);
  const groups=new Map();
  for(const x of rows){if(!groups.has(x.group))groups.set(x.group,[]);groups.get(x.group).push(x);}
  const get=(x,k)=>k==='PC1_x_method_disjoint'?x.PC1*x.method_disjoint:x[k];
  for(const vv of groups.values()){
    const xm=vars.map(k=>vv.reduce((s,x)=>s+get(x,k),0)/vv.length);
    const ym=vv.reduce((s,x)=>s+x.growth_per_decade,0)/vv.length;
    for(const x of vv){
      const dx=vars.map((k,i)=>get(x,k)-xm[i]),dy=x.growth_per_decade-ym;
      for(let i=0;i<d;i++){Xy[i]+=dx[i]*dy;for(let j=0;j<d;j++)XX[i][j]+=dx[i]*dx[j];}
    }
  }
  const theta=solve(XX,Xy);
  return theta?{n:rows.length,n_spatial_blocks:new Set(rows.map(x=>x.block)).size,
    n_region_species_strata:groups.size,
    coefficients:Object.fromEntries(vars.map((v,i)=>[v,theta[i]]))}:null;
}
function randGenerator(seed){let x=seed>>>0;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296;};}
function quantile(arr,p){if(!arr.length)return null;const a=arr.slice().sort((a,b)=>a-b),k=(a.length-1)*p,i=Math.floor(k),f=k-i;return a[i]*(1-f)+a[Math.min(i+1,a.length-1)]*f;}
function main() {
  const ob=readFileSync(OBS),ec=readFileSync(PC);
  assert.equal(blob(ob),SHA_OBS,'Source observation Git blob changed');
  assert.equal(blob(ec),SHA_PC,'Marine PC1 source Git blob changed');
  const all=csvParse(ob.toString('utf8')),env=csvParse(ec.toString('utf8'));
  assert.equal(all.length,2999);assert.equal(env.length,588);
  const marine=new Map(env.map(x=>[x.site_id,x]));
  const focal=all.filter(x=>['ADPE','CHPE','GEPE'].includes(x.species_id));
  const valid=focal.filter(x=>x.n_methods==='1'&&x.method&&x.method!=='unknown'
    &&x.count.trim()!==''&&Number.isFinite(+x.count)&&+x.count>=0);
  assert.equal(valid.length,2724);
  const groups=new Map();
  for(const x of valid){const id=x.site_id+'|'+x.species_id;if(!groups.has(id))groups.set(id,[]);groups.get(id).push(x);}
  const subs=Object.fromEntries(COHORTS.map(x=>[x,[]]));
  const rawCohorts=Object.fromEntries(COHORTS.map(x=>[x,0]));
  for(const rr of groups.values()){
    const E=rr.filter(x=>+x.season>=1980&&+x.season<=2000),L=rr.filter(x=>+x.season>=2005&&+x.season<=2025);
    if(!E.length||!L.length)continue;
    const ef=new Set(E.map(x=>x.method)),lf=new Set(L.map(x=>x.method));
    const shared=[...ef].some(x=>lf.has(x)),strict=ef.size===1&&lf.size===1&&shared;
    const freq=new Map();for(const x of rr)freq.set(x.method,(freq.get(x.method)||0)+1);
    const pref=[...freq].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))[0][0];
    const pe=E.filter(x=>x.method===pref),pl=L.filter(x=>x.method===pref);
    const eligible=['per_year_known_method',shared?'any_shared_method':'no_shared_method'];
    if(strict)eligible.push('strict_single_shared_method');
    if(pe.length&&pl.length)eligible.push('most_frequent_method');
    for(const n of eligible)rawCohorts[n]++;
    const q=marine.get(rr[0].site_id);
    if(!q||!Number.isFinite(+q.PC1)||!q.block)continue;
    const makeRow=(e,l)=>{const n0=med(e.map(x=>+x.count)),n1=med(l.map(x=>+x.count));
      const year0=med(e.map(x=>+x.season)),year1=med(l.map(x=>+x.season));
      assert(year1>year0);
      return {site_id:rr[0].site_id,species:rr[0].species_id,region:rr[0].region,
        group:rr[0].region+'|'+rr[0].species_id,block:q.block,
        PC1:+q.PC1,method_disjoint:shared?0:1,
        early_log_n:Math.log1p(n0),early_years_log:Math.log1p(e.length),
        late_years_log:Math.log1p(l.length),
        growth_per_decade:10*(Math.log1p(n1)-Math.log1p(n0))/(year1-year0)};
    };
    const ar=makeRow(E,L);
    for(const n of eligible)subs[n].push(n==='most_frequent_method'?makeRow(pe,pl):ar);
  }
  // Optional publisher source crosswalk: the shared *count* of 265 is
  // NOT the historically reported 265 cohort (species composition differs).
  const optIndex=process.argv.indexOf('--calendar-roster');
  let candidates=COHORTS.slice();
  let intersectionProvenance=null;
  if(optIndex>=0){
    assert(process.argv[optIndex+1], 'Missing --calendar-roster path');
    const calendar=csvParse(readFileSync(process.argv[optIndex+1],'utf8'));
    const validCalendar=new Set(calendar.filter(x=>x.both_periods_have_known_vantage==='True')
      .map(x=>x.site_id+'|'+x.species));
    assert.equal(validCalendar.size,269);
    const seasonCandidates=[...groups.values()].filter(rr=>{
      const E=rr.filter(x=>+x.season>=1980&&+x.season<=2000);
      const L=rr.filter(x=>+x.season>=2005&&+x.season<=2025);
      return E.length>0&&L.length>0;
    });
    const shared=seasonCandidates.filter(rr=>validCalendar.has(rr[0].site_id+'|'+rr[0].species_id));
    assert.equal(seasonCandidates.length,268);
    assert.equal(shared.length,265);
    const species={ADPE:0,CHPE:0,GEPE:0};
    shared.forEach(x=>species[x[0].species_id]++);
    assert.deepEqual(species,{ADPE:101,CHPE:113,GEPE:51});
    const idset=new Set(shared.map(x=>x[0].site_id+'|'+x[0].species_id));
    const label='season_and_calendar_intersection_265_NOT_PRIOR_265';
    rawCohorts[label]=265;
    subs[label]=subs.per_year_known_method.filter(x=>idset.has(x.site_id+'|'+x.species));
    candidates.push(label);
    intersectionProvenance={
      calendar_year_v5_known_vantage_roster:269,
      season_year_known_vantage_roster:268,
      intersection_source_site_species_count:265,
      intersection_species:species,
      external_reported_unverified_265_species:{ADPE:102,CHPE:116,GEPE:47},
      same_source_roster_as_external_265:false,
      observed_growth_time_definition:'breeding season label (not calendar year); calendar list used ONLY for eligibility'
    };
  }
  assert.deepEqual(COHORTS.map(x=>rawCohorts[x]),[268,159,96,161,107]);
  assert.deepEqual(COHORTS.map(x=>subs[x].length),[262,153,90,155,107]);
  const fits=Object.fromEntries(candidates.map(x=>[x,{total_source_series:rawCohorts[x],marine_matched_series:subs[x].length,fit:fit(subs[x]),bootstrap_250km:null}]));
  // Common block draw for all five cohorts; repeated blocks are repeated original sites.
  const allRows=subs.per_year_known_method;
  const blocks=[...new Set(allRows.map(x=>x.block))].sort();
  const index=Object.fromEntries(candidates.map(k=>[k,new Map(blocks.map(b=>[b,subs[k].filter(x=>x.block===b)]))]));
  const rng=randGenerator(SEED);
  const boots=Object.fromEntries(candidates.map(k=>[k,[]]));
  const intr=[];
  for(let d=0;d<DRAWS;d++){
    const sampled=Array.from({length:blocks.length},()=>blocks[Math.floor(rng()*blocks.length)]);
    for(const k of candidates){
      const sample=sampled.flatMap(b=>index[k].get(b));
      const result=fit(sample);
      if(result)boots[k].push(result.coefficients.PC1);
    }
    const pooled=sampled.flatMap(b=>index.per_year_known_method.get(b));
    const intFit=fit(pooled,'interaction');
    if(intFit)intr.push(intFit.coefficients.PC1_x_method_disjoint);
  }
  for(const k of candidates){
    const q=boots[k];
    fits[k].bootstrap_250km={draws_requested:DRAWS,draws_valid:q.length,
      q025:quantile(q,.025),median:quantile(q,.5),q975:quantile(q,.975),
      interpretation:'Conditional spatial-block resampling quantiles; NOT an Antarctic population confidence interval'};
  }
  const originalInteraction=fit(allRows,'interaction');
  const regionStrata=new Map();
  for(const x of allRows){
    if(!regionStrata.has(x.group))regionStrata.set(x.group,[0,0]);
    regionStrata.get(x.group)[x.method_disjoint]++;
  }
  const overlapGroups=[...regionStrata].filter(([g,v])=>v[0]>=2&&v[1]>=2).map(x=>x[0]);
  const overlapFit=fit(allRows.filter(x=>overlapGroups.includes(x.group)),'interaction');
  const receipt={
    status:'PASS_EXPLORATORY_METHOD_COHORT_PC1_SENSITIVITY_NO_CLIMATE_DOSE_RESPONSE',
    provenance:{derived_source_git_blob_sha1:SHA_OBS,marine_source_git_blob_sha1:SHA_PC},
    model:'OLS within original region-by-species strata, response=decadal log1p nest change, predictors=STATIC marine PC1, log1p early nests, log1p early/late observed years',
    tested_cohorts:fits,
    nominal_265_overlap_not_original_265:intersectionProvenance,
    interaction:{pooled_within_region_species:originalInteraction,
      block_resample_difference_for_no_shared_vs_shared:{draws_requested:DRAWS,draws_valid:intr.length,
        q025:quantile(intr,.025),median:quantile(intr,.5),q975:quantile(intr,.975)},
      overlap_strata_with_at_least_2_per_method_category:overlapGroups,
      overlap_strata_fit:overlapFit},
    limitations:[
      'Previous 265-series roster and coefficients are NOT reproduced by this pinned derived source.',
      'PC1 is spatially averaged marine environment, not warming within each colony.',
      'Method changes and geographic sampling composition are jointly selected, not randomized.',
      'The same species/site can appear in different counts and bootstraps; 250km blocks share climate.',
      'Block resampling uncertainty is unstable when geographic regions are few; not independent p-values.',
      'No future census, population growth, extinction probability, survival rate or biological climate threshold is predicted.'
    ]};
  const out=process.argv[2]||'build/penguin_method_pc1_sensitivity_20261116';
  mkdirSync(out,{recursive:true});
  writeFileSync(join(out,'method_selection_pc1_sensitivity.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({status:receipt.status,
    coefficients:Object.fromEntries(candidates.map(k=>[k,{n:fits[k].marine_matched_series,
      beta:fits[k].fit.coefficients.PC1,
      lower:fits[k].bootstrap_250km.q025,upper:fits[k].bootstrap_250km.q975}])),
    interaction_PC1_x_method_disjoint:originalInteraction.coefficients.PC1_x_method_disjoint,
    interaction_block_quantiles:receipt.interaction.block_resample_difference_for_no_shared_vs_shared
  },null,2));
}
main();
