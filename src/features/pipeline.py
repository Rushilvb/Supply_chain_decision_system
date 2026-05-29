import pandas as pd
from src.features.lag_features import add_lag_features
from src.features.rolling_features import add_rolling_features
from src.features.calendar_features import add_calendar_features


def build_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Run full feature engineering pipeline."""
    df = add_calendar_features(df)
    df = add_lag_features(df, lags=config["features"]["lags"])
    df = add_rolling_features(df, windows=config["features"]["rolling_windows"])
    df = df.dropna().reset_index(drop=True)
    print(f"Features built: {df.shape[1]} columns, {len(df):,} rows after dropping NaN")
    return df
