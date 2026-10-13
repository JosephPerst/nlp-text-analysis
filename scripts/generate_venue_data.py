"""Write the synthetic venue dataset to data/synthetic/.

Usage:  python scripts/generate_venue_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.venue_data import SEED, generate, turned_away_grid, utilization_grid  # noqa: E402

OUT = ROOT / "data" / "synthetic"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    v = generate(seed=SEED)
    v.hourly.to_csv(OUT / "venue_hourly_checkins.csv", index=False)
    v.rooms.to_csv(OUT / "venue_rooms.csv", index=False)
    v.tiers.to_csv(OUT / "venue_membership_tiers.csv", index=False)
    utilization_grid(v.hourly).round(1).to_csv(OUT / "venue_utilization_grid.csv")
    turned_away_grid(v.hourly).round(2).to_csv(OUT / "venue_turned_away_grid.csv")
    print(f"wrote {len(v.hourly):,} hourly rows (seed={SEED}) to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
