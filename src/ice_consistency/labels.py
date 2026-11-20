"""The SWIM ice labels of every grid tile and of every evaluation box, written down."""

from __future__ import annotations

from mars_multisensor_dataset.analysis.ground_truth.nomenclature import catalogue
from mars_multisensor_dataset.analysis.utils.tile_group import every_tile, tile_grid

from ice_consistency.analysis.artifacts import write_ice_labels
from ice_consistency.analysis.fetch import download_swim_maps
from ice_consistency.analysis.sample import ice_labels_of_boxes
from ice_consistency.configs import EVALUATION_ROOT
from ice_consistency.models import IceConsistencySettings


def write_grid_ice_labels(force: bool, settings: IceConsistencySettings) -> None:
    """Label every tile the SWIM maps cover with the ice under it, and write it.

    Args:
        force: Whether to fetch the SWIM maps again rather than read them.
        settings: The settled choices for the sampling.
    """
    download_swim_maps(force)
    labelled = ice_labels_of_boxes(
        {tile.name: tile for tile in every_tile(tile_grid())}, settings
    )
    write_ice_labels(labelled)
    shallow = sum(one.ice_1_5m for one in labelled)
    deep = sum(one.ice_5m for one in labelled)
    print(
        f"swim: {len(labelled):,} tiles, {shallow:,} icy at 1 to 5 m,"
        f" {deep:,} below 5 m"
    )


def write_evaluation_ice_labels(settings: IceConsistencySettings) -> None:
    """Label every box the evaluation draw took with the ice under it, and write it.

    Args:
        settings: The settled choices for the sampling.
    """
    drawn = [one for one in catalogue.read_labels() if one.drawn]
    # Each grid sits on the box its crops are cut to, a crater's own for a crater
    labelled = ice_labels_of_boxes({one.tile: one for one in drawn}, settings)
    write_ice_labels(labelled, EVALUATION_ROOT)
    print(f"swim: {len(labelled):,} of {len(drawn):,} evaluation boxes labelled")
