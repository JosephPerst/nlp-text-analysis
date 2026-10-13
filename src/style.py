"""Shared visual style for all short-form video assets.

The default "navy" theme is the house look: dark navy background, clean
sans-serif, big labels that survive a phone screen, and a small
"SYNTHETIC DATA" tag in the corner whenever data is synthetic.

Alternative themes live in THEMES so the same video can be rendered in
several looks (e.g. light for LinkedIn, neon for TikTok).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, to_rgba  # noqa: E402


@dataclass(frozen=True)
class Theme:
    name: str
    description: str
    bg: str           # page background
    panel: str        # empty cell / slot colour
    ink: str          # primary text
    muted: str        # secondary text
    accent: str       # peak highlight
    quiet: str        # quiet-hours highlight
    ramp: tuple       # sequential colours, low -> high
    light_text: str = "#F5F7FA"  # text drawn on dark cells
    dark_text: str = "#0B1A2D"   # text drawn on light cells
    cmap: LinearSegmentedColormap = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(
            self, "cmap", LinearSegmentedColormap.from_list(f"{self.name}_heat", list(self.ramp))
        )


THEMES: dict[str, Theme] = {
    t.name: t
    for t in [
        Theme(
            name="navy",
            description="House style: dark navy #0B1A2D, teal-to-coral heat ramp",
            bg="#0B1A2D", panel="#132A45", ink="#F5F7FA", muted="#8EA3BC",
            accent="#FFB547", quiet="#5EEAD4",
            ramp=("#16314F", "#1F5F7A", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"),
        ),
        Theme(
            name="light",
            description="Clean paper-white look for LinkedIn / slides",
            bg="#F7F6F2", panel="#E7E5DE", ink="#14213D", muted="#5C6B80",
            accent="#D9480F", quiet="#0B7285",
            ramp=("#E3EEF2", "#A9D6DB", "#5FB3B3", "#2C7DA0", "#1B4E7A", "#14213D"),
            light_text="#FFFFFF", dark_text="#14213D",
        ),
        Theme(
            name="neon",
            description="Near-black with electric violet-to-cyan glow (TikTok energy)",
            bg="#07060D", panel="#15132A", ink="#FFFFFF", muted="#9C97C9",
            accent="#FF2E97", quiet="#39FF88",
            ramp=("#1B1640", "#3A1C71", "#7B2FF7", "#C04DF9", "#3FC8FF", "#B8F7FF"),
            dark_text="#07060D",
        ),
        Theme(
            name="mono",
            description="Minimal greyscale; only the highlights get colour",
            bg="#111111", panel="#1E1E1E", ink="#F2F2F2", muted="#9A9A9A",
            accent="#FF5A36", quiet="#4DA3FF",
            ramp=("#262626", "#454545", "#6B6B6B", "#9C9C9C", "#CFCFCF", "#FFFFFF"),
            dark_text="#111111",
        ),
        Theme(
            name="warm",
            description="Editorial espresso & terracotta",
            bg="#1C1714", panel="#2B2420", ink="#FAF3E8", muted="#BFAE9A",
            accent="#FFD166", quiet="#8ECAE6",
            ramp=("#3A2E28", "#6B4F3A", "#A5683F", "#D9823B", "#F0A04B", "#FFE0A3"),
            dark_text="#1C1714",
        ),
        Theme(
            name="accessible",
            description="Colour-blind-safe cividis ramp on navy, high contrast",
            bg="#0B1A2D", panel="#132A45", ink="#FFFFFF", muted="#A9B8CC",
            accent="#FFFFFF", quiet="#FFFFFF",
            ramp=("#00224E", "#35456C", "#666970", "#948E77", "#C8B866", "#FEE838"),
            dark_text="#00224E",
        ),
    ]
}
DEFAULT_THEME = THEMES["navy"]

# Back-compat constants (house style), used by e.g. the challenge result card.
NAVY = DEFAULT_THEME.bg
NAVY_LIGHT = DEFAULT_THEME.panel
INK = DEFAULT_THEME.ink
MUTED = DEFAULT_THEME.muted
ACCENT = DEFAULT_THEME.accent
QUIET = DEFAULT_THEME.quiet
HEAT_CMAP = DEFAULT_THEME.cmap

# ---- Canvas sizes (pixels) -------------------------------------------------
DPI = 100
SIZES = {
    "vertical": (1080, 1920),
    "landscape": (1920, 1080),
}

FONT_FAMILY = ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


def apply_rcparams(theme: Theme = DEFAULT_THEME) -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "figure.facecolor": theme.bg,
            "axes.facecolor": theme.bg,
            "savefig.facecolor": theme.bg,
            "text.color": theme.ink,
            "axes.labelcolor": theme.ink,
            "xtick.color": theme.ink,
            "ytick.color": theme.ink,
        }
    )


def new_canvas(orientation: str, theme: Theme = DEFAULT_THEME):
    """Return a figure whose pixel size is exactly the target video size."""
    apply_rcparams(theme)
    w, h = SIZES[orientation]
    fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI)
    fig.patch.set_facecolor(theme.bg)
    return fig


def px_to_pt(px: float) -> float:
    """Font sizes are in points; think in on-screen pixels instead."""
    return px * 72 / DPI


def add_synthetic_tag(fig, theme: Theme = DEFAULT_THEME, x: float = 0.97, y: float = 0.975,
                      size_px: float = 22):
    """Small pill in the top-right corner marking the data as synthetic."""
    fig.text(
        x,
        y,
        "SYNTHETIC DATA",
        ha="right",
        va="top",
        fontsize=px_to_pt(size_px),
        fontweight="bold",
        color=theme.bg,
        bbox=dict(boxstyle="round,pad=0.45", fc=theme.muted, ec="none"),
    )


def _luminance(color) -> float:
    r, g, b = to_rgba(color)[:3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def text_color_for(rgba, theme: Theme = DEFAULT_THEME) -> str:
    """Pick dark or light text for legibility on a cell colour."""
    return theme.dark_text if _luminance(rgba) > 0.55 else theme.light_text
