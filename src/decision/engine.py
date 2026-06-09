import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class StoreDecision:
    store_id: int
    sku: str
    forecast_7d: float
    current_stock: float
    reorder_recommended: bool
    reorder_quantity: float
    stockout_risk: float
    overstock_flag: bool
    action: str


def make_decision(
    store_id: int,
    sku: str,
    forecast_7d: float,
    current_stock: float,
    lead_time_days: int,
    safety_stock_multiplier: float,
    stockout_risk_threshold: float,
    overstock_threshold: float,
) -> StoreDecision:
    """
    Core decision logic on top of the forecast.
    Transforms a predicted number into an actionable recommendation.
    """
    daily_forecast = forecast_7d / 7
    demand_during_lead_time = daily_forecast * lead_time_days
    safety_stock = daily_forecast * safety_stock_multiplier

    reorder_point = demand_during_lead_time + safety_stock
    reorder_recommended = current_stock <= reorder_point
    reorder_quantity = max(0, forecast_7d - current_stock + safety_stock)

    # stockout risk: probability stock runs out before reorder arrives
    days_of_stock = current_stock / daily_forecast if daily_forecast > 0 else float("inf")
    stockout_risk = max(0, min(1, 1 - (days_of_stock / lead_time_days)))

    # overstock: current stock covers more than overstock_threshold x 7d forecast
    overstock_flag = current_stock > (forecast_7d * overstock_threshold)

    if stockout_risk > stockout_risk_threshold:
        action = f"URGENT: Order {reorder_quantity:.0f} units immediately — stockout risk {stockout_risk:.0%}"
    elif reorder_recommended:
        action = f"Order {reorder_quantity:.0f} units within {lead_time_days} days"
    elif overstock_flag:
        action = f"Excess inventory. Consider markdown or pause orders."
    else:
        action = "Stock levels healthy. No action needed."

    return StoreDecision(
        store_id=store_id,
        sku=sku,
        forecast_7d=round(forecast_7d, 2),
        current_stock=round(current_stock, 2),
        reorder_recommended=reorder_recommended,
        reorder_quantity=round(reorder_quantity, 2),
        stockout_risk=round(stockout_risk, 4),
        overstock_flag=overstock_flag,
        action=action,
    )