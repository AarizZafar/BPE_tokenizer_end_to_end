import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"
BACKEND_SRC_DIR = ROOT / "backend" / "src"


def run(command, cwd):
    subprocess.run(command, cwd=cwd, check=True, shell=sys.platform == "win32")


def main():
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        run(["npm", "install"], FRONTEND_DIR)

    run(["npm", "run", "build"], FRONTEND_DIR)
    run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "bpe_tokenizer.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
            "--reload",
            "--app-dir",
            str(BACKEND_SRC_DIR),
        ],
        ROOT,
    )


if __name__ == "__main__":
    main()
