"""Video 1 — "Your busiest hour might be costing you money".

Exports, for both vertical (1080x1920) and landscape (1920x1080):
  * v01_heatmap.png              static chart
  * v01_heatmap_reveal.mp4       cells revealed one by one, then a hold
  * v01_clip_quiet_hours.mp4     dead midweek midday highlighted
  * v01_clip_peak_hour.mp4       the single busiest hour highlighted

Usage:  python scripts/make_video01_assets.py
Reads data/synthetic/venue_hourly_checkins.csv (run generate_venue_data.py first).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import style  # noqa: E402
from src.heatmap import DAY_ABBR, HeatmapScene, hour_label  # noqa: E402
from src.venue_data import WEEKDAYS, TIERS, turned_away_grid, utilization_grid  # noqa: E402
from src.video import FPS, Mp4Writer, ease  # noqa: E402

DATA = ROOT / "data" / "synthetic" / "venue_hourly_checkins.csv"
QUIET_DAYS = ["Tuesday", "Wednesday", "Thursday"]
QUIET_HOURS = [12, 13]
DROP_IN_PRICE = int(TIERS.set_index("tier").loc["drop_in", "visit_price"])


def write_reveal(grid: pd.DataFrame, orientation: str, out: Path) -> None:
    scene = HeatmapScene(grid, orientation)
    order = scene.reveal_order()
    w, h = style.SIZES[orientation]
    frames_per_cell = 3  # 84 cells * 3 frames ≈ 8.4 s at 30 fps
    with Mp4Writer(out, w, h) as mp4:
        scene.set_revealed([])
        mp4.write(scene.to_rgba(), repeat=int(0.8 * FPS))  # title card beat
        for i in range(1, len(order) + 1):
            scene.set_revealed(order[:i])
            mp4.write(scene.to_rgba(), repeat=frames_per_cell)
        mp4.write(scene.to_rgba(), repeat=int(2.5 * FPS))  # final hold


def write_focus_clip(grid, orientation, out, focus, color, callout, hold_s=3.0) -> None:
    scene = HeatmapScene(grid, orientation)
    scene.set_revealed(scene.cells.keys())
    scene.set_outline_color(color)
    w, h = style.SIZES[orientation]
    fade = int(0.6 * FPS)
    with Mp4Writer(out, w, h) as mp4:
        mp4.write(scene.to_rgba(), repeat=int(0.6 * FPS))
        for f in range(fade + 1):
            t = ease(f / fade)
            scene.set_focus(focus, dim=t)
            scene.set_callout(callout, color=color, alpha=t)
            mp4.write(scene.to_rgba())
        mp4.write(scene.to_rgba(), repeat=int(hold_s * FPS))


def main() -> None:
    hourly = pd.read_csv(DATA)
    grid = utilization_grid(hourly)
    away = turned_away_grid(hourly)

    # Peak cell = highest % of capacity.
    stacked = grid.stack()
    peak_hour, peak_day = stacked.idxmax()
    peak_pct = stacked.max()
    peak_away = away.loc[peak_hour, peak_day]
    lost_per_year = peak_away * DROP_IN_PRICE * 52  # if every turned-away visitor paid drop-in

    quiet_keys = [(h, d) for d in QUIET_DAYS for h in QUIET_HOURS]
    quiet_pct = grid.loc[QUIET_HOURS, QUIET_DAYS].values.mean()

    print(f"peak: {DAY_ABBR[peak_day]} {hour_label(peak_hour)} = {peak_pct:.0f}% full, "
          f"{peak_away:.1f} turned away per occurrence (~${lost_per_year:,.0f}/yr at drop-in price)")
    print(f"quiet: Tue-Thu 12-2pm = {quiet_pct:.0f}% full on average")

    for orientation in ("vertical", "landscape"):
        out = ROOT / "assets" / orientation
        out.mkdir(parents=True, exist_ok=True)

        scene = HeatmapScene(grid, orientation)
        scene.save_png(out / "v01_heatmap.png")

        write_reveal(grid, orientation, out / "v01_heatmap_reveal.mp4")

        write_focus_clip(
            grid, orientation, out / "v01_clip_quiet_hours.mp4", quiet_keys, style.QUIET,
            f"Tue–Thu, 12–2pm: only {quiet_pct:.0f}% full\nYou're staffing empty rooms",
        )
        write_focus_clip(
            grid, orientation, out / "v01_clip_peak_hour.mp4", [(peak_hour, peak_day)],
            style.ACCENT,
            f"{DAY_ABBR[peak_day]} {hour_label(peak_hour)}: ~{peak_away:.0f} people turned away"
            f"\n≈ ${lost_per_year:,.0f}/yr walking out the door",
        )
        print(f"wrote assets/{orientation}/")


if __name__ == "__main__":
    main()
