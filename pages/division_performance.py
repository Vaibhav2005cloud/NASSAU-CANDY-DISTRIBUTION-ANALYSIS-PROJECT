import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import compute_division_summary
from utils.chart_theme import apply_theme, PALETTE


def render(df: pd.DataFrame):
    st.markdown("""
    <div class="page-banner">
        <h1>🏭 Division Performance</h1>
        <p>Revenue vs profit balance · Margin distribution · Quarterly trends by division</p>
    </div>""", unsafe_allow_html=True)

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    div_sum = compute_division_summary(df)

    cols = st.columns(len(div_sum))
    for i, (_, row) in enumerate(div_sum.iterrows()):
        cols[i].metric(f"{row['Division']} Margin",
                       f"{row['Gross_Margin_pct']:.1f}%",
                       f"${row['Total_Profit']:,.0f} profit")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=div_sum["Division"], y=div_sum["Total_Sales"],
            name="Revenue", marker_color="#818cf8",
            text=div_sum["Total_Sales"].map("${:,.0f}".format), textposition="outside"))
        fig1.add_trace(go.Bar(x=div_sum["Division"], y=div_sum["Total_Profit"],
            name="Gross Profit", marker_color="#e879f9",
            text=div_sum["Total_Profit"].map("${:,.0f}".format), textposition="outside"))
        fig1.update_layout(barmode="group")
        apply_theme(fig1, "💰 Revenue vs Gross Profit by Division")
        fig1.update_layout(height=360)
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        fig2 = px.bar(div_sum, x="Division", y="Gross_Margin_pct",
                      color="Division", color_discrete_map=PALETTE,
                      text=div_sum["Gross_Margin_pct"].map(lambda v: f"{v:.1f}%"))
        fig2.update_traces(textposition="outside", textfont=dict(color="#f0e6ff"))
        apply_theme(fig2, "🎯 Gross Margin % by Division")
        fig2.update_layout(height=360, showlegend=False)
        overall = (df["Gross Profit"].sum() / df["Sales"].sum() * 100)
        fig2.add_hline(y=overall, line_dash="dash", line_color="#f59e0b", line_width=1.5,
                       annotation_text=f"Overall avg {overall:.1f}%",
                       annotation_font_color="#f59e0b")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 📅 Quarterly Profit Trend by Division")
    qtr = (df.groupby(["Quarter","Division"])
             .agg(Profit=("Gross Profit","sum"), Sales=("Sales","sum"))
             .reset_index().sort_values("Quarter"))
    fig3 = px.line(qtr, x="Quarter", y="Profit", color="Division",
                   color_discrete_map=PALETTE, markers=True, line_shape="spline")
    fig3.update_traces(line_width=2.5, marker_size=8)
    apply_theme(fig3, "Quarterly Gross Profit Trend")
    fig3.update_layout(height=320)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 📐 Margin Volatility — Distribution by Division")
    fig4 = px.violin(df, x="Division", y="Gross Margin (%)",
                     color="Division", color_discrete_map=PALETTE, box=True, points="outliers")
    apply_theme(fig4, "Gross Margin (%) Distribution")
    fig4.update_layout(height=360, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### 📋 Division Summary Table")
    show = div_sum.copy()
    for col, fmt in [("Total_Sales","${:,.2f}"),("Total_Profit","${:,.2f}"),
                     ("Total_Cost","${:,.2f}"),("Avg_Margin","{:.2f}%"),
                     ("Gross_Margin_pct","{:.2f}%"),("Revenue_Share","{:.2f}%"),
                     ("Profit_Share","{:.2f}%")]:
        show[col] = show[col].map(fmt.format)
    show.columns = ["Division","Revenue","Gross Profit","Cost","Units",
                    "Avg Margin","Orders","GM%","Profit/Unit","Rev Share","Profit Share"]
    st.dataframe(show, use_container_width=True, hide_index=True)
