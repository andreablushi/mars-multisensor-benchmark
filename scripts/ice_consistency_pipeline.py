#!/usr/bin/env python
"""The SWIM ice labels of every grid tile and evaluation box: run here, or with --dh."""

from __future__ import annotations

from dhub import store, submit
from digitalhub_runtime_python import handler
from mars_multisensor_dataset.analysis.ground_truth.nomenclature import catalogue
from mars_multisensor_dataset.analysis.utils.tile_group import every_tile, tile_grid

from common.config import ice_consistency_settings
from ice_consistency import maps, paths
from ice_consistency.labels import write_ice_labels
from ice_consistency.sample import ice_labels


def compute_ice_labels(force: bool) -> None:
    """Label every tile the SWIM maps cover with the ice under it, and write it.

    Args:
        force: Whether to fetch the SWIM maps again rather than read them.
    """
    maps.download_maps(force)
    labelled = ice_labels(
        {tile.name: tile for tile in every_tile(tile_grid())},
        ice_consistency_settings(),
    )
    write_ice_labels(labelled)
    shallow = sum(one.ice_1_5m for one in labelled)
    deep = sum(one.ice_5m for one in labelled)
    print(
        f"swim: {len(labelled):,} tiles, {shallow:,} icy at 1 to 5 m,"
        f" {deep:,} below 5 m"
    )


def compute_evaluation_ice_labels() -> None:
    """Label every box the evaluation draw took with the ice under it, and write it."""
    drawn = [one for one in catalogue.read_labels() if one.drawn]
    # Each grid sits on the box its crops are cut to, a crater's own for a crater
    labelled = ice_labels({one.tile: one for one in drawn}, ice_consistency_settings())
    write_ice_labels(labelled, paths.EVALUATION_ROOT)
    print(f"swim: {len(labelled):,} of {len(drawn):,} evaluation boxes labelled")


@handler(outputs=[store.ICE_CONSISTENCY])
def run_labels(project, force: bool = False, workers: int | None = None):
    """Label the grid and the evaluation boxes on DigitalHub, and publish them.

    Args:
        project: The DigitalHub project the folder is logged into.
        force: Whether to fetch the SWIM maps again rather than read them.
        workers: How many cores the job was sized with, unused by the labelling.

    Returns:
        ice_consistency: The folder of the SWIM maps and every label they give.
    """
    store.download_folder(project, "labels", store.ARTIFACTS["labels"])
    compute_ice_labels(force)
    compute_evaluation_ice_labels()
    print("done", flush=True)
    return store.upload_folder(
        project, store.ICE_CONSISTENCY, store.ARTIFACTS[store.ICE_CONSISTENCY]
    )


def main() -> int:
    """Label the grid and the evaluation boxes where it was asked for.

    Returns:
        code: A process exit code, zero once the labels are written or submitted.
    """
    arguments = submit.script_parser(
        __doc__, "fetch the SWIM maps again rather than read them"
    ).parse_args()
    if arguments.dh:
        return submit.submitted("ice_consistency", arguments.ref, force=arguments.force)
    compute_ice_labels(arguments.force)
    compute_evaluation_ice_labels()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
