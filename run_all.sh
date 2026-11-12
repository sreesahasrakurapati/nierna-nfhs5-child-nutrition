#!/usr/bin/env bash
# Runs the whole pipeline in order. Put the raw CSV in data/raw/ first.
set -e
cd "$(dirname "$0")/src"
python 01_cleaning.py
python 02_feature_engineering.py
python 03_eda.py
python 04_selection_pca_clusters.py
