import json
from pathlib import Path

from platformdirs import user_config_dir


class AppSettings:
    def __init__(self, config_path: str | Path | None = None):
        self.config_path = Path(config_path or Path(user_config_dir("JobTracker")) / "config.json")

    def _read(self) -> dict[str, object]:
        if not self.config_path.exists():
            return {}
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, data: dict[str, object]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_excel_path(self, path: str | Path) -> None:
        data = self._read()
        data["excel_path"] = str(Path(path).resolve())
        self._write(data)

    def load_excel_path(self) -> Path | None:
        value = self._read().get("excel_path")
        return Path(str(value)) if value else None

    def save_preferences(self, **preferences: object) -> None:
        data = self._read()
        data.update(preferences)
        self._write(data)
