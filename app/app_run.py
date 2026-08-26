import sys
from pathlib import Path
import uvicorn

# Adds the project root to Python's import search path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api.routes import create_app

app = create_app()

def main() -> None:
    uvicorn.run(
        "app.app_run:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT / "app")],
    )


if __name__ == "__main__":
    main()
