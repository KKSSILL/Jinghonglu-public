"""Build an offline source-material shelf for AI personification research."""
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/ai-girls/collection.json'
OUTPUT = ROOT / 'prototype/ai-girls.html'
READING_OUTPUT = ROOT / 'juan/kaoyuan.md'


def build():
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    families = {c['id']: c for c in data['characters']}
    items = data['items']
    assert len({c['id'] for c in items}) == len(items), 'Duplicate item ID'
    esc = lambda value: html.escape(str(value), quote=True)

    def link(url, label):
        parts = urlsplit(url)
        assert parts.scheme == 'https' and parts.hostname and not parts.username
        return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a>'

    cards = []
    reading = [f'# {data["title"]}', data['scope'], f'> {data["reading_note"]}',
               '按模型家族归档，同一模型的不同形象分别追溯。以下保留原作品题名，不能据题名认定角色首创或产品事实。',
               ' · '.join(f'[{c["name"]}](#{c["id"]})' for c in data['characters'])]
    previous_family = None
    for item in items:
        assert item['character_id'] in families
        family = families[item['character_id']]
        stored = bool(item['local_file'])
        if stored:
            asset = (ROOT / item['local_file']).resolve()
            assert asset.is_relative_to((ROOT / 'data/ai-girls/media').resolve())
            assert item.get('permission_url')
            assert hashlib.sha256(asset.read_bytes()).hexdigest() == item['sha256']
            assert item['rights_status'] in ['submitter-declared-cc0', 'author-permission']
            relative = '../' + item['local_file']
            visual = (f'<a class="picture" href="{esc(relative)}" target="_blank" rel="noopener">'
                      f'<img loading="lazy" src="{esc(relative)}" alt="{esc(item["title"])}">'
                      '<span>点击查看原图</span></a>')
        else:
            visual = f'<div class="lead-label">出处线索 · {esc(family["name"])}</div>'
        source_links = [link(item['detail_url'], '作品详情')]
        if item.get('original_source_url'):
            source_links.append(link(item['original_source_url'], '来源线索'))
        if item.get('permission_url'):
            source_links.append(link(item['permission_url'], '投稿与许可'))
        author = item.get('author_credit') or (item['public_image_credit'] + '（页面署名，作者身份未核实）' if item.get('public_image_credit') else item.get('submitter', '') + '（投稿署名）' if item.get('submitter') else '待核实')
        if family['id'] != previous_family:
            reading.extend([f'<a name="{esc(family["id"])}"></a>', f'## {family["name"]}'])
            previous_family = family['id']
        reading.extend([f'### {item["title"]}', item['curator_note'], f'署名：{author}。'])
        if stored:
            reading.append(f'<p><img src="../{esc(item["local_file"])}" alt="{esc(item["title"])}" width="320"></p>')
        reading.extend(['来源：' + ' · '.join(source_links),
                        f'图库投稿：{item.get("submitted_on") or "未核"}；形象首发：未考。',
                        f'<details>\n<summary>许可与核对范围</summary>\n\n{item["rights_note"]}\n\n图像：{"已实看" if item["image_visual_review"] == "reviewed" else "尚未逐图查看，仅留出处链接"}。采集：{item["accessed_on"]}；材料编号：{item["id"]}。\n\n</details>'])
        search = ' '.join([family['name'],item['title'],item['kind'],item['curator_note'],author])
        status = '已存原图' if stored else '原帖看图'
        review = '已看原图' if item['image_visual_review'] == 'reviewed' else '尚未逐图查看'
        cards.append(f'''<article class="card" data-family="{esc(family['id'])}" data-stored="{str(stored).lower()}" data-search="{esc(search)}">
{visual}<div class="card-body"><p class="eyebrow">{esc(family['name'])} · {esc(item['kind'])} <span>{status}</span></p>
<h2>{esc(item['title'])}</h2><p>{esc(item['curator_note'])}</p>
<p class="credit">署名：{esc(author)}</p><nav class="links">{' '.join(source_links)}</nav>
<details><summary>来源记录</summary><p>{esc(item['rights_note'])}</p>
<p>图库投稿日期：{esc(item.get('submitted_on') or '未核')}。本项尚未核到形象首发，投稿与收录日期不能作为起源日期。</p>
<p>画面：{review}。采集：{esc(item['accessed_on'])}。最早发表日期尚未确认。</p>
<p>编号 {esc(item['id'])}；这是同人作品的记录，不是模型的官方人设或行为证明。</p></details></div></article>''')
    options = ''.join(f'<option value="{esc(c["id"])}">{esc(c["name"])}</option>' for c in data['characters'])
    local_count = sum(bool(c['local_file']) for c in items)
    template = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>__TITLE__</title>
