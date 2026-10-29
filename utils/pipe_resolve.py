def norm_kind(kind):
    if kind in ("model", "ckpt", "checkpoint"):
        return "checkpoint"
    if kind in ("lora", "locon", "lycoris"):
        return "lora"
    if kind in ("embedding", "textualinversion"):
        return "embedding"
    if kind in ("vae", "controlnet", "upscaler"):
        return kind
    return None
#!/usr/bin/env python3
"""
pipe_resolve.py - resolve resource refs in the resources table.
Default DB path is out/images.db. Parent directories will be created if missing.
"""

import argparse
import sqlite3
from pathlib import Path
try:
    from utils.path_utils import out_path, ensure_dir
except ModuleNotFoundError:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.path_utils import out_path, ensure_dir

def build_parser():
    p = argparse.ArgumentParser(prog="pipe_resolve")
    p.add_argument("--db", default=str(out_path("images.db")))
    p.add_argument("--rewrite", action="store_true", help="compat flag; not used in stub")
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)
    dbp = Path(args.db)
    ensure_dir(dbp)
    if not dbp.exists():
        print(f"[pipe_resolve] DB not found: {dbp}. Run pipe_normalize first.")
        return 2
    conn = sqlite3.connect(str(dbp))
    cur = conn.cursor()
    cur.execute("UPDATE resources SET kind='resolved' WHERE kind='resource_ref'")
    updated = conn.total_changes
    conn.commit()
    conn.close()
    print(f"[pipe_resolve] Marked resource_ref rows as resolved (approx changes: {updated})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())