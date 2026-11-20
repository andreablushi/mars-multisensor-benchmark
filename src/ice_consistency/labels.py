"""The ice labels as written: one row per tile the SWIM maps cover."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from mars_multisensor_dataset.common.disk import parquet

from ice_consistency import paths
from ice_consistency.models import IceLabel

ICE_LABELS = parquet.schema_of(IceLabel)


def read_ice_labels(root: Path = paths.ICE_CONSISTENCY_ROOT) -> list[IceLabel]:
    """Read back every tile the SWIM maps labelled, in the order they were written."""
    return parquet.read_rows(IceLabel, ICE_LABELS, root / paths.ICE_LABELS_NAME)


def write_ice_labels(
    labels: Sequence[IceLabel], root: Path = paths.ICE_CONSISTENCY_ROOT
) -> None:
    """Write every tile the SWIM maps labelled down."""
    parquet.write_rows(labels, ICE_LABELS, root / paths.ICE_LABELS_NAME)
