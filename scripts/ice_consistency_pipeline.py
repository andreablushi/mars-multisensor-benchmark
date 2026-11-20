#!/usr/bin/env python
"""The SWIM ice labels of every grid tile and evaluation box: run here, or with --dh."""

from __future__ import annotations

from dhub import store, submit
from digitalhub_runtime_python import handler

from ice_consistency.configs import read_ice_consistency_settings
from ice_consistency.labels import write_evaluation_ice_labels, write_grid_ice_labels


def write_every_ice_label(force: bool) -> None:
    """Label the grid tiles and the evaluation boxes with the ice under them.

    Args:
        force: Whether to fetch the SWIM maps again rather than read them.
    """
    settings = read_ice_consistency_settings()
    write_grid_ice_labels(force, settings)
    write_evaluation_ice_labels(settings)


@handler(outputs=[store.ICE_CONSISTENCY])
def published_ice_labels(project, force: bool = False, workers: int | None = None):
    """Label the grid and the evaluation boxes on DigitalHub, and publish them.

    Args:
        project: The DigitalHub project the folder is logged into.
        force: Whether to fetch the SWIM maps again rather than read them.
        workers: How many cores the job was sized with, unused by the labelling.

    Returns:
        ice_consistency: The folder of the SWIM maps and every label they give.
    """
    store.download_published_folder(project, "labels", store.ARTIFACTS["labels"])
    write_every_ice_label(force)
    print("done", flush=True)
    return store.upload_folder_as_artifact(
        project, store.ICE_CONSISTENCY, store.ARTIFACTS[store.ICE_CONSISTENCY]
    )


def main() -> int:
    """Label the grid and the evaluation boxes where it was asked for.

    Returns:
        code: A process exit code, zero once the labels are written or submitted.
    """
    arguments = submit.script_argument_parser(
        __doc__, "fetch the SWIM maps again rather than read them"
    ).parse_args()
    if arguments.dh:
        return submit.submit_stage_run(
            "ice_consistency", arguments.ref, force=arguments.force
        )
    write_every_ice_label(arguments.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
