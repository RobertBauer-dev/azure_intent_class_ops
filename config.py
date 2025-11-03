"""
Project configuration and path settings.
This module provides PROJECT_ROOT for consistent path handling across the project.
The project path should be set up before importing this module.
"""
from pathlib import Path

# Project root (this file is in the project root)
PROJECT_ROOT = Path(__file__).parent.resolve()

