"""The ice labels as written: one row per tile the SWIM maps cover."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from mars_multisensor_dataset.common.disk import parquet

from ice_consistency.configs import ICE_CONSISTENCY_ROOT, ICE_LABELS_NAME
from ice_consistency.models import IceLabel

ICE_LABELS = parquet.schema_of(IceLabel)


def read_ice_labels(root: Path = ICE_CONSISTENCY_ROOT) -> list[IceLabel]:
    """Read back every tile the SWIM maps labelled, in the order they were written.

    Args:
        root: The directory the labels sit in, the grid's or the evaluation's.

    Returns:
        labels: One label per tile.
    """
    return parquet.read_rows(IceLabel, ICE_LABELS, root / ICE_LABELS_NAME)


def write_ice_labels(
    labels: Sequence[IceLabel], root: Path = ICE_CONSISTENCY_ROOT
) -> None:
    """Write every tile the SWIM maps labelled down.

    Args:
        labels: One label per tile.
        root: The directory the labels are written in, the grid's or the evaluation's.
    """
    parquet.write_rows(labels, ICE_LABELS, root / ICE_LABELS_NAME)
