"""Where the ice consistency part writes, the SWIM maps' constants, and its settings."""

from __future__ import annotations

from mars_multisensor_dataset.common.config import load_config

from common.paths import CONFIGS_ROOT, VERSION_ROOT
from ice_consistency.models import IceConsistencySettings

ICE_CONSISTENCY_ROOT = VERSION_ROOT / "ice_consistency"
EVALUATION_ROOT = ICE_CONSISTENCY_ROOT / "evaluation"

SWIM_MAPS_PATH = ICE_CONSISTENCY_ROOT / "maps.zip"
SWIM_RADAR_PATH = ICE_CONSISTENCY_ROOT / "radar.zip"

ICE_LABELS_NAME = "ice_labels.parquet"

LAYERS = {
    "Ci_1_5": (SWIM_MAPS_PATH, "SWIM4MIM_Ci_1_5.tif"),
    "Ci_5": (SWIM_MAPS_PATH, "SWIM4MIM_Ci_5.tif"),
    "RS": (SWIM_RADAR_PATH, "SWIM2_RS.tif"),
}

ARCHIVES = {
    SWIM_MAPS_PATH: (
        "https://swim.psi.edu/SWIM4MIMProducts.php",
        ("Ci_1_5-GeoTIFF", "Ci_5-GeoTIFF"),
    ),
    SWIM_RADAR_PATH: (
        "https://swim.psi.edu/SWIM2Products.php",
        ("C_RS-GeoTIFF",),
    ),
}

# Every map is simple cylindrical at 20 pixels a degree, from 180W and 60N.
PIXELS_PER_DEGREE = 20
WEST_LON = -180.0
NORTH_LAT = 60.0

GRID_POINTS = 11
GRID_SPACING_KM = 3.0


def read_ice_consistency_settings() -> IceConsistencySettings:
    """Read `ice_consistency.yaml` into the settings of the SWIM sampling.

    Returns:
        settings: The thresholds and the icy share every tile is labelled with.
    """
    return load_config("ice_consistency", IceConsistencySettings, root=CONFIGS_ROOT)
