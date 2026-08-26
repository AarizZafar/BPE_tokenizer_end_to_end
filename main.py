import subprocess
import sys
from pathlib import Path

import uvicorn

from app.api.routes import create_app


PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = create_app()


def run_command(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True, shell=sys.platform == "win32")


def build_frontend() -> None:
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        run_command(["npm", "install"], FRONTEND_DIR)
    run_command(["npm", "run", "build"], FRONTEND_DIR)


def main() -> None:
    build_frontend()
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT / "app"), str(PROJECT_ROOT / "frontend" / "src")],
    )


if __name__ == "__main__":
    main()
