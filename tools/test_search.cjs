const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),path=require('path');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'source/catalog.js'),'utf8');
const ctx=vm.createContext({console});vm.runInContext(source.split('// End pure search functions.')[0],ctx);
const fields=(...xs)=>({search_fields:xs});
const score=(r,q)=>ctx.searchScore(r,ctx.searchGroups(q));
assert.equal(score(fields('reconciliation','','','',''),'对账'),10);
assert.equal(score(fields('','核对银行交易','','',''),'对账'),6);
assert.equal(score(fields('','','reconcile-statements','',''),'对账'),4);
assert.equal(score(fields('','','','reconcile balances',''),'对账'),2);
assert.equal(score(fields('','','','','references/reconciliation.md'),'对账'),1);
assert.equal(score(fields('invoice PDF','','','',''),'发票 PDF'),20);
assert.equal(score(fields('invoice','','','',''),'发票 PDF'),0,'Every query word must match');
assert.ok(ctx.exactScore(fields('','对账','','',''),'对账')>ctx.exactScore(fields('','核对','','',''),'对账'),'Exact terms break synonym ties');
assert.equal(score(fields('DUCKDB','','','',''),'DuckDB'),10);
assert.equal(score(fields('','Data lineage','','',''),'血缘'),6);
assert.equal(score(fields('pdf pdf pdf','','','',''),'PDF'),10,'Repeated mentions never inflate relevance');
const dup=ctx.deduplicate([{id:1,file:'a',sha256:'same',duplicates:['b']},{id:2,file:'b',sha256:'same'},{id:3,file:'c'},{id:4,file:'d'}]);assert.equal(dup.length,3);assert.deepEqual(Array.from(dup[0].duplicates),['b']);
assert.ok(ctx.defaultOrder({file:'z',summary_zh:'分析输入',skills:[{}]},{file:'a',summary_zh:'主要用于财务，可查找任务',skills:[{}]})<0);
const siteDir=path.join(root,process.env.CATALOG_SITE||'site');const listPath=path.join(siteDir,'data/list.json');const data=JSON.parse(fs.readFileSync(fs.existsSync(listPath)?listPath:path.join(siteDir,'catalog.json'),'utf8'));
const records=ctx.deduplicate(data.records);let index={};if(data.search_url)index=JSON.parse(fs.readFileSync(path.join(siteDir,data.search_url),'utf8'));
for(const r of records){r._title=r.title||r._title||r.plugins?.find(p=>p.displayName)?.displayName||r.file;r.search_fields=index[r.id]||r.search_fields}
for(const query of ['对账','血缘','PDF','DuckDB']){const top=records.filter(r=>score(r,query)).sort((a,b)=>score(b,query)-score(a,query)||ctx.exactScore(b,query)-ctx.exactScore(a,query)||ctx.defaultOrder(a,b)).slice(0,3);assert.equal(top.length,3);for(const r of top){assert.ok(score({...r,search_fields:ctx.searchFields(r).slice(0,3)},query)>=4,`${query}: top result ${r.file} must match title, summary, taxonomy or skill name`)}console.log(query+': '+top.map(r=>r._title+' ['+score(r,query)+']').join(' | '))}
console.log('PASS: weighted field priority, synonyms, AND queries, case folding, repeat resistance, SHA dedup, default quality, live top-three relevance');