<style>
:root{color-scheme:light;--paper:#f7f2e9;--card:#fffdf8;--ink:#292b2c;--muted:#686661;--line:#d9cdbd;--accent:#826243;--soft:#eee5d8}
@media(prefers-color-scheme:dark){:root{color-scheme:dark;--paper:#1c2022;--card:#252b2e;--ink:#ece8df;--muted:#b8b7af;--line:#485052;--accent:#e2be91;--soft:#323a3e}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.8 'Microsoft YaHei','PingFang SC',system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:42px 24px 64px}a{color:var(--accent);text-underline-offset:4px}h1,h2{font-family:'Noto Serif SC','Songti SC','SimSun',serif;line-height:1.45}h1{font-size:44px;margin:6px 0 16px}h2{font-size:24px;margin:8px 0 12px}p{margin:8px 0 16px}.intro{max-width:800px}.eyebrow{font-size:15px;color:var(--muted);letter-spacing:.02em}.stats{font-size:18px;color:var(--accent);margin:22px 0}.toolbar{display:flex;gap:10px;flex-wrap:wrap;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:20px 0}
input,select,button{font:inherit;line-height:1.4;background:var(--card);border:1px solid var(--line);border-radius:8px;color:var(--ink);padding:10px 13px;min-height:46px}input{flex:1;min-width:180px}button{cursor:pointer}button[aria-pressed=true]{background:var(--accent);color:var(--paper)}:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.card{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}.card-body{padding:20px 24px}.picture{position:relative;display:block;height:340px;background:var(--soft);text-align:center}.picture img{width:100%;height:100%;object-fit:contain}.picture span{position:absolute;bottom:8px;right:10px;padding:2px 9px;background:var(--card);border-radius:5px;font-size:13px}.eyebrow span{float:right}.credit{font-size:15px;color:var(--muted)}.links{display:flex;gap:16px;flex-wrap:wrap;font-size:16px}.lead-label{background:var(--soft);padding:12px 24px;color:var(--accent);font-size:16px}details{border-top:1px solid var(--line);margin-top:16px;padding-top:12px;font-size:15px;color:var(--muted)}summary{cursor:pointer}details p{margin-top:12px;overflow-wrap:anywhere}#count{font-size:16px;color:var(--muted)}#empty{padding:36px 0}footer{border-top:1px solid var(--line);margin-top:36px;padding-top:20px;color:var(--muted);font-size:16px}[hidden]{display:none!important}
@media(max-width:680px){main{padding:24px 16px 40px}h1{font-size:34px}.grid{grid-template-columns:1fr}.picture{height:300px}.card-body{padding:18px}.toolbar input{width:100%;flex-basis:100%}button,select{font-size:16px}}
</style></head><body><main>
<p class="eyebrow">惊鸿录 · 形象考源 / 2026.10.12</p><h1>众娘考源材料簿</h1>
<p class="intro">__SCOPE__</p>
<p class="intro">__READING_NOTE__</p>
<p class="stats">__FAMILIES__ 个模型家族 · __TOTAL__ 条材料 · __LOCAL__ 张已存原图</p>
<p class="intro">已存图片可以离线看；其余条目点击“作品详情”去原帖看图。每件都带来源，插画、设定和梗图分别标注。</p>
<div class="toolbar"><input id="query" type="search" placeholder="找形象版本、作者或作品题名…" aria-label="搜索考源材料"><select id="family" aria-label="按模型家族筛选"><option value="">全部家族</option>__OPTIONS__</select><button data-mode="all" aria-pressed="true">全部</button><button data-mode="stored" aria-pressed="false">已存原图</button><button data-mode="leads" aria-pressed="false">出处线索</button></div>
<p id="count" role="status" aria-live="polite"></p><section class="grid" aria-label="考源材料条目">__CARDS__</section><p id="empty" hidden>没有找到这一项，换个关键词试试。</p>
<footer><p>同一模型的不同形象分开考证。最早可查出处、作品作者与角色设计者尚未确认时留作未考；外形相似不能据以认定传承。后续以原帖、设定发布和可核日期补足。</p><p>本页是写作材料，原作品题名如实保留。志异正文取其简练与余味，评语与事实分开。</p><p>来源数据：<a href="../data/ai-girls/collection.json">collection.json</a> · <a href="../juan/kaoyuan.md">GitHub 阅读版</a> · <a href="zhiyi.html">志异正文</a></p></footer>
</main><script>
const query=document.querySelector('#query'),family=document.querySelector('#family'),cards=[...document.querySelectorAll('.card')],buttons=[...document.querySelectorAll('[data-mode]')];let mode='all';
function update(){const q=query.value.trim().toLocaleLowerCase();let count=0;for(const c of cards){const ok=(!family.value||c.dataset.family===family.value)&&(!q||c.dataset.search.toLocaleLowerCase().includes(q))&&(mode==='all'||(mode==='stored')===(c.dataset.stored==='true'));c.hidden=!ok;if(ok)count++;}document.querySelector('#count').textContent='当前显示 '+count+' / '+cards.length+' 条';document.querySelector('#empty').hidden=count!==0;}
query.addEventListener('input',update);family.addEventListener('change',update);for(const b of buttons)b.addEventListener('click',()=>{mode=b.dataset.mode;for(const x of buttons)x.setAttribute('aria-pressed',String(x===b));update();});update();
</script></body></html>
'''
    for key, value in {'__TITLE__':esc(data['title']),'__SCOPE__':esc(data['scope']),'__READING_NOTE__':esc(data['reading_note']),'__FAMILIES__':len(families),'__TOTAL__':len(items),'__LOCAL__':local_count,'__OPTIONS__':options,'__CARDS__':'\n'.join(cards)}.items():
        template = template.replace(key,str(value))
    reading.extend(['---', '[返回全书目录](../README.md#目录) · [离线材料页](../prototype/ai-girls.html) · [来源数据](../data/ai-girls/collection.json)'])
    return {OUTPUT: template, READING_OUTPUT: '\n\n'.join(reading) + '\n'}, len(items), local_count


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    outputs, total, local = build()
    for target, page in outputs.items():
        if args.check:
            assert target.read_text(encoding='utf-8') == page, f'Generated reading shelf is stale: {target.name}'
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page,encoding='utf-8')
    print(f'PASS: {total} records / {local} local images; source references and image hashes checked.')
