"""The lava flow builds: every candidate crop to review, or the reviewed ones."""

from __future__ import annotations

import shutil

from mars_multisensor_dataset.analysis.selector.artifacts import read_selection
from mars_multisensor_dataset.building import runner
from mars_multisensor_dataset.building.models.settings import BuildSettings

from lavaflow.analysis.artifacts import (
    read_lavaflow_labels_with_verdicts,
    write_lavaflow_labels,
)
from lavaflow.building.draw import selections_holding_lavaflow_tracks
from lavaflow.configs import lavaflow_build_root
from lavaflow.models import LavaFlowBuild


def prepared_lavaflow_build(annotation: bool, force: bool) -> LavaFlowBuild:
    """Clear the build's root if it starts anew, write its labels there, draw its tiles.

    Args:
        annotation: Whether every candidate is built, or only the reviewed crops.
        force: Whether to build the candidates from nothing; the reviewed crops are.

    Returns:
        build: Where the build goes, whether from nothing, and the tiles it builds.
    """
    root = lavaflow_build_root(annotation)
    fresh = force or not annotation
    if fresh:
        shutil.rmtree(root, ignore_errors=True)
    labels = read_lavaflow_labels_with_verdicts(kept_only=not annotation)
    write_lavaflow_labels(labels, root)
    return LavaFlowBuild(
        root, fresh, selections_holding_lavaflow_tracks(read_selection(), labels)
    )


def build_lavaflow_dataset(
    settings: BuildSettings, annotation: bool, force: bool
) -> int:
    """Build the lava flow dataset here, the candidates or the reviewed crops.

    Args:
        settings: The settled choices for the build.
        annotation: Whether every candidate is built, or only the reviewed crops.
        force: Whether to build the candidates from nothing; the reviewed crops are.

    Returns:
        code: A process exit code, non zero when any product failed to build.
    """
    build = prepared_lavaflow_build(annotation, force)
    return runner.build_dataset(
        settings, build.selections, build.fresh, root=build.root
    )
