import os
from pathlib import Path

# __file__ - current python file location.
PROJECT_ROOT         = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR        = Path(os.getenv("ARTIFACTS_DIR", PROJECT_ROOT / 'artifacts')) 
FRONTEND_DIST_DIR    = Path(os.getenv("FRONTEND_DIST_DIR", PROJECT_ROOT / "frontend" / "dist"))
TOKENIZER_TYPES      = {"basic", "regex"}
