import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from api.schemas import PredictRequest, DecisionResponse
from src.decision.engine import make_decision

router = APIRouter()

# --------------------------------------------------------------------------- #
# Load model artifacts once at startup                                         #
# --------------------------------------------------------------------------- #
try:
    model = joblib.load("models/lgbm_model.pkl")
    feature_cols = joblib.load("models/feature_cols.pkl")
    store_df = pd.read_csv("data/raw/store.csv")
except Exception as e:
    raise RuntimeError(f"Failed to load model artifacts: {e}")

# Config thresholds (mirrors configs/config.yaml)
LEAD_TIME_DAYS = 7
STOCKOUT_RISK_THRESHOLD = 0.3
OVERSTOCK_THRESHOLD = 2.0


def get_safety_multiplier(is_promo: bool, has_wednesday: bool) -> float:
    if has_wednesday:
        return 2.5
    elif is_promo:
        return 2.0
    return 1.5


def build_features_for_store(store_id: int, store_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a minimal feature row for a store using store metadata.
    Lag/rolling features are filled with store-level medians from store_df
    since we don't have live transaction history in the API.
    
    In production: replace with a DB query for recent sales history.
    """
    store_row = store_df[store_df["Store"] == store_id]
    if store_row.empty:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")

    store_row = store_row.iloc[0]

    # Store type and assortment encoding (matches feature_engineering notebook)
    store_type_map = {"a": 0, "b": 1, "c": 2, "d": 3}
    assortment_map = {"a": 0, "b": 1, "c": 2}

    today = pd.Timestamp.today()

    # Use median sales as proxy for lag/rolling features (no live DB)
    # These are population medians from EDA — acceptable for a demo API
    MEDIAN_DAILY_SALES = 5000.0

    features = {f: 0.0 for f in feature_cols}

    # Calendar
    features["DayOfWeek"] = today.dayofweek + 1
    features["Month"] = today.month
    features["Year"] = today.year
    features["WeekOfYear"] = today.isocalendar().week
    features["DayOfMonth"] = today.day
    features["IsWeekend"] = int(today.dayofweek >= 5)
    features["DaysToMonthEnd"] = (
        pd.Timestamp(today.year, today.month, 1) + pd.offsets.MonthEnd(1) - today
    ).days

    # Store
    features["StoreType"] = store_type_map.get(str(store_row.get("StoreType", "a")).lower(), 0)
    features["Assortment"] = assortment_map.get(str(store_row.get("Assortment", "a")).lower(), 0)

    # Competition
    comp_dist = store_row.get("CompetitionDistance", 999999)
    features["CompetitionDistance"] = 999999 if pd.isna(comp_dist) else float(comp_dist)
    features["CompetitionOpenMonths"] = 0.0

    # Promo
    features["Promo"] = 0
    features["Promo2"] = int(store_row.get("Promo2", 0))
    features["Promo2Active"] = 0

    # Holiday
    features["StateHoliday"] = 0
    features["SchoolHoliday"] = 0

    # Lag / rolling — proxy with median
    for col in feature_cols:
        if "lag" in col or "rolling" in col:
            features[col] = MEDIAN_DAILY_SALES

    # Interaction features
    features["Promo_DayOfWeek"] = features["Promo"] * features["DayOfWeek"]
    features["StoreType_Promo"] = features["StoreType"] * features["Promo"]

    return pd.DataFrame([features])[feature_cols]


# --------------------------------------------------------------------------- #
# Routes                                                                       #
# --------------------------------------------------------------------------- #

@router.post("/predict", response_model=DecisionResponse)
def predict(request: PredictRequest):
    """
    Forecast 7-day demand for a store and return a reorder decision.

    - **store_id**: Rossmann store ID (1–1115)
    - **current_stock**: current units on hand (optional — defaults to 1.5x forecast if not provided)
    - **forecast_days**: forecast horizon in days (default 7)
    """
    # Build features and predict daily sales
    X = build_features_for_store(request.store_id, store_df)
    daily_pred = float(model.predict(X)[0])
    daily_pred = max(0.0, daily_pred)
    forecast_7d = round(daily_pred * request.forecast_days, 2)

    # Default stock if not provided
    current_stock = (
        request.current_stock
        if request.current_stock is not None
        else round(forecast_7d * 1.5, 2)
    )

    # Context flags for safety stock multiplier
    today = pd.Timestamp.today()
    is_promo = False          # no live promo schedule in demo; extend via request body if needed
    has_wednesday = (today.dayofweek == 2)  # Wednesday = 2 in pandas (Mon=0)

    decision = make_decision(
        store_id=request.store_id,
        sku="default",
        forecast_7d=forecast_7d,
        current_stock=current_stock,
        lead_time_days=LEAD_TIME_DAYS,
        safety_stock_multiplier=get_safety_multiplier(is_promo, has_wednesday),
        stockout_risk_threshold=STOCKOUT_RISK_THRESHOLD,
        overstock_threshold=OVERSTOCK_THRESHOLD,
    )

    return DecisionResponse(
        store_id=decision.store_id,
        forecast_7d=decision.forecast_7d,
        reorder_recommended=decision.reorder_recommended,
        reorder_quantity=decision.reorder_quantity,
        stockout_risk=decision.stockout_risk,
        overstock_flag=decision.overstock_flag,
        action=decision.action,
    )