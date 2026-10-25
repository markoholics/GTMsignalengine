"""One render function per dashboard tab."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from . import ui
from .data import Project, build_roadmap, freshness, overview_metrics

BENCH_CAVEAT = ("Benchmark results are model-specific and not evidence of ChatGPT, Perplexity, Gemini, "
                "or Google AI Overview visibility unless those platforms are explicitly measured.")


def _pct(v):
    return "n/a" if v is None else f"{v}%"


def overview(p: Project) -> None:
    ui.section("Command Center", f"Reading local outputs from {p.path}")
    ui.banner(BENCH_CAVEAT)
    m = overview_metrics(p)
    if not m["prompts_tested"]:
        ui.empty("benchmark")
        return
    mentioned = m["mention_rate"] and m["mention_rate"] > 0
    headline = (f"{p.name} appeared in organic category answers." if mentioned
                else f"{p.name} did not appear in organic category answers.")
    owned_note = ("Owned-source authority was not observed." if not m["owned_rate"]
                  else "Owned sources were cited in some answers.")
    st.markdown(
        f'<div class="gtm-card"><div>{ui.badge("Signal", "warn")}</div>'
        f'<h2 style="margin:10px 0 4px">{ui.e(headline)}</h2>'
        f'<p>In {m["prompts_tested"]} {ui.e(m["model"])} category prompts. {ui.e(owned_note)}</p></div>',
        unsafe_allow_html=True)
    comps = f'{len(m["competitors"])} brands'
    comp_names = ", ".join(m["competitors"][:3]) or "none surfaced"
    ui.metric_row([
        ("Organic mention rate", _pct(m["mention_rate"]), "Unbranded category prompts"),
        ("Prompts tested", m["prompts_tested"], "Configured model only"),
        ("Competitors detected", comps, comp_names),
        ("Owned source reference rate", _pct(m["owned_rate"]), "Owned citations observed"),
        ("VOC confidence", m["voc_confidence"], f'{m["voc_records"]} records analyzed'),
    ])
    st.write("")
    left, right = st.columns([2, 1])
    with left:
        actions = p.get("strategy", {}).get("next_best_actions", [])
        body = "".join(f"<p>{i}. {ui.e(a)}</p>" for i, a in enumerate(actions[:6], 1)) or "<p>No actions yet.</p>"
        st.markdown(f'<div class="gtm-card"><div class="gtm-row"><h4>Next best actions</h4>{ui.badge("build now")}</div>{body}</div>',
                    unsafe_allow_html=True)
    with right:
        meta = p.meta
        st.markdown(
            f'<div class="gtm-card"><div class="gtm-row"><h4>Project context</h4>{ui.badge(meta.get("status", "unknown"), "info")}</div>'
            f'<p>{ui.e(p.slug)} / {ui.e(p.name)}</p><p>{ui.e(meta.get("category", ""))}</p>'
            f'<p>Generated: {ui.e(meta.get("generated_at", "n/a"))}</p></div>', unsafe_allow_html=True)


def source_health(p: Project) -> None:
    ui.section("Source Health", "Which inputs are feeding this project and how trustworthy they are.")
    srcs = p.get("source_health", {}).get("sources", [])
    if not srcs:
        ui.empty("source health")
        return
    ok = sum(1 for s in srcs if s["status"] == "available")
    ui.metric_row([("Sources", len(srcs), "Configured inputs"), ("Available", ok, "Ready to use"),
                   ("Skipped / missing", len(srcs) - ok, "Not feeding insights"),
                   ("Records", sum(s.get("records", 0) for s in srcs), "Across all sources")])
    st.write("")
    for s in srcs:
        ui.card(s["name"], s.get("note", ""), s["status"], f'{s.get("records", 0)} records · {s.get("type", "")}',
                [f'Last checked: {s.get("last_checked", "n/a")}'])


def voc_intelligence(p: Project) -> None:
    ui.section("VOC Intelligence", "Voice-of-customer themes, questions and verbatims.")
    voc = p.get("voc")
    if not voc:
        ui.empty("VOC")
        return
    recs, themes = voc.get("records", []), voc.get("themes", [])
    ui.metric_row([("Records", len(recs), "Verbatims analyzed"), ("Themes", len(themes), "Clustered topics"),
                   ("Confidence", voc.get("confidence", "unknown"), "Based on sample size")])
    st.write("")
    st.markdown("#### Themes")
    if themes:
        df = pd.DataFrame(themes)[["name", "volume"]].set_index("name").sort_values("volume", ascending=False)
        st.bar_chart(df, horizontal=True, height=60 + 34 * len(df))
    for t in sorted(themes, key=lambda t: -t.get("volume", 0)):
        ui.card(t["name"], t.get("question", ""), "high" if t.get("volume", 0) >= 4 else "low",
                f'Owner: {t.get("owner", "n/a")}', [f'{t.get("volume", 0)} mentions'])
    st.markdown("#### Verbatims")
    theme_filter = st.selectbox("Filter by theme", ["All"] + [t["name"] for t in themes], key="voc_theme")
    rows = [r for r in recs if theme_filter == "All" or r.get("theme") == theme_filter]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def aeo_geo(p: Project) -> None:
    ui.section("AEO/GEO Map", "Answer-engine assets, question surfaces, gaps, schema, and briefs.")
    a = p.get("aeo")
    if not a:
        ui.empty("AEO/GEO")
        return
    ui.metric_row([("Questions generated", len(a.get("questions", [])), "VOC-backed answer targets"),
                   ("Content gaps", len(a.get("content_gaps", [])), "Owned content opportunities"),
                   ("Schema opportunities", len(a.get("schema_opportunities", [])), "Structured data candidates"),
                   ("Content briefs", len(a.get("briefs", [])), "Build-ready assets")])
    st.write("")
    ui.section("Answer Assets To Own", "What answer assets should the brand own?")
    for x in a.get("answer_assets", []):
        ui.card(x["title"], x.get("why", ""), x.get("lane", "build_now").replace("_", " "), f'Owner: {x.get("owner", "n/a")}')
    with st.expander("Question surfaces"):
        st.dataframe(pd.DataFrame(a.get("questions", [])), width="stretch", hide_index=True)
    with st.expander("Schema opportunities"):
        st.dataframe(pd.DataFrame(a.get("schema_opportunities", [])), width="stretch", hide_index=True)
    with st.expander("Content briefs"):
        for b in a.get("briefs", []):
            st.markdown(f"**{b['title']}** — _{b.get('audience', '')}_")
            st.markdown("\n".join(f"- {o}" for o in b.get("outline", [])))


def benchmark(p: Project) -> None:
    ui.section("Benchmark", "Unbranded category prompts run against the configured model.")
    ui.banner(BENCH_CAVEAT)
    b = p.get("benchmark")
    if not b:
        ui.empty("benchmark")
        return
    m = overview_metrics(p)
    ui.metric_row([("Model", m["model"], "Configured"), ("Prompts", m["prompts_tested"], "Unbranded"),
                   ("Mention rate", _pct(m["mention_rate"]), "Brand named in answer"),
                   ("Owned citation rate", _pct(m["owned_rate"]), "Own domain cited")])
    st.write("")
    if m["competitor_counts"]:
        st.markdown("#### Competitor / category brand presence")
        st.bar_chart(pd.Series(m["competitor_counts"], name="answers"), horizontal=True)
    st.markdown("#### Prompt results")
    for r in b.get("results", []):
        with st.expander(f'{r["id"]} · {r["prompt"]}'):
            st.markdown(f'Brand mentioned: {ui.badge("yes", "good") if r.get("brand_mentioned") else ui.badge("no", "bad")} '
                        f'&nbsp; Owned source cited: {ui.badge("yes", "good") if r.get("owned_source_cited") else ui.badge("no", "bad")}',
                        unsafe_allow_html=True)
            st.markdown(f'**Competitors surfaced:** {", ".join(r.get("competitors", [])) or "none"}')
            if r.get("answer_excerpt"):
                st.caption(r["answer_excerpt"])


def organic_gap(p: Project) -> None:
    ui.section("Organic Gap Explainer", f"Strategy memo for {p.name} organic category-answer authority.")
    g = p.get("gap")
    if not g:
        ui.empty("organic gap")
        return
    ui.card("Executive Summary", g.get("executive_summary", ""), "available", "Model-specific category benchmark")
    ui.section("Owned Authority Gaps")
    for x in g.get("authority_gaps", []):
        ui.card("Owned Authority Gap", f'Hypothesis: {x["hypothesis"]}', x.get("confidence", "medium"))
    ui.section("Competitor Presence Drivers")
    n = overview_metrics(p)["prompts_tested"]
    for c, k in overview_metrics(p)["competitor_counts"].items():
        ui.card("Competitor Presence Driver",
                f"{c} appeared in {k} of {n} organic answer(s); treat this as model-output presence only, not validated competitor strength.",
                "medium")


def content_roadmap(p: Project) -> None:
    ui.section("Content Roadmap", "Kanban-style action system deduped across benchmark, VOC, and AEO/GEO modules.")
    lanes = build_roadmap(p)
    if not any(lanes.values()):
        ui.empty("roadmap")
        return
    titles = [("build_now", "Build Now"), ("needs_evidence", "Needs Evidence"),
              ("needs_reviews", "Needs Reviews"), ("monitor_later", "Monitor Later")]
    for col, (key, title) in zip(st.columns(4), titles):
        with col:
            st.markdown(f'<div class="gtm-lane-title">{title} <span class="gtm-muted">({len(lanes[key])})</span></div>',
                        unsafe_allow_html=True)
            for it in lanes[key]:
                ui.card(it["title"], it["detail"], it["impact"], f'Owner: {it["owner"]}',
                        list(dict.fromkeys(it["sources"] + it["evidence"][:3])))


def strategy_packet(p: Project) -> None:
    ui.section("Strategy Packet", "Narrative summary you can hand to a stakeholder.")
    s = p.get("strategy")
    if not s:
        ui.empty("strategy packet")
        return
    for sec in s.get("sections", []):
        st.markdown(f'<div class="gtm-card"><h4>{ui.e(sec["heading"])}</h4>'
                    + "".join(f"<p>{ui.e(x)}</p>" for x in sec.get("body", [])) + "</div>", unsafe_allow_html=True)


def llm_prompt_pack(p: Project) -> None:
    ui.section("LLM Prompt Pack", "Copy-ready prompts for benchmarking and content generation.")
    pp = p.get("prompts")
    if not pp:
        ui.empty("prompt pack")
        return
    cats = sorted({x["category"] for x in pp.get("prompts", [])})
    pick = st.multiselect("Category", cats, default=cats)
    for x in pp["prompts"]:
        if x["category"] in pick:
            with st.expander(f'{x["id"]} · {x["purpose"]}'):
                st.code(x["prompt"], language="markdown", wrap_lines=True)


def exports(p: Project) -> None:
    ui.section("Exports & Raw JSON", "Download any module or inspect the underlying data.")
    st.download_button("Download full project JSON", json.dumps(p.data, indent=2), f"{p.slug}_all.json",
                       "application/json")
    if p.errors:
        st.error("Some files failed to parse: " + "; ".join(f"{k}: {v}" for k, v in p.errors.items()))
    for key, val in p.data.items():
        with st.expander(key):
            st.download_button(f"Download {key}.json", json.dumps(val, indent=2), f"{p.slug}_{key}.json",
                               "application/json", key=f"dl_{key}")
            st.json(val, expanded=False)


TABS = [("Overview", overview), ("Source Health", source_health), ("VOC Intelligence", voc_intelligence),
        ("AEO/GEO Map", aeo_geo), ("Benchmark", benchmark), ("Organic Gap Explainer", organic_gap),
        ("Content Roadmap", content_roadmap), ("Strategy Packet", strategy_packet),
        ("LLM Prompt Pack", llm_prompt_pack), ("Exports & Raw JSON", exports)]
