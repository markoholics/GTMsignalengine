"""Write an illustrative sample project to outputs/markoholics/.

All values are placeholders so the dashboard has something to render.
Replace the JSON files with real pipeline output (same schema) for real analysis.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "outputs" / "markoholics"
OUT.mkdir(parents=True, exist_ok=True)


def w(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2), encoding="utf-8")


w("project.json", {
    "brand": "Markoholics", "slug": "markoholics", "category": "Growth marketing & GTM",
    "website": "", "model": "configured-model (sample)", "status": "sample_data",
    "generated_at": "2026-10-25", "competitors": ["Sample Competitor A", "Sample Competitor B", "Sample Competitor C"],
    "sample": True,
    "disclaimer": "Sample data: illustrative placeholders, not measured results. Replace outputs/markoholics/*.json with real pipeline output.",
})

w("source_health.json", {"sources": [
    {"name": "Benchmark (LLM category prompts)", "type": "model", "status": "available", "records": 5, "last_checked": "2026-10-25", "note": "Sample results; swap for a real run."},
    {"name": "VOC verbatims", "type": "customer voice", "status": "available", "records": 18, "last_checked": "2026-10-25", "note": "Small sample; confidence capped at medium."},
    {"name": "Reviews", "type": "marketplace", "status": "skipped", "records": 0, "last_checked": "n/a", "note": "No review source connected."},
    {"name": "Screenshots", "type": "visual proof", "status": "skipped", "records": 0, "last_checked": "n/a", "note": "Not collected."},
    {"name": "Ads", "type": "paid", "status": "skipped", "records": 0, "last_checked": "n/a", "note": "No ad account connected."},
]})

themes = [
    ("Pricing & what's included", 5, "What does it cost and what do I get at each tier?", "Product Page"),
    ("Getting started", 4, "How do I get started and what should I do first?", "Product Page"),
    ("Proof & results", 4, "What results can I realistically expect?", "Trust/Reviews"),
    ("Tool & channel choice", 3, "Which channel or tool should I prioritise first?", "Creative"),
    ("Agency vs in-house", 2, "Should I hire an agency or build in-house?", "Content"),
]
recs = []
texts = {
    "Pricing & what's included": ["Hard to tell what the starter tier actually includes.", "Is reporting extra or bundled?", "Wish pricing was on one page.", "Unclear if setup is billed separately.", "What is the minimum commitment?"],
    "Getting started": ["Where do I begin with no marketing team?", "What is the first 30 days like?", "Do I need analytics set up first?", "How long until I see anything?"],
    "Proof & results": ["Any case studies for small B2B?", "Are the results typical or cherry-picked?", "How do you measure success?", "Looking for numbers, not adjectives."],
    "Tool & channel choice": ["SEO or paid first on a tight budget?", "Is LinkedIn worth it for us?", "Too many tools, which ones matter?"],
    "Agency vs in-house": ["At what size does in-house make sense?", "Hidden costs of hiring a head of growth?"],
}
i = 1
for t, _, _, _ in themes:
    for s in texts[t]:
        recs.append({"id": f"voc_{i:03d}", "source": "sample", "theme": t, "text": s, "sentiment": "neutral"})
        i += 1
w("voc.json", {"confidence": "medium", "records": recs, "themes": [
    {"name": n, "volume": v, "question": q, "owner": o, "record_ids": [r["id"] for r in recs if r["theme"] == n]}
    for n, v, q, o in themes]})

w("aeo_geo.json", {
    "questions": [
        {"id": "q1", "question": "What does a growth marketing partner typically cost?", "intent": "pricing", "voc_backed": True},
        {"id": "q2", "question": "How do I start a GTM motion with no marketing team?", "intent": "getting started", "voc_backed": True},
        {"id": "q3", "question": "What results can B2B startups expect from growth marketing?", "intent": "proof", "voc_backed": True},
        {"id": "q4", "question": "SEO or paid first on a small budget?", "intent": "channel choice", "voc_backed": True},
        {"id": "q5", "question": "Agency vs in-house marketing: when to switch?", "intent": "comparison", "voc_backed": True},
    ],
    "content_gaps": ["Pricing explainer", "First 30 days playbook", "Case study library", "Channel chooser", "Agency vs in-house guide"],
    "schema_opportunities": [
        {"type": "FAQPage", "page": "Pricing", "why": "Answer cost and scope questions directly"},
        {"type": "HowTo", "page": "Getting started", "why": "Step-by-step onboarding"},
        {"type": "Organization", "page": "Home", "why": "Entity clarity for answer engines"},
        {"type": "Service", "page": "Services", "why": "Describe offerings"},
        {"type": "Article", "page": "Blog", "why": "Authorship and dates"},
        {"type": "Review", "page": "Case studies", "why": "Only once real reviews are collected"},
        {"type": "BreadcrumbList", "page": "Site-wide", "why": "Structure"},
    ],
    "briefs": [
        {"title": "Growth marketing pricing explained", "audience": "Founders comparing options", "outline": ["What drives cost", "Tier-by-tier scope", "What is not included", "How to budget"]},
        {"title": "Your first 30 days of GTM", "audience": "Teams with no marketing function", "outline": ["Week 1 foundations", "Week 2 channel test", "Week 3 measure", "Week 4 decide"]},
        {"title": "Case study library", "audience": "Skeptical buyers", "outline": ["Context", "Approach", "Measured result", "What we would do differently"]},
        {"title": "SEO vs paid first", "audience": "Budget-constrained founders", "outline": ["Decision criteria", "Time to signal", "Budget thresholds"]},
        {"title": "Agency vs in-house", "audience": "Scaling startups", "outline": ["Cost model", "Capability gaps", "Switch triggers"]},
    ],
    "answer_assets": [
        {"id": "aeo_gap_001", "title": "Pricing & scope FAQ block", "why": "Pricing questions need clear brand-owned answers near the offer.", "owner": "Near pricing section", "lane": "build_now", "impact": "high"},
        {"id": "aeo_gap_002", "title": "Getting-started chooser", "why": "Uncertainty about where to begin raises first-call friction.", "owner": "Near CTA", "lane": "monitor_later", "impact": "low"},
        {"id": "aeo_gap_003", "title": "Results & proof block", "why": "Buyers want measurable proof, not adjectives.", "owner": "Near claims section", "lane": "needs_reviews", "impact": "unknown"},
        {"id": "aeo_gap_004", "title": "Neutral comparison page", "why": "Handle comparison demand with neutral criteria and owned facts, not unverified competitor claims.", "owner": "Content hub", "lane": "needs_evidence", "impact": "low"},
        {"id": "aeo_gap_005", "title": "Channel chooser", "why": "Reduces channel-choice paralysis with guided criteria.", "owner": "Content hub", "lane": "monitor_later", "impact": "low"},
    ],
})

prompts = [
    ("organic_prompt_001", "What are the best growth marketing partners for B2B startups?", True, ["Sample Competitor A", "Sample Competitor B"], False),
    ("organic_prompt_002", "How do I build a go-to-market strategy with no marketing team?", False, ["Sample Competitor A"], False),
    ("organic_prompt_003", "Agency vs in-house marketing for an early-stage startup?", True, ["Sample Competitor B", "Sample Competitor C"], False),
    ("organic_prompt_004", "What should a growth marketing retainer include?", True, ["Sample Competitor A"], False),
    ("organic_prompt_005", "How do I measure ROI from content marketing?", False, [], False),
]
w("benchmark.json", {"model": "configured-model (sample)", "notes": "Illustrative sample results.", "results": [
    {"id": i, "prompt": p, "brand_mentioned": m, "competitors": c, "owned_source_cited": o,
     "answer_excerpt": "Sample placeholder, not a real model answer."} for i, p, m, c, o in prompts]})

w("organic_gap.json", {
    "executive_summary": "Sample: Markoholics appears in some, not all, category answers in this illustrative benchmark. No owned-source references were observed, so owned authority is the main gap to investigate.",
    "authority_gaps": [
        {"hypothesis": "Detected competitors may be more strongly associated with generic category recommendation terms in this model's answers.", "confidence": "medium"},
        {"hypothesis": "No owned-source citations were observed, so brand-owned category authority is not visible in these answers.", "confidence": "medium"},
        {"hypothesis": "Missing reviews, case studies, or third-party proof may lower confidence in authority-related recommendations.", "confidence": "medium"}],
    "recommended_actions": [
        {"title": "Best growth marketing partner category page", "detail": "Improve organic category-answer inclusion in future model-specific benchmark tests.", "owner": "GEO/AEO", "lane": "build_now", "evidence": ["organic_gap_explainer"]},
        {"title": "Growth marketing FAQ page", "detail": "Improve organic category-answer inclusion in future model-specific benchmark tests.", "owner": "GEO/AEO", "lane": "build_now", "evidence": ["organic_prompt_001"]},
        {"title": "Neutral comparison page", "detail": "Handle comparison demand with neutral criteria and owned facts.", "owner": "GEO/AEO", "lane": "needs_evidence", "evidence": ["organic_prompt_001", "organic_prompt_003"], "impact": "low"},
        {"title": "Review proof block, only after reviews are collected", "detail": "Do not publish proof until real reviews exist.", "owner": "Trust/Reviews", "lane": "needs_reviews"},
        {"title": "FAQPage/Service/HowTo schema support", "detail": "Add structured data once the pages above exist.", "owner": "GEO/AEO", "lane": "build_now"}]})

w("strategy_packet.json", {
    "next_best_actions": [
        "Best growth marketing partner category page", "Growth marketing FAQ page",
        "Pricing & scope FAQ block", "Getting-started playbook",
        "Neutral comparison table, with claims verified before publishing"],
    "sections": [
        {"heading": "Situation", "body": ["Sample data only. Replace with findings from a real benchmark and VOC run."]},
        {"heading": "Where to win", "body": ["Own the answers to pricing, getting-started, proof, channel choice and agency-vs-in-house questions."]},
        {"heading": "Guardrails", "body": ["Benchmark results are model-specific.", "Do not publish competitor claims without evidence.", "Do not publish proof before reviews or case studies exist."]}]})

cats = {
    "Benchmark": [("Best partners", "List the best {category} partners for {audience}. Give a short reason for each."),
                  ("How-to", "How do I {goal} with no dedicated team? Give practical steps."),
                  ("Comparison", "Compare agency vs in-house for {category}. When does each make sense?")],
    "Content": [("FAQ draft", "Write an FAQ for {brand} answering: pricing, scope, getting started, results. Use only facts I supply."),
                ("Case study", "Turn these notes into a case study: context, approach, measured result, lessons. Do not invent numbers.")],
}
w("prompt_pack.json", {"prompts": [
    {"id": f"pp_{n:02d}", "category": c, "purpose": pur, "prompt": txt}
    for n, (c, pur, txt) in enumerate(((c, a, b) for c, xs in cats.items() for a, b in xs), 1)]})
print("wrote", OUT)
