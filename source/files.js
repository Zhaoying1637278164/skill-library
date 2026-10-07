// Original-file browser. Archive contents are treated only as data.
const zipCache=new Map();let viewFile=null,viewBytes=null,viewRecord=null,viewVersion=0,fileLimit=100;
const TEXT_EXT=/\.(md|txt|json|jsonl|csv|tsv|yaml|yml|toml|ini|cfg|conf|py|js|jsx|ts|tsx|html|css|sql|sh|bash|zsh|xml|svg|rst|log|go|rs|java|c|h|cpp|r|rb|ps1|ipynb|env)$/i;
function fileActions(r,path){return r.asset_url?`<div class="file-actions"><button data-read="${esc(path)}">查看原始文件 ↗</button><button data-download-file="${esc(path)}">下载此文件 ↓</button></div>`:'<p class="small">原始文件尚未取回，暂时仅可查看目录说明。</p>'}
function skillDetail(r){return `<h3>全部技能 · ${r.skills.length} 条</h3><p class="small">点击查看原始文件，即可在网站内阅读完整 SKILL.md。</p>${r.skills.map(s=>`<div class="skill"><b>${esc(s.name)}</b><p class="small">${esc(s.name_hint)}</p><p>${esc(s.description||'主要章节：'+s.headings.join(' / '))}</p><code>${esc(s.path)}</code>${fileActions(r,s.path)}</div>`).join('')||'<p>未识别到 SKILL.md；可在文件清单中查找。</p>'}<h3>全部命令 · ${r.commands.length} 条</h3>${r.commands.map(s=>`<div class="skill"><b>${esc(s.name)}</b><p>${esc(s.description||s.headings.join(' / '))}</p><code>${esc(s.path)}</code>${fileActions(r,s.path)}</div>`).join('')||'<p>未识别到命令说明。</p>'}`}
function fileDetail(r){return `<div class="archive-bar"><div><h3>原始压缩包</h3><p>${esc(r.file)} · ${(r.bytes/1048576).toFixed(2)} MB</p></div><button data-zip ${r.asset_url?'':'disabled'}>下载完整 ZIP ↓</button></div><p class="small">${r.asset_url?'原包已就绪。文件内容完整保留，在线阅读不需要先下载 ZIP。':'原包尚未从 iCloud 取回，暂不可下载。'}</p><h3>全部原始文件 · ${(r.members||r.paths).length} 个</h3><input id="fileQuery" class="file-query" aria-label="筛选包内文件" placeholder="搜索文件名、目录或后缀，例如 SKILL.md / references / .py"><div id="fileList"></div><p class="small hash">原包 SHA-256：${esc(r.asset_sha256||r.sha256||'待核验')}</p>`}
async function zipBytes(r){
 if(!r.asset_url)throw Error('此原包暂不可下载。');
 if(zipCache.has(r.asset_sha256))return zipCache.get(r.asset_sha256);
 const response=await fetch(r.asset_url);if(!response.ok)throw Error('原包请求失败（'+response.status+'）。');
 const bytes=new Uint8Array(await response.arrayBuffer());
 const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(v=>v.toString(16).padStart(2,'0')).join('');
 if(sha!==r.asset_sha256)throw Error('原包校验不通过，请刷新后重试。');
 let sum=bytes.length;for(const b of zipCache.values())sum+=b.length;
 if(sum>64*1048576)zipCache.clear();zipCache.set(sha,bytes);return bytes;
}
async function memberBytes(r,path){
 const info=r.members?.find(m=>m.path===path);if(!info)throw Error('未找到原始文件。');
 if(info.size>50*1048576)throw Error('此文件超过 50 MB，请下载完整 ZIP。');
 const data=fflate.unzipSync(await zipBytes(r),{filter:m=>m.name===path});
 if(!Object.prototype.hasOwnProperty.call(data,path))throw Error('原包中未找到此路径。');
 if(data[path].length!==info.size)throw Error('原始文件大小校验失败。');return data[path];
}
function downloadBytes(bytes,name,type='application/octet-stream'){
 const url=URL.createObjectURL(new Blob([bytes],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.rel='noopener';a.textContent='保存 '+name+' ↓';a.className='save-original';const host=$('fileViewer').open?$('viewerStatus'):$('fileFeedback');host.querySelectorAll('a').forEach(old=>old.remove());host.append(a);a.click();setTimeout(()=>{a.remove();URL.revokeObjectURL(url)},300000);
}
async function runDownload(button,r,path){const text=button.textContent;button.disabled=true;button.textContent='正在准备…';try{downloadBytes(path?await memberBytes(r,path):await zipBytes(r),path?path.split('/').pop():r.file)}catch(e){($('fileViewer').open?$('viewerStatus'):$('fileFeedback')).textContent=e.message}finally{button.textContent=text;button.disabled=false}}
function decodeOriginal(bytes){
 if(bytes[0]===255&&bytes[1]===254)return new TextDecoder('utf-16le').decode(bytes);
 if(bytes[0]===254&&bytes[1]===255)return new TextDecoder('utf-16be').decode(bytes);
 try{return new TextDecoder('utf-8',{fatal:true}).decode(bytes)}catch{return new TextDecoder('gb18030').decode(bytes)}
}
async function openOriginal(r,path){
 const version=++viewVersion;viewRecord=r;viewFile=path;viewBytes=null;
 const rawLink=new URL(new URLSearchParams(location.search).get('streamlitUrl')||(window.parent!==window?document.referrer:location.href)||location.href);rawLink.searchParams.set('package',r.id);rawLink.searchParams.set('file',path);rawLink.hash='';$('viewerLink').href=rawLink.href;
 $('viewerTitle').textContent=path.split('/').pop();$('viewerPath').textContent=r._title+' / '+path;
 $('viewerStatus').textContent='正在读取完整原文…';$('sourceText').textContent='';$('sourceText').hidden=false;$('viewerDownload').disabled=true;$('fileViewer').showModal();
 try{
  const info=r.members.find(m=>m.path===path);
  if(info.size>5*1048576){$('viewerStatus').textContent='此文件大于 5 MB，可单独下载原文件。';$('viewerDownload').disabled=false;return}
  const bytes=await memberBytes(r,path);if(version!==viewVersion)return;viewBytes=bytes;$('viewerDownload').disabled=false;
  const text=decodeOriginal(bytes);const isText=TEXT_EXT.test(path)||(!bytes.subarray(0,4096).includes(0)&&!/[\u0000-\u0008]/.test(text.slice(0,4096)));
  if(!isText){$('viewerStatus').textContent='二进制文件 · '+bytes.length.toLocaleString()+' 字节 · 可单独下载原文件';$('sourceText').hidden=true;return}
  $('sourceText').textContent=text;$('viewerStatus').textContent='完整原文 · '+text.split('\n').length.toLocaleString()+' 行 · '+bytes.length.toLocaleString()+' 字节';
 }catch(e){if(version===viewVersion)$('viewerStatus').textContent='读取失败：'+e.message}
}
function bindFiles(){
 $('fileFeedback').textContent='';
 $('detailBody').querySelectorAll('[data-read]').forEach(b=>b.onclick=()=>openOriginal(selected,b.dataset.read));
 $('detailBody').querySelectorAll('[data-download-file]').forEach(b=>b.onclick=()=>runDownload(b,selected,b.dataset.downloadFile));
 const z=$('detailBody').querySelector('[data-zip]');if(z)z.onclick=()=>runDownload(z,selected);
 if($('fileQuery')){$('fileQuery').oninput=()=>{fileLimit=100;renderFiles()};renderFiles()}
}
function renderFiles(){
 const words=$('fileQuery').value.toLowerCase().split(/\s+/).filter(Boolean),paths=(selected.members?.map(m=>m.path)||selected.paths).filter(p=>words.every(w=>p.toLowerCase().includes(w)));
 $('fileList').innerHTML=`<p class="small">${paths.length} 个匹配文件</p>`+paths.slice(0,fileLimit).map(p=>`<div class="file-row"><code title="${esc(p)}">${esc(p)}</code>${fileActions(selected,p)}</div>`).join('')+(paths.length>fileLimit?'<button id="moreFiles">显示更多文件 ↓</button>':'');
 $('fileList').querySelectorAll('[data-read]').forEach(b=>b.onclick=()=>openOriginal(selected,b.dataset.read));
 $('fileList').querySelectorAll('[data-download-file]').forEach(b=>b.onclick=()=>runDownload(b,selected,b.dataset.downloadFile));
 if($('moreFiles'))$('moreFiles').onclick=()=>{fileLimit+=100;renderFiles()};
}
const originalDetailTab=detailTab;detailTab=function(){originalDetailTab();bindFiles()};
$('closeViewer').onclick=()=>$('fileViewer').close();$('fileViewer').addEventListener('close',()=>{viewVersion++;viewBytes=null});
$('viewerDownload').onclick=()=>viewBytes?downloadBytes(viewBytes,viewFile.split('/').pop()):runDownload($('viewerDownload'),viewRecord,viewFile);
if(window.parent!==window){window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:componentReady',apiVersion:1},'*');window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:900},'*')}

let linkedFileOpened=false;function openLinkedFile(args){if(linkedFileOpened||!args?.package||!args?.file)return;const r=R.find(x=>String(x.id)===String(args.package));if(!r||!r.asset_url||!r.members?.some(m=>m.path===args.file))return;linkedFileOpened=true;openDetail(r.id);openOriginal(r,args.file)}
window.addEventListener('message',e=>{if(e.source===window.parent&&e.data?.type==='streamlit:render')openLinkedFile(e.data.args)});if(window.parent===window)openLinkedFile(Object.fromEntries(new URLSearchParams(location.search)));
