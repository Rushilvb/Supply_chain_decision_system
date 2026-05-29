from pydantic import BaseModel
from typing import Optional


class PredictRequest(BaseModel):
    store_id: int
    forecast_days: int = 7
    current_stock: Optional[float] = None


class DecisionResponse(BaseModel):
    store_id: int
    forecast_7d: float
    reorder_recommended: bool
    reorder_quantity: float
    stockout_risk: float
    overstock_flag: bool
    action: str
