"""Project configuration and initialization"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

__all__ = ["PROJECT_ROOT"]
