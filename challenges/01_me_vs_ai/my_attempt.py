"""Challenge 01: my hand-coded forecast. Timer starts now (15 min).

Goal: forecast monthly airline passengers (thousands) for 1960-01..1960-12.
Write the result to forecasts/me.csv with columns: month, forecast
Then score it:  python score.py forecasts/me.csv --name "Me"
"""
from pathlib import Path

import pandas as pd

from data import holdout_months, load_train

HERE = Path(__file__).resolve().parent
OUT = HERE / "forecasts" / "me.csv"

train = load_train()          # columns: month (YYYY-MM), passengers_k
months = holdout_months()     # 12 months to forecast

# ---- your code below -------------------------------------------------------



forecast = None  # TODO: a list/array/Series of 12 numbers, one per month in `months`

# ---- save -------------------------------------------------------------------
if forecast is None:
    raise SystemExit("No forecast yet: fill in `forecast` above.")
OUT.parent.mkdir(exist_ok=True)
pd.DataFrame({"month": months, "forecast": list(forecast)}).to_csv(OUT, index=False)
print(f"saved {OUT.relative_to(HERE)}")
