#!/usr/bin/env python3
"""
aiimagepipe.py - orchestrator wrapper that runs the pipeline scripts in repo root.
This version runs scripts by file path (not via packages) and uses path_utils for repo-relative locations.
It will rely on sub-scripts to create any needed directories (they now do).
"""

import argparse
import subprocess
import sys
from pathlib import Path
try:
    from utils.path_utils import script_path
except ModuleNotFoundError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.path_utils import script_path

def _resolve_script(script_name):
    script = script_path(script_name)
    if script.exists():
        return script
    utils_script = Path(__file__).resolve().parent / script_name
    if utils_script.exists():
        return utils_script
    return script


def run_script(script_name, args=None):
    args = args or []
    script = _resolve_script(script_name)
    if not script.exists():
        print(f"[aiimagepipe] script not found: {script}")
        return 2
    cmd = [sys.executable, str(script)] + args
    print(f"[aiimagepipe] running: {' '.join(cmd)}")
    return subprocess.call(cmd)

def build_parser():
    p = argparse.ArgumentParser(prog="aiimagepipe")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("ingest")
    sub.add_parser("resources")
    sub.add_parser("resolve")
    allp = sub.add_parser("all")
    allp.add_argument("--apply-schema", action="store_true", help="ask pipe_normalize to apply schema if DB missing")
    allp.add_argument("--input", help="input folder for exif_dump")
    return p

def main(argv=None):
    argv = argv or sys.argv[1:]
    p = build_parser()
    args = p.parse_args(argv)
    if args.cmd == "ingest":
        return run_script("pipe_normalize.py")
    elif args.cmd == "resources":
        return run_script("pipe_parse.py")
    elif args.cmd == "resolve":
        return run_script("pipe_resolve.py")
    elif args.cmd == "all":
        exif_args = []
        if args.input:
            exif_args.extend(["--input", args.input])
        rc = run_script("exif_dump.py", exif_args)
        if rc != 0:
            print("[aiimagepipe] exif_dump returned non-zero:", rc)
        norm_args = []
        if args.apply_schema:
            norm_args.append("--apply-schema")
        rc2 = run_script("pipe_normalize.py", norm_args)
        if rc2 != 0:
            print("[aiimagepipe] pipe_normalize returned non-zero:", rc2)
        rc3 = run_script("pipe_parse.py")
        if rc3 != 0:
            print("[aiimagepipe] pipe_parse returned non-zero:", rc3)
        rc4 = run_script("pipe_resolve.py")
        if rc4 != 0:
            print("[aiimagepipe] pipe_resolve returned non-zero:", rc4)
        return 0
    else:
        p.print_help()
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
