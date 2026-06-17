import importlib.util
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_PATH = REPO_ROOT / "setup.py"


def load_setup_module():
    spec = importlib.util.spec_from_file_location("bridgebot_setup", SETUP_PATH)
    setup_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup_module)
    return setup_module


def test_setup_packages_include_runtime_subpackages_and_exclude_tests():
    setup_module = load_setup_module()

    assert setup_module.SETUP_KWARGS["packages"] == [
        "bridgebot",
        "bridgebot.bots",
        "bridgebot.game",
    ]


def test_setup_metadata_queries_work_without_setuptools():
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, "setup.py", "--name"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "bridgebot"


def test_setup_version_query_works_without_setuptools():
    result = subprocess.run(
        [sys.executable, "setup.py", "--version"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "0.0.1"
