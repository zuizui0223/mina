#!/usr/bin/env node
/**
 * Source-method reconciliation for the long-term Antarctic colony cohort.
 * Source: Git-blob SHA1 pinned 2,999-row derived MAPPPD table (NOT full live MAPPPD v5).
 * Deliberately does not estimate climate coefficients or penguin population forecasts.
 */
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import assert from 'node:assert/strict';

const SRC = 'research/climate-penguin/outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv';
const SHA = 'fc134e364cf38699fa7611d7dee5fbbbcb370c0a';
const TAXA = ['ADPE','CHPE','GEPE'];
const EARLY = [1980,2000], LATE = [2005,2025];
const key = r => r.site_id + '|' + r.species_id;

function csvParse(s) {
  const lines = []; let row = [], token = '', quote = false;
  for (let i=0; i<s.length; ++i) {
    const c = s[i];
    if (quote) {
      if (c==='"' && s[i+1]==='"') { token += '"'; ++i; }
      else if (c==='"') quote = false;
      else token += c;
    } else if (c==='"') quote = true;
    else if (c===',') { row.push(token); token = ''; }
    else if (c==='\n') { row.push(token.replace(/\r$/,'')); lines.push(row); row=[]; token=''; }
    else token += c;
  }
  assert(!quote, 'Unterminated CSV quote');
  if (row.length || token) {row.push(token); lines.push(row);}
  const columns = lines.shift();
  assert(columns && columns.length > 0, 'Missing original header');
  assert(lines.every(x=>x.length===columns.length), 'Source CSV row width changed');
  return lines.map(r=>Object.fromEntries(columns.map((c,i)=>[c,r[i]])));
}
function blobSha1(buf) {
  return createHash('sha1').update(Buffer.from('blob '+buf.length+'\0')).update(buf).digest('hex');
}
function assertUnique(rows) {
  const seen = new Set();
  for (const r of rows) {
    const k=key(r)+'|'+r.season;
    assert(!seen.has(k), 'Repeated site/species/season: '+k);
    seen.add(k);
  }
}
function buildCohort(rows) {
  const by = new Map();
  for (const r of rows) {
    const k=key(r);
    if (!by.has(k)) by.set(k,[]);
    by.get(k).push(r);
  }
  const out = [];
  for (const rr of by.values()) {
    const early = rr.filter(x=>+x.season>=EARLY[0]&&+x.season<=EARLY[1]);
    const late = rr.filter(x=>+x.season>=LATE[0]&&+x.season<=LATE[1]);
    if (!early.length || !late.length) continue;
    const e = [...new Set(early.map(x=>x.method))].sort();
    const l = [...new Set(late.map(x=>x.method))].sort();
    const both = e.filter(x=>l.includes(x));
    out.push({
      site_id:rr[0].site_id, species:rr[0].species_id, source_region:rr[0].region,
      n_early_observation_years:early.length, n_late_observation_years:late.length,
      early_method_set:e.join(';'), late_method_set:l.join(';'),
      has_some_same_method:both.length>0,
      strict_single_shared_method:e.length===1 && l.length===1 && both.length===1
    });
  }
  out.sort((a,b)=>a.species.localeCompare(b.species)||a.site_id.localeCompare(b.site_id));
  return out;
}
function summary(rows) {
  return {
    n_site_species_series:rows.length,
    n_unique_site_ids:new Set(rows.map(x=>x.site_id)).size,
    per_species:Object.fromEntries(TAXA.map(s=>[s,rows.filter(x=>x.species===s).length])),
    per_region:Object.fromEntries([...new Set(rows.map(x=>x.source_region))].sort()
      .map(r=>[r,rows.filter(x=>x.source_region===r).length]))
  };
}
function writeCSV(file,records) {
  const cols=Object.keys(records[0]);
  const esc=s=>{const v=String(s??'');return /[",\r\n]/.test(v)?'"'+v.replaceAll('"','""')+'"':v;};
  writeFileSync(file,[cols.join(','),...records.map(r=>cols.map(k=>esc(r[k])).join(','))].join('\n')+'\n');
}
if (process.argv.includes('--self-test')) {
  const p=csvParse('a,b\n"x,y","say ""hi"""\nz,k\n');
  assert.deepEqual(p,[{a:'x,y',b:'say "hi"'},{a:'z',b:'k'}]);
  const ex=[
    {site_id:'A',species_id:'ADPE',region:'R',method:'ground',season:'1998'},
    {site_id:'A',species_id:'ADPE',region:'R',method:'uav',season:'2010'},
    {site_id:'B',species_id:'CHPE',region:'R',method:'ground',season:'1998'},
    {site_id:'B',species_id:'CHPE',region:'R',method:'ground',season:'2010'}
  ];
  const q=buildCohort(ex);
  assert.equal(q.length,2);assert.equal(q.filter(x=>!x.has_some_same_method).length,1);
  assert.equal(q.filter(x=>x.strict_single_shared_method).length,1);
  console.log('PASS method source reconciliation unit test');
  process.exit(0);
}
const outDir=process.argv[2] || 'build/penguin_method_cohort_20261116';
const raw=readFileSync(SRC);
assert.equal(blobSha1(raw),SHA,'Pinned original source blob changed; stop');
const all=csvParse(raw.toString('utf8'));
assert.equal(all.length,2999);
const focal=all.filter(x=>TAXA.includes(x.species_id));
assert.equal(focal.length,2861);
const valid=focal.filter(x=>x.n_methods==='1'&&x.method.trim()!==''&&x.method.trim()!=='unknown'
  && x.count.trim()!==''&&Number.isFinite(+x.count)&&+x.count>=0);
assert.equal(valid.length,2724);
assertUnique(valid);

// Exactly reproduce the earlier source-builder policy:
// the most frequently recorded known method, with lexical tie-breaking,
// is selected over the FULL series of site-by-species years.
const groups=new Map();
for (const r of valid) {
  const k=key(r);if (!groups.has(k)) groups.set(k,new Map());
  const freq=groups.get(k);freq.set(r.method,(freq.get(r.method)||0)+1);
}
const selected=new Map([...groups].map(([k,f])=>
  [k,[...f].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))[0][0]]));
