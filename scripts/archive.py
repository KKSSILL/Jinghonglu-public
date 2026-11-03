"""Validate the authored records and build deterministic, offline reading copies."""
from pathlib import Path
import argparse
import datetime as dt
import html
import json
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def load():
    result = {name: json.loads((ROOT / 'data' / f'{name}.json').read_text(encoding='utf-8'))
              for name in ('archive', 'sources', 'points', 'timeline', 'transitions', 'leads')}
    result['cases'] = [json.loads(p.read_text(encoding='utf-8'))
                       for p in sorted((ROOT / 'data/cases').glob('*.json'))]
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}(?:-\d{2}(?:-\d{2})?)?', value):
        return False
    try:
        dt.date.fromisoformat(value + ('-01-01' if len(value) == 4 else '-01' if len(value) == 7 else ''))
        return True
    except ValueError:
        return False


def safe_url(value):
    u = urlsplit(value)
    return u.scheme == 'https' and bool(u.hostname) and not u.username and not u.password


def validate(d, for_publication=False):
    ids = {}
    for group in ('sources', 'points', 'cases', 'timeline', 'transitions', 'leads'):
        items = d[group]
        ids[group] = {x['id'] for x in items}
        require(len(ids[group]) == len(items), f'duplicate ID in {group}')
        require(all(re.fullmatch(r'[A-Za-z0-9_-]+', x['id']) for x in items), f'unsafe ID in {group}')
    families = {x['id'] for x in d['archive']['families']}
    lenses = {x['id'] for x in d['archive']['lenses']}
    sources = {x['id']: x for x in d['sources']}

    def refs(obj, label):
        for field, target in [('source_ids', 'sources'), ('point_ids', 'points'), ('case_ids', 'cases'), ('related_case_ids', 'cases')]:
            require(set(obj.get(field, [])).issubset(ids[target]), f'{label}: missing {field}')

    for s in d['sources']:
        require(safe_url(s['url']), f"{s['id']}: unsafe URL")
        require(valid_date(s['accessed_on']), f"{s['id']}: invalid access date")
        require(s['published_on'] is None or valid_date(s['published_on']), f"{s['id']}: invalid publication date")
        require(s['kind'] in ['vendor-statement', 'research-paper', 'research-report', 'public-user-report'], f"{s['id']}: unknown source kind")
        require(s['access'] == 'readable', f"{s['id']}: unread sources belong in leads")
        require(s['rights'] == 'link-and-original-summary-only' and s['local_copy'] is False, f"{s['id']}: media rights require separate review")
        require(bool(s['author']) and bool(s['context']), f"{s['id']}: incomplete provenance")
    for p in d['points']:
        refs(p, p['id'])
        require(p['family'] in families and valid_date(p['anchor_date']), f"{p['id']}: bad family/date")
        require(p['kind'] in ['documented-system', 'model-release', 'research-variant', 'product-configuration'], f"{p['id']}: bad point kind")
        require(p['source_ids'] and p['anchor_kind'], f"{p['id']}: missing public anchor")
        require(any(sources[s]['kind'] != 'public-user-report' for s in p['source_ids']), f"{p['id']}: subjective report cannot anchor Point")
        for rel in p['related_points']:
            require(rel['target'] in ids['points'] and rel['source_ids'], f"{p['id']}: unresolved relation")
            require(rel['relation'] in ['research-variant-of', 'rollback-of', 'public-sequence'], f"{p['id']}: undeclared relation")
            refs(rel, p['id'])
    for c in d['cases']:
        needed = ['schema_version', 'title', 'status', 'family', 'date', 'date_basis', 'occurred_on', 'recorded_on', 'kind', 'lenses', 'point_ids', 'source_ids', 'model', 'context_completeness', 'summary', 'evidence', 'interpretation', 'limits', 'consciousness', 'welfare', 'revisions']
        require(all(k in c for k in needed), f"{c['id']}: missing case fields")
        require(re.fullmatch(r'HAI-\d{4}-\d{4}', c['id']), f"{c['id']}: malformed case ID")
        require(c['schema_version'] == 1 and c['status'] == 'catalogued', f"{c['id']}: draft case cannot enter public reader")
        require(c['family'] in families and set(c['lenses']).issubset(lenses) and c['lenses'], f"{c['id']}: unknown family/lens")
        require(c['kind'] in ['vendor-document', 'research', 'user-report'], f"{c['id']}: unknown case kind")
        require(c['model']['certainty'] in ['official-family', 'research-reported', 'user-reported', 'unknown'], f"{c['id']}: missing model uncertainty")
        require(c['model']['family'] == c['family'], f"{c['id']}: inconsistent model family")
        require(valid_date(c['date']) and valid_date(c['recorded_on']) and c['date_basis'], f"{c['id']}: missing time basis")
        require(c['occurred_on'] is None or valid_date(c['occurred_on']), f"{c['id']}: invalid occurrence date")
        require(c['source_ids'] and c['evidence'] and c['limits'] and c['interpretation']['author'], f"{c['id']}: missing evidence or limits")
        require(c['consciousness'] == 'not-assessed' and c['welfare'] == 'not-assessed', f"{c['id']}: unsupported assessment")
        refs(c, c['id'])
        for e in c['evidence']:
            require(e['claim'] and e['attribution'] and e['source_ids'] and e['locator'], f"{c['id']}: weak evidence attribution")
            require(set(e['source_ids']).issubset(c['source_ids']), f"{c['id']}: evidence source absent from case")
        require(c['revisions'], f"{c['id']}: missing revision provenance")
        for revision in c['revisions']:
            require(valid_date(revision['recorded_on']) and revision['author'] and revision['change'], f"{c['id']}: invalid revision")
            refs(revision, c['id'])
    for t in d['timeline']:
        refs(t, t['id'])
        require(t['track'] in ['official', 'observed'] and valid_date(t['date']) and t['date_basis'], f"{t['id']}: bad timeline")
        require(t['source_ids'] and t['family'] in families, f"{t['id']}: missing source or family")
    for c in d['archive']['collections']:
        refs(c, c['id'])
    for t in d['transitions']:
        refs(t, t['id'])
        require(t['status'] == 'unconfirmed' and not t['point_ids'] and t['reason'] and t['next_check'], f"{t['id']}: false confirmation")
    for lead in d['leads']:
        refs(lead, lead['id'])
        require(safe_url(lead['url']), f"{lead['id']}: unsafe lead URL")
    # Explicit public release check, never a hidden requirement for local reading.
    if for_publication:
        contact = d['archive']['publication']['private_contact']
        require(isinstance(contact, str) and urlsplit(contact).scheme in ['mailto', 'https'], 'Publication blocked: configure a working private takedown contact first.')
    return f"{len(d['cases'])} cases / {len(d['points'])} points / {len(d['sources'])} sources / {len(d['timeline'])} events"


