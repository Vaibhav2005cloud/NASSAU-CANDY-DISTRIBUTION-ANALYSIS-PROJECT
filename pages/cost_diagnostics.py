import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import compute_product_summary, margin_risk_flags
from utils.chart_theme import apply_theme, PALETTE, GRADIENT_SCALE


def render(df: pd.DataFrame):
    st.markdown("""
    <div class="page-banner">
        <h1>🔬 Cost Diagnostics</h1>
        <p>Cost-sales scatter · Margin risk flags · Pricing efficiency analysis</p>
    </div>""", unsafe_allow_html=True)

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    prod = margin_risk_flags(compute_product_summary(df))
    high_risk = len(prod[prod["Risk_Flag"]=="🔴 High Risk"])
    watch      = len(prod[prod["Risk_Flag"]=="🟡 Watch"])
    healthy    = len(prod[prod["Risk_Flag"]=="🟢 Healthy"])
    cost_ratio = (prod["Total_Cost"].sum()/prod["Total_Sales"].sum()*100)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🔴 High Risk Products", high_risk)
    c2.metric("🟡 Watch Products",     watch)
    c3.metric("🟢 Healthy Products",   healthy)
    c4.metric("📊 Avg Cost Ratio",     f"{cost_ratio:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    max_val = max(prod["Total_Cost"].max(), prod["Total_Sales"].max())
    fig1 = px.scatter(prod, x="Total_Cost", y="Total_Sales",
                      color="Gross_Margin_pct", color_continuous_scale=GRADIENT_SCALE,
                      size="Total_Units", hover_name="Product Name", text="Product Name",
                      size_max=50,
                      labels={"Total_Cost":"Total Cost ($)","Total_Sales":"Total Revenue ($)",
                              "Gross_Margin_pct":"Margin %"})
    fig1.add_trace(go.Scatter(x=[0,max_val], y=[0,max_val], mode="lines",
                              line=dict(color="#f59e0b",width=1.5,dash="dot"),
                              name="Break-even line"))
    fig1.update_traces(selector=dict(mode="markers+text"),
                       textposition="top center",
                       textfont=dict(size=9,color="#f0e6ff"),
                       marker=dict(line=dict(color="#0a041a",width=1)))
    apply_theme(fig1, "💸 Cost vs Revenue (colour = margin, size = units)")
    fig1.update_layout(height=440,
                       coloraxis_colorbar=dict(title="Margin %",tickfont=dict(color="#f0e6ff")))
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        ps = prod.sort_values("Total_Cost", ascending=False)
        fig2 = go.Figure(go.Bar(
            x=ps["Product Name"], y=ps["Total_Cost"],
            marker=dict(color=ps["Gross_Margin_pct"], colorscale=GRADIENT_SCALE,
                        showscale=True,
                        colorbar=dict(title="Margin %",tickfont=dict(color="#f0e6ff",size=9))),
            text=ps["Total_Cost"].map(lambda v: f"${v:,.0f}"),
            textposition="outside", textfont=dict(color="#f0e6ff",size=9)))
        apply_theme(fig2, "🏗️ Total Cost by Product")
        fig2.update_layout(height=380, xaxis_tickangle=-40)
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        prod2 = prod.copy()
        prod2["Cost_Ratio"] = (prod2["Total_Cost"]/prod2["Total_Sales"]*100).round(2)
        fig3 = px.scatter(prod2, x="Cost_Ratio", y="Gross_Margin_pct",
                          color="Division", color_discrete_map=PALETTE,
                          size="Total_Sales", hover_name="Product Name",
                          labels={"Cost_Ratio":"Cost Ratio (%)","Gross_Margin_pct":"Gross Margin (%)"},
                          size_max=40)
        fig3.update_traces(marker=dict(line=dict(color="#0a041a",width=1)))
        fig3.add_vline(x=60, line_dash="dash", line_color="#ef4444", line_width=1.5,
                       annotation_text="60% cost threshold", annotation_font_color="#ef4444")
        apply_theme(fig3, "⚖️ Cost Ratio vs Gross Margin")
        fig3.update_layout(height=380)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 🚚 Ship Mode — Margin Impact")
    ship = (df.groupby("Ship Mode")
              .agg(Avg_Margin=("Gross Margin (%)","mean"),
                   Total_Profit=("Gross Profit","sum"),
                   Order_Count=("Order ID","count"))
              .reset_index().sort_values("Avg_Margin", ascending=False))
    fig4 = px.bar(ship, x="Ship Mode", y="Avg_Margin",
                  color="Avg_Margin", color_continuous_scale=GRADIENT_SCALE,
                  text=ship["Avg_Margin"].map(lambda v: f"{v:.1f}%"))
    fig4.update_traces(textposition="outside", textfont=dict(color="#f0e6ff"))
    apply_theme(fig4, "Average Gross Margin by Shipping Mode")
    fig4.update_layout(height=300, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### 📋 Product Action Recommendations")
    actions = {"🔴 High Risk":"Reprice / renegotiate cost / review discontinuation",
               "🟡 Watch":"Monitor monthly — optimise cost or raise price",
               "🟢 Healthy":"Sustain — consider volume expansion"}
    act = prod[["Product Name","Division","Factory","Total_Sales","Total_Cost",
                "Gross_Margin_pct","Risk_Flag"]].copy()
    act["Action"] = act["Risk_Flag"].map(actions)
    act["Total_Sales"]      = act["Total_Sales"].map("${:,.2f}".format)
    act["Total_Cost"]       = act["Total_Cost"].map("${:,.2f}".format)
    act["Gross_Margin_pct"] = act["Gross_Margin_pct"].map("{:.2f}%".format)
    act.columns = ["Product","Division","Factory","Revenue","Cost","Margin %","Risk","Action"]
    st.dataframe(act, use_container_width=True, hide_index=True)
