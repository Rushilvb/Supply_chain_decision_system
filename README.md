# Supply Chain Decision System

> Retail demand forecasting that goes beyond prediction — generates actionable reorder decisions.

Most demand forecasting projects stop at predicting a number. This system treats forecasting as a **decision-making problem**: given predicted demand, current stock levels, and supplier lead times, it tells you *what to order, how much, and by when*.

---

## The problem

600,000+ kirana and retail stores in India manage inventory manually. Stockouts cost revenue. Overstock ties up capital. The gap between "we have a forecast" and "we know what to do" is where most systems fail.

---

## Architecture

```
Raw Data (Rossmann)
    ↓
Feature Engineering
(lag, rolling, calendar features)
    ↓
LightGBM Forecaster
(walk-forward validated)
    ↓
Decision Engine
(reorder point, stockout risk, overstock detection)
    ↓
FastAPI  ←→  MLflow (experiment tracking)
    ↓
Streamlit Monitoring Dashboard
```

---

## Quickstart

```bash
# install
make install

# download Rossmann data from Kaggle → data/raw/

# train
make train

# serve
make serve

# dashboard
make dashboard
```

---

## Results

| Metric | Value |
|--------|-------|
| MAPE   | TBD after training |
| RMSE   | TBD after training |
| MAE    | TBD after training |

---

## Tech stack

`LightGBM` `Optuna` `FastAPI` `MLflow` `Docker` `Streamlit` `Evidently` `pandas` `scikit-learn`

---

## Project structure

```
supply_chain_decision_system/
├── data/               ← raw + processed (gitignored)
├── notebooks/          ← exploration only
├── src/
│   ├── ingestion/      ← load + validate data
│   ├── features/       ← lag, rolling, calendar features
│   ├── models/         ← train, predict, tune, evaluate
│   ├── decision/       ← reorder engine, stockout risk, overstock
│   └── evaluation/     ← walk-forward CV, metrics
├── api/                ← FastAPI serving layer
├── monitoring/         ← drift detection + Streamlit dashboard
├── tests/
├── configs/config.yaml
├── Dockerfile
└── Makefile
```
