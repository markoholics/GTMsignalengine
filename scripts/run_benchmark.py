"""Run unbranded category prompts through an OpenRouter model and write outputs/<slug>/benchmark.json.

Usage:
    export OPENROUTER_API_KEY=...
    python scripts/run_benchmark.py --project markoholics --model <openrouter-model-id>

Prompts come from --prompts (one per line) or, by default, from the prompts already in the project's
benchmark.json. Results are model-specific: they say nothing about ChatGPT, Perplexity, Gemini or
Google AI Overviews unless you measure those platforms directly.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE = "https://openrouter.ai/api/v1"
URL_RE = re.compile(r"https?://[^\s)\]>\"']+|\b(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s)\]>\"']*)?", re.I)


def word_match(name: str, text: str) -> bool:
    """Case-insensitive match that doesn't fire inside longer words (e.g. 'Triple' in 'Tripled')."""
    pattern = r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])"
    return re.search(pattern, text, re.I) is not None


def host_of(url: str) -> str:
    h = re.sub(r"^https?://", "", url.strip().lower()).split("/")[0]
    return h[4:] if h.startswith("www.") else h


def analyse(answer: str, brand: str, aliases: list[str], competitors: list[str], domain: str) -> dict:
    owned = False
    if domain:
        d = host_of(domain)
        owned = any(host_of(u) == d or host_of(u).endswith("." + d) for u in URL_RE.findall(answer))
    return {
        "brand_mentioned": any(word_match(n, answer) for n in [brand, *aliases]),
        "competitors": [c for c in competitors if word_match(c, answer)],
        "owned_source_cited": owned,
    }


def ask(prompt: str, model: str, key: str, base: str, retries: int = 3) -> str:
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            return data["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as exc:
            retryable = exc.code in (429, 500, 502, 503, 504)
            if not retryable or attempt == retries - 1:
                raise RuntimeError(f"HTTP {exc.code}: {exc.read()[:200]!r}") from exc
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError("unreachable")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default="markoholics")
    ap.add_argument("--model", default=os.environ.get("OPENROUTER_MODEL"), help="OpenRouter model id")
    ap.add_argument("--prompts", help="text file, one prompt per line")
    ap.add_argument("--runs", type=int, default=1, help="repeat each prompt N times (answers vary)")
    ap.add_argument("--base-url", default=os.environ.get("OPENROUTER_BASE_URL", DEFAULT_BASE))
    ap.add_argument("--out-dir", default=str(ROOT / "outputs"))
    a = ap.parse_args()

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("Set OPENROUTER_API_KEY first.")
    if not a.model:
        sys.exit("Pass --model <openrouter-model-id> (or set OPENROUTER_MODEL).")

    folder = Path(a.out_dir) / a.project
    meta = json.loads((folder / "project.json").read_text())
    if not meta.get("website"):
        print("Warning: project.json has no 'website'; owned-source citations cannot be detected.", file=sys.stderr)
    if a.prompts:
        prompts = [l.strip() for l in Path(a.prompts).read_text().splitlines() if l.strip()]
    else:
        prompts = [r["prompt"] for r in json.loads((folder / "benchmark.json").read_text())["results"]]

    results = []
    for i, prompt in enumerate(prompts, 1):
        for run in range(1, a.runs + 1):
            print(f"[{i}/{len(prompts)} run {run}] {prompt[:70]}", file=sys.stderr)
            answer = ask(prompt, a.model, key, a.base_url)
            res = analyse(answer, meta["brand"], meta.get("aliases", []), meta.get("competitors", []),
                          meta.get("website", ""))
            results.append({"id": f"organic_prompt_{len(results) + 1:03d}", "prompt": prompt, "run": run,
                            **res, "answer_excerpt": answer[:600], "answer_full": answer})

    out = {"model": a.model, "measured": True, "run_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "notes": "Model-specific benchmark. Not evidence of visibility on other AI platforms.",
           "results": results}
    (folder / "benchmark.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    n = len(results)
    print(f"Wrote {folder/'benchmark.json'}: mentioned {sum(r['brand_mentioned'] for r in results)}/{n}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
