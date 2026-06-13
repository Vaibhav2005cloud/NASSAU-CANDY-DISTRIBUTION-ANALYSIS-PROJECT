# 🍬 Nassau Candy Distributor — Product Line Profitability Analytics

> **Unified Mentor Project** · Streamlit Dashboard · Dark Cosmos Theme

A full-stack, production-ready analytics dashboard that transforms raw order data
into actionable profitability intelligence across product lines, divisions, and factories.

---

## 📁 Project Structure

```
nassau_candy_analytics/
│
├── app.py                        # ← Main entry point (run this)
│
├── data/
│   └── Nassau_Candy_Distributor.csv   # Source dataset (10,194 orders)
│
├── pages/
│   ├── __init__.py
│   ├── overview.py               # Executive KPIs + monthly trends
│   ├── product_profitability.py  # Margin leaderboard + risk flags
│   ├── division_performance.py   # Division revenue vs profit + violin
│   ├── cost_diagnostics.py       # Cost-sales scatter + action table
│   ├── pareto_analysis.py        # 80/20 concentration charts
│   └── geo_factory.py            # US choropleth + factory map
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py            # Data cleaning, KPI computation, caching
│   └── chart_theme.py            # Centralised Plotly dark theme & palette
│
├── .streamlit/
│   └── config.toml               # Theme + server config
│
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start (VS Code)

### 1. Clone / open the folder
Open `nassau_candy_analytics/` in VS Code.

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 📊 Dashboard Pages

| Page | What it shows |
|------|---------------|
| 🏠 Overview | Revenue, profit, margin KPIs · Monthly trend · Division pie · Region bars |
| 📦 Product Profitability | Margin leaderboard · Bubble chart · Profit-per-unit · Risk table |
| 🏭 Division Performance | Revenue vs profit · Quarterly trend · Margin violin · Summary table |
| 🔬 Cost Diagnostics | Cost-sales scatter · Cost ratio analysis · Ship mode impact · Action recs |
| 📊 Pareto Analysis | 80/20 profit & revenue concentration · Cumulative charts · Contribution table |
| 🌍 Geo & Factory | US state choropleth · Factory bubble map · Top-10 states |

---

## 🎛️ Sidebar Filters (global, affect all pages)
- **Division** — Chocolate / Sugar / Other
- **Region** — Atlantic / Gulf / Interior / Pacific
- **Min Gross Margin (%)** — slider threshold
- **Order Date Range** — date picker

---

## 🔑 KPIs Computed

| KPI | Formula |
|-----|---------|
| Gross Margin % | Gross Profit ÷ Sales × 100 |
| Profit per Unit | Gross Profit ÷ Units |
| Cost Ratio % | Cost ÷ Sales × 100 |
| Revenue Contribution | Product Sales ÷ Total Sales × 100 |
| Profit Contribution | Product Profit ÷ Total Profit × 100 |
| Margin Volatility | Std-dev of Gross Margin across orders |

---

## 🏭 Factory Reference

| Factory | Location |
|---------|----------|
| Lot's O' Nuts | Arizona |
| Wicked Choccy's | Georgia |
| Sugar Shack | Minnesota |
| Secret Factory | Illinois |
| The Other Factory | Tennessee |

---

## 🛠️ Tech Stack
- **Streamlit** 1.35 — UI framework
- **Plotly** 5.22 — interactive charts (choropleth, violin, scatter, pareto)
- **Pandas / NumPy** — data processing
- **scikit-learn / scipy** — statistical helpers

---

*Built for Unified Mentor · Nassau Candy Distributor case study*
