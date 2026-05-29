import pandas as pd
import numpy as np
from typing import Iterator


def walk_forward_splits(
    df: pd.DataFrame,
    n_splits: int,
    gap_days: int,
    forecast_horizon: int,
) -> Iterator[tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Time-series walk-forward cross validation.
    Never leaks future data into training — critical for time series.

    Args:
        df: dataframe sorted by Date
        n_splits: number of folds
        gap_days: gap between train end and test start (simulates lead time)
        forecast_horizon: number of days to forecast

    Yields:
        (train_df, test_df) for each fold
    """
    dates = df["Date"].sort_values().unique()
    total_days = len(dates)
    fold_size = total_days // (n_splits + 1)

    for i in range(n_splits):
        train_end_idx = fold_size * (i + 1)
        test_start_idx = train_end_idx + gap_days
        test_end_idx = test_start_idx + forecast_horizon

        if test_end_idx > total_days:
            break

        train_end = dates[train_end_idx]
        test_start = dates[test_start_idx]
        test_end = dates[min(test_end_idx, total_days - 1)]

        train = df[df["Date"] <= train_end]
        test = df[(df["Date"] >= test_start) & (df["Date"] <= test_end)]

        print(f"Fold {i+1}: train up to {train_end.date()} | "
              f"test {test_start.date()} → {test_end.date()}")
        yield train, test
