import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import compute_product_summary, compute_division_summary
from utils.chart_theme import apply_theme, PALETTE


def render(df: pd.DataFrame):
    st.markdown("""
    <div class="page-banner">
        <h1>🍬 Executive Overview</h1>
        <p>Aggregate profitability health across all product lines &amp; divisions</p>
    </div>""", unsafe_allow_html=True)

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    total_sales  = df["Sales"].sum()
    total_profit = df["Gross Profit"].sum()
    total_cost   = df["Cost"].sum()
    total_units  = df["Units"].sum()
    avg_margin   = (total_profit / total_sales * 100) if total_sales else 0
    total_orders = df["Order ID"].nunique()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("💰 Total Revenue",    f"${total_sales:,.0f}")
    c2.metric("📈 Total Profit",     f"${total_profit:,.0f}")
    c3.metric("🏭 Total Cost",       f"${total_cost:,.0f}")
    c4.metric("📦 Units Sold",       f"{total_units:,}")
    c5.metric("🎯 Avg Gross Margin", f"{avg_margin:.1f}%")
    c6.metric("🧾 Orders",          f"{total_orders:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    monthly = (df.groupby("Month")
               .agg(Sales=("Sales","sum"), Profit=("Gross Profit","sum"))
               .reset_index().sort_values("Month"))
    monthly["Margin"] = (monthly["Profit"]/monthly["Sales"]*100).round(2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Sales"],
        name="Revenue", mode="lines+markers",
        line=dict(color="#818cf8",width=2.5), marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(129,140,248,0.08)"))
    fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Profit"],
        name="Gross Profit", mode="lines+markers",
        line=dict(color="#e879f9",width=2.5), marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(232,121,249,0.08)"))
    apply_theme(fig, "📅 Monthly Revenue & Profit Trend")
    fig.update_layout(height=300, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        div_sum = compute_division_summary(df)
        fig2 = px.pie(div_sum, names="Division", values="Total_Profit",
                      color="Division", color_discrete_map=PALETTE, hole=0.55)
        fig2.update_traces(textposition="outside", textinfo="label+percent",
                           textfont=dict(color="#f0e6ff",size=12),
                           marker=dict(line=dict(color="#0a041a",width=2)))
        apply_theme(fig2, "🏭 Profit Share by Division")
        fig2.update_layout(height=340)
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        prod = compute_product_summary(df).head(5)
        fig3 = px.bar(prod, x="Total_Profit", y="Product Name", orientation="h",
                      color="Division", color_discrete_map=PALETTE,
                      text=prod["Total_Profit"].map(lambda v: f"${v:,.0f}"))
        fig3.update_traces(textposition="outside", textfont=dict(color="#f0e6ff",size=11))
        apply_theme(fig3, "🏆 Top 5 Products by Gross Profit")
        fig3.update_layout(height=340, yaxis=dict(autorange="reversed"), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    region_df = (df.groupby("Region")
                 .agg(Sales=("Sales","sum"), Profit=("Gross Profit","sum"))
                 .reset_index())
    fig4 = px.bar(region_df, x="Region", y=["Sales","Profit"], barmode="group",
                  color_discrete_sequence=["#818cf8","#e879f9"], text_auto=".2s")
    apply_theme(fig4, "🗺️ Revenue vs Profit by Region")
    fig4.update_layout(height=320)
    st.plotly_chart(fig4, use_container_width=True)
