# path_utils.py - repo-relative path helpers (creates directories when requested)
from pathlib import Path
import os

def repo_root():
    # Return the repository root (directory containing this file's parent)
    return Path(__file__).resolve().parent.parent

def input_path(*parts):
    # Use lowercase 'input' directory to match repo tree
    p = repo_root().joinpath("input", *parts)
    return p

def out_path(*parts):
    p = repo_root().joinpath("out", *parts)
    return p

def schema_path(name="schema.sql"):
    return repo_root().joinpath(name)

def script_path(name):
    return repo_root().joinpath(name)

def ensure_dir(path):
    """
    Ensure the directory for `path` exists.
    `path` can be a Path or string; if it's a file path, ensure its parent exists.
    Returns the Path object for convenience.
    """
    p = Path(path)
    # If p looks like a file (has suffix) then ensure parent, else ensure p
    target = p.parent if p.suffix else p
    target.mkdir(parents=True, exist_ok=True)
    return p

def ensure_exists(path):
    # Return True if path exists, False otherwise (does not create)
    return Path(path).exists()

def readable(path):
    p = Path(path)
    return p.exists() and p.is_file()
