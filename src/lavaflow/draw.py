"""Drawing the tiles the lava flow builds cover out of what the selection kept."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from mars_multisensor_dataset.analysis.selector.models.selection import (
    SelectedObservation,
    Selection,
)
from mars_multisensor_dataset.building.configs import sharad

from lavaflow.models import LavaFlowLabel


def draw_lavaflow(
    picked: Sequence[Selection], labels: Sequence[LavaFlowLabel]
) -> list[Selection]:
    """Keep every tile a lava flow crop lies on, holding its labelled tracks alone.

    Args:
        picked: What the search left of every tile it searched, kept or not.
        labels: Every candidate crop, one per track and tile.

    Returns:
        kept: The selections to build, each tile's own observations replaced by
            the tracks labelled on it, in selection order.
    """
    tracks: dict[str, list[SelectedObservation]] = {}
    for one in labels:
        tracks.setdefault(one.tile, []).append(
            SelectedObservation(
                tile=one.tile,
                **sharad.ODE,
                pt=sharad.PRODUCT_TYPES[sharad.Kind.OBSERVATION],
                pdsid=one.pdsid,
                t_start=one.t_start,
                standing=True,
            )
        )
    return [
        replace(one, observations=tracks[one.tile.tile])
        for one in picked
        if one.tile.tile in tracks
    ]
