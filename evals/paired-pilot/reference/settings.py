import copy
import json
import os
from pathlib import Path
import stat
import tempfile


def update_settings(path, patch):
    path = Path(path)
    current = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(current, dict) or not isinstance(patch, dict):
        raise ValueError("Object required")

    def merge(old, new):
        result = copy.deepcopy(old)
        for key, value in new.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result

    result = merge(current, patch)
    serialized = json.dumps(result, indent=2, allow_nan=False)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return result
