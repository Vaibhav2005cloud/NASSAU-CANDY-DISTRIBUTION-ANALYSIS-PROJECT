import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import FACTORY_COORDS
from utils.chart_theme import apply_theme, GRADIENT_SCALE

STATE_ABBREV = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
    'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
    'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
    'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
    'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
    'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH',
    'New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC',
    'North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA',
    'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',
    'Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
    'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY','District of Columbia':'DC',
}


def render(df: pd.DataFrame):
    st.markdown("""
    <div class="page-banner">
        <h1>🌍 Geo &amp; Factory Intelligence</h1>
        <p>Order geography · State-level profit density · Factory performance map</p>
    </div>""", unsafe_allow_html=True)

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    # ── State heatmap ─────────────────────────────────────────────────────────
    st.markdown("### 🗺️ US State — Profit Density Heatmap")
    state_df = (df.groupby("State/Province")
                  .agg(Total_Sales=("Sales","sum"), Total_Profit=("Gross Profit","sum"),
                       Orders=("Order ID","count"), Margin=("Gross Margin (%)","mean"))
                  .reset_index())
    state_df["abbrev"] = state_df["State/Province"].map(STATE_ABBREV).fillna(state_df["State/Province"])

    fig1 = px.choropleth(state_df, locations="abbrev", locationmode="USA-states",
                         color="Total_Profit", hover_name="State/Province",
                         hover_data={"Total_Sales":":$,.0f","Orders":True,"Margin":":.1f"},
                         color_continuous_scale=GRADIENT_SCALE, scope="usa",
                         labels={"Total_Profit":"Gross Profit ($)"})
    fig1.update_layout(
        geo=dict(bgcolor="rgba(10,4,26,0)", lakecolor="rgba(10,4,26,0)",
                 landcolor="rgba(30,15,60,0.6)", showland=True,
                 subunitcolor="rgba(255,255,255,0.1)"),
        paper_bgcolor="rgba(0,0,0,0)", height=440,
        coloraxis_colorbar=dict(title="Gross Profit", tickfont=dict(color="#f0e6ff")),
        font=dict(color="#f0e6ff"))
    st.plotly_chart(fig1, use_container_width=True)

    # ── Factory map ───────────────────────────────────────────────────────────
    st.markdown("### 🏭 Factory Performance Map")
    fac_df = (df.groupby("Factory")
                .agg(Total_Sales=("Sales","sum"), Total_Profit=("Gross Profit","sum"),
                     Total_Units=("Units","sum"), Orders=("Order ID","count"),
                     Avg_Margin=("Gross Margin (%)","mean"))
                .reset_index())
    fac_df["lat"] = fac_df["Factory"].map(lambda f: FACTORY_COORDS.get(f,{}).get("lat"))
    fac_df["lon"] = fac_df["Factory"].map(lambda f: FACTORY_COORDS.get(f,{}).get("lon"))
    fac_df = fac_df.dropna(subset=["lat","lon"])
    fac_df["GM_pct"] = (fac_df["Total_Profit"]/fac_df["Total_Sales"]*100).round(2)

    fig2 = px.scatter_geo(fac_df, lat="lat", lon="lon",
                          size="Total_Profit", color="GM_pct",
                          color_continuous_scale=GRADIENT_SCALE,
                          hover_name="Factory",
                          hover_data={"Total_Sales":":$,.0f","Total_Profit":":$,.0f",
                                      "Orders":True,"Avg_Margin":":.1f"},
                          text="Factory", scope="usa", size_max=55,
                          labels={"GM_pct":"Margin %"})
    fig2.update_traces(textposition="top center", textfont=dict(color="#ffffff",size=11))
    fig2.update_layout(
        geo=dict(bgcolor="rgba(10,4,26,0)", lakecolor="rgba(10,4,26,0)",
                 landcolor="rgba(30,15,60,0.6)", showland=True,
                 subunitcolor="rgba(255,255,255,0.1)", showcoastlines=True,
                 coastlinecolor="rgba(255,255,255,0.15)"),
        paper_bgcolor="rgba(0,0,0,0)", height=440,
        coloraxis_colorbar=dict(title="Margin %", tickfont=dict(color="#f0e6ff")),
        font=dict(color="#f0e6ff"))
    st.plotly_chart(fig2, use_container_width=True)

    left, right = st.columns(2)
    with left:
        fs = fac_df.sort_values("Total_Profit")
        fig3 = px.bar(fs, x="Total_Profit", y="Factory", orientation="h",
                      color="GM_pct", color_continuous_scale=GRADIENT_SCALE,
                      text=fs["Total_Profit"].map("${:,.0f}".format))
        fig3.update_traces(textposition="outside", textfont=dict(color="#f0e6ff",size=10))
        apply_theme(fig3, "Gross Profit by Factory")
        fig3.update_layout(height=320, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with right:
        fm = fac_df.sort_values("GM_pct")
        fig4 = px.bar(fm, x="GM_pct", y="Factory", orientation="h",
                      color="GM_pct", color_continuous_scale=GRADIENT_SCALE,
                      text=fm["GM_pct"].map("{:.1f}%".format))
        fig4.update_traces(textposition="outside", textfont=dict(color="#f0e6ff",size=10))
        apply_theme(fig4, "Gross Margin % by Factory")
        fig4.update_layout(height=320, coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### 🏆 Top 10 States by Gross Profit")
    top10 = state_df.nlargest(10,"Total_Profit")
    fig5 = px.bar(top10, x="State/Province", y="Total_Profit",
                  color="Margin", color_continuous_scale=GRADIENT_SCALE,
                  text=top10["Total_Profit"].map("${:,.0f}".format))
    fig5.update_traces(textposition="outside", textfont=dict(color="#f0e6ff",size=10))
    apply_theme(fig5, "Top 10 States — Gross Profit")
    fig5.update_layout(height=340,
                       coloraxis_colorbar=dict(title="Avg Margin %",
                                               tickfont=dict(color="#f0e6ff")))
    st.plotly_chart(fig5, use_container_width=True)
