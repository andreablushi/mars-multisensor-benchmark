"""Every box between 60S and 60N, sampled on one grid under the SWIM maps."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from mars_multisensor_dataset.common.maths import geodesy
from mars_multisensor_dataset.common.maths.box import Boxed

from ice_consistency.analysis.fetch import read_swim_consistency_layer
from ice_consistency.analysis.position import (
    grid_point_positions,
    swim_pixels_of_points,
)
from ice_consistency.configs import LAYERS, NORTH_LAT
from ice_consistency.models import IceConsistencySettings, IceLabel


def ice_labels_of_boxes(
    boxes: Mapping[str, Boxed], settings: IceConsistencySettings
) -> list[IceLabel]:
    """Label every box the SWIM maps cover whole with the ice under its grid.

    Args:
        boxes: The box each tile's crops are cut to, by the tile's name.
        settings: The settled choices for the sampling.

    Returns:
        labels: One label per box between 60S and 60N, in the order given.
    """
    mapped = {
        name: cut
        for name, cut in boxes.items()
        if -NORTH_LAT <= cut.min_lat and cut.max_lat <= NORTH_LAT
    }
    centres = np.array([geodesy.bbox_centre(cut) for cut in mapped.values()])
    pixels = swim_pixels_of_points(*grid_point_positions(centres[:, 0], centres[:, 1]))
    shallow, deep, radar = (
        read_swim_consistency_layer(layer)[pixels] for layer in LAYERS
    )
    icy_shallow = shallow >= settings.threshold_1_5m
    icy_deep = deep >= settings.threshold_5m
    return [
        IceLabel(
            tile=name,
            centre_lon=float(lon),
            centre_lat=float(lat),
            consistency_1_5m=tuple(shallow[at].tolist()),
            consistency_5m=tuple(deep[at].tolist()),
            radar_surface_power=tuple(radar[at].tolist()),
            icy_points_1_5m=tuple(icy_shallow[at].tolist()),
            icy_points_5m=tuple(icy_deep[at].tolist()),
            ice_1_5m=bool(np.mean(icy_shallow[at]) >= settings.icy_share),
            ice_5m=bool(np.mean(icy_deep[at]) >= settings.icy_share),
        )
        for at, (name, (lon, lat)) in enumerate(zip(mapped, centres, strict=True))
    ]
