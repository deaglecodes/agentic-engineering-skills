"""Update a JSON settings file."""
import json
import os
from pathlib import Path
import stat
import tempfile


def _merge(current, patch):
    merged = current.copy()
    for key, value in patch.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def update_settings(path, patch):
    if not isinstance(patch, dict):
        raise ValueError("Settings patch must be an object")
    path = Path(path)
    mode = None
    try:
        contents = path.read_text()
    except FileNotFoundError:
        current = {}
    else:
        current = json.loads(contents)
        mode = stat.S_IMODE(path.stat().st_mode)
    if not isinstance(current, dict):
        raise ValueError("Settings root must be an object")

    merged = _merge(current, patch)
    serialized = json.dumps(merged, indent=2, allow_nan=False)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(serialized)
        if mode is not None:
            temporary_path.chmod(mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return merged
