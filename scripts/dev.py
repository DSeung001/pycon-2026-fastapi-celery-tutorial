import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
API_REQUIREMENTS = PROJECT_ROOT / "api" / "requirements.txt"
WORKER_REQUIREMENTS = PROJECT_ROOT / "worker" / "requirements.txt"
DATA_ROOT = PROJECT_ROOT / "data"
WORKER_DIR = PROJECT_ROOT / "worker"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


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


def local_env() -> dict[str, str]:
    return {
        **os.environ,
        "DATA_ROOT": str(DATA_ROOT),
        "REDIS_URL": REDIS_URL,
    }


def install() -> None:
    """api + worker 의존성을 하나의 .venv에 설치"""
    if not VENV_DIR.exists():
        print("가상환경을 생성합니다.")
        run([sys.executable, "-m", "venv", VENV_DIR])

    py = get_venv_python()
    run([py, "-m", "pip", "install", "-r", API_REQUIREMENTS])
    run([py, "-m", "pip", "install", "-r", WORKER_REQUIREMENTS])
    DATA_ROOT.mkdir(parents=True, exist_ok=True)


def redis() -> None:
    """로컬용 Redis만 Docker로 기동"""
    run(["docker", "compose", "up", "-d", "redis"])


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
        env=local_env(),
    )


def worker() -> None:
    """Celery worker (로컬, cwd=worker/)"""
    install()
    run(
        [
            get_venv_python(),
            "-m",
            "celery",
            "-A",
            "app.celery_app.celery",
            "worker",
            "--loglevel=info",
        ],
        env=local_env(),
        cwd=WORKER_DIR,
    )


def docker() -> None:
    """전체 스택 (api + redis + worker)"""
    run(["docker", "compose", "up", "--build"])


def main() -> None:
    parser = argparse.ArgumentParser(description="FastAPI + Celery 튜토리얼 개발 도우미")
    parser.add_argument(
        "command",
        choices=["install", "redis", "api", "worker", "docker"],
        help="실행할 명령",
    )
    args = parser.parse_args()

    commands = {
        "install": install,
        "redis": redis,
        "api": api,
        "worker": worker,
        "docker": docker,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()