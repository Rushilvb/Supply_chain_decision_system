import pandas as pd


def validate(df: pd.DataFrame) -> None:
    """Basic sanity checks on raw data."""
    assert "Sales" in df.columns, "Missing Sales column"
    assert "Date" in df.columns, "Missing Date column"
    assert "Store" in df.columns, "Missing Store column"
    assert df["Sales"].isnull().sum() == 0, "Null values in Sales"
    assert (df["Sales"] >= 0).all(), "Negative sales detected"
    print("Validation passed.")
