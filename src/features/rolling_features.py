import pandas as pd


def add_rolling_features(df: pd.DataFrame, windows: list[int]) -> pd.DataFrame:
    """Add rolling mean and std of sales per store."""
    df = df.sort_values(["Store", "Date"])
    for w in windows:
        df[f"sales_rolling_mean_{w}"] = (
            df.groupby("Store")["Sales"]
            .transform(lambda x: x.shift(1).rolling(w).mean())
        )
        df[f"sales_rolling_std_{w}"] = (
            df.groupby("Store")["Sales"]
            .transform(lambda x: x.shift(1).rolling(w).std())
        )
    return df
