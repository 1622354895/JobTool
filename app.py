import sys
from pathlib import Path

import ttkbootstrap as ttk

from job_tracker.excel_builder import save_template
from job_tracker.settings import AppSettings
from job_tracker.ui.main_window import MainWindow


ROOT = Path(__file__).resolve().parent


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return ROOT


def default_excel_path() -> Path:
    return runtime_root() / "求职投递管理工具.xlsx"


def default_config_path() -> Path:
    return runtime_root() / "config.json"


def ensure_excel(settings: AppSettings) -> Path:
    configured = settings.load_excel_path()
    path = configured if configured and configured.exists() else default_excel_path()
    if not path.exists():
        save_template(path)
    settings.save_excel_path(path)
    return path


def main():
    settings = AppSettings(default_config_path())
    excel_path = ensure_excel(settings)
    root = ttk.Window(themename="flatly", title="求职投递记录助手", size=(1280, 800), minsize=(1120, 740))
    MainWindow(root, excel_path, settings)
    root.mainloop()


if __name__ == "__main__":
    main()
