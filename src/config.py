import logging
import sys
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse
import json
import os

CONFIG_FILEPATH = "../scrapper.json"

@dataclass(init=False)
class ScrapperConfig:
    url: str
    headers: Optional[list[tuple[str, str]]] = None
    cookies: Optional[list[tuple[str, str]]] = None
    proxy: Optional[str] = None
    timeout_ms: float = 5000
    interval_ms: float = 2000

    _instances: dict[str, "ScrapperConfig"] = field(default_factory=dict, init=False, repr=False)

    def __new__(cls, url: str):
        if not hasattr(cls, "_instances"):
            cls._instances = {}

        if url in cls._instances:
            return cls._instances[url]

        config_data = cls._load_config_data(url)

        instance = super().__new__(cls)
        for key, value in config_data.items():
            setattr(instance, key, value)

        cls._instances[url] = instance
        return instance

    @staticmethod
    def _load_config_data(url: str) -> dict:
        if not os.path.exists(CONFIG_FILEPATH):
            print("scrapper.json doesn't exist, loading default parameters")
            return {"url": url}

        with open(CONFIG_FILEPATH, 'r') as file:
            config: dict[str, dict] = json.load(file)

            current_config = config.get('*', {})
            for url_config in config:
                if urlparse(url).path.startswith(url_config):
                    current_config = config[url_config]
                    break

            return {"url": url, **current_config}

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )