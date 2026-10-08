from pathlib import Path
import argparse, json, re, csv, sys
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source'
GENERATED=ROOT/'tools/catalog/generated'

def template_summary(text):
 return bool(re.search(r'主要用于.*可查找.*(?:相关技能或服务|具体操作范围见包内说明)',text))

def validate_editorial(data):
 templates=[{'id':r['id'],'file':r['file']} for r in data['records'] if template_summary(r.get('summary_zh',''))]
 missing=[{'file':r['file'],'path':s['path']} for r in data['records'] for s in r['skills'] if not s.get('description_zh')]
 invalid=[{'file':r['file'],'path':s['path']} for r in data['records'] for s in r['skills'] if Path(s['path'].lower()).name!='skill.md']
 return {'template_summaries':templates,'missing_skill_chinese':missing,'invalid_skills':invalid}

def product_title(r):
 return next((p['displayName'] for p in r['plugins'] if p.get('displayName')),None) or re.sub(r'-(?:\d[\w.]*-)?v\d+$','',re.sub(r' \(\d+\)$','',re.sub(r'\.zip$','',r['file'],flags=re.I)),flags=re.I).replace('_',' ')

def search_fields(r):
 return [' '.join([r['title'],r['file']]),' '.join([r['summary_zh'],*[v for t in r['taxons'] for v in t]]),' '.join(s['name'] for s in r['skills']),' '.join([r.get('description',''),*[s.get('description_zh','')+' '+s.get('description','') for s in r['skills']+r['commands']]]),' '.join(r['paths'])]

def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 text=json.dumps(value,ensure_ascii=False,separators=(',',':'))
 if path.exists() and path.read_text(encoding='utf-8')==text:return
 temporary=path.with_suffix(path.suffix+'.tmp')
 temporary.write_text(text,encoding='utf-8')
 temporary.replace(path)

