"""Small JSON persistence helpers shared by Qwerty's recruitment features."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar


T = TypeVar("T")


def load_json(path: Path, default: T) -> T:
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    temporary_path.replace(path)
