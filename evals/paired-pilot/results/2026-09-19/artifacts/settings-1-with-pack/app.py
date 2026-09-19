"""Update a JSON settings file."""
import json
import os
from pathlib import Path
import stat
import tempfile


def _merge(current, patch):
    merged = current.copy()
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def update_settings(path, patch):
    path = Path(path)
    if not isinstance(patch, dict):
        raise ValueError("Settings patch must be an object")
    try:
        with path.open(encoding="utf-8") as stream:
            current = json.load(stream)
            mode = stat.S_IMODE(os.fstat(stream.fileno()).st_mode)
    except FileNotFoundError:
        current = {}
        mode = None
    if not isinstance(current, dict):
        raise ValueError("Settings root must be an object")
    merged = _merge(current, patch)
    serialized = json.dumps(merged, indent=2, allow_nan=False)

    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(serialized)
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return merged
