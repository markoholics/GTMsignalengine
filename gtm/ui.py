"""Theme and small HTML components shared by all tabs."""
from __future__ import annotations

import html
import streamlit as st

PALETTES = {
    "light": dict(bg="#eef1f7", card="#ffffff", text="#111827", muted="#5b6578",
                  border="#e3e8f2", accent="#2563eb", shadow="0 4px 14px rgba(30,41,90,.07)"),
    "dark": dict(bg="#0d1117", card="#161b26", text="#e6e9f0", muted="#98a2b8",
                 border="#262d3d", accent="#60a5fa", shadow="0 4px 14px rgba(0,0,0,.4)"),
}
BADGES = {  # badge text -> (bg, fg)
    "good": ("#dcf7e6", "#146c3b"), "warn": ("#fdecd2", "#8a5200"),
    "bad": ("#fde0e0", "#a12626"), "info": ("#dfeafd", "#1d4ed8"), "neutral": ("#eceff5", "#3b4559"),
}
STATUS_TONE = {
    "available": "good", "build now": "good", "build_now": "good", "high": "good",
    "medium": "warn", "needs evidence": "warn", "skipped": "warn", "missing": "warn",
    "low": "bad", "error": "bad", "unknown": "neutral",
}


def e(x) -> str:
    return html.escape(str(x))


def inject_css(theme: str) -> None:
    p = PALETTES[theme]
    st.markdown(f"""
<style>
.stApp {{ background:{p['bg']}; color:{p['text']}; }}
[data-testid="stHeader"] {{ background:transparent; }}
section[data-testid="stSidebar"] {{ background:{p['card']}; border-right:1px solid {p['border']}; }}
section[data-testid="stSidebar"] * {{ color:{p['text']}; }}
.block-container {{ max-width:1100px; padding-top:2rem; }}
h1,h2,h3,h4,p,span,label,li {{ color:{p['text']}; }}
.gtm-hero,.gtm-card {{ background:{p['card']}; border:1px solid {p['border']}; border-radius:12px;
  padding:16px 20px; box-shadow:{p['shadow']}; margin-bottom:12px; }}
.gtm-hero h1 {{ margin:0; font-size:2rem; }}
.gtm-muted {{ color:{p['muted']} !important; font-size:.85rem; }}
.gtm-card h4 {{ margin:0 0 6px 0; font-size:.95rem; }}
.gtm-card p {{ margin:4px 0; font-size:.85rem; color:{p['muted']}; }}
.gtm-row {{ display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }}
.gtm-badge {{ display:inline-block; padding:2px 10px; border-radius:999px; font-size:.7rem;
  font-weight:700; white-space:nowrap; }}
.gtm-metric {{ background:{p['card']}; border:1px solid {p['border']}; border-radius:10px;
  padding:14px 16px; box-shadow:{p['shadow']}; height:100%; }}
.gtm-metric .l {{ font-size:.68rem; letter-spacing:.06em; text-transform:uppercase; color:{p['muted']}; }}
.gtm-metric .v {{ font-size:1.5rem; font-weight:800; margin:4px 0; line-height:1.2; }}
.gtm-metric .s {{ font-size:.75rem; color:{p['muted']}; }}
.gtm-banner {{ background:#fff7c2; color:#6b5a00; border:1px solid #f0e08a; border-radius:8px;
  padding:10px 14px; font-size:.85rem; margin:8px 0 16px; }}
.gtm-tag {{ display:inline-block; font-size:.68rem; color:{p['muted']}; background:{p['bg']};
  border:1px solid {p['border']}; border-radius:6px; padding:1px 6px; margin:2px 4px 0 0; }}
.gtm-lane-title {{ font-weight:800; font-size:1.05rem; margin-bottom:8px; }}
div[data-testid="stTabs"] button {{ font-weight:600; }}
</style>""", unsafe_allow_html=True)


def badge(text: str, tone: str | None = None) -> str:
    tone = tone or STATUS_TONE.get(str(text).lower(), "neutral")
    bg, fg = BADGES[tone]
    return f'<span class="gtm-badge" style="background:{bg};color:{fg}">{e(text)}</span>'


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="gtm-hero"><h1>{e(title)}</h1><div class="gtm-muted">{e(subtitle)}</div></div>',
                unsafe_allow_html=True)


def section(title: str, caption: str = "") -> None:
    st.markdown(f"### {title}")
    if caption:
        st.markdown(f'<div class="gtm-muted" style="margin:-8px 0 12px">{e(caption)}</div>', unsafe_allow_html=True)


def metric(label: str, value, sub: str = "") -> str:
    return (f'<div class="gtm-metric"><div class="l">{e(label)}</div>'
            f'<div class="v">{e(value)}</div><div class="s">{e(sub)}</div></div>')


def metric_row(metrics: list[tuple]) -> None:
    for col, m in zip(st.columns(len(metrics)), metrics):
        col.markdown(metric(*m), unsafe_allow_html=True)


def card(title: str, body: str = "", status: str | None = None, footer: str = "", tags: list[str] | None = None) -> None:
    tag_html = "".join(f'<span class="gtm-tag">{e(t)}</span>' for t in (tags or []))
    st.markdown(
        f'<div class="gtm-card"><div class="gtm-row"><h4>{e(title)}</h4>{badge(status) if status else ""}</div>'
        f'{f"<p>{e(body)}</p>" if body else ""}{f"<p><b>{e(footer)}</b></p>" if footer else ""}{tag_html}</div>',
        unsafe_allow_html=True)


def banner(text: str) -> None:
    st.markdown(f'<div class="gtm-banner">⚠ {e(text)}</div>', unsafe_allow_html=True)


def empty(module: str) -> None:
    st.info(f"No {module} data found for this project yet. Run the pipeline or add the JSON file to the project's output folder.")
