"""Data loading and the fixed train / holdout split for Challenge 01.

    from data import load_train, holdout_months
    train = load_train()          # 1949-01 .. 1959-12  (132 months)
    months = holdout_months()     # ['1960-01', ..., '1960-12']  (what you must forecast)

The holdout values live in holdout.csv and are only read by score.py.
No peeking on camera.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "data" / "public" / "air_passengers_monthly.csv"
TRAIN_CSV = HERE / "train.csv"
HOLDOUT_CSV = HERE / "holdout.csv"

TARGET = "passengers_k"
HOLDOUT_START = "1960-01"  # last 12 months are held out


def _split() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(SOURCE, dtype={"month": str})
    train = df[df["month"] < HOLDOUT_START].reset_index(drop=True)
    holdout = df[df["month"] >= HOLDOUT_START].reset_index(drop=True)
    return train, holdout


def load_train() -> pd.DataFrame:
    """Training history: columns `month` (YYYY-MM) and `passengers_k`."""
    return pd.read_csv(TRAIN_CSV, dtype={"month": str})


def holdout_months() -> list[str]:
    """The months you need to forecast, in order."""
    return pd.read_csv(HOLDOUT_CSV, dtype={"month": str})["month"].tolist()


def load_holdout() -> pd.DataFrame:
    """Used by score.py. Don't call this from your attempt."""
    return pd.read_csv(HOLDOUT_CSV, dtype={"month": str})


if __name__ == "__main__":
    # Rebuild train.csv / holdout.csv from the public source file.
    train, holdout = _split()
    train.to_csv(TRAIN_CSV, index=False)
    holdout.to_csv(HOLDOUT_CSV, index=False)
    print(f"train: {train['month'].iloc[0]}..{train['month'].iloc[-1]} ({len(train)} months)")
    print(f"holdout: {holdout['month'].iloc[0]}..{holdout['month'].iloc[-1]} ({len(holdout)} months)")
