from job_tracker.manual import USER_MANUAL_TEXT


def test_manual_covers_core_user_workflows():
    required = [
        "首次使用",
        "录入岗位",
        "选项管理",
        "跟进中心",
        "数据看板",
        "备份",
        "发给别人使用",
    ]

    for section in required:
        assert section in USER_MANUAL_TEXT
