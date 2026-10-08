"""Audit source-linked Chinese skill descriptions without executing archives."""
import argparse, csv, hashlib, json, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHOD = '本地逐条人工意译并核对适用范围'

def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=ROOT / 'site')
    parser.add_argument('--output', type=Path, default=ROOT / 'tools/catalog/技能中文批次验收.json')
    args = parser.parse_args()
    labels = json.loads((ROOT / 'tools/catalog/技能中文说明.json').read_text())
    scanned = json.loads((ROOT / 'tools/catalog/generated/catalog.json').read_text())
    originals = {(r['id'], s['path']): s for r in scanned['records'] for s in r['skills']}
    sources = {(r['file'], s['path']): (r, s) for r in scanned['records'] for s in r['skills']}
    for key, entry in labels['translations'].items():
        if isinstance(entry, dict) and entry.get('method') == METHOD:
            assert sha(entry['source']) == key == entry['source_sha256'], key
            if entry.get('source_package'):
                r, s = sources[entry['source_package'], entry['source_path']]
                assert r['sha256'] == entry['package_sha256'], key
                assert sha(s['description']) == key, key
    assets = json.loads((ROOT / 'assets.json').read_text())
    asset_rows = assets['records'] if isinstance(assets, dict) and 'records' in assets else assets
    body_checked = 0
    for path_key, entry in labels.get('by_path', {}).items():
        if not isinstance(entry, dict) or entry.get('method') != METHOD:
            continue
        r, skill = sources[entry['source_package'], entry['source_path']]
        assert path_key == entry['source_package'] + ':' + entry['source_path']
        assert r['sha256'] == entry['package_sha256'], path_key
        assert sha(skill['description']) == entry['source_sha256'] == sha(entry['source']), path_key
        if entry.get('evidence_kind') == 'skill_body':
            asset = next(a for a in asset_rows if a['asset_sha256'] == r['sha256'])
            with zipfile.ZipFile(args.site / asset['asset_url']) as archive:
                raw = archive.read(entry['source_path'])
            body = raw.decode('utf-8-sig', errors='replace')
            assert body.strip(), path_key
            assert sha(body) == entry['body_sha256'], path_key
            body_checked += 1
    details = [json.loads(p.read_text()) for p in sorted((args.site / 'data/pkg').glob('*.json'))]
    rows = {(r['file'], s['path']): s for r in details for s in r['skills']}
    total = translated = 0
    unavailable = []
    missing = []
    matched = set()
    for r in details:
        for s in r['skills']:
            total += 1
            original = originals[r['id'], s['path']]
            assert s['name'] == original['name'], (r['file'], s['path'], 'original name')
            assert s['description'] == original['description'], (r['file'], s['path'], 'original description')
            label = labels.get('by_path', {}).get(r['file'] + ':' + s['path'], {})
            if isinstance(label, dict) and label.get('source_kind') == 'empty_source':
                unavailable.append({'file': r['file'], 'path': s['path']})
            zh = s.get('description_zh', '')
            if zh:
                assert re.search(r'[\u3400-\u9fff]', zh), (r['file'], s['path'], 'not Chinese')
                assert '中文说明待补充' not in zh, (r['file'], s['path'], 'placeholder')
                translated += 1
            else:
                missing.append({'file': r['file'], 'path': s['path'], 'description_sha256': sha(s['description'])})
            matched.add((r['file'], s['path']))
    with (args.site / '技能明细.csv').open(encoding='utf-8-sig', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == total
    for row in csv_rows:
        s = rows[row['包'], row['原始路径']]
        assert row['skill'] == s['name'] and row['中文用途'] == s.get('description_zh', '')
    search = json.loads((args.site / 'data/search.json').read_text())
    for r in details:
        for s in r['skills']:
            if s.get('description_zh'):
                assert s['description_zh'] in search[str(r['id'])][3], (r['file'], s['path'], 'search')
    report = {'total_skills': total, 'translated_skills': translated, 'missing_skill_chinese': len(missing),
              'all_skills_complete': not missing and not unavailable, 'unavailable_source_skills': unavailable, 'unique_missing_descriptions': len({m['description_sha256'] for m in missing}),
              'body_sources_verified': body_checked,
              'checks': ['body translations match nonempty archived skill body hashes and package paths', 'original names and descriptions unchanged', 'manual translations match source hashes and representative package paths',
                         'Chinese text and no pending placeholders', 'CSV exactly matches package details', 'search contains all Chinese descriptions'],
              'missing_inventory': 'tools/catalog/generated/缺失中文说明.json'}
    (ROOT / 'tools/catalog/generated/缺失中文说明.json').write_text(json.dumps(missing, ensure_ascii=False, indent=2) + '\n')
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'missing'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
