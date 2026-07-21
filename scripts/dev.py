import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
API_REQUIREMENTS = PROJECT_ROOT / "api" / "requirements.txt"


def run(command: list[str], *, env=None, cwd: Path | None = None) -> None:
    """subprocess로 명령어 실행"""
    print(f"\n> {' '.join(map(str, command))}")
    subprocess.run(
        [str(arg) for arg in command],
        cwd=str(cwd or PROJECT_ROOT),
        env=env,
        check=True,
    )


def get_venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def install() -> None:
    """api 의존성을 .venv에 설치"""
    if not VENV_DIR.exists():
        print("가상환경을 생성합니다.")
        run([sys.executable, "-m", "venv", VENV_DIR])

    py = get_venv_python()
    run([py, "-m", "pip", "install", "-r", API_REQUIREMENTS])


def api() -> None:
    """FastAPI (로컬)"""
    install()
    run(
        [
            get_venv_python(),
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            "api",
            "--reload",
        ],
        env=os.environ.copy(),
    )


def docker() -> None:
    """API만 Docker로 기동"""
    run(["docker", "compose", "up", "--build"])


def main() -> None:
    parser = argparse.ArgumentParser(description="FastAPI 튜토리얼 개발 도우미")
    parser.add_argument(
        "command",
        choices=["install", "api", "docker"],
        help="실행할 명령",
    )
    args = parser.parse_args()

    commands = {
        "install": install,
        "api": api,
        "docker": docker,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
