"""Every config file of the benchmark, read through Hydra into the model it settles."""

from __future__ import annotations

from collections.abc import Sequence

from mars_multisensor_dataset.common.config import load_config

from common.paths import CONFIGS_ROOT
from ice_consistency.models import SwimSettings
from lavaflow.models import LavaFlowSettings


def ice_consistency_settings() -> SwimSettings:
    """Read `ice_consistency.yaml`."""
    return load_config("ice_consistency", SwimSettings, root=CONFIGS_ROOT)


def lavaflow_settings(
    workers: int | None = None, overrides: Sequence[str] = ()
) -> LavaFlowSettings:
    """Read `lavaflow.yaml` with its overrides, its build's workers unless None."""
    workers_override = () if workers is None else (f"build.workers={workers}",)
    return load_config(
        "lavaflow",
        LavaFlowSettings,
        (*overrides, *workers_override),
        root=CONFIGS_ROOT,
    )
