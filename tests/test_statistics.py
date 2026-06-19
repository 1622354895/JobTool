from datetime import date

from job_tracker.statistics import calculate_metrics, pending_follow_ups


def test_metrics_use_real_denominators():
    rows = [
        {"投递日期": date(2026, 6, 18), "当前状态": "已投递", "岗位方向": "Agent开发", "投递渠道": "官网", "优先级": "高"},
        {"投递日期": date(2026, 6, 18), "当前状态": "一面", "岗位方向": "Java后端", "投递渠道": "内推", "优先级": "中"},
        {"投递日期": date(2026, 6, 17), "当前状态": "Offer", "岗位方向": "Agent开发", "投递渠道": "官网", "优先级": "高"},
    ]
    metrics = calculate_metrics(rows, today=date(2026, 6, 18))
    assert metrics["total"] == 3
    assert metrics["interview_count"] == 2
    assert metrics["offer_count"] == 1
    assert metrics["interview_rate"] == 2 / 3
    assert metrics["by_priority"] == {"高": 2, "中": 1}


def test_empty_metrics_are_zero_safe():
    metrics = calculate_metrics([], today=date(2026, 6, 18))
    assert metrics["interview_rate"] == 0
    assert metrics["offer_rate"] == 0


def test_pending_follow_ups_prioritize_overdue_and_exclude_finished():
    rows = [
        {"投递编号": "3", "公司名称": "未来公司", "岗位名称": "Agent", "当前状态": "已投递", "下次跟进日期": date(2026, 6, 22)},
        {"投递编号": "1", "公司名称": "逾期公司", "岗位名称": "Java", "当前状态": "一面", "下次跟进日期": date(2026, 6, 17)},
        {"投递编号": "2", "公司名称": "今日公司", "岗位名称": "算法", "当前状态": "笔试中", "下次跟进日期": date(2026, 6, 18)},
        {"投递编号": "4", "公司名称": "结束公司", "岗位名称": "测试", "当前状态": "Offer", "下次跟进日期": date(2026, 6, 16)},
        {"投递编号": "5", "公司名称": "无计划公司", "岗位名称": "产品", "当前状态": "已投递", "下次跟进日期": None},
    ]

    result = pending_follow_ups(rows, today=date(2026, 6, 18), limit=3)

    assert [row["投递编号"] for row in result] == ["1", "2", "3"]
    assert [row["待办状态"] for row in result] == ["已逾期", "今日跟进", "未来安排"]
