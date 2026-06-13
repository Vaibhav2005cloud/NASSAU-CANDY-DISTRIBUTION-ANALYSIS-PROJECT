import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import compute_product_summary, margin_risk_flags
from utils.chart_theme import apply_theme, PALETTE, GRADIENT_SCALE


def render(df: pd.DataFrame):
    st.markdown("""
    <div class="page-banner">
        <h1>📦 Product Profitability</h1>
        <p>Margin leaderboard · Profit contribution · Risk classification per product</p>
    </div>""", unsafe_allow_html=True)

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    prod = margin_risk_flags(compute_product_summary(df))

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Products Tracked",     f"{len(prod)}")
    best = prod.iloc[0]["Product Name"]
    c2.metric("Best Margin Product",  best[:22]+"…" if len(best)>22 else best)
    c3.metric("Highest Gross Margin", f"{prod['Gross_Margin_pct'].max():.1f}%")
    c4.metric("Lowest Gross Margin",  f"{prod['Gross_Margin_pct'].min():.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    search = st.text_input("🔍 Search product", placeholder="e.g. Wonka, Nerds…")
    if search:
        prod = prod[prod["Product Name"].str.contains(search, case=False)]

    ps = prod.sort_values("Gross_Margin_pct", ascending=False)
    fig1 = px.bar(ps, x="Gross_Margin_pct", y="Product Name", orientation="h",
                  color="Gross_Margin_pct", color_continuous_scale=GRADIENT_SCALE,
                  text=ps["Gross_Margin_pct"].map(lambda v: f"{v:.1f}%"),
                  hover_data={"Total_Sales":":$,.0f","Total_Profit":":$,.0f","Division":True})
    fig1.update_traces(textposition="outside", textfont=dict(color="#f0e6ff",size=11))
    apply_theme(fig1, "🏆 Product Gross Margin Leaderboard (%)")
    fig1.update_layout(height=420, yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        fig2 = px.scatter(prod, x="Total_Sales", y="Gross_Margin_pct",
                          size="Total_Profit", color="Division",
                          color_discrete_map=PALETTE,
                          hover_name="Product Name", text="Product Name", size_max=60)
        fig2.update_traces(textposition="top center",
                           textfont=dict(size=9,color="#f0e6ff"),
                           marker=dict(line=dict(color="#0a041a",width=1)))
        apply_theme(fig2, "💡 Sales vs Margin (bubble = profit)")
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        pp = prod.sort_values("Profit_per_Unit", ascending=True)
        fig3 = px.bar(pp, x="Profit_per_Unit", y="Product Name", orientation="h",
                      color="Division", color_discrete_map=PALETTE,
                      text=pp["Profit_per_Unit"].map(lambda v: f"${v:.3f}"))
        fig3.update_traces(textposition="outside", textfont=dict(color="#f0e6ff",size=10))
        apply_theme(fig3, "💲 Profit per Unit by Product")
        fig3.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 🚦 Margin Risk Classification")
    cols = ["Product Name","Division","Factory","Total_Sales","Total_Profit",
            "Gross_Margin_pct","Profit_per_Unit","Revenue_Contribution","Profit_Contribution","Risk_Flag"]
    show = prod[cols].copy().sort_values("Gross_Margin_pct", ascending=False)
    show["Total_Sales"]          = show["Total_Sales"].map("${:,.2f}".format)
    show["Total_Profit"]         = show["Total_Profit"].map("${:,.2f}".format)
    show["Gross_Margin_pct"]     = show["Gross_Margin_pct"].map("{:.2f}%".format)
    show["Profit_per_Unit"]      = show["Profit_per_Unit"].map("${:.3f}".format)
    show["Revenue_Contribution"] = show["Revenue_Contribution"].map("{:.2f}%".format)
    show["Profit_Contribution"]  = show["Profit_Contribution"].map("{:.2f}%".format)
    show.columns = ["Product","Division","Factory","Revenue","Gross Profit",
                    "Margin %","Profit/Unit","Rev Share %","Profit Share %","Risk"]
    st.dataframe(show, use_container_width=True, hide_index=True)
