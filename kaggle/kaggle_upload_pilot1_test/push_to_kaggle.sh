#!/usr/bin/env bash
# Push the Pilot 1 TEST notebook to Kaggle.
# Set KAGGLE_USERNAME and KAGGLE_KEY before running, and update
# kernel-metadata.json with your real Kaggle username.
set -euo pipefail

if [[ -z "${KAGGLE_USERNAME:-}" || -z "${KAGGLE_KEY:-}" ]]; then
  echo "ERROR: Set KAGGLE_USERNAME and KAGGLE_KEY environment variables."
  exit 1
fi

python -m pip install --quiet kaggle
kaggle kernels push -p "$(dirname "$0")"
