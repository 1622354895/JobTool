from pathlib import Path

import app
import ttkbootstrap as ttk

from job_tracker.excel_builder import build_workbook
from job_tracker.settings import AppSettings
from job_tracker.ui.main_window import MainWindow


def test_packaged_app_keeps_excel_next_to_executable(monkeypatch, tmp_path):
    executable = tmp_path / "JobTracker.exe"
    monkeypatch.setattr(app.sys, "frozen", True, raising=False)
    monkeypatch.setattr(app.sys, "executable", str(executable))

    assert app.default_excel_path() == tmp_path / "求职投递管理工具.xlsx"


def test_packaged_app_keeps_config_next_to_executable(monkeypatch, tmp_path):
    executable = tmp_path / "JobTracker.exe"
    monkeypatch.setattr(app.sys, "frozen", True, raising=False)
    monkeypatch.setattr(app.sys, "executable", str(executable))

    assert app.default_config_path() == tmp_path / "config.json"


def test_main_window_can_construct_all_pages(tmp_path):
    workbook = tmp_path / "tracker.xlsx"
    build_workbook().save(workbook)
    root = ttk.Window(themename="flatly")
    root.withdraw()
    try:
        MainWindow(root, workbook, AppSettings(tmp_path / "config.json"))
    finally:
        root.destroy()
