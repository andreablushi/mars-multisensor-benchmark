"""The review: every candidate crop of a region beside its cluttergram, to judge."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from functools import partial
from html import escape

import ipywidgets as widgets
import numpy as np
from mars_multisensor_dataset.analysis.utils.tile_group import tile_grid
from mars_multisensor_dataset.building.configs import sharad
from mars_multisensor_dataset.building.preprocessing.common import store
from mars_multisensor_dataset.building.preprocessing.sharad.window import (
    FEWEST_ROWS,
    rows_below_atmosphere,
)
from mars_multisensor_dataset.visualization import panels
from mars_multisensor_dataset.visualization.labelled import TileStepper
from mars_multisensor_dataset.visualization.training_qualitative.preprocessing import (
    shown_crop,
    shown_range,
)
from matplotlib.figure import Figure

from lavaflow.analysis.artifacts import write_lavaflow_verdicts
from lavaflow.configs import candidate_crop_path
from lavaflow.models import LavaFlowLabel
from lavaflow.visualization import config


def crop_review_widget(
    labels: Sequence[LavaFlowLabel], verdicts: dict[str, str]
) -> widgets.Widget:
    """Step through every candidate crop of a region, track by track, to judge it.

    Args:
        labels: Every crop shown in the review.
        verdicts: What each reviewed crop shows, written on every verdict.

    Returns:
        review: The review's controls, note and crop, or a note when none is listed.
    """
    ranked: dict[str, list[LavaFlowLabel]] = {}
    for label in labels:
        ranked.setdefault(label.region, []).append(label)
    if not ranked:
        return panels.unavailable(config.NOTHING_LISTED)
    return CropReview(ranked, verdicts).box


def review_progress_table(
    labels: Sequence[LavaFlowLabel], verdicts: dict[str, str]
) -> widgets.Widget:
    """Tabulate every region's verdicts so far, for the paper's tracks, the rest, all.

    Args:
        labels: Every crop shown in the review.
        verdicts: What each reviewed crop shows.

    Returns:
        table: One row per region and group of tracks, each verdict counted and as
            a share of the group's crops.
    """
    rows = []
    for region in dict.fromkeys(label.region for label in labels):
        held = [label for label in labels if label.region == region]
        for group, members in (
            (config.FROM_PAPER_GROUP, [label for label in held if label.named]),
            (config.NOT_NAMED_GROUP, [label for label in held if not label.named]),
            (config.ALL_GROUP, held),
        ):
            judged = Counter(
                verdicts.get(label.crop, config.NOT_REVIEWED) for label in members
            )
            total = max(len(members), 1)
            rows.append(
                (
                    region,
                    held[0].source,
                    group,
                    f"{len({label.track for label in members}):,}",
                    f"{len({label.tile for label in members}):,}",
                    f"{len(members):,}",
                    *(
                        f"{judged[kind]:,} ({judged[kind] / total:.0%})"
                        for kind in (*config.BUTTON_STYLES, config.NOT_REVIEWED)
                    ),
                )
            )
    return panels.written("Every region, as the review leaves it", config.REVIEW, rows)


def crop_radargram_panel(label: LavaFlowLabel) -> widgets.Widget:
    """Draw one crop's radargram beside its cluttergram, from its surface down.

    Args:
        label: The candidate crop.

    Returns:
        panel: The two panels rendered, or a note when the crop is not on disk.
    """
    frame = tile_grid().tile_named(label.tile)
    path = candidate_crop_path(label)
    if not path.exists():
        return panels.unavailable(config.NOT_BUILT)
    with np.load(path) as crop:
        measured = crop[store.MEASURED]
        power = crop[sharad.LAYOUT.measurement].astype(np.float32)
        clutter = crop["clutter"].astype(np.float32)
    below = rows_below_atmosphere(power, measured)
    rows = slice(below.start, min(below.start + FEWEST_ROWS, below.stop))
    shown = (
        np.where(measured, power, np.nan),
        np.where(measured & (clutter > sharad.CLUTTER_FLOOR_DB), clutter, np.nan),
    )
    figure = Figure(figsize=config.FIGURE_SIZE, layout="constrained")
    figure.suptitle(
        f"{label.track} on {label.tile}, {frame.centre_lat:.2f}° N"
        + (config.FROM_PAPER if label.named else ""),
        fontsize=14,
    )
    for axis, values, kind in zip(
        figure.subplots(1, 2), shown, config.KINDS, strict=True
    ):
        ranged = values[rows] if np.isfinite(values[rows]).any() else values
        shown_crop(figure, axis, values, shown_range(ranged), kind, rows)
        axis.set_xlabel("Trace")
        axis.set_ylabel("Delay row")
    return panels.rendered(figure)


class CropReview(TileStepper):
    """The crops of every region, stepped through track by track and judged.

    Attributes:
        box: The review's controls, note and crop, as one widget.
    """

    def __init__(
        self, ranked: dict[str, list[LavaFlowLabel]], verdicts: dict[str, str]
    ) -> None:
        """Build the controls, the first region offered.

        Args:
            ranked: The crops of every region, each track south to north.
            verdicts: What each reviewed crop shows, written on every verdict.
        """
        self._verdicts = verdicts
        buttons = []
        for verdict, style in config.BUTTON_STYLES.items():
            button = widgets.Button(
                description=verdict.capitalize(), button_style=style
            )
            button.on_click(partial(self._judge, verdict))
            buttons.append(button)
        super().__init__(ranked, widgets.Box(), [widgets.HBox(buttons)])
        self._group.description = "Region:"
        self._tile.description = "Crop:"

    def _first(self, tiles: list[LavaFlowLabel]) -> int:
        """Return the index of the chosen region's first crop not yet reviewed.

        Args:
            tiles: The chosen region's crops, in review order.

        Returns:
            index: Its first crop with no verdict, or 0 when every one has one.
        """
        return next(
            (at for at, label in enumerate(tiles) if label.crop not in self._verdicts),
            0,
        )

    def _name(self, label: LavaFlowLabel) -> str:
        """Return what the crop picker calls one crop.

        Args:
            label: The candidate crop.

        Returns:
            name: Its track and tile, marked when the paper names the track.
        """
        return f"{label.track} on {label.tile}" + (
            config.FROM_PAPER if label.named else ""
        )

    def _drawn(self, label: LavaFlowLabel) -> widgets.Widget:
        """Draw one crop's radargram beside its cluttergram.

        Args:
            label: The candidate crop.

        Returns:
            panel: The two panels rendered.
        """
        return crop_radargram_panel(label)

    def _place(self) -> str:
        """Return the chosen crop's place and verdict, and its region's count so far.

        Returns:
            note: The note shown above the crop.
        """
        label = self._tile.value
        judged = Counter(
            self._verdicts.get(one.crop, config.NOT_REVIEWED)
            for one in self._ranked[label.region]
        )
        return (
            f"{self._tile.index + 1} of {len(self._tile.options)}, "
            f"{'named' if label.named else 'not named'} by {label.source}, "
            f"{self._verdicts.get(label.crop, config.NOT_REVIEWED)}. "
            f"{label.region}: "
            + ", ".join(
                f"{judged[held]:,} {held}"
                for held in (*config.BUTTON_STYLES, config.NOT_REVIEWED)
            )
        )

    def _judge(self, verdict: str, _button) -> None:
        """Write the verdict on the chosen crop, then move on to the next one.

        Args:
            verdict: What the crop shows.
            _button: The button clicked, unused.
        """
        self._verdicts[self._tile.value.crop] = verdict
        write_lavaflow_verdicts(self._verdicts)
        if self._tile.index + 1 < len(self._tile.options):
            self._tile.index += 1
        else:
            self._note.value = escape(self._place())
