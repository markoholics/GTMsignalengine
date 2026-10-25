# GTM Signal Engine for Markoholics

Streamlit dashboard for AI growth, voice-of-customer (VOC) and organic/AI-answer visibility intelligence.

## Run

```bash
pip install -r requirements.txt
python scripts/seed_sample.py      # writes illustrative sample data to outputs/markoholics/
streamlit run app.py
```

Open `http://localhost:8501/?project=markoholics&theme=light`.

## Tabs

Overview · Source Health · VOC Intelligence · AEO/GEO Map · Benchmark · Organic Gap Explainer ·
Content Roadmap · Strategy Packet · LLM Prompt Pack · Exports & Raw JSON

## Data

Each project is a folder `outputs/<slug>/` of JSON files (`project`, `source_health`, `voc`, `aeo_geo`,
`benchmark`, `organic_gap`, `strategy_packet`, `prompt_pack`; optional `reviews`, `screenshots`, `ads`).
Missing files show as skipped/missing in the sidebar. The Content Roadmap is derived by merging and
de-duplicating actions from the gap, AEO/GEO and VOC modules.

**The bundled `markoholics` data is placeholder sample data, not measurements.** Replace the JSON with
real pipeline output (same schema) before drawing conclusions. Benchmark results are model-specific and
are not evidence of visibility on ChatGPT, Perplexity, Gemini or Google AI Overviews.

## Benchmark runner (OpenRouter)

```bash
export OPENROUTER_API_KEY=...
# set "website" in outputs/<slug>/project.json so owned-source citations can be detected
python scripts/run_benchmark.py --project markoholics --model <openrouter-model-id> [--runs 3]
```

Sends each unbranded prompt to the model, records whether the brand and each competitor is named and
whether the brand's domain is cited, and writes `outputs/<slug>/benchmark.json` (`measured: true`).
Matching is whole-word and case-insensitive. Results are model-specific.

## Static site (Vercel)

Streamlit needs a long-running server, which Vercel does not provide, so `web/` is a static port that
reads the same JSON. After changing data: `python scripts/build_static.py`, then redeploy `web/`.
