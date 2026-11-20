"""Where a tile's SWIM grid points stand, and the map pixel each one falls in."""

from __future__ import annotations

import numpy as np
from mars_multisensor_dataset.common.maths import geodesy
from mars_multisensor_dataset.common.maths.geodesy import SPHEROID
from mars_multisensor_dataset.common.maths.physics import METRES_PER_KM

from ice_consistency.configs import (
    GRID_POINTS,
    GRID_SPACING_KM,
    NORTH_LAT,
    PIXELS_PER_DEGREE,
    WEST_LON,
)


def grid_offsets_from_tile_centre() -> tuple[np.ndarray, np.ndarray]:
    """Return how far east and north of a tile's centre each labelled point stands.

    Returns:
        east: The metres east of the centre, rows from the north. (P, P)
        north: The metres north of the centre, rows from the north. (P, P)
    """
    steps = (np.arange(GRID_POINTS) - (GRID_POINTS - 1) / 2) * (
        GRID_SPACING_KM * METRES_PER_KM
    )
    north, east = np.meshgrid(steps[::-1], steps, indexing="ij")
    return east, north


def grid_point_positions(
    centre_lon: np.ndarray, centre_lat: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return where every tile's labelled points stand, rows from the north.

    Args:
        centre_lon: The longitude each tile is centred on, in degrees. (T,)
        centre_lat: The latitude each tile is centred on, in degrees. (T,)

    Returns:
        lon: The longitude of every point, -180 to 180. (T, P * P)
        lat: The latitude of every point. (T, P * P)
    """
    east, north = grid_offsets_from_tile_centre()
    # Placed by the same geodesic east and north of the centre the tokens are
    azimuth = np.degrees(np.arctan2(east, north)).ravel()
    span = np.hypot(east, north).ravel()
    count = len(centre_lon)
    lon, lat, _ = SPHEROID.fwd(
        np.repeat(centre_lon, azimuth.size),
        np.repeat(centre_lat, azimuth.size),
        np.tile(azimuth, count),
        np.tile(span, count),
    )
    return lon.reshape(count, -1), lat.reshape(count, -1)


def swim_pixels_of_points(
    lon: np.ndarray, lat: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return the pixel every point falls in on any of the maps.

    Args:
        lon: The longitudes of the points, in degrees.
        lat: The latitudes of the points, in degrees.

    Returns:
        rows: The row each point falls in.
        columns: The column each point falls in, wrapped across 180 degrees.
    """
    rows = np.floor((NORTH_LAT - lat) * PIXELS_PER_DEGREE).astype(int)
    columns = np.floor(
        (geodesy.normalise_longitude(lon) - WEST_LON) * PIXELS_PER_DEGREE
    ).astype(int)
    return (
        np.clip(rows, 0, round(2 * NORTH_LAT * PIXELS_PER_DEGREE) - 1),
        columns % round(geodesy.TURN * PIXELS_PER_DEGREE),
    )
