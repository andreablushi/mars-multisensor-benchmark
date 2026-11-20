#!/usr/bin/env python
"""The lava flow labels and builds: the reviewed crops, every candidate, or the list.

By default it builds from nothing the crops reviewed as reflector or none into
`data/<version>/lavaflow/dataset`, so an unsure or unreviewed crop is never fetched.
With --annotation it fills in every candidate crop into
`data/<version>/lavaflow/candidates`, for the review, or with --force deletes what it
held, on disk or published, and builds it from nothing. With --labels it lists the
candidate crops alone, from the coverage on disk. Run here, or submitted with --dh.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from dhub import build, store, submit
from digitalhub_runtime_python import handler
from mars_multisensor_dataset.analysis.selector.artifacts import read_selection
from mars_multisensor_dataset.analysis.selector.filters.admit import floor_km2
from mars_multisensor_dataset.analysis.selector.models.selection import Selection
from mars_multisensor_dataset.analysis.utils.tile_group import every_tile, tile_grid
from mars_multisensor_dataset.building import runner
from mars_multisensor_dataset.building.configs import sharad
from mars_multisensor_dataset.common.config import analysis_settings

from common.config import lavaflow_settings
from lavaflow import paths
from lavaflow.candidates import candidate_labels
from lavaflow.draw import draw_lavaflow
from lavaflow.labels import (
    judged_labels,
    read_lavaflow_labels,
    read_lavaflow_verdicts,
    write_lavaflow_labels,
)
from lavaflow.models import NONE, REFLECTOR

KEPT_VERDICTS = (REFLECTOR, NONE)
REBUILT = (
    "build the dataset again from nothing, rather than filling in what the last "
    "build left missing"
)


def compute_lavaflow_labels() -> None:
    """List every crop a lava flow reflector is looked for in, and write it."""
    settings = analysis_settings()
    regions = lavaflow_settings()
    radargrams = next(
        one for one in settings.instrument_sets if one.iid == sharad.LAYOUT.instrument
    )
    labels = candidate_labels(
        every_tile(tile_grid()),
        radargrams,
        regions,
        floor_km2(settings.criteria, radargrams.iid),
    )
    write_lavaflow_labels(labels)
    for name, region in regions.regions.items():
        held = [one for one in labels if one.region == name]
        named = {one.track for one in held if one.named}
        print(
            f"lavaflow: {name}, {len(named)} of {len(region.tracks)} named tracks,"
            f" {sum(one.named for one in held)} named crops,"
            f" {sum(not one.named for one in held)} unnamed"
        )


def lavaflow_root(annotation: bool) -> Path:
    """Return where the build is written, the candidates or the reviewed crops."""
    return paths.CANDIDATES_ROOT if annotation else paths.DATASET_ROOT


def lavaflow_selections(annotation: bool) -> list[Selection]:
    """Write the lava flow labels beside the build, and read the tiles they lie on.

    Args:
        annotation: Whether every candidate is built, or only the reviewed crops.

    Returns:
        picked: The tiles to build, each with the tracks labelled on it.

    Raises:
        FileNotFoundError: When no lava flow crops have been listed.
    """
    labels = judged_labels(read_lavaflow_labels(), read_lavaflow_verdicts())
    if not annotation:
        labels = [one for one in labels if one.verdict in KEPT_VERDICTS]
    write_lavaflow_labels(labels, lavaflow_root(annotation))
    return draw_lavaflow(read_selection(), labels)


@handler(outputs=[store.LAVAFLOW])
def run_labels(project, force: bool = False, workers: int | None = None):
    """List the lava flow crops on DigitalHub, and publish the list.

    Args:
        project: The DigitalHub project the folder is logged into.
        force: Unused, since the list is always written anew.
        workers: How many cores the job was sized with, unused by the listing.

    Returns:
        lavaflow: The folder holding the candidate list.
    """
    store.download_folder(project, "coverage", store.ARTIFACTS["coverage"])
    compute_lavaflow_labels()
    print("done", flush=True)
    listed = paths.LAVAFLOW_ROOT / paths.LAVAFLOW_LABELS_NAME
    return store.upload_folder(project, store.LAVAFLOW, paths.LAVAFLOW_ROOT, [listed])


@handler(outputs=["dataset"])
def run_build(
    project,
    force: bool = False,
    workers: int | None = None,
    overrides=(),
    annotation: bool = False,
):
    """Build the lava flow dataset on DigitalHub and publish what it left on disk.

    Args:
        project: The DigitalHub project the dataset is logged into.
        force: Whether to delete the candidates and build them from nothing.
        workers: How many products to build at once, as the job was sized.
        overrides: Hydra overrides of the lava flow config file.
        annotation: Whether every candidate is built, or only the reviewed crops.

    Returns:
        dataset: The published folder, one object per crop.
    """
    settings = lavaflow_settings(workers, overrides).build
    store.download_folder(project, "selection", store.ARTIFACTS["selection"])
    store.download_folder(
        project,
        store.LAVAFLOW,
        paths.LAVAFLOW_ROOT,
        [paths.LAVAFLOW_LABELS_NAME, paths.LAVAFLOW_VERDICTS_PATH.name],
    )
    root = lavaflow_root(annotation)
    fresh = force or not annotation
    if fresh:
        subfolder = root.relative_to(paths.LAVAFLOW_ROOT).as_posix()
        store.delete_folder(project, store.LAVAFLOW, subfolder)
    return build.published_build(
        project,
        store.LAVAFLOW,
        paths.LAVAFLOW_ROOT,
        root,
        settings,
        lavaflow_selections(annotation),
        fresh,
    )


def main() -> int:
    """Run the listing or the build where it was asked for.

    Returns:
        code: A process exit code, non zero when a product failed.
    """
    parser = submit.script_parser(__doc__, REBUILT)
    parser.add_argument(
        "--annotation",
        action="store_true",
        help="build every candidate crop to review, rather than the reviewed ones",
    )
    parser.add_argument(
        "--labels",
        action="store_true",
        help="list the candidate crops alone, from the coverage on disk",
    )
    parser.add_argument("overrides", nargs="*", help="Hydra overrides, as key=value")
    arguments = parser.parse_args()
    if arguments.labels:
        if arguments.dh:
            return submit.submitted("lavaflow_labels", arguments.ref)
        compute_lavaflow_labels()
        return 0
    if arguments.dh:
        return submit.submitted(
            "build_lavaflow",
            arguments.ref,
            arguments.overrides,
            force=arguments.force,
            annotation=arguments.annotation,
        )
    settings = lavaflow_settings(None, arguments.overrides).build
    root = lavaflow_root(arguments.annotation)
    fresh = arguments.force or not arguments.annotation
    if fresh:
        shutil.rmtree(root, ignore_errors=True)
    return runner.build_dataset(
        settings, lavaflow_selections(arguments.annotation), fresh, root=root
    )


if __name__ == "__main__":
    raise SystemExit(main())
