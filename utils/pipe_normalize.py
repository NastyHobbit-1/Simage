#!/usr/bin/env python3
"""
pipe_normalize.py - normalize exif_raw.jsonl into SQLite DB.
"""
import sys
import os
import json
import hashlib
import datetime
import argparse
import sqlite3
from pathlib import Path

try:
    from utils.path_utils import out_path, schema_path, ensure_dir, input_path
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.path_utils import out_path, schema_path, ensure_dir, input_path

def utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

def stable_id_for_path(path):
    # Return a stable string for a given path using sha256
    return hashlib.sha256(str(path).encode('utf-8')).hexdigest()

def sha256_file(path):
    sha256_hash = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return "dummyhash"

def is_probably_json(s):
    if not isinstance(s, str):
        return False
    s = s.strip()
    if not (s.startswith('{') or s.startswith('[')):
        return False
    try:
        json.loads(s)
        return True
    except Exception:
        return False

def safe_json_loads(s):
    try:
        return json.loads(s)
    except Exception:
        return None

def first_present(obj, keys):
    for k in keys:
        v = obj.get(k)
        if v is not None:
            return v
    return None

def clean_ws(s):
    return s.strip()

def sha256_file_backup(path):
    return sha256_file(path)

def _table_columns(conn, table_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {r[1] for r in rows}

def _table_exists(conn, table_name):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None

def _parse_size(value):
    if isinstance(value, str) and "x" in value:
        parts = value.lower().split("x", 1)
        try:
            return int(parts[0]), int(parts[1])
        except Exception:
            return None, None
    return None, None

# Defaults use repo-root input/out via path_utils (input: 'input', output DB: 'out/images.db').
# If necessary directories are missing they will be created. Use --apply-schema to create DB with schema.

def build_parser():
    p = argparse.ArgumentParser(prog="pipe_normalize")
    p.add_argument("--in", dest="infile", default=str(out_path("exif_raw.jsonl")))
    p.add_argument("--db", dest="db", default=str(out_path("images.db")))
    p.add_argument("--schema", dest="schema", default=str(schema_path()))
    p.add_argument("--apply-schema", action="store_true", help="create DB and apply schema if DB is missing")
    return p

def simple_normalize(exif_obj):
    # Minimal normalization: keep path and raw JSON
    return {
        "path": exif_obj.get("SourceFile") or exif_obj.get("FileName") or "UNKNOWN",
        "raw_json": json.dumps(exif_obj, ensure_ascii=False)
    }

def insert_simple(conn, rec):
    cur = conn.cursor()
    # create minimal table only if schema hasn't provided one
    cur.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        path TEXT,
        raw_json TEXT
    )
    """)
    cur.execute("INSERT INTO images (path, raw_json) VALUES (?, ?)", (rec["path"], rec["raw_json"]))
    conn.commit()

def insert_schema_image(conn, rec, columns):
    img_path = rec["path"]
    file_name = os.path.basename(img_path)
    ext = os.path.splitext(file_name)[1].lstrip(".").lower()
    width = rec.get("width")
    height = rec.get("height")
    raw_json = rec["raw_json"]
    row = {
        "id": stable_id_for_path(img_path),
        "source_file": img_path,
        "file_name": file_name,
        "ext": ext,
        "width": width,
        "height": height,
        "created_utc": None,
        "imported_utc": utc_now_iso(),
        "sha256": sha256_file(img_path) if os.path.exists(img_path) else None,
        "format_hint": rec.get("format_hint"),
        "raw_text_preview": raw_json[:2048],
    }
    keys = [k for k in row if k in columns]
    if not keys:
        return
    placeholders = ",".join(["?"] * len(keys))
    sql = f"INSERT OR REPLACE INTO images ({','.join(keys)}) VALUES ({placeholders})"
    conn.execute(sql, [row[k] for k in keys])

def insert_raw_json_kv(conn, rec):
    if not _table_exists(conn, "kv"):
        return
    kv_columns = _table_columns(conn, "kv")
    if "image_id" not in kv_columns or "k" not in kv_columns:
        return
    cols = [c for c in ("image_id", "k", "v_json") if c in kv_columns]
    if not cols:
        return
    sql = f"INSERT OR REPLACE INTO kv ({','.join(cols)}) VALUES ({','.join(['?'] * len(cols))})"
    values = {
        "image_id": stable_id_for_path(rec["path"]),
        "k": "raw_json",
        "v_json": rec["raw_json"],
    }
    conn.execute(sql, [values[c] for c in cols])

def main(argv=None):
    args = build_parser().parse_args(argv)
    infile = Path(args.infile)
    dbp = Path(args.db)
    schemap = Path(args.schema)
    # Ensure directories exist for input and database
    ensure_dir(infile)
    ensure_dir(dbp)
    if not infile.exists():
        print(f"[pipe_normalize] Input JSONL not found: {infile}. Run exif_dump first.")
        return 2
    if not dbp.exists():
        if args.apply_schema:
            if not schemap.exists():
                print(f"[pipe_normalize] Schema file not found at {schemap}; cannot apply schema.")
                return 3
            # create DB parent dir (already ensured) and apply schema
            conn = sqlite3.connect(str(dbp))
            with open(schemap, "r", encoding="utf8") as fh:
                conn.executescript(fh.read())
            conn.commit()
            conn.close()
            print(f"[pipe_normalize] Created DB and applied schema at {dbp}")
        else:
            print(f"[pipe_normalize] DB not found: {dbp}. Use --apply-schema to create with schema.sql")
            return 4
    conn = sqlite3.connect(str(dbp))
    columns = _table_columns(conn, "images") if _table_exists(conn, "images") else set()
    use_schema = "source_file" in columns
    inserted = 0
    with open(infile, "r", encoding="utf8") as fh:
        for ln in fh:
            if not ln.strip():
                continue
            try:
                obj = json.loads(ln)
            except Exception:
                continue
            rec = simple_normalize(obj)
            width = obj.get("ImageWidth") or obj.get("ExifImageWidth") or obj.get("Width")
            height = obj.get("ImageHeight") or obj.get("ExifImageHeight") or obj.get("Height")
            if (width is None or height is None) and obj.get("ImageSize"):
                w, h = _parse_size(obj.get("ImageSize"))
                width = width or w
                height = height or h
            rec["width"] = width
            rec["height"] = height
            rec["format_hint"] = obj.get("FileType") or obj.get("MIMEType")
            if use_schema:
                insert_schema_image(conn, rec, columns)
                insert_raw_json_kv(conn, rec)
            else:
                insert_simple(conn, rec)
            inserted += 1
    conn.commit()
    conn.close()
    print(f"[pipe_normalize] Inserted {inserted} records into {dbp}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
