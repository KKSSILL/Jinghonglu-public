// data/zhiyi.json -> README, juan and offline HTML. Run with --check to verify.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const root = fileURLToPath(new URL('../', import.meta.url));
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/zhiyi.json'), 'utf8'));
const template = fs.readFileSync(path.join(root, 'templates/zhiyi.html'), 'utf8');
const materialData = JSON.parse(fs.readFileSync(path.join(root, 'data/ai-girls/collection.json'), 'utf8'));
const families = new Map(materialData.characters.map(c => [c.id, c.name]));
const entries = data.entries, chapters = data.chapters;
const check = process.argv.includes('--check'), outputs = new Map();
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const asScript = value => JSON.stringify(value, null, 2).replace(/</g, '\\u003c');
const file = e => e.id.toLowerCase() + '.md';
const nums = '零一二三四五六七八九';
const cn = n => n < 10 ? nums[n] : n < 100 ? (n < 20 ? '' : nums[Math.floor(n / 10)]) + '十' + (n % 10 ? nums[n % 10] : '') : String(n);
const link = s => {
  const url = new URL(s.url);
  assert(['https:', 'http:'].includes(url.protocol) && !url.username && !url.password, 'Invalid source URL');
  return '[' + s.label + '](<' + s.url + '>)';
};
const banner = (prefix, name, width) => '<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="' + prefix + 'assets/' + name + '-dark.svg">\n  <img src="' + prefix + 'assets/' + name + '-light.svg" alt="惊鸿录" width="' + width + '">\n</picture>';
assert.equal(new Set(entries.map(e => e.id)).size, entries.length, 'Duplicate entry ID');
for (const e of entries) {
  assert(/^Z-\d{3}$/.test(e.id) && chapters[e.chap], 'Invalid ID or chapter');
  for (const family of e.material_families || []) assert(families.has(family), 'Unknown material family');
}

const seq = {};
entries.forEach((e, i) => {
  const number = seq[e.chap] = (seq[e.chap] || 0) + 1;
  const prev = entries[i - 1], next = entries[i + 1];
  const out = ['<div align="center">\n\n' + banner('../', 'seal', 72) + '\n\n<sub>' + esc(chapters[e.chap]) + ' · 其' + cn(number) + '</sub>\n\n# ' + e.title + '\n\n<sub>' + esc(e.time) + '　·　' + esc(e.who) + '</sub><br>\n' + e.tags.map(t => '<code>' + esc(t) + '</code>').join(' ') + '\n\n</div>\n\n---\n'];
  out.push(...e.zhi.map(p => p + '\n'));
  if (e.image_file) out.push('<p align="center"><img src="../' + esc(e.image_file) + '" alt="' + esc(e.imgalt || '') + '" width="460"><br><sub>' + esc(e.imgnote || '') + '</sub></p>\n');
  if (e.quote) out.push('> **' + e.quote.from + '**　' + e.quote.text + '\n');
  if (e.yishi) out.push('<table><tr><td>\n\n**异史氏曰**　' + e.yishi + '\n\n</td></tr></table>\n');
  if (e.kao) out.push('<details>\n<summary><b>考据状态</b></summary>\n\n' + e.kao + '\n\n</details>\n');
  if (e.revisions?.length) out.push('<details>\n<summary>编目修订</summary>\n\n' + e.revisions.map(r=>r.date + '：' + r.note).join('\n\n') + '\n\n</details>\n');
  const sources = [link(e.src) + '（读取于 ' + e.src.read + '）', ...(e.more || []).map(link)];
  if (e.src2) sources.push(link(e.src2));
  out.push('<sub>出处：' + sources.join(' · ') + '</sub>\n');
  if (e.material_families?.length) out.push('相关考源材料：' + e.material_families.map(id=>'[' + families.get(id) + '](kaoyuan.md#' + id + ')').join(' · ') + '。材料收录不代表起源已考实。\n');
  const cell = (x, arrow) => x ? '<a href="' + file(x) + '">' + (arrow === '←' ? '← ' : '') + esc(x.title) + (arrow === '→' ? ' →' : '') + '</a>' : '　';
  out.push('---\n\n<table width="100%"><tr>\n<td align="left" width="40%">' + cell(prev, '←') + '</td>\n<td align="center" width="20%"><a href="../README.md#目录">目录</a></td>\n<td align="right" width="40%">' + (next ? cell(next, '→') : '<a href="zizhi.md">卷末 · 自志 →</a>') + '</td>\n</tr></table>\n');
  outputs.set('juan/' + file(e), out.join('\n'));
});

outputs.set('juan/zizhi.md', [
  '<div align="center">\n\n' + banner('../', 'seal', 72) + '\n\n# 自志\n\n</div>\n\n---\n',
  ...data.self_note.map(p => p + '\n'),
  '撤下请求优先于一切收录，见 [TAKEDOWN.md](../TAKEDOWN.md)。\n\n---\n\n## 待核实的线索\n',
  ...data.leads.map(l => '- ' + link({label:l.t, url:l.u})),
  '\n<sub>以上仅有搜索线索，尚未逐条核实。已补读的图库材料另列于<a href="kaoyuan.md">考源附录</a>。</sub>\n\n---\n\n<p align="center"><a href="../README.md#目录">回到目录</a></p>\n'
].join('\n'));

