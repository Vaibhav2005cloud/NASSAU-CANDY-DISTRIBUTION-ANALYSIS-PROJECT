import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import pareto_table
from utils.chart_theme import apply_theme, GRADIENT_SCALE


def render(df: pd.DataFrame):
    st.markdown("""
    <div class="page-banner">
        <h1>📊 Pareto Concentration Analysis</h1>
        <p>Identify the vital few products driving 80% of profit &amp; revenue</p>
    </div>""", unsafe_allow_html=True)

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    pareto = pareto_table(df)
    top80p = pareto[pareto["Cum_Profit_Pct"] <= 80]
    top80r = pareto[pareto["Cum_Revenue_Pct"] <= 80]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Products for 80% Profit",  f"{len(top80p)} / {len(pareto)}")
    c2.metric("Products for 80% Revenue", f"{len(top80r)} / {len(pareto)}")
    c3.metric("Product Concentration",    f"{round(len(top80p)/len(pareto)*100,1)}% SKUs → 80% profit")
    c4.metric("Top Product Profit Share", f"{pareto.iloc[0]['Profit_Contribution']:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=pareto["Product Name"], y=pareto["Total_Profit"], name="Gross Profit",
        marker=dict(color=pareto["Profit_Contribution"], colorscale=GRADIENT_SCALE,
                    showscale=False),
        yaxis="y",
        text=pareto["Total_Profit"].map("${:,.0f}".format),
        textposition="outside", textfont=dict(color="#f0e6ff",size=9)))
    fig1.add_trace(go.Scatter(
        x=pareto["Product Name"], y=pareto["Cum_Profit_Pct"],
        name="Cumulative Profit %", mode="lines+markers",
        line=dict(color="#f59e0b",width=2.5), marker=dict(size=8,color="#f59e0b"),
        yaxis="y2"))
    fig1.add_hline(y=80, line_dash="dash", line_color="#ef4444", line_width=1.5,
                   annotation_text="80% threshold", annotation_font_color="#ef4444",
                   yref="y2")
    fig1.update_layout(
        yaxis =dict(title="Gross Profit ($)",   gridcolor="rgba(255,255,255,0.06)"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                    range=[0,105], gridcolor="rgba(0,0,0,0)",
                    tickfont=dict(color="#f59e0b")),
        xaxis =dict(tickangle=-35, gridcolor="rgba(255,255,255,0.06)"),
        legend=dict(x=0.01,y=0.97), height=440)
    apply_theme(fig1, "📊 Pareto — Profit Concentration by Product")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        pr = pareto.sort_values("Total_Sales", ascending=False)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=pr["Product Name"], y=pr["Total_Sales"],
                              name="Revenue", marker_color="#818cf8", opacity=0.85))
        fig2.add_trace(go.Scatter(x=pr["Product Name"], y=pr["Cum_Revenue_Pct"],
                                  name="Cumulative Revenue %", mode="lines+markers",
                                  line=dict(color="#06b6d4",width=2.5), marker=dict(size=7),
                                  yaxis="y2"))
        fig2.add_hline(y=80, line_dash="dash", line_color="#ef4444", line_width=1,
                       yref="y2", annotation_text="80%", annotation_font_color="#ef4444")
        fig2.update_layout(
            yaxis =dict(title="Revenue ($)",    gridcolor="rgba(255,255,255,0.06)"),
            yaxis2=dict(overlaying="y", side="right", range=[0,105],
                        gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#06b6d4")),
            xaxis=dict(tickangle=-35), height=360)
        apply_theme(fig2, "Revenue Pareto")
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        fig3 = px.pie(pareto, names="Product Name", values="Profit_Contribution",
                      color_discrete_sequence=px.colors.sequential.Purpor, hole=0.5)
        fig3.update_traces(textposition="outside", textinfo="label+percent",
                           textfont=dict(color="#f0e6ff",size=10),
                           marker=dict(line=dict(color="#0a041a",width=1.5)))
        apply_theme(fig3, "Profit Contribution Share")
        fig3.update_layout(height=360, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 📋 Cumulative Contribution Table")
    show = pareto[["Product_Rank","Product Name","Division","Total_Sales","Total_Profit",
                   "Revenue_Contribution","Profit_Contribution",
                   "Cum_Revenue_Pct","Cum_Profit_Pct"]].copy()
    show["Total_Sales"]          = show["Total_Sales"].map("${:,.2f}".format)
    show["Total_Profit"]         = show["Total_Profit"].map("${:,.2f}".format)
    show["Revenue_Contribution"] = show["Revenue_Contribution"].map("{:.2f}%".format)
    show["Profit_Contribution"]  = show["Profit_Contribution"].map("{:.2f}%".format)
    show["Cum_Revenue_Pct"]      = show["Cum_Revenue_Pct"].map("{:.2f}%".format)
    show["Cum_Profit_Pct"]       = show["Cum_Profit_Pct"].map("{:.2f}%".format)
    show.columns = ["Rank","Product","Division","Revenue","Gross Profit",
                    "Rev Share","Profit Share","Cum Rev %","Cum Profit %"]
    st.dataframe(show, use_container_width=True, hide_index=True)
