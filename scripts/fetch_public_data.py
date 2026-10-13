"""Download public datasets into data/public/ (cached CSVs are committed, so this
only needs re-running if you want to refresh them).

Sources are cited in README.md.

Usage:  python scripts/fetch_public_data.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "public"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def air_passengers() -> pd.DataFrame:
    """Monthly international airline passengers (thousands), 1949-1960.

    Box & Jenkins (1976) "Series G", distributed via seaborn's `flights` dataset
    (https://github.com/mwaskom/seaborn-data/blob/master/flights.csv).
    """
    import seaborn as sns

    df = sns.load_dataset("flights")
    month_num = df["month"].astype(str).map({m: i + 1 for i, m in enumerate(MONTHS)})
    df["month"] = pd.to_datetime(
        dict(year=df["year"], month=month_num, day=1)
    ).dt.strftime("%Y-%m")
    return df[["month", "passengers"]].rename(columns={"passengers": "passengers_k"})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = air_passengers()
    df.to_csv(OUT / "air_passengers_monthly.csv", index=False)
    print(f"wrote {len(df)} rows to data/public/air_passengers_monthly.csv")


if __name__ == "__main__":
    main()
