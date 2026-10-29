"""
core.py - minimal package entry that mirrors README usage: python -m src.TryCode
"""
import argparse
import sys
import subprocess
from pathlib import Path

def main(argv=None):
    argv = argv or sys.argv[1:]
    p = argparse.ArgumentParser(prog="TryCode")
    p.add_argument("--run", choices=["all","ingest"], default="all")
    args = p.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[2]
    pipeline = repo_root / "utils" / "aiimagepipe.py"
    if args.run == "all":
        # call top-level orchestrator
        subprocess.check_call([sys.executable, str(pipeline), "all"])
    elif args.run == "ingest":
        subprocess.check_call([sys.executable, str(pipeline), "ingest"])