const fixedRows=valid.filter(x=>x.method===selected.get(key(x)));
assert.equal(fixedRows.length,2456);

const any=buildCohort(focal), eligible=buildCohort(valid), fixed=buildCohort(fixedRows);
const strict=eligible.filter(x=>x.strict_single_shared_method);
const noCommon=eligible.filter(x=>!x.has_some_same_method);
const fixedKeys=new Set(fixed.map(x=>x.site_id+'|'+x.species));
const lostShared=eligible.filter(x=>x.has_some_same_method&&!fixedKeys.has(x.site_id+'|'+x.species));
assert.deepEqual([any.length,eligible.length,fixed.length,strict.length,noCommon.length,lostShared.length],
  [283,268,159,96,107,2]);
assert.deepEqual(summary(eligible).per_species,{ADPE:103,CHPE:114,GEPE:51});
assert.deepEqual(summary(fixed).per_species,{ADPE:64,CHPE:51,GEPE:44});
assert(eligible.every(x=>x.has_some_same_method || !fixedKeys.has(x.site_id+'|'+x.species)));
assert(strict.every(x=>fixedKeys.has(x.site_id+'|'+x.species)));
assert.deepEqual(lostShared.map(x=>x.site_id+'|'+x.species).sort(),['GLAN|GEPE','LOUB|GEPE']);

const roster=eligible.map(x=>({
  ...x,
  in_most_frequent_method_159:fixedKeys.has(x.site_id+'|'+x.species),
  selected_method_by_full_series:selected.get(x.site_id+'|'+x.species)
}));
const receipt={
  status:'PASS_PINNED_METHOD_COHORT_RECONCILIATION_265_NOT_REPRODUCED',
  original_derived_source:SRC, original_git_blob_sha1:SHA,
  source_rows:all.length, focal_rows:focal.length, known_single_method_rows:valid.length,
  frozen_most_frequent_method_rows:fixedRows.length,
  early_seasons:EARLY, late_seasons:LATE,
  candidate_cohorts:{
    any_unambiguous_rows:summary(any),
    each_year_known_single_method:summary(eligible),
    frozen_most_frequent_method:summary(fixed),
    one_identical_method_through_both_periods:summary(strict),
    no_common_method_in_early_vs_late:summary(noCommon)
  },
  audit:{
    n_268_not_159:eligible.length-fixed.length,
    no_cross_period_shared_method:noCommon.length,
    some_shared_method_but_lost_to_dominant_method:lostShared.length,
    two_site_species_lost_despite_common_method:lostShared.map(x=>x.site_id+'|'+x.species)
  },
  externally_reported_265_unverified:{n:265,per_species:{ADPE:102,CHPE:116,GEPE:47}},
  exact_265_row_roster_or_generation_filters_verified:false,
  original_full_MAPPPD5_5487_observations_reanalyzed:false,
  climate_effect_reproduced:false, future_demographic_prediction:false,
  inference_boundary:'Method-dependent sampling denominator in frozen DERIVED 2999-row file only; no historical climate slope or new animal observations.'
};
mkdirSync(outDir,{recursive:true});
writeCSV(join(outDir,'known_method_268_site_species_roster.csv'),roster);
writeFileSync(join(outDir,'method_cohort_reconciliation.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({status:receipt.status,series_283:any.length,series_268:eligible.length,
  series_159:fixed.length,strict_96:strict.length,method_switch_107:noCommon.length,
  other_excluded_2:lostShared.length,output:outDir}));