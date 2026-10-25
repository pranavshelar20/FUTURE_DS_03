#!/usr/bin/env bash
# Reproduce the full analysis from the raw CSV
set -e
python src/01_clean.py
python src/02_analysis.py
python src/03_build_dashboard.py
