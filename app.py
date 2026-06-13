"""
app.py  ·  Nassau Candy Distributor — Product Line Profitability Analytics
Run:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Nassau Candy · Profit Analytics",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

:root {
    --bg-deep:   #0a041a;
    --bg-card:   rgba(30,15,60,0.70);
    --bg-card2:  rgba(20,10,45,0.85);
    --accent1:   #c026d3;
    --accent2:   #7c3aed;
    --accent3:   #06b6d4;
    --gold:      #f59e0b;
    --green:     #10b981;
    --red:       #ef4444;
    --text-main: #f0e6ff;
    --text-muted:#a78bca;
    --border:    rgba(192,38,211,0.25);
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg-deep) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#10052a 0%,#0d0420 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-main) !important; }

[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 20px 24px !important;
    backdrop-filter: blur(12px);
}
[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-main) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}

.js-plotly-plot, .stPlotlyChart {
    border-radius: 16px;
    border: 1px solid var(--border);
    background: var(--bg-card) !important;
}

div[data-baseweb="select"] > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-main) !important;
}

h1 { font-family:'Space Grotesk',sans-serif !important; font-weight:700 !important; }
h2 { font-family:'Space Grotesk',sans-serif !important; font-weight:600 !important; }

footer { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

.page-banner {
    background: linear-gradient(135deg,rgba(124,58,237,0.3) 0%,rgba(192,38,211,0.2) 50%,rgba(6,182,212,0.15) 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    backdrop-filter: blur(12px);
}
.page-banner h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg,#ffffff,#e879f9,#818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 8px !important;
}
.page-banner p { color: var(--text-muted); font-size:14px; margin:0; }
.section-label {
    font-size:11px; font-weight:600; letter-spacing:0.1em;
    text-transform:uppercase; color:var(--accent1); margin-bottom:12px;
}
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#0a041a; }
::-webkit-scrollbar-thumb { background:var(--accent2); border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px;'>
        <div style='font-size:48px;'>🍬</div>
        <div style='font-family:Space Grotesk,sans-serif;font-size:16px;
                    font-weight:700;color:#f0e6ff;margin-top:8px;'>Nassau Candy</div>
        <div style='font-size:11px;color:#a78bca;letter-spacing:0.1em;
                    text-transform:uppercase;margin-top:4px;'>Profit Analytics Suite</div>
    </div>
    <hr style='border-color:rgba(192,38,211,0.2);margin:12px 0 20px;'/>
    """, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import load_data
import pandas as pd

df_raw = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-label">Filters</p>', unsafe_allow_html=True)

    divisions = st.multiselect(
        "Division",
        options=sorted(df_raw["Division"].unique()),
        default=sorted(df_raw["Division"].unique()),
    )
    regions = st.multiselect(
        "Region",
        options=sorted(df_raw["Region"].unique()),
        default=sorted(df_raw["Region"].unique()),
    )
    margin_thresh = st.slider("Min Gross Margin (%)", 0, 100, 0, 1)

    date_min = df_raw["Order Date"].min().date()
    date_max = df_raw["Order Date"].max().date()
    date_range = st.date_input("Order Date Range",
                               value=(date_min, date_max),
                               min_value=date_min, max_value=date_max)

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:11px;color:#a78bca;text-align:center;'>
        Dataset · <b style='color:#e879f9;'>{len(df_raw):,}</b> orders<br>
        <span style='color:#818cf8;'>Unified Mentor Project</span>
    </div>""", unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "🏠  Overview",
        "📦  Product Profitability",
        "🏭  Division Performance",
        "🔬  Cost Diagnostics",
        "📊  Pareto Analysis",
        "🌍  Geo & Factory",
    ], label_visibility="collapsed")

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if divisions:
    df = df[df["Division"].isin(divisions)]
if regions:
    df = df[df["Region"].isin(regions)]
if len(date_range) == 2:
    df = df[(df["Order Date"] >= pd.Timestamp(date_range[0])) &
            (df["Order Date"] <= pd.Timestamp(date_range[1]))]
df = df[df["Gross Margin (%)"] >= margin_thresh]

# ── Route to page ─────────────────────────────────────────────────────────────
if page == "🏠  Overview":
    from pages.overview import render
elif page == "📦  Product Profitability":
    from pages.product_profitability import render
elif page == "🏭  Division Performance":
    from pages.division_performance import render
elif page == "🔬  Cost Diagnostics":
    from pages.cost_diagnostics import render
elif page == "📊  Pareto Analysis":
    from pages.pareto_analysis import render
else:
    from pages.geo_factory import render

render(df)
