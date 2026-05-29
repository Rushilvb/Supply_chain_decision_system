from fastapi import APIRouter, HTTPException
from api.schemas import PredictRequest, DecisionResponse
import joblib
import pandas as pd

router = APIRouter()

model = None
feature_cols = None


@router.on_event("startup")
def load_model():
    global model, feature_cols
    try:
        model = joblib.load("models/lgbm_model.pkl")
        feature_cols = joblib.load("models/feature_cols.pkl")
    except FileNotFoundError:
        print("Warning: model not found. Train first.")


@router.post("/predict", response_model=DecisionResponse)
def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Run training first.")

    # placeholder: in real use, fetch store features from processed data
    # and run model.predict() then decision engine
    return DecisionResponse(
        store_id=request.store_id,
        forecast_7d=0.0,
        reorder_recommended=False,
        reorder_quantity=0.0,
        stockout_risk=0.0,
        overstock_flag=False,
        action="Implement prediction logic in routes.py",
    )
