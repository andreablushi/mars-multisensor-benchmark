"""Where this repo lives on disk, under the dataset version it labels."""

from __future__ import annotations

from pathlib import Path

from mars_multisensor_dataset.common.paths import VERSION

REPO_ROOT = Path(__file__).resolve().parents[2]

CONFIGS_ROOT = REPO_ROOT / "configs"
DATA_ROOT = REPO_ROOT / "data"
VERSION_ROOT = DATA_ROOT / VERSION if VERSION else DATA_ROOT
