#!/usr/bin/env python3
"""
Thin wrapper around kaggle_run_logs/v69/compare_v68_v69.py.

The canonical comparison script lives in kaggle_run_logs/v69/ because that is
where v69 outputs and the v68-vs-v69 report are stored. This wrapper preserves
the old root-level invocation path for backwards compatibility.

Usage:
    python kaggle_run_logs/compare_v68_v69.py
    python kaggle_run_logs/compare_v68_v69.py --v69-dir path/to/v69 --out-dir path/to/output
"""

import sys
from pathlib import Path

# Import the canonical script as a module.
SCRIPT_DIR = Path(__file__).resolve().parent
CANONICAL = SCRIPT_DIR / "v69" / "compare_v68_v69.py"

if not CANONICAL.exists():
    raise FileNotFoundError(
        f"Canonical comparison script not found: {CANONICAL}. "
        "Please run kaggle_run_logs/v69/compare_v68_v69.py directly."
    )

# Execute the canonical script in its own namespace so it can resolve relative paths.
sys.path.insert(0, str(CANONICAL.parent))
try:
    import compare_v68_v69  # type: ignore
    compare_v68_v69.main()
finally:
    sys.path.pop(0)
