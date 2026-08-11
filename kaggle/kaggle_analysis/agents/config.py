#!/usr/bin/env python3
from pathlib import Path

# Base directory is the parent of agents/ (i.e., kaggle_analysis/)
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / 'input'
OUTPUT_DIR = BASE_DIR / 'analysis_output'
REPORT_DIR = BASE_DIR / 'reports'

OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)
