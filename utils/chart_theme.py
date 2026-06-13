"""
chart_theme.py
Centralised Plotly theme and colour palette for Nassau Candy Analytics.
"""

import plotly.graph_objects as go
import plotly.express as px

# ── Brand palette ────────────────────────────────────────────────────────────
PALETTE = {
    "Chocolate": "#8B4513",
    "Sugar":     "#FF6B9D",
    "Other":     "#7C3AED",
}

DIVISION_COLORS = ["#8B4513", "#FF6B9D", "#7C3AED"]

GRADIENT_SCALE = [
    [0.00, "#1a0533"],
    [0.25, "#4a1b6d"],
    [0.50, "#9b59b6"],
    [0.75, "#e056c4"],
    [1.00, "#ff9ff3"],
]

CHART_BG     = "rgba(15,10,30,0)"   # transparent (CSS handles background)
PAPER_BG     = "rgba(15,10,30,0)"
GRID_COLOR   = "rgba(255,255,255,0.08)"
FONT_COLOR   = "#e8d5ff"
AXIS_COLOR   = "rgba(200,180,255,0.4)"

BASE_LAYOUT = dict(
    paper_bgcolor = PAPER_BG,
    plot_bgcolor  = CHART_BG,
    font          = dict(color=FONT_COLOR, family="Inter, sans-serif", size=12),
    title_font    = dict(color="#ffffff", size=16, family="Inter, sans-serif"),
    legend        = dict(
        bgcolor     = "rgba(255,255,255,0.05)",
        bordercolor = "rgba(255,255,255,0.1)",
        borderwidth = 1,
        font        = dict(color=FONT_COLOR, size=11),
    ),
    xaxis = dict(
        gridcolor    = GRID_COLOR,
        linecolor    = AXIS_COLOR,
        tickfont     = dict(color=FONT_COLOR, size=11),
        title_font   = dict(color=FONT_COLOR),
        showgrid     = True,
    ),
    yaxis = dict(
        gridcolor    = GRID_COLOR,
        linecolor    = AXIS_COLOR,
        tickfont     = dict(color=FONT_COLOR, size=11),
        title_font   = dict(color=FONT_COLOR),
        showgrid     = True,
    ),
    margin = dict(l=50, r=30, t=60, b=50),
)


def apply_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply the Nassau dark theme to any Plotly figure."""
    layout = dict(BASE_LAYOUT)
    if title:
        layout["title"] = dict(text=title, x=0.02, xanchor="left")
    fig.update_layout(**layout)
    return fig


def kpi_color(value: float, threshold_good: float, threshold_warn: float) -> str:
    """Return CSS colour string based on KPI thresholds."""
    if value >= threshold_good:
        return "#00e676"
    elif value >= threshold_warn:
        return "#ffeb3b"
    return "#ff5252"
