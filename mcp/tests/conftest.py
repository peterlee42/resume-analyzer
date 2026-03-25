"""Pytest configuration for stable local imports in tests."""

import sys
from pathlib import Path

# Ensure the project root is importable so `tools.*` imports resolve.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
