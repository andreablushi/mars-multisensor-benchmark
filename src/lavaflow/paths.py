"""Where the lava flow part writes its labels, its verdicts and both builds."""

from __future__ import annotations

from common.paths import VERSION_ROOT

LAVAFLOW_ROOT = VERSION_ROOT / "lavaflow"
CANDIDATES_ROOT = LAVAFLOW_ROOT / "candidates"
DATASET_ROOT = LAVAFLOW_ROOT / "dataset"

LAVAFLOW_VERDICTS_PATH = LAVAFLOW_ROOT / "verdicts_lavaflow.json"

LAVAFLOW_LABELS_NAME = "lavaflow_labels.parquet"
