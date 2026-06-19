from job_tracker.settings import AppSettings


def test_settings_can_save_excel_path_without_database(tmp_path):
    config = tmp_path / "config.json"
    settings = AppSettings(config)
    expected = tmp_path / "求职投递管理工具.xlsx"
    settings.save_excel_path(expected)
    assert settings.load_excel_path() == expected
