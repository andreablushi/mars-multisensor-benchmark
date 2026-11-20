"""The lava flow labels as written, and the review's verdict on each crop."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from mars_multisensor_dataset.common.disk import parquet
from mars_multisensor_dataset.common.disk.files import read_json, write_json

from lavaflow.configs import (
    KEPT_VERDICTS,
    LAVAFLOW_LABELS_NAME,
    LAVAFLOW_ROOT,
    LAVAFLOW_VERDICTS_PATH,
)
from lavaflow.models import LavaFlowLabel

LAVAFLOW_LABELS = parquet.schema_of(LavaFlowLabel)


def read_lavaflow_labels(root: Path = LAVAFLOW_ROOT) -> list[LavaFlowLabel]:
    """Read back every candidate crop, in the order they were written.

    Args:
        root: The directory the labels sit in, the part's own or a build's.

    Returns:
        labels: One label per track and tile.
    """
    return parquet.read_rows(
        LavaFlowLabel, LAVAFLOW_LABELS, root / LAVAFLOW_LABELS_NAME
    )


def write_lavaflow_labels(
    labels: Sequence[LavaFlowLabel], root: Path = LAVAFLOW_ROOT
) -> None:
    """Write every candidate crop down, each with the verdict it holds.

    Args:
        labels: One label per track and tile.
        root: The directory the labels are written in, the part's own or a build's.
    """
    parquet.write_rows(labels, LAVAFLOW_LABELS, root / LAVAFLOW_LABELS_NAME)


def read_lavaflow_verdicts() -> dict[str, str]:
    """Read the review's verdict on every crop, from a file the pipeline never writes.

    Returns:
        verdicts: What the review saw in each reviewed crop, by tile and track.
    """
    if not LAVAFLOW_VERDICTS_PATH.is_file():
        return {}
    return read_json(LAVAFLOW_VERDICTS_PATH)


def write_lavaflow_verdicts(verdicts: dict[str, str]) -> None:
    """Write the review's verdict on every crop, sorted by tile and track.

    Args:
        verdicts: What the review saw in each reviewed crop, by tile and track.
    """
    write_json(LAVAFLOW_VERDICTS_PATH, verdicts, indent=1, sort_keys=True)


def read_lavaflow_labels_with_verdicts(kept_only: bool) -> list[LavaFlowLabel]:
    """Read every candidate crop holding the review's verdict on it, if any.

    Args:
        kept_only: Whether to keep only the crops reviewed as one of `KEPT_VERDICTS`.

    Returns:
        labels: The candidate crops, in the order they were written.
    """
    verdicts = read_lavaflow_verdicts()
    labels = [
        replace(one, verdict=verdicts.get(one.crop)) for one in read_lavaflow_labels()
    ]
    if kept_only:
        return [one for one in labels if one.verdict in KEPT_VERDICTS]
    return labels
