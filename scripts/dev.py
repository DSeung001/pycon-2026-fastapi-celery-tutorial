import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS = PROJECT_ROOT / "api" / "requirements.txt"
DATA_ROOT = PROJECT_ROOT / "data"

def run(command: list[str], *, env=None) -> None:
    """subprocess로 명령어 실행"""

    print(f"\n> {' '.join(map(str, command))}")
    subprocess.run(
        [str(arg) for arg in command],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )

def get_venv_python() -> Path:
    """OS별로 가상환경 파이썬 경로 찾기"""

    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def install() -> None:
    """local 개발 환경 설정"""

    if not VENV_DIR.exists():
        print("가상환경을 생성합니다.")
        run([sys.executable, "-m", "venv", VENV_DIR])
    venv_python = get_venv_python()
    run([
        venv_python,
        "-m",
        "pip",
        "install",
        "-r",
        REQUIREMENTS,
    ])

def local() -> None:
    """local 실행 환경 설정"""

    install()
    venv_python = get_venv_python()
    # 로컬에서 실행을 위한 환경 변수 설정
    env = {**os.environ, "DATA_ROOT": str(DATA_ROOT)}

    run([
        venv_python,
        "-m",
        "uvicorn",
        "app.main:app",
        "--app-dir",
        "api",
        "--reload",
    ], env=env)


def docker() -> None:
    """docker 실행 환경 설정"""

    run([
        "docker",
        "compose",
        "up",
        "--build",
    ])

def main() -> None:
    parser = argparse.ArgumentParser(
        description="FastAPI 튜토리얼 개발 도우미"
    )
    parser.add_argument(
        "command",
        choices=["install", "local", "docker"],
        help="실행할 명령",
    )
    args = parser.parse_args()

    if args.command == "install":
        install()
    elif args.command == "local":
        local()
    elif args.command == "docker":
        docker()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()