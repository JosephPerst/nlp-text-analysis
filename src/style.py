"""Shared visual style for all short-form video assets.

Dark navy background, clean sans-serif, big labels that survive a phone screen,
and a small "SYNTHETIC DATA" tag in the corner whenever data is synthetic.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

# ---- Palette ---------------------------------------------------------------
NAVY = "#0B1A2D"        # background
NAVY_LIGHT = "#132A45"  # empty cells / panels
INK = "#F5F7FA"         # primary text
MUTED = "#8EA3BC"       # secondary text
ACCENT = "#FFB547"      # amber highlight (peak)
QUIET = "#5EEAD4"       # teal highlight (quiet hours)

# Sequential scale for "% of capacity": cool & dim when empty, hot when full.
HEAT_CMAP = LinearSegmentedColormap.from_list(
    "venue_heat",
    ["#16314F", "#1F5F7A", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"],
)

# ---- Canvas sizes (pixels) -------------------------------------------------
DPI = 100
SIZES = {
    "vertical": (1080, 1920),
    "landscape": (1920, 1080),
}

FONT_FAMILY = ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


def apply_rcparams() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "figure.facecolor": NAVY,
            "axes.facecolor": NAVY,
            "savefig.facecolor": NAVY,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
        }
    )


def new_canvas(orientation: str):
    """Return a figure whose pixel size is exactly the target video size."""
    apply_rcparams()
    w, h = SIZES[orientation]
    fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI)
    fig.patch.set_facecolor(NAVY)
    return fig


def px_to_pt(px: float) -> float:
    """Font sizes are in points; think in on-screen pixels instead."""
    return px * 72 / DPI


def add_synthetic_tag(fig, x: float = 0.97, y: float = 0.975, size_px: float = 22):
    """Small pill in the top-right corner marking the data as synthetic."""
    fig.text(
        x,
        y,
        "SYNTHETIC DATA",
        ha="right",
        va="top",
        fontsize=px_to_pt(size_px),
        fontweight="bold",
        color=NAVY,
        bbox=dict(boxstyle="round,pad=0.45", fc=MUTED, ec="none"),
    )


def text_color_for(rgba) -> str:
    """Pick dark or light text for legibility on a cell colour."""
    r, g, b = rgba[:3]
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return NAVY if luminance > 0.55 else INK
