import os
import subprocess
import sys
from pathlib import Path

def test_bridgebot_main_imports_without_pythonpath_hack():
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, "-c", "import bridgebot.main"],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def assert_main_reached_terminal_hand(stdout):
    assert "The declarer" in stdout or "The hand was passed out" in stdout


def test_bridgebot_main_runs_as_module_without_pythonpath_hack():
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, "-m", "bridgebot.main"],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert_main_reached_terminal_hand(result.stdout)


def test_bridgebot_main_runs_as_script_without_pythonpath_hack():
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, "bridgebot/main.py"],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert_main_reached_terminal_hand(result.stdout)
