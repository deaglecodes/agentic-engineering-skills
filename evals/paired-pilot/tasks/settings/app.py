"""Update a JSON settings file."""
import json
from pathlib import Path


def update_settings(path, patch):
    path = Path(path)
    current = json.loads(path.read_text()) if path.exists() else {}
    current.update(patch)
    with path.open("w") as stream:
        json.dump(current, stream, indent=2)
    return current
