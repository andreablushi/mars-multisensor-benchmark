"""Running one stage as a platform job, the repository's requirements installed."""

from __future__ import annotations

import importlib
import io
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

from digitalhub_runtime_python.utils.inputs import compose_inputs

UV = "/opt/nuclio/uv/uv"
DATASET_PACKAGE = "mars-multisensor-dataset"
DATASET_ROOT = Path("/shared")

STAGES = {
    "ice_consistency": "scripts.ice_consistency_pipeline:run_labels",
    "lavaflow_labels": "scripts.lavaflow_pipeline:run_labels",
    "build_lavaflow": "scripts.lavaflow_pipeline:run_build",
}


def job_parameters(
    stage: str, arguments: dict, requirements: list[str], dataset_archive: str
) -> None:
    """Name what the platform hands a job, for its runtime to compose.

    Args:
        stage: Which stage, naming its handler.
        arguments: What the stage's handler is called with.
        requirements: The repository's pinned requirements.
        dataset_archive: The dataset repository's archive, unpacked and installed.
    """


def run_installed_stage(
    project_name: str,
    run_key: str,
    stage: str,
    arguments: dict,
    requirements: list[str],
    dataset_archive: str,
) -> dict:
    """Return the outputs of one stage's handler, the requirements installed first.

    Args:
        project_name: The project, as the runtime hands a handler.
        run_key: The run, as the runtime hands a handler.
        stage: Which stage, naming its handler.
        arguments: What the stage's handler is called with.
        requirements: The repository's pinned requirements.
        dataset_archive: The dataset repository's archive, unpacked and installed
            editable in place of its pin, so its configs and data sit beside its code.

    Returns:
        outputs: What the stage's handler logged, for the run's status.
    """
    pins = [one for one in requirements if not one.startswith(DATASET_PACKAGE)]
    subprocess.run(
        [UV, "pip", "install", "--python", sys.executable, *pins], check=True
    )
    with urllib.request.urlopen(dataset_archive) as response:
        with tarfile.open(fileobj=io.BytesIO(response.read()), mode="r:gz") as archive:
            top = archive.getnames()[0].split("/")[0]
            archive.extractall(DATASET_ROOT, filter="data")
    subprocess.run(
        [UV, "pip", "install", "--python", sys.executable, "--no-deps", "-e"]
        + [str(DATASET_ROOT / top)],
        check=True,
    )
    module, name = STAGES[stage].split(":")
    stage_handler = getattr(importlib.import_module(module), name)
    composed = compose_inputs({}, arguments, False, stage_handler, project_name)
    return stage_handler(project_name, run_key, **composed)


run_installed_stage.__wrapped__ = job_parameters
