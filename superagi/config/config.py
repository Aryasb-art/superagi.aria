import os
from typing import Optional
from pathlib import Path
import yaml
from pydantic import BaseSettings

CONFIG_FILE = "config.yaml"
ROOT_DIR = os.path.dirname(Path(__file__))


class Config(BaseSettings):
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_PORT: Optional[int] = 5432
    DB_URL: Optional[str] = None
    DB_USERNAME: Optional[str] = None
    ENCRYPTION_KEY: Optional[str] = None
    ENV: Optional[str] = "DEV"
    OPENAI_API_KEY: Optional[str] = None
    PIP_NO_BINARY: Optional[str] = "1"
    PYTHON_VERSION: Optional[str] = None

    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"

    @classmethod
    def load_config(cls, config_file=CONFIG_FILE):
        config_data = {}
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f) or {}

        env_vars = dict(os.environ)
        config_data = {**config_data, **env_vars}

        return cls(**config_data)


_config_instance = Config.load_config()


def get_config(key: str, default=None):
    return getattr(_config_instance, key, default)
