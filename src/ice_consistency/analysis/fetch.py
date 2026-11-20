"""The SWIM ice consistency maps: fetched once, and read back from their archives."""

from __future__ import annotations

import io
import zipfile

import httpx
import numpy as np
import tifffile
from mars_multisensor_dataset.common.fetch.http import (
    REQUEST_TIMEOUT,
    TLS_CONTEXT,
    FetchError,
    streamed,
)

from ice_consistency.configs import ARCHIVES, LAYERS


def download_swim_maps(force: bool) -> None:
    """Fetch every archive the layers read come in, unless it is already on disk.

    Args:
        force: Whether to fetch them again even when they are on disk.

    Raises:
        FetchError: When a products page answers without the archive it builds.
    """
    with httpx.Client(verify=TLS_CONTEXT, timeout=REQUEST_TIMEOUT) as client:
        for path, (url, fields) in ARCHIVES.items():
            if path.exists() and not force:
                continue
            # The page zips the layers asked for and redirects to where it put them
            asked = client.get(
                url, params=dict.fromkeys(fields, "True") | {"DL-Sel": "True"}
            )
            if asked.next_request is None:
                raise FetchError(f"{url} answered {asked.status_code}, no archive")
            streamed(str(asked.next_request.url), path, client=client, spans=())


def read_swim_consistency_layer(layer: str) -> np.ndarray:
    """Read one layer from the archive it comes in.

    Args:
        layer: The layer, as SWIM names it, such as "Ci_1_5".

    Returns:
        consistency: Its ice consistency, rows from 60N and columns from 180W. (R, C)
    """
    path, name = LAYERS[layer]
    with zipfile.ZipFile(path) as archive:
        return tifffile.imread(io.BytesIO(archive.read(name))).astype(np.float32)
