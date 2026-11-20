"""Where the ice consistency part writes the SWIM maps and its labels."""

from __future__ import annotations

from common.paths import VERSION_ROOT

ICE_CONSISTENCY_ROOT = VERSION_ROOT / "ice_consistency"
EVALUATION_ROOT = ICE_CONSISTENCY_ROOT / "evaluation"

SWIM_MAPS_PATH = ICE_CONSISTENCY_ROOT / "maps.zip"
SWIM_RADAR_PATH = ICE_CONSISTENCY_ROOT / "radar.zip"

ICE_LABELS_NAME = "ice_labels.parquet"
