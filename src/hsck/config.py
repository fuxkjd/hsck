import json
from pathlib import Path
from typing import Any


class ConfigManager:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self._config: dict[str, Any] | None = None

    def _get_default_config(self) -> dict[str, Any]:
        return {"host": "", "image_host": "", "vod_counts": {}}

    def _load(self) -> dict[str, Any]:
        if self._config is not None:
            return self._config
        if not self.config_file.exists():
            self._config = self._get_default_config()
            return self._config
        try:
            self._config = json.loads(self.config_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._config = self._get_default_config()
        return self._config

    def flush(self):
        if self._config is None:
            return
        self.config_file.write_text(
            json.dumps(self._config, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get_saved_host(self) -> str | None:
        return self._load().get("host")

    def save_host(self, host: str):
        self._load()["host"] = host
        self.flush()

    def get_saved_vod_counts(self) -> dict[str, dict[str, int]]:
        return self._load().get("vod_counts", {})

    def save_vod_counts(self, counts: dict[str, dict[str, int]]):
        self._load()["vod_counts"] = counts
        self.flush()

    def get_saved_image_host(self) -> str | None:
        return self._load().get("image_host")

    def save_image_host(self, host: str):
        self._load()["image_host"] = host
        self.flush()
