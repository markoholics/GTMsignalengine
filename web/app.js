const FILES={project:'project',source_health:'source_health',voc:'voc',aeo:'aeo_geo',benchmark:'benchmark',gap:'organic_gap',strategy:'strategy_packet',prompts:'prompt_pack'};
const OPTIONAL=['reviews','screenshots','ads'];
const CAVEAT='Benchmark results are model-specific and not evidence of ChatGPT, Perplexity, Gemini, or Google AI Overview visibility unless those platforms are explicitly measured.';
const $=s=>document.querySelector(s);
const e=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const TONE={available:'good','build now':'good',build_now:'good',high:'good',medium:'warn','needs evidence':'warn',skipped:'warn',missing:'warn',low:'bad',error:'bad'};
const badge=(t,tone)=>`<span class="badge ${tone||TONE[String(t).toLowerCase()]||''}">${e(t)}</span>`;
const card=(t,b,s,f,tags=[])=>`<div class="card"><div class="row"><h4>${e(t)}</h4>${s?badge(s):''}</div>${b?`<p>${e(b)}</p>`:''}${f?`<p><b>${e(f)}</b></p>`:''}${tags.map(x=>`<span class="tag">${e(x)}</span>`).join('')}</div>`;
const metrics=m=>`<div class="grid">${m.map(([l,v,s])=>`<div class="metric"><div class="l">${e(l)}</div><div class="v">${e(v)}</div><div class="s">${e(s)}</div></div>`).join('')}</div>`;
const sec=(t,c)=>`<h3>${e(t)}</h3>${c?`<div class="muted" style="margin:-8px 0 12px">${e(c)}</div>`:''}`;
const banner=t=>`<div class="banner">⚠ ${e(t)}</div>`;
const empty=m=>`<p class="muted">No ${e(m)} data found for this project yet.</p>`;
let P={};

function overview(){const b=P.benchmark?.results||[];const n=b.length;
 const ment=b.filter(r=>r.brand_mentioned).length,own=b.filter(r=>r.owned_source_cited).length;
 const cc={};b.forEach(r=>(r.competitors||[]).forEach(c=>cc[c]=(cc[c]||0)+1));
 return{n,ment,own,cc,comps:Object.keys(cc).sort((a,b)=>cc[b]-cc[a]),pct:v=>n?Math.round(100*v/n)+'%':'n/a'};}
const T={};
T['Overview']=()=>{const o=overview();if(!o.n)return sec('Command Center')+empty('benchmark');const nm=P.project.brand;
 return sec('Command Center','Reading outputs/'+P.slug)+banner(CAVEAT)+
 `<div class="card">${badge('Signal','warn')}<h2>${e(nm)} ${o.ment?'appeared in':'did not appear in'} organic category answers.</h2><p>In ${o.n} ${e(P.benchmark.model)} category prompts. ${o.own?'Owned sources were cited in some answers.':'Owned-source authority was not observed.'}</p></div>`+
 metrics([['Organic mention rate',o.pct(o.ment),'Unbranded category prompts'],['Prompts tested',o.n,'Configured model only'],['Competitors detected',o.comps.length+' brands',o.comps.slice(0,3).join(', ')||'none surfaced'],['Owned source reference rate',o.pct(o.own),'Owned citations observed'],['VOC confidence',P.voc?.confidence||'unknown',(P.voc?.records||[]).length+' records analyzed']])+
 `<div class="card"><div class="row"><h4>Next best actions</h4>${badge('build now')}</div>${(P.strategy?.next_best_actions||[]).map((a,i)=>`<p>${i+1}. ${e(a)}</p>`).join('')}</div>`;};
T['Source Health']=()=>{const s=P.source_health?.sources;if(!s)return empty('source health');
 return sec('Source Health','Which inputs are feeding this project.')+metrics([['Sources',s.length,'Configured inputs'],['Available',s.filter(x=>x.status==='available').length,'Ready to use']])+s.map(x=>card(x.name,x.note,x.status,`${x.records} records · ${x.type}`,['Last checked: '+x.last_checked])).join('');};
