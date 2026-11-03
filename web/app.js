'use strict';
const D=JSON.parse(document.getElementById('archive-data').textContent);
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const index=xs=>Object.fromEntries(xs.map(x=>[x.id,x]));
const F=index(D.archive.families),L=index(D.archive.lenses),S=index(D.sources),P=index(D.points),C=index(D.cases);
const kinds={'vendor-document':'厂商材料','research':'研究材料','user-report':'用户自述'};
const sourceKinds={'vendor-statement':'厂商说明','research-paper':'原始论文','research-report':'研究说明','public-user-report':'公开用户报告'};
const pointKinds={'documented-system':'有文献记录的系统','model-release':'模型发布','research-variant':'研究变体','product-configuration':'产品配置阶段'};
const certainty={'official-family':'系列由官方说明；具体快照以来源为限','research-reported':'型号来自研究者报告','user-reported':'型号由用户自述，未独立核验','unknown':'未知'};
const state={lens:'',collection:'',point:''};
const selectedCases=()=>D.cases.filter(c=>{
 const q=$('search').value.trim().toLocaleLowerCase();
 const text=[c.title,c.summary,F[c.family].label,...c.evidence.map(e=>e.claim),...c.lenses.map(l=>L[l].label)].join(' ').toLocaleLowerCase();
 return (!q||text.includes(q))&&(!$('family').value||c.family===$('family').value)&&(!$('kind').value||c.kind===$('kind').value)&&(!state.lens||c.lenses.includes(state.lens))&&(!state.point||c.point_ids.includes(state.point))&&(!state.collection||D.archive.collections.find(x=>x.id===state.collection).case_ids.includes(c.id));
}).sort((a,b)=>b.date.localeCompare(a.date)||a.id.localeCompare(b.id));
function renderCases(){
 const cases=selectedCases();
 $('result-count').textContent=`${cases.length} 条记录 / 共 ${D.cases.length} 条`;
 $('active-scope').textContent=state.point?`节点：${P[state.point].title}`:state.collection?`专题：${D.archive.collections.find(x=>x.id===state.collection).title}`:'';
 $('cases').innerHTML=cases.map(c=>`<article class="case-card"><div class="case-meta"><span>${esc(F[c.family].label)}</span><time>${esc(c.date)}</time></div><h3>${esc(c.title)}</h3><p>${esc(c.summary)}</p><div class="case-bottom"><span>${esc(kinds[c.kind])} · ${esc(L[c.lenses[0]].label)}</span><button data-case="${esc(c.id)}" type="button" aria-label="阅读：${esc(c.title)}">读这条 ↗</button></div></article>`).join('')||'<p class="empty">这个组合还没有记录。试试清除筛选，或换一个关键词。</p>';
 document.querySelectorAll('[data-lens]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lens===state.lens)));
 document.querySelectorAll('[data-collection]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.collection===state.collection)));
}
function sources(ids){return `<ul class="sources">${ids.map(id=>{const s=S[id];return `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a><small>${esc(sourceKinds[s.kind])} · ${esc(s.author)}<br>发表：${esc(s.published_on||'未知')} · 读取：${esc(s.accessed_on)}<br>${esc(s.context)}</small></li>`}).join('')}</ul>`}
function showCase(id){
 const c=C[id];if(!c)return;
 $('detail-kind').textContent=`${c.id} · ${kinds[c.kind]}`;
 $('detail-body').innerHTML=`<h2 id="detail-title">${esc(c.title)}</h2><p class="lead">${esc(c.summary)}</p><dl><dt>目录日期</dt><dd>${esc(c.date)} · ${esc(c.date_basis)}</dd><dt>实际发生</dt><dd>${esc(c.occurred_on||'未确认具体日期')}</dd><dt>型号</dt><dd>${esc(c.model.version||'未锁定具体版本')}<br>${esc(certainty[c.model.certainty])}</dd><dt>模型节点</dt><dd>${esc(c.point_ids.map(x=>P[x].title).join('；')||'未归属具体节点')}</dd></dl><h3>材料说了什么</h3>${c.evidence.map(e=>`<p><strong>${esc(e.attribution)}：</strong>${esc(e.claim)}</p><p class="muted">定位：${esc(e.locator)}<br>依据：${e.source_ids.map(id=>`<a href="${esc(S[id].url)}" target="_blank" rel="noopener noreferrer">${esc(S[id].title)}</a>`).join(' · ')}</p>`).join('')}<h3>为什么保存</h3><p>${esc(c.interpretation.text)}</p><p class="muted">馆员解释 · ${esc(c.interpretation.author)}</p><h3>不能由此推出</h3><ul>${c.limits.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><h3>回到来源</h3>${sources(c.source_ids)}<details><summary>编目与修订记录</summary><p>收录 ${esc(c.recorded_on)} · ${esc(c.context_completeness)}</p><ul>${c.revisions.map(r=>`<li>${esc(r.recorded_on)} · ${esc(r.change)}</li>`).join('')}</ul><p>意识与福利：未评估。未镜像第三方原文或媒体。</p></details>`;
 $('detail').showModal();$('detail').scrollTop=0;
}
function showPoint(id){
 const p=P[id];if(!p)return;
 $('detail-kind').textContent=`${p.id} · ${pointKinds[p.kind]}`;
 const cases=D.cases.filter(c=>c.point_ids.includes(id));
 $('detail-body').innerHTML=`<h2 id="detail-title">${esc(p.title)}</h2><dl><dt>公开锚点</dt><dd>${esc(p.anchor_date)} · ${esc(p.anchor_kind)}</dd><dt>型号说明</dt><dd>${esc(p.model_version||'没有可核验的精确版本')}</dd></dl><p>${esc(p.scope_note||'该节点由下列公开来源锚定。')}</p><p class="muted">档案节点不等于持续人格或主体；关联案例也不自动证明同一模型快照。</p><h3>关联案例</h3>${cases.map(c=>`<p><button data-case="${esc(c.id)}" type="button">${esc(c.title)} ↗</button></p>`).join('')||'<p>目前只有公开锚点，尚无关联案例。</p>'}<button data-scope="${esc(id)}" type="button">在档案中筛选这个节点</button><h3>节点来源</h3>${sources(p.source_ids)}`;
 $('detail').showModal();$('detail').scrollTop=0;
}
function renderTimeline(){
 const f=$('time-family').value;
 const ps=D.points.filter(p=>!f||p.family===f).sort((a,b)=>a.anchor_date.localeCompare(b.anchor_date));
 $('points').innerHTML=ps.map(p=>`<button class="point" data-point="${esc(p.id)}" type="button"><time>${esc(p.anchor_date)}</time><strong>${esc(p.title)}</strong><small>${esc(pointKinds[p.kind])} · 阅读节点 ↗</small></button>`).join('')||'<p class="muted">这个家族尚无已核实的具体模型节点。相关研究仍可独立收录。</p>';
 for(const track of ['official','observed']){
 const events=D.timeline.filter(e=>e.track===track&&(!f||e.family===f)).sort((a,b)=>a.date.localeCompare(b.date)||a.id.localeCompare(b.id));
 $(track).innerHTML=events.map(e=>{const action=e.case_ids.length?`data-case="${esc(e.case_ids[0])}"`:`data-point="${esc(e.point_ids[0])}"`;return `<li class="event"><time>${esc(e.date)}</time><button ${action} type="button">${esc(e.title)}</button><small>${esc(F[e.family].label)} · ${esc(e.date_basis)}</small></li>`}).join('')||'<li class="muted">这一轨暂时没有材料。</li>';
 }
}
$('edition-count').textContent=`${D.cases.length} 个案例 · ${D.points.length} 个阶段节点 · ${D.sources.length} 个来源`;
for(const id of ['family','time-family'])$(''+id).insertAdjacentHTML('beforeend',D.archive.families.map(f=>`<option value="${esc(f.id)}">${esc(f.label)}</option>`).join(''));
$('collections').innerHTML=D.archive.collections.map(c=>`<button class="collection" data-collection="${esc(c.id)}" type="button" aria-pressed="false"><strong>${esc(c.title)} ↗</strong><span>${esc(c.description)}</span></button>`).join('');
$('lenses').innerHTML=`<button data-lens="" type="button" aria-pressed="true">全部视角</button>`+D.archive.lenses.map(l=>`<button data-lens="${esc(l.id)}" title="${esc(l.description)}" type="button" aria-pressed="false">${esc(l.label)}</button>`).join('');
$('pending').innerHTML=D.transitions.map(t=>`<p><strong>变化候选 · ${esc(t.date)}：</strong>${esc(t.reason)} <button data-case="${esc(t.case_ids[0])}" type="button">读报告</button></p>`).join('')+D.leads.map(t=>`<p><strong>待补来源：</strong>${esc(t.title)}。${esc(t.reason)} <a href="${esc(t.url)}" target="_blank" rel="noopener noreferrer">原链接 ↗</a></p>`).join('');
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.hasAttribute('data-case'))showCase(b.dataset.case);
 else if(b.hasAttribute('data-point'))showPoint(b.dataset.point);
 else if(b.hasAttribute('data-scope')){state.point=b.dataset.scope;state.collection='';state.lens='';$('family').value='';$('kind').value='';$('search').value='';$('detail').close();renderCases();$('archive').scrollIntoView();}
 else if(b.hasAttribute('data-lens')){state.lens=b.dataset.lens;renderCases();}
 else if(b.hasAttribute('data-collection')){state.collection=state.collection===b.dataset.collection?'':b.dataset.collection;state.point='';renderCases();}
});
$('close').addEventListener('click',()=>$('detail').close());
$('search').addEventListener('input',renderCases);
$('family').addEventListener('change',renderCases);
$('kind').addEventListener('change',renderCases);
$('time-family').addEventListener('change',renderTimeline);
$('reset').addEventListener('click',()=>{state.lens='';state.collection='';state.point='';$('search').value='';$('family').value='';$('kind').value='';renderCases();});
$('theme').addEventListener('click',()=>{const dark=document.body.classList.toggle('dark');$('theme').textContent=dark?'日间':'夜间';$('theme').setAttribute('aria-pressed',String(dark));});
renderCases();renderTimeline();
