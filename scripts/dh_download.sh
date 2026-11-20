#!/usr/bin/env bash
set -euo pipefail

# The project is read from this repo's platform config, the version from the dataset's
configs="$(dirname "$0")/../configs"
project="$(sed -n 's/^project: *//p' "$configs/digitalhub.yaml")"

usage() {
    cat <<'TEXT'
usage: dh_download.sh [name ...]

Brings down what the benchmark published under data/<version>, the version set in
the dataset's configs/version.yaml. With no name, ice-consistency and the lava flow
labels come down, never a build.

  ice-consistency     the SWIM maps and every ice label  -> data/<version>/ice_consistency
  lavaflow-labels     the candidate list and verdicts    -> data/<version>/lavaflow
  lavaflow-candidates every candidate crop               -> data/<version>/lavaflow/candidates
  lavaflow-dataset    the reviewed crops                 -> data/<version>/lavaflow/dataset
TEXT
}

if [[ ${1-} == -h || ${1-} == --help ]]; then
    usage
    exit 0
fi

(($#)) || set -- ice-consistency lavaflow-labels

for name in "$@"; do
    case "$name" in
        ice-consistency) call='store.download_folder(project, store.ICE_CONSISTENCY, store.ARTIFACTS[store.ICE_CONSISTENCY])' ;;
        lavaflow-labels) call='store.download_folder(project, store.LAVAFLOW, paths.LAVAFLOW_ROOT, [paths.LAVAFLOW_LABELS_NAME, paths.LAVAFLOW_VERDICTS_PATH.name])' ;;
        lavaflow-candidates) call='store.download_folder(project, store.LAVAFLOW, paths.CANDIDATES_ROOT, subfolder="candidates")' ;;
        lavaflow-dataset) call='store.download_folder(project, store.LAVAFLOW, paths.DATASET_ROOT, subfolder="dataset")' ;;
        *)
            echo "nothing is published under \`$name\`" >&2
            usage >&2
            exit 1
            ;;
    esac
    (cd "$(dirname "$0")" && uv run --group digitalhub python -c \
        "import sys, digitalhub as dh; from dhub import store; from lavaflow import paths
project = dh.get_or_create_project(sys.argv[1]); $call" "$project")
done