T['VOC Intelligence']=()=>{const v=P.voc;if(!v)return empty('VOC');const mx=Math.max(...v.themes.map(t=>t.volume),1);
 return sec('VOC Intelligence','Voice-of-customer themes, questions and verbatims.')+metrics([['Records',v.records.length,'Verbatims'],['Themes',v.themes.length,'Clustered topics'],['Confidence',v.confidence,'Based on sample size']])+
 [...v.themes].sort((a,b)=>b.volume-a.volume).map(t=>`<div class="card"><div class="row"><h4>${e(t.name)}</h4>${badge(t.volume>=4?'high':'low')}</div><p>${e(t.question)}</p><div class="bar" style="width:${100*t.volume/mx}%"></div><p><b>Owner: ${e(t.owner)}</b> · ${t.volume} mentions</p></div>`).join('')+
 sec('Verbatims')+`<table><tr><th>ID</th><th>Theme</th><th>Text</th></tr>${v.records.map(r=>`<tr><td>${e(r.id)}</td><td>${e(r.theme)}</td><td>${e(r.text)}</td></tr>`).join('')}</table>`;};
T['AEO/GEO Map']=()=>{const a=P.aeo;if(!a)return empty('AEO/GEO');
 return sec('AEO/GEO Map','Answer-engine assets, question surfaces, gaps, schema, and briefs.')+metrics([['Questions',a.questions.length,'VOC-backed'],['Content gaps',a.content_gaps.length,'Owned opportunities'],['Schema opportunities',a.schema_opportunities.length,'Structured data'],['Content briefs',a.briefs.length,'Build-ready']])+
 sec('Answer Assets To Own')+a.answer_assets.map(x=>card(x.title,x.why,(x.lane||'build_now').replace('_',' '),'Owner: '+x.owner)).join('')+
 `<details><summary>Question surfaces</summary><table>${a.questions.map(q=>`<tr><td>${e(q.question)}</td><td>${e(q.intent)}</td></tr>`).join('')}</table></details>`+
 `<details><summary>Schema opportunities</summary><table>${a.schema_opportunities.map(q=>`<tr><td>${e(q.type)}</td><td>${e(q.page)}</td><td>${e(q.why)}</td></tr>`).join('')}</table></details>`+
 `<details><summary>Content briefs</summary>${a.briefs.map(b=>`<p><b>${e(b.title)}</b> — <i>${e(b.audience)}</i></p><ul>${b.outline.map(o=>`<li>${e(o)}</li>`).join('')}</ul>`).join('')}</details>`;};
T['Benchmark']=()=>{const b=P.benchmark;if(!b)return empty('benchmark');const o=overview();
 return sec('Benchmark','Unbranded category prompts run against the configured model.')+banner(CAVEAT)+(b.measured?badge('Measured run','good')+` <span class="muted">${e(b.run_at||'')}</span>`:'')+
 metrics([['Model',b.model,'Configured'],['Prompts',o.n,'Unbranded'],['Mention rate',o.pct(o.ment),'Brand named'],['Owned citation rate',o.pct(o.own),'Own domain cited']])+
 b.results.map(r=>`<details><summary>${e(r.id)} · ${e(r.prompt)}</summary><p>Brand mentioned: ${badge(r.brand_mentioned?'yes':'no',r.brand_mentioned?'good':'bad')} Owned source cited: ${badge(r.owned_source_cited?'yes':'no',r.owned_source_cited?'good':'bad')}</p><p><b>Competitors:</b> ${e((r.competitors||[]).join(', ')||'none')}</p><pre>${e(r.answer_full||r.answer_excerpt||'')}</pre></details>`).join('');};
T['Organic Gap Explainer']=()=>{const g=P.gap;if(!g)return empty('organic gap');const o=overview();
 return sec('Organic Gap Explainer','Strategy memo for '+P.project.brand+' organic category-answer authority.')+card('Executive Summary',g.executive_summary,'available','Model-specific category benchmark')+
 sec('Owned Authority Gaps')+g.authority_gaps.map(x=>card('Owned Authority Gap','Hypothesis: '+x.hypothesis,x.confidence)).join('')+
 sec('Competitor Presence Drivers')+o.comps.map(c=>card('Competitor Presence Driver',`${c} appeared in ${o.cc[c]} of ${o.n} organic answer(s); treat this as model-output presence only, not validated competitor strength.`,'medium')).join('');};
