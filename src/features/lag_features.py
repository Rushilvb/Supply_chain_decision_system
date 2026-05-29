import pandas as pd


def add_lag_features(df: pd.DataFrame, lags: list[int]) -> pd.DataFrame:
    """Add lagged sales features per store."""
    df = df.sort_values(["Store", "Date"])
    for lag in lags:
        df[f"sales_lag_{lag}"] = (
            df.groupby("Store")["Sales"]
            .shift(lag)
        )
    return df
