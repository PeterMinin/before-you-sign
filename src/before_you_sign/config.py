from pathlib import Path
from typing import TypedDict

import yaml


class Config(TypedDict):
    GOOGLE_API_KEY: str
    log_dir: Path


def load_config(path: Path) -> Config:
    with open(path) as f:
        config = yaml.full_load(f)
    for key in Config.__required_keys__:
        if key not in config:
            raise ValueError(f"No '{key}' found in the config")
    config["log_dir"] = Path(config["log_dir"])
    return config
