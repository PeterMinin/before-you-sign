from typing import TypedDict
from pathlib import Path

import yaml


class Config(TypedDict):
    GOOGLE_API_KEY: str


def load_config(path: Path) -> Config:
    with open(path) as f:
        config = yaml.full_load(f)
    return config
