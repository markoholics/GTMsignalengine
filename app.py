"""GTM Signal Engine for Markoholics - Streamlit dashboard."""
from pathlib import Path

import streamlit as st

from gtm import ui
from gtm.data import OUTPUTS_DIR, freshness, list_projects, load_project
from gtm.tabs import TABS

st.set_page_config(page_title="GTM Signal Engine", page_icon="📡", layout="wide")

qp = st.query_params
projects = list_projects()

with st.sidebar:
    st.markdown("**Workspace**")
    default = qp.get("project", projects[0] if projects else "")
    idx = projects.index(default) if default in projects else 0
    project = st.selectbox("Project", projects, index=idx) if projects else ""
    override = st.text_input("Manual project override", value="", placeholder="folder name under outputs/")
    st.markdown("**Theme**")
    theme = st.radio("Theme", ["light", "dark"], index=0 if qp.get("theme", "light") == "light" else 1,
                     horizontal=True, label_visibility="collapsed")
    st.caption("Output folder")
    slug = override.strip() or project
    st.code(str(OUTPUTS_DIR / slug) if slug else str(OUTPUTS_DIR), language=None)
    if st.button("Reload", width="stretch"):
        st.rerun()

ui.inject_css(theme)

if not slug or not (OUTPUTS_DIR / slug / "project.json").exists():
    ui.hero("GTM Signal Engine", "AI Growth, VOC & Organic Visibility Intelligence")
    st.warning(f"No project found at outputs/{slug}/project.json. Run `python scripts/seed_sample.py` to create the sample project.")
    st.stop()

proj = load_project(slug)
st.query_params.update({"project": slug, "theme": theme})

with st.sidebar:
    st.markdown("**Data freshness**")
    chips = "".join(f'<div style="margin:4px 0">{ui.badge(f"{lbl}: {st_}")}</div>' for lbl, st_ in freshness(proj))
    st.markdown(chips, unsafe_allow_html=True)

ui.hero("GTM Signal Engine", "AI Growth, VOC & Organic Visibility Intelligence")
if proj.meta.get("sample"):
    ui.banner(proj.meta.get("disclaimer", "Sample data - illustrative only, not measured."))

for tab, (_, render) in zip(st.tabs([t for t, _ in TABS]), TABS):
    with tab:
        render(proj)
