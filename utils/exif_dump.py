#!/usr/bin/env python3
"""
exif_dump.py - wrapper to run ExifTool (if available) and produce a JSONL file.
This script will create input/out directories if they do not exist.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
try:
    from utils.path_utils import input_path, out_path, ensure_dir
except ModuleNotFoundError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.path_utils import input_path, out_path, ensure_dir

def build_parser():
    import platform, os
    p = argparse.ArgumentParser(prog="exif_dump")
    p.add_argument("--input", "-i", default=str(input_path()))
    p.add_argument("--out", "-o", default=str(out_path("exif_raw.jsonl")))
    # Use repo-bundled ExifTool.exe on Windows by default
    if platform.system() == "Windows":
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        default_exiftool = os.path.join(repo_root, "exiftool-13.45_64", "ExifTool.exe")
    else:
        default_exiftool = "exiftool"
    p.add_argument("--exiftool", default=default_exiftool)
    return p

def run_exiftool(input_path_str, exiftool, out_jsonl):
    inp = Path(input_path_str)
    outp = Path(out_jsonl)
    # Ensure directories exist (create if needed)
    ensure_dir(inp)
    ensure_dir(outp)
    if not inp.exists() or not inp.is_dir():
        print(f"[exif_dump] Input folder not found (created if necessary): {inp} (no files will be processed)")
        # continue — producing empty file is reasonable
    try:
        # call exiftool -j -ext webp <dir>
        p = subprocess.run([exiftool, "-j", "-ext", "webp", str(inp)], check=True, stdout=subprocess.PIPE)
        arr = json.loads(p.stdout.decode())
        with open(outp, "w", encoding="utf8") as fh:
            for obj in arr:
                json.dump(obj, fh, ensure_ascii=False)
                fh.write("\n")
        print(f"[exif_dump] Wrote {len(arr)} records to {outp}")
        return 0
    except FileNotFoundError:
        print("[exif_dump] exiftool not found on PATH; writing empty output file.")
        outp.touch()
        return 3
    except subprocess.CalledProcessError as e:
        print("[exif_dump] exiftool failed:", e)
        outp.touch()
        return 4
    except Exception as e:
        print("[exif_dump] Unexpected error:", e)
        outp.touch()
        return 5

def main(argv=None):
    args = build_parser().parse_args(argv)
    rc = run_exiftool(args.input, args.exiftool, args.out)
    return rc

if __name__ == "__main__":
    raise SystemExit(main())