def outputs(d):
    source_map = {s['id']: s for s in d['sources']}
    point_map = {p['id']: p for p in d['points']}
    case_map = {c['id']: c for c in d['cases']}
    family_map = {f['id']: f['label'] for f in d['archive']['families']}
    lens_map = {l['id']: l['label'] for l in d['archive']['lenses']}
    kind_map = {'vendor-document': '厂商材料', 'research': '研究材料', 'user-report': '用户自述'}
    out = {}
    # Sorting partial dates is only for reading order; precision remains visible.
    cases = sorted(d['cases'], key=lambda c: (c['date'], c['id']))
    def md(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    def source_link(sid):
        s = source_map[sid]
        return f"[{s['title']}]({s['url']})"
    rows = ['# 案例总览', '', '自动生成；编辑 data/ 后运行构建。编目不等于独立证实。', '', '| 编目日期依据 | 案例 | 家族 | 材料 | 视角 |', '| --- | --- | --- | --- | --- |']
    for c in cases:
        rows.append(f"| {c['date']} | [{md(c['title'])}](cases/{c['id']}.md) | {family_map[c['family']]} | {kind_map[c['kind']]} | {'、'.join(lens_map[x] for x in c['lenses'])} |")
        text = [f"# {c['title']}", '', f"`{c['id']}` · {kind_map[c['kind']]} · {family_map[c['family']]}", '', c['summary'], '', '## 编目', '', f"- 目录日期：{c['date']}；{c['date_basis']}", f"- 实际发生日期：{c['occurred_on'] or '未确认'}", f"- 收录日期：{c['recorded_on']}", f"- 型号：{c['model']['version'] or '未锁定具体版本'}；{c['model']['certainty']}", f"- 上下文：{c['context_completeness']}", f"- 模型节点：{'；'.join(point_map[x]['title'] for x in c['point_ids']) or '未归属具体节点'}", '', '## 材料说了什么', '']
        for e in c['evidence']:
            text += [f"{e['attribution']}：{e['claim']}", '', f"依据：{' · '.join(source_link(x) for x in e['source_ids'])}；定位：{e['locator']}。", '']
        text += ['## 馆员解释', '', c['interpretation']['text'], '', f"解释署名：{c['interpretation']['author']}", '', '## 不能由此推出', ''] + ['- '+x for x in c['limits']]
        text += ['', '## 来源与读取范围', '']
        for sid in c['source_ids']:
            s = source_map[sid]
            text += [f"- {source_link(sid)} — {s['author']}；发表 {s['published_on'] or '未知'}；读取 {s['accessed_on']}。{s['context']}"]
        text += ['', '## 修订记录', '']
        for r in c['revisions']:
            text += [f"- {r['recorded_on']} · {r['author']}：{r['change']}"]
        text += ['', '意识与福利：未评估。本站未镜像第三方原文或媒体。', '', '[返回总览](../CATALOG.md)', '']
        out[f"docs/cases/{c['id']}.md"] = '\n'.join(text)
    out['docs/CATALOG.md'] = '\n'.join(rows) + '\n'
    timeline = ['# 双时间线', '', '自动生成。official 表示公开机构记录；observed 包含用户报告和研究发表。日期精度与依据保留，顺序不等于因果。', '']
    for track, label in [('official', '官方记录'), ('observed', '观察与研究')]:
        timeline += [f'## {label}', '', '| 日期 | 事件 | 依据类型 | 来源 |', '| --- | --- | --- | --- |']
        for e in sorted((x for x in d['timeline'] if x['track'] == track), key=lambda x: (x['date'], x['id'])):
            case_links = ' '.join(f"[{cid}](cases/{cid}.md)" for cid in e['case_ids'])
            timeline.append(f"| {e['date']} | {md(e['title'])} {case_links} | {md(e['date_basis'])} | {' · '.join(source_link(s) for s in e['source_ids'])} |")
        timeline.append('')
    out['docs/TIMELINE.md'] = '\n'.join(timeline)
    template = (ROOT/'web/index.template.html').read_text(encoding='utf-8')
    data = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    out['site/index.html'] = template.replace('@@STYLE@@', (ROOT/'web/style.css').read_text(encoding='utf-8')).replace('@@DATA@@', data).replace('@@APP@@', (ROOT/'web/app.js').read_text(encoding='utf-8'))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'build', 'check'])
    parser.add_argument('--for-publication', action='store_true')
    args = parser.parse_args()
    d = load()
    counts = validate(d, args.for_publication)
    if args.command != 'validate':
        generated = outputs(d)
        for name, value in generated.items():
            p = ROOT/name
            if args.command == 'check':
                require(p.exists() and p.read_text(encoding='utf-8') == value, f'Generated file stale: {name}')
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(value, encoding='utf-8', newline='\n')
        existing = {str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT/'docs/cases').glob('*.md')}
        require(existing.issubset(generated), 'Orphan generated case page: remove or redact it intentionally, then rebuild.')
    print(f'PASS {args.command}: {counts}')
    if not d['archive']['publication']['private_contact']:
        print('Local draft: private takedown contact is not configured; no publication performed.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
