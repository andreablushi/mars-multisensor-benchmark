# Benchmark ground truth for the Mars multi-sensor dataset

This repo labels the tiles of the [multi-sensor dataset](https://github.com/andreablushi/mars-multisensor-dataset) for its benchmarks. Every part reads the dataset's grid and selection, and the lava flow part builds its crops with the dataset's own builder.

- `ice_consistency`: the [SWIM](https://swim.psi.edu) ice consistency at 1 to 5 m and below 5 m, sampled on an 11 by 11 grid under every tile between 60S and 60N, and under every box of the evaluation draw.
- `lavaflow`: every SHARAD crop over a region where papers report buried lava flow reflectors, reviewed by eye, and built for the MAE.

## Setup

The dataset repo has to sit beside this one, at `../mars-multisensor-dataset`: it is installed editable from there, and its `configs/version.yaml` names the version every part writes under.

```bash
uv sync                                     # environment
uv run ruff check . && uv run ruff format . # lint, over the whole repo
```

## Running it

Each script runs here by default, or on DigitalHub with `--dh`. Run them after the dataset's selection and evaluation draw.

```bash
uv run python scripts/ice_consistency_pipeline.py            # the grid and evaluation ice labels
uv run python scripts/lavaflow_pipeline.py --labels          # list the lava flow crops
uv run python scripts/lavaflow_pipeline.py --annotation      # build every candidate, to review
uv run python scripts/lavaflow_pipeline.py                   # build the reviewed crops
```

| Flag | Script | What it does |
| --- | --- | --- |
| `--labels` | `lavaflow_pipeline.py` | list the candidate crops alone, from the dataset's coverage |
| `--annotation` | `lavaflow_pipeline.py` | build every candidate crop, rather than the reviewed ones |
| `--force` | all | fetch the SWIM maps again, or build from nothing |
| `--dh` | all | submit to DigitalHub instead of running here |
| `--ref` | all | with `--dh`, the branch, tag, or commit the platform clones |

A DigitalHub job installs `requirements.txt`, then unpacks the dataset's main branch under `/shared` and installs it editable, so the dataset finds its configs and data root. Export the requirements again whenever `uv.lock` changes:

```bash
uv export --no-hashes --no-dev --group digitalhub --no-emit-project --no-sources -o requirements.txt
```

## The lava flow build

The lava flow build holds SHARAD alone, for retrieving buried lava flow reflectors. `regions` in `configs/lavaflow.yaml` lists the regions where papers report them and the tracks each paper names. `--labels` lists one crop per track and tile of a region that the dataset selection's own admit takes (`admits.SHARAD` traces on the tile), kept by the selection or not, and flags the tracks the paper names as `named`. A crop the build cannot fill with one whole patch is emptied, as in every dataset build.

Review the candidate crops in `notebooks/annotation_lavaflow.ipynb`, which writes `data/<version>/lavaflow/verdicts_lavaflow.json`, and upload it with `dh_upload.py`. `lavaflow_pipeline.py` without `--annotation` then builds, from nothing, only the crops reviewed as reflector or none into `data/<version>/lavaflow/dataset`, with `lavaflow_labels.parquet` holding each crop's verdict and `named` flag. It deletes what that build held before, on disk or published, so an unsure crop is never fetched; run it with `--dh`, since it downloads every crop again.

## What it publishes

One artifact per part, under the dataset version, mirrored under `data/<version>/`:

| Artifact | Holds |
| --- | --- |
| `<version>-ice-consistency` | `maps.zip`, `radar.zip`, `ice_labels.parquet` of every grid tile, `evaluation/ice_labels.parquet` of every evaluation box |
| `<version>-lavaflow` | `lavaflow_labels.parquet` (the candidates), `verdicts_lavaflow.json`, `candidates/` and `dataset/` (the two SHARAD builds, each with its own `lavaflow_labels.parquet`) |

```bash
./scripts/dh_download.sh                       # ice-consistency and the lava flow labels
./scripts/dh_download.sh lavaflow-candidates   # every candidate crop, before the review
uv run --group digitalhub python scripts/dh_upload.py   # publish the lava flow verdicts
```

## Notebooks

```bash
uv sync --group notebook
uv run --group notebook jupyter lab
```

- `notebooks/ice_consistency.ipynb`: every labelled tile by the depths it is icy at, then one icy and one dry tile with the SWIM grid over them.
- `notebooks/annotation_lavaflow.ipynb`: every lava flow crop beside its cluttergram, to mark as reflector, none or unsure.
