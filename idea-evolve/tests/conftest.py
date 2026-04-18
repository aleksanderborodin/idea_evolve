"""Shared pytest fixtures.

Puts idea-evolve/ on sys.path so `orchestrator`, `problems._shared.*`, etc.
import cleanly from any test module.
"""

from __future__ import annotations

import sys
from pathlib import Path

IDEA_EVOLVE = Path(__file__).resolve().parent.parent
if str(IDEA_EVOLVE) not in sys.path:
    sys.path.insert(0, str(IDEA_EVOLVE))
