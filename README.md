# analytics-shorts

Code, data, and rendered assets for short-form data analytics videos
(Instagram Reels, TikTok, LinkedIn, YouTube Shorts).

**Data policy:** this repo contains **no real client data and no client names**.
Every dataset is either **synthetic** (generated with a fixed random seed) or
**public** (cited below).

## Layout
```
data/synthetic/     generated datasets (fixed seed, fully reproducible)
data/public/        cached copies of public datasets (sources below)
src/                shared code: brand style, data generators, heatmap, MP4 writer
scripts/            entry points that build data and render assets
challenges/         "Me vs. AI" challenge kits (rules, data split, scorer)
assets/vertical/    1080x1920 renders (Reels / TikTok / Shorts)
assets/landscape/   1920x1080 renders (LinkedIn / YouTube)
content_tracker.csv content pipeline: id, title, pillar, status, dates, platform, views, notes
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# MP4 export also needs ffmpeg on PATH (brew install ffmpeg / apt install ffmpeg)
```
The style uses the **Inter** font if it's installed and falls back to Helvetica, Arial, or DejaVu Sans.

## Video 01: "Your busiest hour might be costing you money"
A fictional family play-and-coworking venue. The heatmap shows % of capacity by hour × weekday.
```bash
python scripts/generate_venue_data.py   # -> data/synthetic/*.csv  (seed 42)
python scripts/make_video01_assets.py   # -> assets/{vertical,landscape}/v01_*
```
| File | What it is |
|---|---|
| `v01_heatmap.png` | static heatmap |
| `v01_heatmap_reveal.mp4` | cells revealed one by one (~11.7 s) |
| `v01_clip_quiet_hours.mp4` | dead midweek midday (Tue–Thu 12–2pm) highlighted |
| `v01_clip_peak_hour.mp4` | busiest hour highlighted, with people turned away and the revenue estimate |

**Synthetic venue model** (`src/venue_data.py`): calendar year 2025, open 8am–8pm
(hourly slots 8–19), closed Jan 1 and Dec 25. Three rooms: Play Hall (60),
Cowork Lounge (30), Party Studio (20). Six membership tiers (drop-in, family
monthly/annual, cowork flex, premium family+desk, party guest). It has weekend
peaks, a dead Tue–Thu midday, a made-up school-holiday calendar, monthly
seasonality, ~10% membership growth over the year, day-level shocks, and
overdispersed (negative-binomial) hourly counts. Demand above capacity is
recorded as `turned_away`. The "$/yr" figure in the peak clip assumes each
turned-away visitor would have paid the $18 drop-in price.

Outputs in `data/synthetic/`:
- `venue_hourly_checkins.csv`: one row per date × hour × room, with check-ins (total and by tier), occupancy, capacity, utilization, turned_away, and a school-holiday flag
- `venue_rooms.csv`, `venue_membership_tiers.csv`: lookup tables
- `venue_utilization_grid.csv`, `venue_turned_away_grid.csv`: the hour × weekday grids behind the chart

## Challenge 01: Me vs. AI forecast
See [`challenges/01_me_vs_ai/RULES.md`](challenges/01_me_vs_ai/RULES.md).
Forecast 12 months of airline passengers in 15 minutes and score both attempts with MAE.

## Public data sources
| File | Dataset | Source |
|---|---|---|
| `data/public/air_passengers_monthly.csv` | Monthly international airline passengers (thousands), Jan 1949 – Dec 1960 | Box, G. E. P. and Jenkins, G. M. (1976) *Time Series Analysis: Forecasting and Control*, Series G (the classic "AirPassengers" data). Retrieved via the seaborn `flights` dataset: https://github.com/mwaskom/seaborn-data/blob/master/flights.csv |

To refresh cached public data: `python scripts/fetch_public_data.py`, then
`python challenges/01_me_vs_ai/data.py` to rebuild the split.
