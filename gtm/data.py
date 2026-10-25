"""Loading and deriving data from a project's output folder."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"

# file name -> (key, freshness label)
MODULES = {
    "project.json": ("project", "Project"),
    "source_health.json": ("source_health", "Source health"),
    "voc.json": ("voc", "VOC"),
    "aeo_geo.json": ("aeo", "AEO/GEO"),
    "benchmark.json": ("benchmark", "Benchmark"),
    "organic_gap.json": ("gap", "Organic gap"),
    "strategy_packet.json": ("strategy", "Strategy packet"),
    "prompt_pack.json": ("prompts", "Prompt pack"),
    "reviews.json": ("reviews", "Reviews"),
    "screenshots.json": ("screenshots", "Screenshots"),
    "ads.json": ("ads", "Ads"),
}
OPTIONAL = {"reviews", "screenshots", "ads"}


@dataclass
class Project:
    slug: str
    path: Path
    data: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def available(self, key: str) -> bool:
        return key in self.data

    @property
    def meta(self) -> dict:
        return self.data.get("project", {})

    @property
    def name(self) -> str:
        return self.meta.get("brand", self.slug)


def list_projects(root: Path = OUTPUTS_DIR) -> list[str]:
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir() and (p / "project.json").exists())


def load_project(slug: str, root: Path = OUTPUTS_DIR) -> Project:
    path = root / slug
    proj = Project(slug=slug, path=path)
    for fname, (key, _) in MODULES.items():
        f = path / fname
        if not f.exists():
            continue
        try:
            proj.data[key] = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            proj.errors[fname] = str(exc)
    return proj


def freshness(proj: Project) -> list[tuple[str, str]]:
    """(label, status) where status is available | skipped | error."""
    out = []
    for fname, (key, label) in MODULES.items():
        if key == "project":
            continue
        if fname in proj.errors:
            out.append((label, "error"))
        elif key in proj.data:
            out.append((label, "available"))
        elif key in OPTIONAL:
            out.append((label, "skipped"))
        else:
            out.append((label, "missing"))
    return out


# ---- derived metrics -------------------------------------------------------

def overview_metrics(proj: Project) -> dict:
    bench = proj.get("benchmark", {})
    results = bench.get("results", [])
    n = len(results)
    mentioned = sum(1 for r in results if r.get("brand_mentioned"))
    owned = sum(1 for r in results if r.get("owned_source_cited"))
    comps: dict[str, int] = {}
    for r in results:
        for c in r.get("competitors", []):
            comps[c] = comps.get(c, 0) + 1
    voc = proj.get("voc", {})
    return {
        "prompts_tested": n,
        "mention_rate": round(100 * mentioned / n) if n else None,
        "owned_rate": round(100 * owned / n) if n else None,
        "competitors": sorted(comps, key=lambda c: -comps[c]),
        "competitor_counts": comps,
        "voc_confidence": voc.get("confidence", "unknown"),
        "voc_records": len(voc.get("records", [])),
        "model": bench.get("model", "unconfigured model"),
    }


def build_roadmap(proj: Project) -> dict[str, list[dict]]:
    """Merge action items from benchmark, VOC and AEO modules into lanes, deduped by title."""
    items: dict[str, dict] = {}

    def add(title, lane, detail, owner, source, evidence, impact="unknown"):
        key = title.strip().lower()
        if key in items:
            items[key]["sources"].add(source)
            items[key]["evidence"].extend(e for e in evidence if e not in items[key]["evidence"])
            return
        items[key] = {"title": title, "lane": lane, "detail": detail, "owner": owner,
                      "sources": {source}, "evidence": list(evidence), "impact": impact}

    for a in proj.get("gap", {}).get("recommended_actions", []):
        add(a["title"], a.get("lane", "build_now"), a.get("detail", ""), a.get("owner", "GEO/AEO"),
            "organic_gap_explainer", a.get("evidence", []), a.get("impact", "unknown"))
    for a in proj.get("aeo", {}).get("answer_assets", []):
        add(a["title"], a.get("lane", "build_now"), a.get("why", ""), a.get("owner", "GEO/AEO"),
            "aeo_geo", [a["id"]] if a.get("id") else [], a.get("impact", "unknown"))
    for t in proj.get("voc", {}).get("themes", []):
        lane = "build_now" if t.get("volume", 0) >= 4 else "monitor_later"
        add(t["name"], lane, t.get("question", ""), t.get("owner", "Content"),
            "voc_intelligence", t.get("record_ids", []), "high" if lane == "build_now" else "low")

    lanes = {"build_now": [], "needs_evidence": [], "needs_reviews": [], "monitor_later": []}
    for it in items.values():
        it["sources"] = sorted(it["sources"])
        lanes.setdefault(it["lane"], []).append(it)
    return lanes
