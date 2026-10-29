def table_exists(conn, table_name):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cur.fetchone() is not None

def apply_filters(records, include_re=None, *_args):
    exclude_re = _args[0] if len(_args) > 0 else None
    min_count = _args[1] if len(_args) > 1 else None
    max_count = _args[2] if len(_args) > 2 else None
    filtered = records
    if include_re is not None:
        filtered = [r for r in filtered if include_re.search(r[0])]
    if exclude_re is not None:
        filtered = [r for r in filtered if not exclude_re.search(r[0])]
    if min_count is not None:
        filtered = [r for r in filtered if r[1] >= min_count]
    if max_count is not None:
        filtered = [r for r in filtered if r[1] <= max_count]
    return filtered
#!/usr/bin/env python3
"""
export_wildcards.py - export simple wildcard lists from DB.
Defaults: DB at out/images.db and outputs into out/.
This script will create out/ if missing.
"""
import argparse
import sqlite3
from pathlib import Path
try:
    from utils.path_utils import out_path, ensure_dir
except ModuleNotFoundError:
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.path_utils import out_path, ensure_dir

def build_parser():
    p = argparse.ArgumentParser(prog="export_wildcards")
    p.add_argument("what", choices=["tokens","resources","prompts","sql"])
    p.add_argument("--db", default=str(out_path("images.db")))
    p.add_argument("--out", default=str(out_path("wildcards.txt")))
    p.add_argument("--sql", default="")
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)
    dbp = Path(args.db)
    # Ensure output folder exists
    outp = Path(args.out)
    ensure_dir(outp)
    ensure_dir(dbp)
    if not dbp.exists():
        print(f"[export_wildcards] DB not found: {dbp}")
        return 2
    conn = sqlite3.connect(str(dbp))
    cur = conn.cursor()
    lines = []
    if args.what == "resources":
        cur.execute("SELECT DISTINCT name FROM resources")
        lines = [r[0] for r in cur.fetchall()]
    elif args.what == "sql":
        if not args.sql:
            print("[export_wildcards] --sql required for 'sql' mode")
            conn.close()
            return 4
        cur.execute(args.sql)
        lines = [str(r[0]) for r in cur.fetchall()]
    else:
        print(f"[export_wildcards] Mode {args.what} not implemented in stub.")
    conn.close()
    with open(outp, "w", encoding="utf8") as fh:
        for L in lines:
            fh.write(f"{L}\n")
    print(f"[export_wildcards] Wrote {len(lines)} lines to {outp}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
