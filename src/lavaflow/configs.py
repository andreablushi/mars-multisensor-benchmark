"""Where the lava flow part writes, what a verdict can be, and its settings."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from mars_multisensor_dataset.analysis.utils.tile_group import tile_grid
from mars_multisensor_dataset.building.configs import sharad
from mars_multisensor_dataset.building.preprocessing.common import store
from mars_multisensor_dataset.common.config import load_config

from common.paths import CONFIGS_ROOT, VERSION_ROOT
from lavaflow.models import LavaFlowLabel, LavaFlowSettings

LAVAFLOW_ROOT = VERSION_ROOT / "lavaflow"
CANDIDATES_ROOT = LAVAFLOW_ROOT / "candidates"
DATASET_ROOT = LAVAFLOW_ROOT / "dataset"

LAVAFLOW_VERDICTS_PATH = LAVAFLOW_ROOT / "verdicts_lavaflow.json"

LAVAFLOW_LABELS_NAME = "lavaflow_labels.parquet"

REFLECTOR = "reflector"
NONE = "none"
UNSURE = "unsure"
KEPT_VERDICTS = (REFLECTOR, NONE)


def read_lavaflow_settings(
    workers: int | None = None, overrides: Sequence[str] = ()
) -> LavaFlowSettings:
    """Read `lavaflow.yaml` with its overrides, its build's workers unless None.

    Args:
        workers: How many products the build fetches at once, or None for the yaml's.
        overrides: Hydra overrides of the file, such as `build.name=x`.

    Returns:
        settings: Every region and its tracks, and the build of their crops.
    """
    workers_override = () if workers is None else (f"build.workers={workers}",)
    return load_config(
        "lavaflow",
        LavaFlowSettings,
        (*overrides, *workers_override),
        root=CONFIGS_ROOT,
    )


def lavaflow_build_root(annotation: bool) -> Path:
    """Return where the build is written, the candidates or the reviewed crops.

    Args:
        annotation: Whether every candidate is built, or only the reviewed crops.

    Returns:
        root: The build's root directory.
    """
    return CANDIDATES_ROOT if annotation else DATASET_ROOT


def candidate_crop_path(label: LavaFlowLabel) -> Path:
    """Return where the build of every lava flow candidate writes one crop.

    Args:
        label: The candidate crop.

    Returns:
        path: The crop's file under the candidates' build.
    """
    return CANDIDATES_ROOT / store.sample_path(
        tile_grid().tile_named(label.tile), sharad.LAYOUT.instrument, label.track
    )
