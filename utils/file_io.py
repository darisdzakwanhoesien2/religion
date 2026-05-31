import json
from pathlib import Path

def load_json(path):
    """
    Load JSON from a filesystem path.

    Accepts either a string path or a pathlib.Path.
    """
    with open(Path(path), "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(Path(path), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
