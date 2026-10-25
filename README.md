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
