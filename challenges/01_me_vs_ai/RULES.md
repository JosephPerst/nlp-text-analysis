# Challenge 01: Me vs. AI, forecast edition

## The task
Forecast **monthly international airline passengers (thousands)** for the
12 months of **1960 (1960-01 to 1960-12)**, using only the history from
1949-01 to 1959-12.

## Rules
| | |
|---|---|
| **Time limit** | **15 minutes** per contestant, from opening the starter file to saving the CSV |
| **Training data** | `train.csv`: 1949-01 to 1959-12 (132 months), via `data.load_train()` |
| **Holdout** | `holdout.csv`: 1960-01 to 1960-12 (12 months). **Don't open it.** Only `score.py` reads it |
| **Metric** | **MAE** (mean absolute error, in thousands of passengers). Lower wins |
| **Tie-break** | MAPE, then whoever finished faster |
| **Output** | CSV with columns `month` (YYYY-MM) and `forecast`: exactly the 12 holdout months |
| **Allowed** | Any Python library already in `requirements.txt` (numpy, pandas, matplotlib, seaborn). Docs and your own memory |
| **Not allowed** | Looking at 1960 data in any form, or external data |

Me: hand-code in `my_attempt.py`, writing to `forecasts/me.csv`.
AI: the AI gets the same prompt, files and 15 minutes, live on camera, writing to `forecasts/ai.csv`.

## Scoring
```bash
cd challenges/01_me_vs_ai
python score.py forecasts/me.csv forecasts/ai.csv --name "Me" --name "AI" --png result_card.png
```
The scorer prints a result card per contestant. It also shows a
**seasonal-naive baseline** (each 1960 month = same month in 1959) as the bar to
clear. With `--png` it saves a 1080x1920 card ready for the video.

## Why this dataset
- **Readable story**: "how many people will fly next year?" needs no explanation on camera.
- **Clear structure in a small dataset**: a strong upward trend plus summer
  peaks that grow over time (multiplicative seasonality). A human can eyeball it,
  and there's still room for a model to do better.
- **Tiny and fast**: 144 rows, so nothing slows the 15-minute clock.
- **Reproducible**: a classic public benchmark (Box & Jenkins, 1976), so viewers
  can try it themselves.

## Files
- `data.py`: loading helpers plus the fixed split (`python data.py` rebuilds the CSVs from `data/public/`)
- `train.csv` / `holdout.csv`: the split
- `my_attempt.py`: blank starter for the human attempt (no solution inside)
- `score.py`: scorer and result card
