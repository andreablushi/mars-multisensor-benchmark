"""The lava flow candidate crops, listed and written down, or read back as built."""

from __future__ import annotations

from collections.abc import Mapping

from mars_multisensor_dataset.analysis.models.settings import AnalysisSettings
from mars_multisensor_dataset.analysis.selector.filters.admit import floor_km2
from mars_multisensor_dataset.analysis.utils.tile_group import every_tile, tile_grid
from mars_multisensor_dataset.building.configs import sharad

from lavaflow.analysis.artifacts import read_lavaflow_labels, write_lavaflow_labels
from lavaflow.analysis.candidates import candidate_lavaflow_labels
from lavaflow.configs import candidate_crop_path
from lavaflow.models import LavaFlowLabel, LavaFlowRegion


def write_candidate_lavaflow_labels(
    analysis: AnalysisSettings, regions: Mapping[str, LavaFlowRegion]
) -> None:
    """List every crop a lava flow reflector is looked for in, and write it.

    Args:
        analysis: The dataset's analysis settings, holding SHARAD's admit floor.
        regions: Every region a paper reports reflectors in, by its name.
    """
    radargrams = next(
        one for one in analysis.instrument_sets if one.iid == sharad.LAYOUT.instrument
    )
    labels = candidate_lavaflow_labels(
        every_tile(tile_grid()),
        radargrams,
        regions,
        floor_km2(analysis.criteria, radargrams.iid),
    )
    write_lavaflow_labels(labels)
    for name, region in regions.items():
        held = [one for one in labels if one.region == name]
        named = {one.track for one in held if one.named}
        print(
            f"lavaflow: {name}, {len(named)} of {len(region.tracks)} named tracks,"
            f" {sum(one.named for one in held)} named crops,"
            f" {sum(not one.named for one in held)} unnamed"
        )


def built_candidate_labels() -> list[LavaFlowLabel]:
    """Read back the candidate crops the build of every candidate left on disk.

    Returns:
        labels: The candidate crops on disk, in the order they were written.
    """
    return [
        label for label in read_lavaflow_labels() if candidate_crop_path(label).exists()
    ]
