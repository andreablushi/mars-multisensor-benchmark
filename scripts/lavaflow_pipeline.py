#!/usr/bin/env python
"""The lava flow labels and builds: the reviewed crops, every candidate, or the list."""

from __future__ import annotations

from collections.abc import Sequence

from dhub import build, store, submit
from digitalhub_runtime_python import handler
from mars_multisensor_dataset.analysis.config import analysis_settings

from lavaflow import configs
from lavaflow.build import build_lavaflow_dataset, prepared_lavaflow_build
from lavaflow.labels import write_candidate_lavaflow_labels

REBUILT = (
    "build the dataset again from nothing, rather than filling in what the last "
    "build left missing"
)


def write_every_lavaflow_label() -> None:
    """List every crop a lava flow reflector is looked for in, and write it."""
    write_candidate_lavaflow_labels(
        analysis_settings(), configs.read_lavaflow_settings().regions
    )


def build_lavaflow(overrides: Sequence[str], annotation: bool, force: bool) -> int:
    """Build the lava flow dataset here, the candidates or the reviewed crops.

    Args:
        overrides: Hydra overrides of the lava flow config file.
        annotation: Whether every candidate is built, or only the reviewed crops.
        force: Whether to build the candidates from nothing; the reviewed crops are.

    Returns:
        code: A process exit code, non zero when a product failed.
    """
    settings = configs.read_lavaflow_settings(overrides=overrides).build
    return build_lavaflow_dataset(settings, annotation, force)


@handler(outputs=[store.LAVAFLOW])
def published_lavaflow_labels(project, force: bool = False, workers: int | None = None):
    """List the lava flow crops on DigitalHub, and publish the list.

    Args:
        project: The DigitalHub project the folder is logged into.
        force: Unused, since the list is always written anew.
        workers: How many cores the job was sized with, unused by the listing.

    Returns:
        lavaflow: The folder holding the candidate list.
    """
    store.download_published_folder(project, "coverage", store.ARTIFACTS["coverage"])
    write_every_lavaflow_label()
    print("done", flush=True)
    listed = configs.LAVAFLOW_ROOT / configs.LAVAFLOW_LABELS_NAME
    return store.upload_folder_as_artifact(
        project, store.LAVAFLOW, configs.LAVAFLOW_ROOT, [listed]
    )


@handler(outputs=["dataset"])
def published_lavaflow_build(
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
    settings = configs.read_lavaflow_settings(workers, overrides).build
    store.download_published_folder(project, "selection", store.ARTIFACTS["selection"])
    store.download_published_folder(
        project,
        store.LAVAFLOW,
        configs.LAVAFLOW_ROOT,
        [configs.LAVAFLOW_LABELS_NAME, configs.LAVAFLOW_VERDICTS_PATH.name],
    )
    prepared = prepared_lavaflow_build(annotation, force)
    if prepared.fresh:
        subfolder = prepared.root.relative_to(configs.LAVAFLOW_ROOT).as_posix()
        store.delete_published_folder(project, store.LAVAFLOW, subfolder)
    return build.build_and_publish_dataset(
        project,
        store.LAVAFLOW,
        configs.LAVAFLOW_ROOT,
        prepared.root,
        settings,
        prepared.selections,
        prepared.fresh,
    )


def main() -> int:
    """Run the listing or the build where it was asked for.

    Returns:
        code: A process exit code, non zero when a product failed.
    """
    parser = submit.script_argument_parser(__doc__, REBUILT)
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
            return submit.submit_stage_run("lavaflow_labels", arguments.ref)
        write_every_lavaflow_label()
        return 0
    if arguments.dh:
        return submit.submit_stage_run(
            "build_lavaflow",
            arguments.ref,
            arguments.overrides,
            force=arguments.force,
            annotation=arguments.annotation,
        )
    return build_lavaflow(arguments.overrides, arguments.annotation, arguments.force)


if __name__ == "__main__":
    raise SystemExit(main())
