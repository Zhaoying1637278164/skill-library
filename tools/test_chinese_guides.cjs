const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),path=require('path');
const root=path.join(__dirname,'..');const data=JSON.parse(fs.readFileSync(path.join(root,'site/catalog.json'),'utf8'));
const context=vm.createContext({console,esc:s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))});
vm.runInContext(fs.readFileSync(path.join(root,'source/guides.js'),'utf8'),context);
let count=0;
for(const r of data.records){r._title=r.file;for(const s of [null,...r.skills]){const g=context.guideData(r,s);assert.ok(g.prepare.length&&g.steps.length&&g.prompt&&g.basis);assert.ok(context.guideContent(r,s).includes('复制中文问法'));count++}}
const bank=data.records.find(r=>r.id===193),skill=bank.skills.find(s=>s.name==='analyze-spending');const g=context.guideData(bank,skill);
assert.match(g.prepare[0],/已转换/);assert.match(g.steps.join(' '),/categorize_statement/);assert.match(g.boundary,/首次 PDF/);assert.match(g.prompt,/content_hash/);
assert.equal(context.guideData({...bank,id:99999},skill).specific,undefined,'Do not attribute a reviewed workflow to an unrelated package');
const html=context.guideContent({...bank,_title:'<script>test</script>'},{...skill,name:'<img onerror=bad>'});assert.ok(!html.includes('<img onerror=bad>'));
console.log('PASS: '+count+' package/skill guides; source-specific boundaries, citations and HTML escaping');
