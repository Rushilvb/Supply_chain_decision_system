# Supply Chain Decision System

> Retail demand forecasting + automated reorder recommendations across 1,115 stores.

![Dashboard](assets/dashboard.png)

---

## What it does

This is not just a forecasting model. It is a decision-making system that:

1. **Forecasts** 7-day SKU-level demand for each store using LightGBM
2. **Decides** whether to reorder, how much, and how urgently — based on current stock, lead time, and stockout risk
3. **Serves** predictions via a REST API containerized with Docker
4. **Visualizes** decisions in a real-time Streamlit dashboard

The core insight: a MAPE number alone is not useful. A store manager needs *"Order 25,000 units by Thursday or you'll stockout by Saturday."*

---

## Results

| Model | MAPE |
|---|---|
| Naive baseline (lag-7) | 38.35% |
| LightGBM default | 14.09% |
| LightGBM tuned (Optuna) | **13.74%** |

**64% improvement over naive baseline** — validated with 5-fold walk-forward cross-validation, 42-day horizon, 7-day gap.

- Train MAPE: 9.37% · Test MAPE: 13.74% · Gap: 4.37 pts (no significant overfitting)
- 405,058 training samples across 1,115 stores after filtering closed days
- Fold 2 (Dec/Jan holiday period) worst at ~22% — expected; demand spikes from lag features alone

---

## Architecture

```
train.csv + store.csv
        │
        ▼
Feature Engineering (31 features)
  lag_7/14/21/28 · rolling_mean/std · calendar · store type · promo · competition
        │
        ▼
LightGBM (Optuna-tuned) ──── walk-forward CV (5 folds)
        │
        ▼
7-day Forecast
        │
        ▼
Decision Engine
  stockout_risk · reorder_point · safety_stock (1.5x / 2.0x promo / 2.5x Wednesday)
        │
        ▼
FastAPI  ──────►  Streamlit Dashboard
(Docker)
```

---

## Features engineered (31 total)

| Group | Features |
|---|---|
| Lag | sales_lag_7, 14, 21, 28 |
| Rolling | sales_rolling_mean/std (7, 14, 28 days) |
| Calendar | DayOfWeek, Month, Year, WeekOfYear, DayOfMonth, IsWeekend, DaysToMonthEnd |
| Store | StoreType (0–3), Assortment (0–2) |
| Competition | CompetitionDistance, CompetitionOpenMonths |
| Promo | Promo, Promo2, Promo2Active |
| Holiday | StateHoliday (0–3), SchoolHoliday |
| Interaction | Promo_DayOfWeek, StoreType_Promo |

Dropped leaky features: `Customers`, `Open`, `PromoInterval`, `CompetitionOpenSince*`, `Promo2Since*`

---

## Decision engine logic

```python
safety_stock_multiplier = 1.5   # base
                        = 2.0   # promo days
                        = 2.5   # Wednesdays (highest error day)

stockout_risk = 1 - (days_of_stock / lead_time_days)
reorder_recommended = current_stock <= reorder_point
reorder_quantity = forecast_7d + safety_stock - current_stock
```

---

## API

```bash
POST /predict
{
  "store_id": 1,
  "current_stock": 5000
}
```

```json
{
  "store_id": 1,
  "forecast_7d": 24947.0,
  "reorder_recommended": true,
  "reorder_quantity": 25293.0,
  "stockout_risk": 0.80,
  "overstock_flag": false,
  "action": "URGENT: Order 25294 units immediately — stockout risk 80%"
}
```

---

## Setup

**Local**
```bash
git clone https://github.com/yourusername/supply_chain_decision_system
cd supply_chain_decision_system
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# Train model (notebooks 01–03)
jupyter notebook

# Start API
uvicorn api.main:app --reload

# Start dashboard
streamlit run monitoring/dashboard.py
```

**Docker**
```bash
docker build -t supply-chain-api .
docker run -p 8000:8000 supply-chain-api
```

Then open `http://localhost:8000/docs` for the interactive API docs.

---

## Project structure

```
supply_chain_decision_system/
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_modelling.ipynb
│   └── 04_decision_layer.ipynb
├── src/
│   ├── decision/engine.py       # core reorder logic
│   ├── features/                # lag, rolling, calendar features
│   ├── models/                  # train, predict, evaluate
│   └── evaluation/              # walk-forward CV, metrics
├── api/
│   ├── main.py
│   ├── routes.py                # /predict endpoint
│   └── schemas.py
├── monitoring/
│   └── dashboard.py             # Streamlit UI
├── models/                      # saved lgbm_model.pkl
├── configs/config.yaml
├── Dockerfile
└── requirements.txt
```

---

## Dataset

[Rossmann Store Sales](https://www.kaggle.com/competitions/rossmann-store-sales) — Kaggle competition dataset

- `train.csv`: 1,017,209 rows · 9 columns · Jan 2013 – Jul 2015
- `store.csv`: 1,115 stores · 10 columns
- After filtering closed days + dropna: **405,058 rows · 31 features**

---

## Tech stack

`Python 3.11` · `LightGBM` · `Optuna` · `pandas` · `scikit-learn` · `FastAPI` · `Docker` · `Streamlit` · `MLflow`
