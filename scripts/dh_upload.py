#!/usr/bin/env python
"""Publish the lava flow verdicts on DigitalHub, under the current version."""

from __future__ import annotations

import argparse

import digitalhub as dh
from dhub import store
from omegaconf import OmegaConf

from common.paths import CONFIGS_ROOT
from lavaflow import paths


def main() -> int:
    """Upload the verdicts the lava flow annotation notebook wrote.

    Returns:
        code: A process exit code, zero once they are up.
    """
    argparse.ArgumentParser(description=__doc__).parse_args()
    platform = OmegaConf.load(CONFIGS_ROOT / "digitalhub.yaml")
    store.upload_folder(
        dh.get_or_create_project(platform.project),
        store.LAVAFLOW,
        paths.LAVAFLOW_ROOT,
        [paths.LAVAFLOW_VERDICTS_PATH],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
