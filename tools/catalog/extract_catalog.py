#!/usr/bin/env python3
"""Read ZIP metadata as data; never import or execute package code."""
import concurrent.futures as cf
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '目录报告'
OUT.mkdir(exist_ok=True)

def clean(s):
    s = str(s or '')
    s = re.sub(r'(?i)(bearer\s+|(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*)[^\s,;]+', r'\1[已隐藏]', s)
    return s.replace('\x00', '')

def readtext(z, n, limit=60000, redact=True):
    if z.getinfo(n).file_size > 2_000_000:
        return ''
    text = z.read(n).decode('utf-8', errors='replace')[:limit]
    return clean(text) if redact else text

def fm(text):
    if not text.startswith('---'):
        return {}
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}
    result = {}
    lines = parts[1].splitlines()
    key = None
    for line in lines:
        m = re.match(r'^([\w-]+):\s*(.*)', line)
        if m:
            key, val = m.groups()
            result[key] = val.strip().strip('\"\'')
        elif key and line.startswith((' ', '\t')):
            result[key] += ' ' + line.strip()
    for k, v in result.items():
        result[k] = re.sub(r'^[>|][-+]?\s*', '', v).strip()
    return result

def extract(p):
    r = {'file': p.name, 'bytes': p.stat().st_size, 'status': '已读取', 'plugins': [], 'skills': [], 'commands': [], 'readmes': [], 'mcp_servers': [], 'config_names': [], 'paths': [], 'sha256': '', 'scanner_version': 2}
    try:
        with zipfile.ZipFile(p) as z:
            ns = [n for n in z.namelist() if not n.endswith('/')]
            r['paths'] = ns
            r['file_count'] = len(ns)
            for n in ns:
                low = n.lower()
                if low.endswith('/plugin.json') or low == 'plugin.json':
                    try:
                        j = json.loads(readtext(z, n, redact=False))
                        if isinstance(j, dict):
                            r['plugins'].append({'path': n, **{k: j[k] for k in ['name', 'displayName', 'description', 'version', 'license', 'repository', 'homepage', 'keywords'] if k in j}})
                            if isinstance(j.get('mcpServers'), dict): r['mcp_servers'] += list(j['mcpServers'])
                            if isinstance(j.get('userConfig'), dict): r['config_names'] += list(j['userConfig'])
                    except Exception:
                        pass
                if low.endswith('skill.md'):
                    t = readtext(z, n)
                    f = fm(t)
                    heads = re.findall(r'^#{1,3}\s+(.+)', t, re.M)
                    body = t.split('---', 2)[-1] if t.startswith('---') else t
                    r['skills'].append({'path': n, 'name': f.get('name') or Path(n).parent.name, 'description': f.get('description', ''), 'headings': heads[:18], 'excerpt': body[:2600]})
                if '/commands/' in '/' + low and low.endswith('.md'):
                    t = readtext(z, n)
                    f = fm(t)
                    r['commands'].append({'path': n, 'name': Path(n).stem, 'description': f.get('description', ''), 'headings': re.findall(r'^#{1,3}\s+(.+)', t, re.M)[:8]})
                if Path(low).name in ['readme.md', 'readme', 'readme.txt', 'readme.zh-cn.md', 'readme_zh.md']:
                    t = readtext(z, n, 18000)
                    r['readmes'].append({'path': n, 'text': t, 'headings': re.findall(r'^#{1,3}\s+(.+)', t, re.M)[:30]})
                if Path(low).name in ['.mcp.json', 'mcp.json']:
                    try:
                        j = json.loads(readtext(z, n, redact=False))
                        servers = j.get('mcpServers', j.get('servers', {}))
                        if isinstance(servers, dict):
                            r['mcp_servers'] += list(servers)
                    except Exception:
                        pass
            r['readmes'].sort(key=lambda x: (x['path'].count('/'), len(x['path'])))
        r['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception as e:
        r['status'] = '读取失败'
        r['error'] = str(e)[:300]
    return r

def main():
    fs = sorted(ROOT.glob('*.zip'), key=lambda p: p.name.casefold())
    existing = {}
    cache = OUT / '原始扫描.jsonl'
    if cache.exists():
        for line in cache.read_text().splitlines():
            try:
                r = json.loads(line)
                if r['status'] == '已读取' and r.get('scanner_version') == 2: existing[r['file']] = r
            except Exception:
                pass
    local = [p for p in fs if p.stat().st_blocks > 0 and p.name not in existing]
    print(f'总数 {len(fs)}；已缓存 {len(existing)}；本地待扫描 {len(local)}；占位 {sum(p.stat().st_blocks == 0 for p in fs)}', flush=True)
    with cache.open('a', encoding='utf-8') as sink, cf.ThreadPoolExecutor(max_workers=8) as ex:
        for i, r in enumerate(ex.map(extract, local), 1):
            sink.write(json.dumps(r, ensure_ascii=False) + '\n'); sink.flush()
            existing[r['file']] = r
            if i % 100 == 0: print(f'新增读取 {i}/{len(local)}', flush=True)
    rs = []
    for p in fs:
        rs.append(existing.get(p.name) or {'file':p.name, 'bytes':p.stat().st_size, 'status':'iCloud占位待读取', 'plugins':[], 'skills':[], 'commands':[], 'readmes':[], 'mcp_servers':[], 'paths':[], 'sha256':''})
    (OUT / '完整扫描.json').write_text(json.dumps(rs, ensure_ascii=False, indent=2))
    # Keep one checkpoint per successfully read package, avoiding old scanner
    # versions and repeated cache entries from growing the report indefinitely.
    cache.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rs if r['status']=='已读取'), encoding='utf-8')
    print(f'已生成完整扫描：{len(rs)} 项；已读取 {sum(r["status"] == "已读取" for r in rs)}', flush=True)

if __name__ == '__main__':
    main()
