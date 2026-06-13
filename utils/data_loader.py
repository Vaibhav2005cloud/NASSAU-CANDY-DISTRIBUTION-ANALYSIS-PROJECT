"""
data_loader.py
Nassau Candy Distributor – Data loading, cleaning, and KPI computation.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

# ── Factory metadata ────────────────────────────────────────────────────────
FACTORY_COORDS = {
    "Lot's O' Nuts":     {"lat": 32.881893, "lon": -111.768036},
    "Wicked Choccy's":  {"lat": 32.076176, "lon": -81.088371},
    "Sugar Shack":       {"lat": 48.11914,  "lon": -96.18115},
    "Secret Factory":    {"lat": 41.446333, "lon": -90.565487},
    "The Other Factory": {"lat": 35.1175,   "lon": -89.971107},
}

PRODUCT_FACTORY = {
    "Wonka Bar - Nutty Crunch Surprise":    "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows":            "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious":       "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate":           "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel":    "Wicked Choccy's",
    "Laffy Taffy":                          "Sugar Shack",
    "SweeTARTS":                            "Sugar Shack",
    "Nerds":                                "Sugar Shack",
    "Fun Dip":                              "Sugar Shack",
    "Fizzy Lifting Drinks":                 "Sugar Shack",
    "Everlasting Gobstopper":               "Secret Factory",
    "Hair Toffee":                          "The Other Factory",
    "Lickable Wallpaper":                   "Secret Factory",
    "Wonka Gum":                            "Secret Factory",
    "Kazookles":                            "The Other Factory",
}

DATA_PATH = Path(__file__).parent.parent / "data" / "Nassau_Candy_Distributor.csv"


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load and clean the Nassau Candy dataset."""
    df = pd.read_csv(DATA_PATH)

    # Parse dates (DD-MM-YYYY format in source)
    for col in ["Order Date", "Ship Date"]:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["Sales", "Gross Profit", "Cost", "Units"])
    df = df[(df["Sales"] > 0) & (df["Units"] > 0)]

    # Derived KPIs
    df["Gross Margin (%)"]   = (df["Gross Profit"] / df["Sales"] * 100).round(2)
    df["Profit per Unit"]    = (df["Gross Profit"] / df["Units"]).round(3)
    df["Cost per Unit"]      = (df["Cost"] / df["Units"]).round(3)
    df["Revenue per Unit"]   = (df["Sales"] / df["Units"]).round(3)
    df["Days to Ship"]       = (df["Ship Date"] - df["Order Date"]).dt.days

    # Factory mapping
    df["Factory"] = df["Product Name"].map(PRODUCT_FACTORY).fillna("Unknown")

    # Month / Quarter
    df["Month"]   = df["Order Date"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["Year"]    = df["Order Date"].dt.year

    return df


def compute_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("Product Name").agg(
        Division        = ("Division", "first"),
        Factory         = ("Factory", "first"),
        Total_Sales     = ("Sales", "sum"),
        Total_Profit    = ("Gross Profit", "sum"),
        Total_Cost      = ("Cost", "sum"),
        Total_Units     = ("Units", "sum"),
        Order_Count     = ("Order ID", "count"),
        Avg_Margin      = ("Gross Margin (%)", "mean"),
    ).reset_index()

    agg["Profit_per_Unit"]    = (agg["Total_Profit"] / agg["Total_Units"]).round(3)
    agg["Revenue_Contribution"] = (agg["Total_Sales"] / agg["Total_Sales"].sum() * 100).round(2)
    agg["Profit_Contribution"]  = (agg["Total_Profit"] / agg["Total_Profit"].sum() * 100).round(2)
    agg["Gross_Margin_pct"]     = (agg["Total_Profit"] / agg["Total_Sales"] * 100).round(2)

    return agg.sort_values("Total_Profit", ascending=False)


def compute_division_summary(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("Division").agg(
        Total_Sales   = ("Sales", "sum"),
        Total_Profit  = ("Gross Profit", "sum"),
        Total_Cost    = ("Cost", "sum"),
        Total_Units   = ("Units", "sum"),
        Avg_Margin    = ("Gross Margin (%)", "mean"),
        Order_Count   = ("Order ID", "count"),
    ).reset_index()

    agg["Gross_Margin_pct"]   = (agg["Total_Profit"] / agg["Total_Sales"] * 100).round(2)
    agg["Profit_per_Unit"]    = (agg["Total_Profit"] / agg["Total_Units"]).round(3)
    agg["Revenue_Share"]      = (agg["Total_Sales"] / agg["Total_Sales"].sum() * 100).round(2)
    agg["Profit_Share"]       = (agg["Total_Profit"] / agg["Total_Profit"].sum() * 100).round(2)

    return agg.sort_values("Total_Profit", ascending=False)


def pareto_table(df: pd.DataFrame, value_col: str = "Total_Profit") -> pd.DataFrame:
    """Return cumulative contribution sorted by value_col descending."""
    prod = compute_product_summary(df).copy()
    prod = prod.sort_values(value_col, ascending=False).reset_index(drop=True)
    prod["Cumulative_Profit"]  = prod["Total_Profit"].cumsum()
    prod["Cumulative_Revenue"] = prod["Total_Sales"].cumsum()
    prod["Cum_Profit_Pct"]     = (prod["Cumulative_Profit"]  / prod["Total_Profit"].sum()  * 100).round(2)
    prod["Cum_Revenue_Pct"]    = (prod["Cumulative_Revenue"] / prod["Total_Sales"].sum()   * 100).round(2)
    prod["Product_Rank"]       = prod.index + 1
    prod["Product_Pct"]        = (prod["Product_Rank"] / len(prod) * 100).round(1)
    return prod


def margin_risk_flags(prod_df: pd.DataFrame) -> pd.DataFrame:
    """Tag each product with a risk tier."""
    median_margin = prod_df["Gross_Margin_pct"].median()
    median_sales  = prod_df["Total_Sales"].median()

    def tag(row):
        if row["Gross_Margin_pct"] < median_margin * 0.7 and row["Total_Sales"] > median_sales:
            return "🔴 High Risk"
        elif row["Gross_Margin_pct"] < median_margin:
            return "🟡 Watch"
        else:
            return "🟢 Healthy"

    prod_df = prod_df.copy()
    prod_df["Risk_Flag"] = prod_df.apply(tag, axis=1)
    return prod_df
