"""Synthetic data for a fictional family play-and-coworking venue.

Everything here is invented. No real business, client or customer is modelled.
The generator is deterministic for a given seed.

Output grain: one row per date x hour x room for a full calendar year.
Open 08:00-20:00, so hourly slots start at 8, 9, ..., 19.

Patterns baked in:
  * weekend peaks (Saturday late morning is the crunch)
  * a dead midweek midday (Tue-Thu, 12:00-15:00)
  * school-holiday spikes (weekday traffic looks weekend-ish)
  * mild seasonality (indoor play busier in winter) and slow membership growth
  * day-level noise (weather, local events) plus hour-level count noise
  * demand above capacity is recorded as `turned_away`
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

SEED = 42
YEAR = 2025
OPEN_HOURS = list(range(8, 20))  # slot start hours; venue closes at 20:00

ROOMS = pd.DataFrame(
    [
        {"room": "Play Hall", "capacity": 60, "dwell_retention": 0.50},
        {"room": "Cowork Lounge", "capacity": 30, "dwell_retention": 0.75},
        {"room": "Party Studio", "capacity": 20, "dwell_retention": 0.55},
    ]
)

TIERS = pd.DataFrame(
    [
        {"tier": "drop_in", "label": "Drop-in", "monthly_price": 0, "visit_price": 18},
        {"tier": "family_monthly", "label": "Family Monthly", "monthly_price": 89, "visit_price": 0},
        {"tier": "family_annual", "label": "Family Annual", "monthly_price": 69, "visit_price": 0},
        {"tier": "cowork_flex", "label": "Cowork Flex", "monthly_price": 149, "visit_price": 0},
        {"tier": "premium_family_desk", "label": "Premium Family + Desk", "monthly_price": 229, "visit_price": 0},
        {"tier": "party_guest", "label": "Party Guest", "monthly_price": 0, "visit_price": 0},
    ]
)

# Expected occupancy as a fraction of capacity, by hour slot 8..19.
_H = OPEN_HOURS
PROFILES = {
    "Play Hall": {
        "midweek": [0.10, 0.36, 0.46, 0.34, 0.07, 0.04, 0.05, 0.20, 0.46, 0.50, 0.30, 0.12],
        "mon_fri": [0.12, 0.40, 0.50, 0.40, 0.18, 0.13, 0.15, 0.30, 0.55, 0.60, 0.38, 0.16],
        "sat":     [0.25, 0.72, 0.98, 1.10, 0.95, 0.78, 0.86, 0.90, 0.76, 0.52, 0.32, 0.15],
        "sun":     [0.20, 0.62, 0.90, 0.98, 0.84, 0.68, 0.74, 0.76, 0.60, 0.40, 0.22, 0.10],
    },
    "Cowork Lounge": {
        "midweek": [0.28, 0.62, 0.78, 0.70, 0.20, 0.22, 0.55, 0.60, 0.50, 0.34, 0.14, 0.07],
        "mon_fri": [0.22, 0.52, 0.66, 0.64, 0.32, 0.36, 0.55, 0.50, 0.40, 0.26, 0.10, 0.05],
        "sat":     [0.08, 0.18, 0.26, 0.28, 0.24, 0.22, 0.24, 0.22, 0.16, 0.10, 0.05, 0.03],
        "sun":     [0.05, 0.12, 0.18, 0.20, 0.18, 0.16, 0.16, 0.14, 0.10, 0.06, 0.03, 0.02],
    },
    "Party Studio": {
        "midweek": [0.00, 0.02, 0.03, 0.03, 0.01, 0.01, 0.01, 0.04, 0.10, 0.12, 0.08, 0.03],
        "mon_fri": [0.00, 0.03, 0.06, 0.06, 0.04, 0.03, 0.04, 0.12, 0.30, 0.38, 0.28, 0.10],
        "sat":     [0.05, 0.30, 0.75, 0.92, 0.85, 0.70, 0.88, 0.92, 0.80, 0.55, 0.25, 0.08],
        "sun":     [0.04, 0.25, 0.65, 0.82, 0.75, 0.60, 0.78, 0.80, 0.62, 0.38, 0.15, 0.05],
    },
}

# Indoor play is busier in the colder months. Index 0 = January.
MONTH_SEASONALITY = {
    "Play Hall":     [1.06, 1.05, 1.00, 0.96, 0.90, 0.86, 0.92, 0.92, 0.90, 1.00, 1.06, 1.10],
    "Cowork Lounge": [1.05, 1.03, 1.02, 1.00, 0.98, 0.95, 0.85, 0.82, 1.04, 1.04, 1.03, 0.90],
    "Party Studio":  [0.95, 1.00, 1.00, 1.02, 1.05, 1.00, 0.90, 0.90, 1.00, 1.05, 1.05, 1.10],
}

# Fictional school-holiday calendar (generic, not tied to any real district).
SCHOOL_HOLIDAYS = [
    ("2025-01-01", "2025-01-05"),   # winter break tail
    ("2025-02-17", "2025-02-21"),   # mid-winter break
    ("2025-04-07", "2025-04-18"),   # spring break
    ("2025-06-23", "2025-08-29"),   # summer
    ("2025-10-27", "2025-10-31"),   # autumn mid-term
    ("2025-12-22", "2025-12-31"),   # winter break
]
CLOSED_DATES = ["2025-01-01", "2025-12-25"]

# Tier mix of check-ins, by room and whether it is a weekend/holiday.
TIER_MIX = {
    "Play Hall": {
        "regular": {"drop_in": 0.32, "family_monthly": 0.45, "family_annual": 0.17, "premium_family_desk": 0.06},
        "busy":    {"drop_in": 0.50, "family_monthly": 0.33, "family_annual": 0.13, "premium_family_desk": 0.04},
    },
    "Cowork Lounge": {
        "regular": {"drop_in": 0.18, "cowork_flex": 0.52, "premium_family_desk": 0.30},
        "busy":    {"drop_in": 0.30, "cowork_flex": 0.40, "premium_family_desk": 0.30},
    },
    "Party Studio": {
        "regular": {"party_guest": 1.0},
        "busy":    {"party_guest": 1.0},
    },
}


@dataclass
class VenueData:
    hourly: pd.DataFrame
    rooms: pd.DataFrame
    tiers: pd.DataFrame


def _is_holiday(dates: pd.DatetimeIndex) -> np.ndarray:
    mask = np.zeros(len(dates), dtype=bool)
    for start, end in SCHOOL_HOLIDAYS:
        mask |= (dates >= start) & (dates <= end)
    return mask


def _day_profile(room: str, weekday: int, holiday: bool) -> np.ndarray:
    p = PROFILES[room]
    if weekday == 5:
        return np.array(p["sat"])
    if weekday == 6:
        return np.array(p["sun"])
    base = np.array(p["midweek"] if weekday in (1, 2, 3) else p["mon_fri"])
    if holiday:
        if room == "Play Hall":
            # Kids are off school: weekdays start looking like a softer Saturday.
            return 0.5 * base + 0.5 * np.array(p["sat"]) * 0.85
        if room == "Cowork Lounge":
            return base * 0.85  # parents take time off
        return 0.6 * base + 0.4 * np.array(p["sun"])
    return base


def generate(seed: int = SEED, year: int = YEAR) -> VenueData:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
    dates = dates[~dates.isin(pd.to_datetime(CLOSED_DATES))]
    holiday = _is_holiday(dates)
    # Membership growth: demand drifts up ~10% across the year.
    growth = np.linspace(0.95, 1.05, len(dates))
    # Shared day-level shock (weather, local events) + room-specific wobble.
    day_shock = rng.lognormal(mean=0.0, sigma=0.10, size=len(dates))

    rows = []
    for _, room in ROOMS.iterrows():
        name, cap, retention = room["room"], room["capacity"], room["dwell_retention"]
        room_shock = rng.lognormal(mean=0.0, sigma=0.08, size=len(dates))
        for i, d in enumerate(dates):
            profile = _day_profile(name, d.weekday(), holiday[i])
            mult = MONTH_SEASONALITY[name][d.month - 1] * growth[i] * day_shock[i] * room_shock[i]
            expected = np.clip(profile * mult * cap, 0.05, None)
            # Negative binomial: Poisson with gamma-distributed rate (overdispersed counts).
            k = 12.0
            demand = rng.poisson(rng.gamma(shape=k, scale=expected / k))
            occupancy = np.minimum(demand, cap)
            turned_away = np.maximum(demand - cap, 0)
            prev = np.concatenate([[0], occupancy[:-1]])
            arrivals_mean = np.maximum(occupancy - retention * prev, 0.3)
            checkins = rng.poisson(arrivals_mean)

            busy = d.weekday() >= 5 or holiday[i]
            mix = TIER_MIX[name]["busy" if busy else "regular"]
            tier_names = list(mix)
            tier_counts = np.array([rng.multinomial(c, list(mix.values())) for c in checkins])

            for j, h in enumerate(OPEN_HOURS):
                row = {
                    "date": d.date().isoformat(),
                    "weekday": d.day_name(),
                    "hour": h,
                    "room": name,
                    "capacity": cap,
                    "is_school_holiday": bool(holiday[i]),
                    "checkins": int(checkins[j]),
                    "occupancy": int(occupancy[j]),
                    "turned_away": int(turned_away[j]),
                }
                for t in TIERS["tier"]:
                    row[f"checkins_{t}"] = 0
                for t, c in zip(tier_names, tier_counts[j]):
                    row[f"checkins_{t}"] = int(c)
                rows.append(row)

    hourly = pd.DataFrame(rows)
    hourly["utilization"] = (hourly["occupancy"] / hourly["capacity"]).round(4)
    hourly = hourly.sort_values(["date", "hour", "room"]).reset_index(drop=True)
    return VenueData(hourly=hourly, rooms=ROOMS[["room", "capacity"]].copy(), tiers=TIERS.copy())


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def utilization_grid(hourly: pd.DataFrame) -> pd.DataFrame:
    """Hour x weekday grid of venue-wide % of capacity (all rooms pooled)."""
    g = hourly.groupby(["hour", "weekday"])[["occupancy", "capacity"]].sum()
    pct = (g["occupancy"] / g["capacity"] * 100).unstack("weekday")
    return pct[WEEKDAYS].loc[OPEN_HOURS]


def turned_away_grid(hourly: pd.DataFrame) -> pd.DataFrame:
    """Hour x weekday grid of the average number of people turned away per occurrence."""
    per_day = hourly.groupby(["date", "weekday", "hour"])["turned_away"].sum().reset_index()
    g = per_day.groupby(["hour", "weekday"])["turned_away"].mean().unstack("weekday")
    return g[WEEKDAYS].loc[OPEN_HOURS]