def render_shell(site,preview,errors,editorial_notice=False):
 html=(SRC/'catalog.html').read_text()
 vendor='../site/vendor/fflate.min.js' if preview else 'vendor/fflate.min.js'
 html=html.replace('<script id="data" type="application/json">__DATA__</script>','<script src="'+vendor+'"></script>')
 js='const PACKAGE_EDITORIAL='+(SRC/'package-editorial.json').read_text()+';\n'+'const SKILL_LABELS='+(SRC/'skill-labels.json').read_text()+';\n'+'const ICONS='+ (SRC/'icons.json').read_text()+';\n'+(SRC/'marked.js').read_text()+'\n'+(SRC/'catalog.js').read_text()+'\n'+(SRC/'guides.js').read_text()+'\n'+(SRC/'files.js').read_text()
 html=html.replace('__CSS__',(SRC/'catalog.css').read_text()+'\n'+(SRC/'files.css').read_text()).replace('__JS__',js)
 (site/'topics.json').write_text((SRC/'topics.json').read_text(),encoding='utf-8')
 if preview or editorial_notice:
  label='本地预览：' if preview else '中文说明完善中：'
  html=html.replace('<body>','<body><div class="preview-status">'+label+str(len(errors['template_summaries']))+' 个摘要与 '+str(len(errors['missing_skill_chinese']))+' 条技能中文说明仍待完成</div>')
 (site/'index.html').write_text(html,encoding='utf-8')

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--output-dir',type=Path,help='构建到独立发布目录，便于验证后部署')
 parser.add_argument('--allow-incomplete-editorial',action='store_true',help='在明确授权发布当前页面时保留未完成提示；不放行伪技能')
 parser.add_argument('--preview-incomplete',action='store_true',help='仅生成带未完成标记的本地preview，不写部署site')
 parser.add_argument('--ui-only',action='store_true',help='只更新已有本地预览的界面，不重写目录详情')
 parser.add_argument('--reuse-catalog',action='store_true',help='仅用于界面迭代，复用已扫描目录并仍执行编辑校验')
 args=parser.parse_args()
 if args.ui_only:
  if not args.preview_incomplete:parser.error('--ui-only 只能用于本地未完成预览')
  site=ROOT/'preview'
  if not (site/'data/list.json').exists():parser.error('请先完成一次数据构建')
  errors=json.loads((GENERATED/'编辑校验.json').read_text())
  render_shell(site,True,errors)
  report=json.loads((site/'构建验收.json').read_text())
  sizes=report['sizes'];sizes.update(html_bytes=(site/'index.html').stat().st_size,topics_bytes=(site/'topics.json').stat().st_size)
  sizes['first_load_bytes']=sum(sizes[k] for k in ['html_bytes','list_bytes','vendor_bytes','topics_bytes'])
  if sizes['first_load_bytes']>3_000_000:raise ValueError('首页体积超过预算')
  report['ui_only']=True
  report['editorial_errors']={k:len(v) for k,v in errors.items()}
  dump(site/'构建验收.json',report)
  print(json.dumps(report,ensure_ascii=False));return 0
 sys.path.insert(0,str(ROOT/'tools/catalog'))
 import extract_catalog, build_catalog
 if not (GENERATED/'完整扫描.json').exists():extract_catalog.main()
 if not args.reuse_catalog:build_catalog.main()
 data=json.loads((GENERATED/'catalog.json').read_text())
 errors=validate_editorial(data)
 dump(GENERATED/'编辑校验.json',errors)
 if errors['invalid_skills'] or (any(errors.values()) and not (args.preview_incomplete or args.allow_incomplete_editorial)):
  for label,items in errors.items():
   if items:
    print(label+': '+str(len(items)))
    for item in items:print(json.dumps(item,ensure_ascii=False))
  print('编辑校验未通过，未更新部署站点。完整清单见 tools/catalog/generated/编辑校验.json')
  return 1
 site=args.output_dir or ROOT/('preview' if args.preview_incomplete else 'site')
 site.mkdir(exist_ok=True)
 assets={r['id']:r for r in json.loads((ROOT/'assets.json').read_text())}
 evidence=json.loads((ROOT/'tools/catalog/原包静态验收.json').read_text())
 blocked={r['id'] for r in evidence['verification'].get('credential_pattern_findings',[])}
 labels=json.loads((SRC/'skill-labels.json').read_text())
 for r in data['records']:
  for item in r['skills']:
   if item['name'] in labels.get(str(r['id']),{}):item['name_zh']=labels[str(r['id'])][item['name']]
  a=assets.get(r['id'],{})
  e=evidence['records'].get(str(r['id']),{})
  if a.get('asset_sha256')!=r['sha256'] or e.get('sha256')!=r['sha256']:
   raise ValueError('原包静态验收和SHA清单不一致：'+r['file'])
  r['reuse']=e.get('reuse',{})
  if r['id'] not in blocked:r.update({k:v for k,v in a.items() if k!='id'})
  else:r['asset_error']='包内发现待核实的凭据格式，暂缓公开原文件。'
  r['title']=product_title(r)
  if args.preview_incomplete and r.get('asset_url'):r['asset_url']='../site/'+r['asset_url']
 # Metadata comes from previously verified unchanged archives; browser rechecks actual SHA on every download.
 stats=data['stats'];stats.update(downloads=sum(bool(r.get('asset_url')) for r in data['records']))
 stats['download_pending']=len(data['records'])-stats['downloads']
 stats['unique_packages']=len({r['sha256'] or str(r['id']) for r in data['records']})
 stats['mcp_packages']=len({r['sha256'] or str(r['id']) for r in data['records'] if r['mcp_servers']})
 records=[];search={}
 for r in data['records']:
  search[str(r['id'])]=search_fields(r)
  light={k:r[k] for k in ['id','file','title','summary_zh','taxons','category','scene','task','status','sha256','duplicates','mcp_servers']}
  light.update(skills=[{'name':s['name']} for s in r['skills']],commands=[{'name':s['name']} for s in r['commands']],file_count=len(r['paths']),asset_url=r.get('asset_url'))
  records.append(light)
  detail={**r}
  for item in detail['skills']+detail['commands']:item.pop('excerpt',None)
  for item in detail['readmes']:item.pop('text',None)
  dump(site/'data/pkg'/f"{r['id']}.json",detail)
 dump(site/'data/list.json',{'stats':stats,'records':records,'search_url':'data/search.json'})
 dump(site/'data/search.json',search)
 render_shell(site,args.preview_incomplete,errors,editorial_notice=args.allow_incomplete_editorial)
 # Complete catalog is a build intermediate, never part of the deployed homepage.
 (site/'catalog.json').unlink(missing_ok=True)
 def write_csv(name,headers,rows):
  with (site/name).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.writer(f);w.writerow(headers);w.writerows(rows)
 write_csv('目录总表.csv',['编号','文件','领域','场景','能帮你做什么','skill 数量','原包可下载'],([r['id'],r['file'],r['category'],r['scene'],r['summary_zh'],len(r['skills']),bool(r.get('asset_url'))] for r in data['records']))
 write_csv('技能明细.csv',['包','skill','原始路径','中文用途','原始用途'],([r['file'],s['name'],s['path'],s.get('description_zh',''),s['description']] for r in data['records'] for s in r['skills']))
 write_csv('分类目录.csv',['包','领域','场景','具体任务'],([r['file'],*t] for r in data['records'] for t in r['taxons']))
 write_csv('待读取清单.csv',['原包','目录状态','下载状态'],([r['file'],r['status'],r.get('asset_error','原文件尚未取回')] for r in data['records'] if r['status']!='已读取' or not r.get('asset_url')))
 unlicensed=[r for r in data['records'] if not any(p.get('license') for p in r['plugins']) and not r['reuse'].get('licenses')]
 write_csv('无许可证清单.csv',['编号','文件','SHA-256','说明'],([r['id'],r['file'],r['sha256'],'未检出plugin许可声明或LICENSE/COPYING文件；未改变下载策略'] for r in unlicensed))
 sys.path.insert(0,str(ROOT/'tools/catalog'))
 import build_catalog
 build_catalog.OUT=site
 build_catalog.build_md(data['records'],stats)
 sizes={'html_bytes':(site/'index.html').stat().st_size,'list_bytes':(site/'data/list.json').stat().st_size,'search_bytes':(site/'data/search.json').stat().st_size,'vendor_bytes':(ROOT/'site/vendor/fflate.min.js').stat().st_size}
 sizes['topics_bytes']=(site/'topics.json').stat().st_size
 sizes['first_load_bytes']=sizes['html_bytes']+sizes['list_bytes']+sizes['vendor_bytes']+sizes['topics_bytes']
 report={'preview':args.preview_incomplete,'editorial_incomplete_disclosed':args.allow_incomplete_editorial,'stats':stats,'sizes':sizes,'unlicensed_records':len(unlicensed),'unlicensed_unique':len({r['sha256'] for r in unlicensed}),'editorial_errors':{k:len(v) for k,v in errors.items()}}
 dump(site/'构建验收.json',report)
 if sizes['list_bytes']>2_000_000 or sizes['first_load_bytes']>3_000_000:raise ValueError('首次加载体积超过预算：'+str(sizes))
 print(json.dumps(report,ensure_ascii=False))
 return 0

if __name__=='__main__':sys.exit(main())
