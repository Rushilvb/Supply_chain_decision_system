import lightgbm as lgb
import mlflow
import pandas as pd
import numpy as np
from src.evaluation.metrics import evaluate


FEATURE_COLS = None  # set dynamically at runtime


def get_feature_cols(df: pd.DataFrame, target: str) -> list[str]:
    exclude = ["Date", "Store", target]
    return [c for c in df.columns if c not in exclude]


def train(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    config: dict,
    log_mlflow: bool = True,
) -> lgb.Booster:
    target = config["features"]["target"]
    feature_cols = get_feature_cols(train_df, target)

    X_train, y_train = train_df[feature_cols], train_df[target]
    X_val, y_val = val_df[feature_cols], val_df[target]

    params = config["model"]["params"]

    if log_mlflow:
        mlflow.lightgbm.autolog()

    model = lgb.LGBMRegressor(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)],
    )

    preds = model.predict(X_val)
    metrics = evaluate(y_val.values, preds)
    print(f"Val metrics: {metrics}")

    if log_mlflow:
        mlflow.log_metrics(metrics)

    return model, feature_cols, metrics
