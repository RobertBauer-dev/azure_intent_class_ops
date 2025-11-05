"""
Pytest configuration file.
This ensures the project root is in the Python path for imports.
"""
import sys
from pathlib import Path

# Add project root to Python path
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