function roadmap(){const items={};const add=(t,lane,detail,owner,src,ev,impact='unknown')=>{const k=t.trim().toLowerCase();if(items[k]){items[k].sources.add(src);ev.forEach(x=>{if(!items[k].evidence.includes(x))items[k].evidence.push(x)});return}items[k]={t,lane,detail,owner,sources:new Set([src]),evidence:[...ev],impact}};
 (P.gap?.recommended_actions||[]).forEach(a=>add(a.title,a.lane||'build_now',a.detail||'',a.owner||'GEO/AEO','organic_gap_explainer',a.evidence||[],a.impact));
 (P.aeo?.answer_assets||[]).forEach(a=>add(a.title,a.lane||'build_now',a.why||'',a.owner||'GEO/AEO','aeo_geo',a.id?[a.id]:[],a.impact));
 (P.voc?.themes||[]).forEach(t=>{const l=t.volume>=4?'build_now':'monitor_later';add(t.name,l,t.question||'',t.owner||'Content','voc_intelligence',t.record_ids||[],l==='build_now'?'high':'low')});
 const lanes={build_now:[],needs_evidence:[],needs_reviews:[],monitor_later:[]};Object.values(items).forEach(i=>(lanes[i.lane]=lanes[i.lane]||[]).push(i));return lanes;}
T['Content Roadmap']=()=>{const L=roadmap();const names=[['build_now','Build Now'],['needs_evidence','Needs Evidence'],['needs_reviews','Needs Reviews'],['monitor_later','Monitor Later']];
 return sec('Content Roadmap','Kanban-style action system deduped across benchmark, VOC, and AEO/GEO modules.')+`<div class="lanes">${names.map(([k,n])=>`<div><b>${n}</b> <span class="muted">(${L[k].length})</span>${L[k].map(i=>card(i.t,i.detail,i.impact,'Owner: '+i.owner,[...new Set([...i.sources,...i.evidence.slice(0,3)])])).join('')}</div>`).join('')}</div>`;};
T['Strategy Packet']=()=>{const s=P.strategy;if(!s)return empty('strategy packet');return sec('Strategy Packet','Narrative summary you can hand to a stakeholder.')+s.sections.map(x=>`<div class="card"><h4>${e(x.heading)}</h4>${x.body.map(b=>`<p>${e(b)}</p>`).join('')}</div>`).join('');};
T['LLM Prompt Pack']=()=>{const p=P.prompts;if(!p)return empty('prompt pack');return sec('LLM Prompt Pack','Copy-ready prompts for benchmarking and content generation.')+p.prompts.map(x=>`<details><summary>${e(x.id)} · ${e(x.purpose)} <span class="tag">${e(x.category)}</span></summary><pre>${e(x.prompt)}</pre></details>`).join('');};
T['Exports & Raw JSON']=()=>sec('Exports & Raw JSON','Inspect or download the underlying data.')+Object.entries(P).filter(([k])=>k!=='slug').map(([k,v])=>`<details><summary>${e(k)}</summary><pre>${e(JSON.stringify(v,null,2))}</pre></details>`).join('');

async function load(slug){P={slug};const miss=[];
 await Promise.all(Object.entries(FILES).map(async([k,f])=>{try{const r=await fetch(`outputs/${slug}/${f}.json`);if(r.ok)P[k]=await r.json();else miss.push(k)}catch{miss.push(k)}}));
 $('#fresh').innerHTML=Object.keys(FILES).filter(k=>k!=='project').map(k=>`<div>${badge(k.replace('_',' ')+': '+(P[k]?'available':'missing'))}</div>`).join('')+OPTIONAL.map(k=>`<div>${badge(k+': skipped')}</div>`).join('');
 $('#sample').innerHTML=P.project?.sample?banner(P.project.disclaimer||'Sample data – illustrative only.'):'';show(sessionStorage.tab||'Overview');}
function show(name){sessionStorage.tab=name;document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.textContent===name));$('#view').innerHTML=P.project?T[name]():empty('project');}
(async()=>{const q=new URLSearchParams(location.search);
 const idx=await (await fetch('outputs/projects.json')).json();
 $('#project').innerHTML=idx.map(s=>`<option>${e(s)}</option>`).join('');if(idx.includes(q.get('project')))$('#project').value=q.get('project');
 $('#theme').value=q.get('theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
 const setTheme=()=>document.documentElement.dataset.theme=$('#theme').value;setTheme();$('#theme').onchange=setTheme;
 $('#tabs').innerHTML=Object.keys(T).map(n=>`<button>${e(n)}</button>`).join('');$('#tabs').onclick=ev=>ev.target.tagName==='BUTTON'&&show(ev.target.textContent);
 $('#project').onchange=()=>load($('#project').value);load($('#project').value);})();
