import streamlit as st

st.set_page_config(
    page_title="Aegis AI — Enterprise Risk & Harm Prevention",
    page_icon="🛡️",
    layout="wide",
)

from src.ui import (
    render_overview,
    render_risk_analysis,
    render_responsible_ai,
    render_enterprise_architecture,
    render_demo_mode,
    render_footer,
)

PAGES = [
    "Overview",
    "Risk Analysis",
    "Responsible AI & Governance",
    "Enterprise Architecture",
    "Demo Mode",
]

with st.sidebar:
    st.title("Aegis AI")
    st.caption("Enterprise Risk & Harm Prevention")
    st.divider()
    page = st.radio("Navigation", PAGES, index=0)

if page == "Overview":
    render_overview()
elif page == "Risk Analysis":
    render_risk_analysis()
elif page == "Responsible AI & Governance":
    render_responsible_ai()
elif page == "Enterprise Architecture":
    render_enterprise_architecture()
elif page == "Demo Mode":
    render_demo_mode()

render_footer()
