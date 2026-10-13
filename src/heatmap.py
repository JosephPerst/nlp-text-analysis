"""Phone-friendly utilization heatmap with frame-level control for video.

`HeatmapScene` draws the full chart once, then exposes small state setters
(how many cells are revealed, which cells are dimmed/outlined, callout text)
so a video can be produced by changing state and grabbing frames.

Vertical layout:   rows = hours,    columns = weekdays
Landscape layout:  rows = weekdays, columns = hours
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.patches import FancyBboxPatch, Rectangle

from . import style

DAY_ABBR = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu",
            "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}


def hour_label(h: int) -> str:
    suffix = "am" if h < 12 else "pm"
    h12 = h if h <= 12 else h - 12
    return f"{h12}{suffix}"


LAYOUT = {
    # axes rect [left, bottom, width, height] in figure fraction + font sizes in px
    # Vertical keeps the bottom ~12% clear: TikTok/Reels/Shorts overlay captions there.
    "vertical": dict(ax=[0.17, 0.25, 0.78, 0.50], title_y=0.945, title_px=64, sub_px=34,
                     tick_px=34, cell_px=32, cbar=[0.17, 0.215, 0.78, 0.012], cbar_px=28,
                     callout_y=0.145, callout_px=42, title_wrap=True),
    "landscape": dict(ax=[0.09, 0.15, 0.86, 0.60], title_y=0.94, title_px=58, sub_px=30,
                      tick_px=30, cell_px=28, cbar=[0.09, 0.085, 0.40, 0.018], cbar_px=24,
                      callout_y=0.075, callout_px=34, title_wrap=False, callout_x=0.95,
                      callout_ha="right"),
}

TITLE = "Your busiest hour might be costing you money"
SUBTITLE = "Avg % of capacity by hour · family play + cowork venue · 12 months"


class HeatmapScene:
    def __init__(self, grid: pd.DataFrame, orientation: str, vmax: float = 80.0,
                 theme: style.Theme = style.DEFAULT_THEME):
        self.orientation = orientation
        self.t = theme
        self.L = LAYOUT[orientation]
        self.fig = style.new_canvas(orientation, theme)
        # grid: index = hours, columns = weekdays
        self.hours = list(grid.index)
        self.days = list(grid.columns)
        values = grid.values  # [hour, day]
        self.norm = Normalize(vmin=0, vmax=vmax)
        self.cells: dict[tuple[int, str], dict] = {}
        self._draw_frame_text()
        self._draw_grid(values)
        self._draw_colorbar(vmax)
        style.add_synthetic_tag(self.fig, theme, size_px=24 if orientation == "vertical" else 22)
        self.callout = self.fig.text(self.L.get("callout_x", 0.5), self.L["callout_y"], "",
                                     ha=self.L.get("callout_ha", "center"), va="center",
                                     multialignment=self.L.get("callout_ha", "center"),
                                     fontsize=style.px_to_pt(self.L["callout_px"]),
                                     fontweight="bold", color=self.t.ink)

    # ---- static parts ------------------------------------------------------
    def _draw_frame_text(self):
        L = self.L
        title = TITLE.replace("hour ", "hour\n") if L["title_wrap"] else TITLE
        self.fig.text(0.5 if L["title_wrap"] else L["ax"][0], L["title_y"], title,
                      ha="center" if L["title_wrap"] else "left", va="top",
                      fontsize=style.px_to_pt(L["title_px"]), fontweight="bold",
                      color=self.t.ink, linespacing=1.1)
        sub_y = L["title_y"] - (0.085 if L["title_wrap"] else 0.085)
        sub = SUBTITLE.replace(" · 12", "\n12") if L["title_wrap"] else SUBTITLE
        self.fig.text(0.5 if L["title_wrap"] else L["ax"][0], sub_y, sub,
                      ha="center" if L["title_wrap"] else "left", va="top",
                      fontsize=style.px_to_pt(L["sub_px"]), color=self.t.muted, linespacing=1.25)

    def _cell_xy(self, hi: int, di: int) -> tuple[int, int]:
        """Return (col, row) for an hour index and day index; row 0 is the top."""
        if self.orientation == "vertical":
            return di, hi
        return hi, di

    def _draw_grid(self, values: np.ndarray):
        L = self.L
        ax = self.fig.add_axes(L["ax"])
        self.ax = ax
        ncols = len(self.days) if self.orientation == "vertical" else len(self.hours)
        nrows = len(self.hours) if self.orientation == "vertical" else len(self.days)
        ax.set_xlim(0, ncols)
        ax.set_ylim(nrows, 0)
        ax.set_axis_off()
        gap = 0.06
        tick_pt = style.px_to_pt(L["tick_px"])
        cell_pt = style.px_to_pt(L["cell_px"])

        # axis labels as plain text so we control size & placement
        col_labels = [DAY_ABBR[d] for d in self.days] if self.orientation == "vertical" \
            else [hour_label(h) for h in self.hours]
        row_labels = [hour_label(h) for h in self.hours] if self.orientation == "vertical" \
            else [DAY_ABBR[d] for d in self.days]
        for c, lab in enumerate(col_labels):
            ax.text(c + 0.5, -0.18, lab, ha="center", va="bottom", fontsize=tick_pt,
                    color=self.t.ink, fontweight="semibold")
        for r, lab in enumerate(row_labels):
            ax.text(-0.12, r + 0.5, lab, ha="right", va="center", fontsize=tick_pt,
                    color=self.t.ink, fontweight="semibold")

        for hi, h in enumerate(self.hours):
            for di, d in enumerate(self.days):
                v = float(values[hi, di])
                c, r = self._cell_xy(hi, di)
                rgba = self.t.cmap(self.norm(v))
                bg = FancyBboxPatch((c + gap, r + gap), 1 - 2 * gap, 1 - 2 * gap,
                                    boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=self.t.panel, ec="none")
                cell = FancyBboxPatch((c + gap, r + gap), 1 - 2 * gap, 1 - 2 * gap,
                                      boxstyle="round,pad=0,rounding_size=0.08",
                                      fc=rgba, ec="none")
                outline = Rectangle((c + gap / 2, r + gap / 2), 1 - gap, 1 - gap, fill=False,
                                    ec=self.t.ink, lw=5, visible=False, zorder=5)
                txt = ax.text(c + 0.5, r + 0.5, f"{v:.0f}%", ha="center", va="center",
                              fontsize=cell_pt, fontweight="bold",
                              color=style.text_color_for(rgba, self.t))
                ax.add_patch(bg)
                ax.add_patch(cell)
                ax.add_patch(outline)
                self.cells[(h, d)] = dict(cell=cell, txt=txt, outline=outline, value=v)

    def _draw_colorbar(self, vmax: float):
        L = self.L
        cax = self.fig.add_axes(L["cbar"])
        grad = np.linspace(0, 1, 256)[None, :]
        cax.imshow(grad, aspect="auto", cmap=self.t.cmap, extent=(0, vmax, 0, 1))
        cax.set_yticks([])
        ticks = np.arange(0, vmax + 1, 20)
        cax.set_xticks(ticks)
        cax.set_xticklabels([f"{t:.0f}%" for t in ticks[:-1]] + [f"{vmax:.0f}%+"],
                            fontsize=style.px_to_pt(L["cbar_px"]), color=self.t.muted)
        cax.tick_params(length=0, pad=8)
        for s in cax.spines.values():
            s.set_visible(False)

    # ---- state setters for animation --------------------------------------
    def reveal_order(self) -> list[tuple[int, str]]:
        """Column by column in vertical (day by day), row by row in landscape: both
        read as 'Monday through Sunday, morning to evening'."""
        return [(h, d) for d in self.days for h in self.hours]

    def set_revealed(self, keys) -> None:
        keys = set(keys)
        for k, c in self.cells.items():
            on = k in keys
            c["cell"].set_visible(on)
            c["txt"].set_visible(on)

    def set_focus(self, focus_keys=None, dim: float = 0.0, outline: bool = True) -> None:
        """Dim every cell not in focus_keys by `dim` (0 = no dim, 1 = fully dim)."""
        focus_keys = set(focus_keys or [])
        for k, c in self.cells.items():
            in_focus = k in focus_keys
            alpha = 1.0 if (in_focus or not focus_keys) else 1.0 - 0.8 * dim
            c["cell"].set_alpha(alpha)
            c["txt"].set_alpha(alpha)
            c["outline"].set_visible(outline and in_focus and dim > 0.5)

    def set_outline_color(self, color: str) -> None:
        for c in self.cells.values():
            c["outline"].set_edgecolor(color)

    def set_callout(self, text: str, color: str | None = None, alpha: float = 1.0) -> None:
        self.callout.set_text(text)
        self.callout.set_color(color or self.t.ink)
        self.callout.set_alpha(alpha)

    def to_rgba(self) -> np.ndarray:
        self.fig.canvas.draw()
        return np.asarray(self.fig.canvas.buffer_rgba())

    def save_png(self, path) -> None:
        self.fig.savefig(path, dpi=style.DPI, facecolor=self.t.bg)
