import pandas as pd


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract date-based features."""
    df["day_of_week"] = df["Date"].dt.dayofweek
    df["month"] = df["Date"].dt.month
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["days_to_month_end"] = df["Date"].dt.days_in_month - df["Date"].dt.day
    return df
