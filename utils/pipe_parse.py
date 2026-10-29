def as_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except Exception:
        return None

def classify_urn(urn):
    if "checkpoint" in urn:
        return "checkpoint"
    if "lora" in urn:
        return "lora"
    if "embedding" in urn:
        return "embedding"
    if "vae" in urn:
        return "vae"
    if "controlnet" in urn:
        return "controlnet"
    if "upscaler" in urn:
        return "upscaler"
    return None
#!/usr/bin/env python3
"""
pipe_parse.py - populate resources table from DB records.
Default DB path is out/images.db (repo-root out).
If out/ is missing, it will be created; the script requires an existing DB file.
"""

import argparse
import sqlite3
import json
from pathlib import Path
try:
    from utils.path_utils import out_path, ensure_dir
except ModuleNotFoundError:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.path_utils import out_path, ensure_dir

def _table_columns(conn, table_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {r[1] for r in rows}

def _table_exists(conn, table_name):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None

def build_parser():
    p = argparse.ArgumentParser(prog="pipe_parse")
    p.add_argument("--db", default=str(out_path("images.db")))
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)
    dbp = Path(args.db)
    # Ensure parent directories exist
    ensure_dir(dbp)
    if not dbp.exists():
        print(f"[pipe_parse] DB not found: {dbp}. Run pipe_normalize with --apply-schema first.")
        return 2
    conn = sqlite3.connect(str(dbp))
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY,
        image_id INTEGER,
        kind TEXT,
        name TEXT,
        extra_json TEXT
    )
    """)
    rows = []
    if _table_exists(conn, "images"):
        image_cols = _table_columns(conn, "images")
        if "raw_json" in image_cols:
            cur.execute("SELECT id, raw_json FROM images")
            rows = cur.fetchall()
    if not rows and _table_exists(conn, "kv"):
        kv_cols = _table_columns(conn, "kv")
        if "image_id" in kv_cols and "k" in kv_cols and "v_json" in kv_cols:
            cur.execute("SELECT image_id, v_json FROM kv WHERE k='raw_json' AND v_json IS NOT NULL")
            rows = cur.fetchall()
    if not rows:
        print("[pipe_parse] No raw JSON found in DB (images.raw_json or kv.raw_json).")
        conn.close()
        return 0
    inserted = 0
    for rid, raw in rows:
        try:
            o = json.loads(raw)
            kind = "unknown"
            name = o.get("Model") or o.get("SourceFile") or "unnamed"
            cur.execute("INSERT INTO resources (image_id, kind, name, extra_json) VALUES (?,?,?,?)",
                        (rid, kind, name, raw))
            inserted += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    print(f"[pipe_parse] Inserted {inserted} resource rows into {dbp}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
