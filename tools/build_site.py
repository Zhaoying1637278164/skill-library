from pathlib import Path
import json,tarfile,zipfile,re,hashlib,csv
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'; SRC=ROOT/'source'
data=json.loads((SITE/'catalog.json').read_text()); assets={r['id']:r for r in json.loads((ROOT/'assets.json').read_text())}
# High-confidence credential signatures only; report paths, never values.
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'\bAKIA[A-Z0-9]{16}\b',rb'\bgh[pousr]_[A-Za-z0-9]{36,}\b',rb'\bgithub_pat_[A-Za-z0-9_]{70,}\b',rb'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{40,}\b']
findings=[]; checked=0
reviewed=json.loads((ROOT/'reviewed_examples.json').read_text())
for a in assets.values():
 if not a.get('asset_url'):continue
 with zipfile.ZipFile(SITE/a['asset_url']) as z:
  for m in z.infolist():
   if m.is_dir() or m.file_size>5*1048576:continue
   if not re.search(r'\.(md|txt|json|py|js|ts|yml|yaml|toml|env|pem|key|sh|ini|cfg|conf)$|(?:^|/)\.env',m.filename,re.I):continue
   checked+=1;b=z.read(m)
   if any(re.search(p,b) for p in patterns) and hashlib.sha256(b).hexdigest() not in reviewed:findings.append({'id':a['id'],'path':m.filename})
blocked={r['id'] for r in findings}
for r in data['records']:
 a=assets.get(r['id'],{})
 if r['id'] in blocked:
  r['asset_error']='包内发现待核实的凭据格式，暂缓公开原文件。'
 else:
  r.update({k:v for k,v in a.items() if k!='id'})
for r in data['records']:
 for item in r['skills']+r['commands']:item.pop('excerpt',None)
 for item in r['readmes']:item.pop('text',None)
data['stats']['downloads']=sum(bool(r.get('asset_url')) for r in data['records'])
data['stats']['download_pending']=len(data['records'])-data['stats']['downloads']
SITE.mkdir(exist_ok=True);(SITE/'vendor').mkdir(exist_ok=True)
viewer='''<dialog id="fileViewer" class="source-viewer" aria-labelledby="viewerTitle"><header class="viewer-head"><div><h2 id="viewerTitle"></h2><p id="viewerPath"></p></div><div class="file-actions"><a id="viewerLink" target="_blank" rel="noopener">打开原文链接 ↗</a><button id="viewerDownload">下载原文件 ↓</button><button id="viewerZip">下载完整包 ↓</button><button id="closeViewer" aria-label="关闭原文">×</button></div></header><nav class="viewer-tabs"><button id="showSource">原始文件</button><button id="showGuide">中文怎么用</button></nav><div id="sourceScroll" class="reader-scroll"><div class="viewer-info" id="viewerStatus" role="status"></div><div id="viewerGuide" hidden></div><pre id="sourceText"></pre><p id="sourceEnd" class="source-end">— 已到原文件末尾 —</p></div></dialog>'''
html=(SRC/'catalog.html').read_text()
html=html.replace('<div id="detailBody" class="detail-body"></div></dialog>','<div id="detailBody" class="detail-body"></div><div id="fileFeedback" role="status"></div></dialog>')
html=html.replace('<script id="data"',viewer+'<script src="vendor/fflate.min.js"></script><script id="data"')
html=html.replace('COLLECTION / 本地收藏','COLLECTION / 公开收藏').replace('可离线浏览 · 原始资料完整保留','公开浏览 · 原文阅读与下载')
js=(SRC/'catalog.js').read_text()
# Main dialogs render the additional handlers supplied in files.js.
js=js.replace(' · 分类按资料推定，功能未运行验收`',' · ${S.downloads||0} 个原包可下载 · 分类按资料推定，功能未运行验收`')
js=js.replace('<h3>下载完整资料</h3>','<h3>原文与下载</h3><p>已就绪 ${S.downloads||0} 个原包。技能页可阅读全文；文件清单可筛选、阅读并单独下载。ZIP 与单文件均保留原始字节。原包尚未取回时明确标记，不提供无效入口。</p><h3>下载完整资料</h3>')
html=html.replace('__CSS__',(SRC/'catalog.css').read_text()+'\n'+(SRC/'files.css').read_text()).replace('__JS__',js+'\n'+(SRC/'guides.js').read_text()+'\n'+(SRC/'files.js').read_text())
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
html=html.replace('__DATA__',payload)
(SITE/'index.html').write_text('<!doctype html>'+html)
(SITE/'catalog.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
with (SITE/'目录总表.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['编号','文件','领域','场景','能帮你做什么','技能数量','原包可下载'])
 for r in data['records']:w.writerow([r['id'],r['file'],r['category'],r['scene'],r['summary_zh'],len(r['skills']),bool(r.get('asset_url'))])
with (SITE/'技能明细.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['包','技能','原始路径','用途'])
 for r in data['records']:
  for s in r['skills']:w.writerow([r['file'],s['name'],s['path'],s['description']])
with (SITE/'分类目录.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['包','领域','场景','具体任务'])
 for r in data['records']:
  for t in r['taxons']:w.writerow([r['file'],*t])
with (SITE/'待读取清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['原包','目录状态','下载状态'])
 for r in data['records']:
  if r['status']!='已读取' or not r.get('asset_url'):w.writerow([r['file'],r['status'],r.get('asset_error',r.get('error','原文件尚未取回'))])
report={'total':len(data['records']),'downloads':data['stats']['downloads'],'pending':data['stats']['download_pending'],'text_files_scanned':checked,'credential_pattern_findings':findings}
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'README.md').write_text(f'''# 技能书架

公开的插件与技能资料目录，支持三级任务分类、搜索、完整原文阅读、单文件下载及原 ZIP 下载。

覆盖 {len(data['records'])} 个目录记录；当前 {data['stats']['downloads']} 个原包已复制并核验。未取回的文件明确标记。

## 运行

Python 3.12：`pip install -r requirements.txt`，然后 `streamlit run streamlit_app.py`。

静态前端来自既有目录，原始包按 SHA-256 命名，仅做静态内容浏览，不执行包内代码。文本以纯文本方式显示，HTML/SVG 不作为页面运行。 ZIP 下载和单文件下载保留原始字节。

第三方 ZIP 文件中的声明与许可由原作者保留；fflate 0.8.2 为 MIT，许可见 `site/vendor/fflate-LICENSE.txt`。

验证记录见 `verification.json`。如目录元数据已读取而原包仍是 iCloud 占位文件，站点仍显示目录说明，但下载入口禁用。
''')
print(json.dumps(report,ensure_ascii=False))

import sys
sys.path.insert(0,str(ROOT/'tools/catalog'))
import build_catalog
build_catalog.OUT=SITE
build_catalog.build_md(data['records'],data['stats'])
