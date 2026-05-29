import pandas as pd
import yaml
from pathlib import Path


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_raw_data(config: dict) -> pd.DataFrame:
    """Load and merge sales + store data from Rossmann dataset."""
    sales = pd.read_csv(config["data"]["raw_sales"], parse_dates=["Date"])
    store = pd.read_csv(config["data"]["raw_store"])

    df = sales.merge(store, on="Store", how="left")

    # basic cleaning
    df = df[df["Open"] == 1]          # remove closed store days
    df = df[df["Sales"] > 0]          # remove zero-sales days
    df = df.sort_values(["Store", "Date"]).reset_index(drop=True)

    print(f"Loaded {len(df):,} rows | {df['Store'].nunique()} stores | "
          f"{df['Date'].min().date()} to {df['Date'].max().date()}")
    return df
