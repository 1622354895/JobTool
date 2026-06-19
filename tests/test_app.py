from pathlib import Path

import app


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
