import pathlib
import subprocess

repo_root = pathlib.Path(__file__).resolve().parent

raise SystemExit(subprocess.call(["pytest", "-q"], cwd=str(repo_root)))
