# AIImageMetaPipe: Copilot Agent Instructions

## Project Architecture
- **Pipeline-based design:** Main flow is orchestrated by `aiimagepipe.py` and/or `src/TryCode/core.py`, with each stage as a separate module.
- **Stages:**
  - EXIF extraction (`exif_dump.py`)
  - Metadata normalization and DB ingestion (`pipe_normalize.py`)
  - Resource parsing (`pipe_parse.py`)
  - Reference resolution (`pipe_resolve.py`)
  - Wildcard export (`export_wildcards.py`)
- **UI:** `ui/` contains a multi-tab image browser and search interface, with robust error handling and clear labels.
- **Database:** SQLite schema in `schema.sql` is auto-applied and validated during pipeline runs.

## Developer Workflows
- **Run full pipeline:**
  - Windows: `run.cmd` or `run.ps1`
  - Linux/macOS: `python -m src.TryCode`
- **Run individual stages:**
  - `python exif_dump.py --input ./Input --out ./out/exif_raw.jsonl`
  - `python pipe_normalize.py --in ./out/exif_raw.jsonl --db ./out/images.db --schema ./schema.sql --jsonl ./out/records.jsonl --csv ./out/records.csv`
  - `python pipe_parse.py --db ./out/images.db`
  - `python pipe_resolve.py --db ./out/images.db --rewrite`
- **Testing:**
  - `python -m pytest tests` (all tests)
  - `python -m pytest tests/test_core.py -v` (core pipeline)

## Project-Specific Conventions
- **Input images:** Place in `input/` (case-insensitive, but code expects `Input/`)
- **Outputs:** All results go to `out/` (EXIF, DB, CSV, JSONL)
- **Schema:** `schema.sql` is always applied before DB writes; update this file for schema changes.
- **Path handling:** Use `path_utils.py` for all path normalization and resolution.
- **UI tabs:** Enable/disable tabs by editing `ui/main.py` (look for commented code for expansion).
- **Backup logic:** `pipe_normalize.py` includes backup/restore for robust file handling.

## Integration Points & Dependencies
- **ExifTool:** Must be installed and on PATH (`exiftool -ver` should work).
- **SQLite:** DB Browser for SQLite recommended for validation.
- **Python:** 3.10+ required; dependencies in `pyproject.toml` and `requirements.txt`.

## Cross-Component Patterns
- **All pipeline modules accept CLI arguments for input/output paths.**
- **Resource relationships:** Resolved in DB via `pipe_resolve.py`.
- **UI and pipeline are loosely coupled; UI reads from DB and image files, not from pipeline memory.**

## Key Files & Directories
- `aiimagepipe.py`, `exif_dump.py`, `pipe_normalize.py`, `pipe_parse.py`, `pipe_resolve.py`, `export_wildcards.py`, `path_utils.py`
- `src/TryCode/core.py`, `src/TryCode/__main__.py`
- `ui/` (UI logic)
- `tests/` (unit tests)
- `schema.sql` (DB schema)
- `run.cmd`, `run.ps1` (Windows entry points)

## Example: Adding a New Pipeline Stage
1. Create new module in root or `src/`
2. Import and call from `src/TryCode/core.py`
3. Add CLI interface
4. Add tests in `tests/`
5. Update `README.md` and this file

---
**For unclear or missing conventions, review `README.md` and `src/TryCode/core.py`.**