const pre = data.preface;
const readme = ['<div align="center">\n\n' + banner('', 'banner', 760) + '\n\n<sub>' + esc(data.credit_line) + '</sub>\n\n</div>\n\n<br>\n',
  '<div align="center">\n\n<sub>' + pre.title + '</sub>\n\n' + pre.quotes.map((q,i)=>(i === 0 ? '##' : '###') + ' ' + q.text + '\n\n<sub>' + q.attribution + '</sub>').join('\n\n') + '\n\n</div>\n'];
readme.push(...pre.asides.map(a=>'> **' + a.label + '**　' + a.text + '\n'));
const pre2 = data.preface_two;
if (pre2) readme.push('<br>\n\n<div align="center">\n\n<sub>' + pre2.title + '</sub>\n\n</div>\n\n' + pre2.paragraphs.join('\n\n') + '\n\n<p align="right"><sub>' + esc(pre2.sign) + '</sub></p>\n');
readme.push('<br>\n\n## 目录\n');
for (const c of [...new Set(entries.map(e => e.chap))]) {
  readme.push('<table>\n<tr><th colspan="3" align="left">' + esc(chapters[c]) + '</th></tr>');
  entries.filter(e=>e.chap===c).forEach((e,i)=>readme.push('<tr><td>其' + cn(i+1) + '</td><td><a href="juan/' + file(e) + '"><b>' + esc(e.title) + '</b></a></td><td><sub>' + esc(e.time) + '</sub></td></tr>'));
  readme.push('</table>\n');
}
readme.push('<table>\n<tr><th colspan="3" align="left">附录 · 考源材料</th></tr>\n<tr><td>　</td><td><a href="juan/kaoyuan.md"><b>众娘考源材料簿</b></a></td><td><sub>' + families.size + ' 个模型家族 · ' + materialData.items.length + ' 条线索 · 起源待考</sub></td></tr>\n</table>\n');
readme.push('<table>\n<tr><th colspan="3" align="left">卷末</th></tr>\n<tr><td>　</td><td><a href="juan/zizhi.md"><b>自志</b></a></td><td><sub>说明与待核实线索</sub></td></tr>\n</table>\n');
readme.push('---\n\n<sub>' + esc(data.editorial_note) + '<br>\n离线阅读：<a href="prototype/zhiyi.html">志异正文</a> · <a href="prototype/ai-girls.html">考源材料</a>（下载仓库后打开）。早期档案见 <a href="docs/ARCHIVE_README.md">档案说明</a>；维护见 <a href="prototype/README.md">目录与生成方式</a>。撤下请求见 <a href="TAKEDOWN.md">TAKEDOWN.md</a>。</sub>\n');
outputs.set('README.md', readme.join('\n'));

const browserEntries = entries.map(e => {
  if (!e.image_file) return e;
  assert(/^prototype\/img\/[a-z0-9-]+\.jpg$/.test(e.image_file), 'Invalid image path');
  return {...e, img:'data:image/jpeg;base64,' + fs.readFileSync(path.join(root,e.image_file)).toString('base64')};
});
const prefaceHtml = '<p class="note" style="text-align:center">' + esc(data.credit_line) + '</p>\n<section class="preface" aria-label="序">\n<p class="pre-h">' + esc(pre.title) + '</p>\n' + pre.quotes.map((q,i)=>'<blockquote class="q' + (i+1) + '">' + esc(q.text) + '<cite>' + esc(q.attribution) + '</cite></blockquote>').join('\n') + '\n' + pre.asides.map(a=>'<p class="aside"><b>' + esc(a.label) + '</b>' + esc(a.text) + '</p>').join('\n') + '\n</section>' + (pre2 ? '\n<section class="preface" aria-label="序二">\n<p class="pre-h">' + esc(pre2.title) + '</p>\n' + pre2.paragraphs.map(t=>'<p class="pre-b">' + esc(t) + '</p>').join('\n') + '\n<p class="pre-b" style="text-align:right">' + esc(pre2.sign) + '</p>\n</section>' : '');
const tokens = {'__ENTRY_COUNT__':entries.length,'__PREFACE__':prefaceHtml,'__SELF_NOTE__':'<section class="zhi-note" aria-label="自志"><h3>自志</h3>\n' + data.self_note.map(p=>'<p>' + esc(p) + '</p>').join('\n') + '\n</section>','__ZHIYI_DATA__':'const ENTRIES=' + asScript(browserEntries) + ';\nconst LEADS=' + asScript(data.leads) + ';','__CHAPTERS__':asScript(chapters)};
let html = template;
for (const [token,value] of Object.entries(tokens)) {
  assert(html.includes(token), 'Missing template token: ' + token);
  html = html.replace(token, () => String(value));
}
outputs.set('prototype/zhiyi.html', html);

for (const [relative, content] of outputs) {
  const target = path.join(root,relative);
  if (check) assert.equal(fs.readFileSync(target,'utf8').replace(/\r\n/g,'\n'), content.replace(/\r\n/g,'\n'), 'Stale output: ' + relative);
  else {fs.mkdirSync(path.dirname(target),{recursive:true}); fs.writeFileSync(target,content);}
}
console.log('PASS ' + (check ? 'check' : 'build') + ': ' + entries.length + ' entries / ' + Object.keys(chapters).length + ' chapters / ' + outputs.size + ' reading files.');
