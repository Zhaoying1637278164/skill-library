const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const fflate=require(require('path').join(__dirname,'../site/vendor/fflate.min.js'));
const raw=Buffer.from('---\nname: 示例\n---\n<script>throw Error("must never execute")</script>\n全文末尾\n');
const packed=fflate.zipSync({'skills/示例/SKILL.md':raw});
const sha=crypto.createHash('sha256').update(packed).digest('hex');
let fetches=0;const elements=new Map();
function $(id){if(!elements.has(id))elements.set(id,{textContent:'',hidden:false,disabled:false,open:false,showModal(){this.open=true},addEventListener(){},querySelectorAll(){return []}});return elements.get(id)}
const context=vm.createContext({console,TextDecoder,Uint8Array,URL,URLSearchParams,Blob,setTimeout,fflate,
 crypto:crypto.webcrypto,$,R:[],detailTab(){},location:{href:'http://localhost/library',search:''},
 document:{referrer:'http://localhost/app'},window:{parent:{postMessage(){}},addEventListener(){}},
 fetch:async()=>{fetches++;return {ok:true,arrayBuffer:async()=>packed.buffer.slice(packed.byteOffset,packed.byteOffset+packed.byteLength)}}});
vm.runInContext(fs.readFileSync(require('path').join(__dirname,'../source/files.js'),'utf8'),context);
const r={id:1,_title:'测试包',asset_url:'packages/test.zip',asset_sha256:sha,members:[{path:'skills/示例/SKILL.md',size:raw.length}]};
(async()=>{
 assert.deepEqual(Buffer.from(await context.memberBytes(r,r.members[0].path)),raw);
 await context.openOriginal(r,r.members[0].path);assert.equal($('sourceText').textContent,raw.toString('utf8'));assert.ok($('sourceText').textContent.endsWith('全文末尾\n'));
 assert.ok($('viewerLink').href.startsWith('http://localhost/app?package=1&file='));
 assert.equal(fetches,1,'Verified ZIP should be reused');
 await assert.rejects(context.zipBytes({...r,asset_sha256:'bad'}),/校验不通过/);
 await assert.rejects(context.memberBytes(r,'../unknown'),/未找到/);
 await assert.rejects(context.memberBytes({...r,members:[{path:r.members[0].path,size:raw.length+1}]},r.members[0].path),/大小校验失败/);
 await assert.rejects(context.memberBytes({...r,members:[{path:r.members[0].path,size:51*1048576}]},r.members[0].path),/50 MB/);
 console.log('PASS: original bytes, complete Unicode text, inert HTML source, cache, tamper rejection, unknown paths, size mismatch and decompression bound');
})().catch(e=>{console.error(e);process.exitCode=1});
