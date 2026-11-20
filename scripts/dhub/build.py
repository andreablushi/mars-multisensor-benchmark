"""Building one lava flow dataset on DigitalHub, published a checkpoint at a time."""

from __future__ import annotations

import os
from collections.abc import Sequence
from functools import partial
from pathlib import Path

from mars_multisensor_dataset.analysis.selector.models.selection import Selection
from mars_multisensor_dataset.building import paths, runner
from mars_multisensor_dataset.building.models.settings import BuildSettings
from mars_multisensor_dataset.common.console import PLAIN_LOG_ENV

from dhub import store


def checkpoint(project, name: str, base: Path, root: Path, uploads: int):
    """Publish the dataset as it stands, then delete the crops it sent from disk.

    Args:
        project: The DigitalHub project the dataset is logged into.
        name: The folder the dataset is published in.
        base: The directory the folder's keys are taken relative to.
        root: The dataset's own root directory, inside the base.
        uploads: How many crops are sent at once.

    Returns:
        dataset: The published folder.
    """
    crops = paths.crop_paths(root)
    print(f"CHECKPOINT UPLOADING AND CLEANING {len(crops):,} crops", flush=True)
    # Whatever sits beside the crops describes them, so it goes up after them
    index = sorted(one for one in root.iterdir() if one.is_file())
    dataset = store.upload_folder(project, name, base, crops, index, uploads)
    for crop in crops:
        crop.unlink()
    return dataset


def fetch_build(
    project, workers: int, build: str, into: Path, names: Sequence[str]
) -> None:
    """Bring the named objects of one published dataset build back into a directory."""
    store.download_folder(project, f"dataset-{build}", into, names, workers)


def published_build(
    project,
    name: str,
    base: Path,
    root: Path,
    settings: BuildSettings,
    picked: Sequence[Selection],
    force: bool,
):
    """Build one dataset on DigitalHub into a subfolder, and publish what it left.

    Args:
        project: The DigitalHub project the dataset is logged into.
        name: The folder the dataset is published in.
        base: The directory the folder's keys are taken relative to.
        root: Where the build is written, a subfolder of the base.
        settings: The settled choices for the build, sized as the job was.
        picked: The tiles to build, each with the observations it keeps.
        force: Whether to build from nothing rather than fill in what is missing.

    Returns:
        dataset: The published folder.

    Raises:
        RuntimeError: When a product failed.
    """
    os.environ[PLAIN_LOG_ENV] = "1"
    subfolder = root.relative_to(base).as_posix()
    # A job starts on an empty disk, so only the index of what is built comes down
    if not force:
        store.download_folder(
            project, name, root, paths.INDEX_NAMES, subfolder=subfolder
        )
    print(f"building the dataset as {settings.name}", flush=True)
    published = partial(checkpoint, project, name, base, root, settings.workers)
    fetch = partial(fetch_build, project, settings.workers)
    failed = runner.build_dataset(settings, picked, force, published, fetch, root)
    dataset = published()
    if failed:
        raise RuntimeError(
            "the build had failures; what was published holds what finished"
        )
    print("done", flush=True)
    return dataset
