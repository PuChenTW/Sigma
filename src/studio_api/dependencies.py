import os
from functools import lru_cache
from pathlib import Path

from studio_api.storage import JsonStore


def default_data_file() -> Path:
    return Path(os.environ.get("STUDIO_API_DATA_FILE", ".local/studio-api.json"))


@lru_cache
def get_store() -> JsonStore:
    return JsonStore(default_data_file())
