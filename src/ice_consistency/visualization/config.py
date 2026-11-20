"""How the ice notebook marks a tile, and which tiles it draws a grid over."""

from __future__ import annotations

import ipywidgets as widgets

TILE_MARKER = 1.5
CATEGORIES = (
    "Icy at both depths",
    "Icy at 1 to 5 m only",
    "Icy below 5 m only",
    "Icy at neither",
)

ICE_SAMPLES = {
    "Ice rich, Deuteronilus Mensae": "b239_c0035",
    "Ice poor, Meridiani Planum": "b175_c0657",
}

ICE_CMAP = "RdBu"
ICE_ALPHA = 0.5
ICE_PANEL = widgets.Layout(width="50%")
