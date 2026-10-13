"""Score a forecast CSV against the 1960 holdout and print a result card.

Usage:
    python score.py forecasts/me.csv --name "Me"
    python score.py forecasts/ai.csv --name "AI"
    python score.py forecasts/me.csv forecasts/ai.csv     # head-to-head
    python score.py forecasts/me.csv --png card.png       # also save a 1080x1920 card

The forecast CSV needs columns `month` (YYYY-MM) and `forecast`, covering
exactly the 12 holdout months. Lower MAE wins.

For context the card also shows a seasonal-naive baseline ("same month last
year"): the bar any real forecast should clear.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from data import TARGET, load_holdout, load_train  # noqa: E402


def load_forecast(path: Path, months: list[str]) -> pd.Series:
    df = pd.read_csv(path, dtype={"month": str})
    missing_cols = {"month", "forecast"} - set(df.columns)
    if missing_cols:
        raise SystemExit(f"{path}: missing column(s) {sorted(missing_cols)}")
    df = df.set_index("month")
    if df.index.duplicated().any():
        raise SystemExit(f"{path}: duplicate months")
    missing = [m for m in months if m not in df.index]
    if missing:
        raise SystemExit(f"{path}: missing forecast for {missing}")
    fc = pd.to_numeric(df.loc[months, "forecast"], errors="coerce")
    if fc.isna().any():
        raise SystemExit(f"{path}: non-numeric forecast values")
    return fc


def seasonal_naive(months: list[str]) -> pd.Series:
    train = load_train().set_index("month")[TARGET]
    prev = [f"{int(m[:4]) - 1}{m[4:]}" for m in months]
    return pd.Series(train.loc[prev].values, index=months)


def metrics(actual: pd.Series, fc: pd.Series) -> dict:
    err = fc.values - actual.values
    return {
        "mae": float(np.mean(np.abs(err))),
        "mape": float(np.mean(np.abs(err) / actual.values) * 100),
        "bias": float(np.mean(err)),
        "worst_month": actual.index[int(np.argmax(np.abs(err)))],
        "worst_err": float(err[int(np.argmax(np.abs(err)))]),
    }


def card(name: str, m: dict, baseline_mae: float) -> str:
    beat = baseline_mae - m["mae"]
    verdict = (f"beats baseline by {beat:.1f}k" if beat > 0
               else f"loses to baseline by {-beat:.1f}k")
    w = 46

    def row(label: str, value: str = "") -> str:
        if not value:
            return f"│ {label:<{w - 2}} │"
        return f"│ {label:<22}{value:>{w - 24}} │"

    rule = "├" + "─" * w + "┤"
    lines = [
        "┌" + "─" * w + "┐",
        row("ME vs AI · FORECAST CHALLENGE 01"),
        row(name),
        rule,
        row("MAE (lower wins)", f"{m['mae']:.2f}k pax"),
        row("MAPE", f"{m['mape']:.2f}%"),
        row("Bias (+ = too high)", f"{m['bias']:+.2f}k"),
        row("Worst month", f"{m['worst_month']} ({m['worst_err']:+.0f}k)"),
        rule,
        row("Seasonal-naive MAE", f"{baseline_mae:.2f}k"),
        row(verdict),
        "└" + "─" * w + "┘",
    ]
    return "\n".join(lines)


def save_png(results: list[tuple[str, dict]], baseline_mae: float, path: Path) -> None:
    root = HERE.parents[1]
    sys.path.insert(0, str(root))
    from src import style

    fig = style.new_canvas("vertical")
    fig.text(0.5, 0.88, "Me vs AI", ha="center", fontsize=style.px_to_pt(96),
             fontweight="bold", color=style.INK)
    fig.text(0.5, 0.835, "Forecast challenge · 12 months of airline passengers",
             ha="center", fontsize=style.px_to_pt(34), color=style.MUTED)
    winner = min(results, key=lambda r: r[1]["mae"])[0] if len(results) > 1 else None
    y = 0.70
    for name, m in results:
        color = style.ACCENT if name == winner else style.INK
        fig.text(0.5, y, name, ha="center", fontsize=style.px_to_pt(60), fontweight="bold",
                 color=color)
        fig.text(0.5, y - 0.07, f"MAE {m['mae']:.1f}k", ha="center",
                 fontsize=style.px_to_pt(110), fontweight="bold", color=color)
        fig.text(0.5, y - 0.105, f"MAPE {m['mape']:.1f}%  ·  bias {m['bias']:+.1f}k",
                 ha="center", fontsize=style.px_to_pt(34), color=style.MUTED)
        y -= 0.22
    fig.text(0.5, 0.17, f"Baseline (same month last year): MAE {baseline_mae:.1f}k",
             ha="center", fontsize=style.px_to_pt(32), color=style.MUTED)
    fig.text(0.5, 0.14, "Data: Box & Jenkins airline passengers, 1949–1960",
             ha="center", fontsize=style.px_to_pt(26), color=style.MUTED)
    fig.savefig(path, dpi=style.DPI, facecolor=style.NAVY)
    print(f"saved {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("forecasts", nargs="+", type=Path, help="forecast CSV(s)")
    ap.add_argument("--name", action="append", help="label per CSV (repeatable)")
    ap.add_argument("--png", type=Path, help="also save a 1080x1920 result card")
    args = ap.parse_args()

    holdout = load_holdout().set_index("month")[TARGET]
    months = holdout.index.tolist()
    baseline_mae = metrics(holdout, seasonal_naive(months))["mae"]
    names = args.name or []
    names += [p.stem for p in args.forecasts[len(names):]]

    results = []
    for name, path in zip(names, args.forecasts):
        m = metrics(holdout, load_forecast(path, months))
        results.append((name, m))
        print(card(name, m, baseline_mae))
    if len(results) > 1:
        ranked = sorted(results, key=lambda r: r[1]["mae"])
        print(f"\n🏆 Winner: {ranked[0][0]} (MAE {ranked[0][1]['mae']:.2f}k)")
    if args.png:
        save_png(results, baseline_mae, args.png)


if __name__ == "__main__":
    main()
