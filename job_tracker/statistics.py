from collections import Counter
from datetime import date, datetime, timedelta


INTERVIEW_STATES = {"一面", "二面", "终面", "等待结果", "Offer"}
REPLIED_STATES = {"初筛沟通", "笔试中", *INTERVIEW_STATES}


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def pending_follow_ups(rows: list[dict[str, object]], today: date | None = None, limit: int = 8) -> list[dict[str, object]]:
    today = today or date.today()
    finished_states = {"Offer", "已拒绝", "已结束"}
    pending = []
    for row in rows:
        follow_date = _as_date(row.get("下次跟进日期"))
        if not isinstance(follow_date, date) or row.get("当前状态") in finished_states:
            continue
        item = dict(row)
        item["下次跟进日期"] = follow_date
        item["待办状态"] = "已逾期" if follow_date < today else "今日跟进" if follow_date == today else "未来安排"
        pending.append(item)
    pending.sort(key=lambda item: (item["下次跟进日期"], str(item.get("公司名称", "")), str(item.get("岗位名称", ""))))
    return pending[:max(limit, 0)]


def calculate_metrics(rows: list[dict[str, object]], today: date | None = None) -> dict[str, object]:
    today = today or date.today()
    total = len(rows)
    statuses = [str(row.get("当前状态", "")) for row in rows]
    dates = [_as_date(row.get("投递日期")) for row in rows]
    week_start = today - timedelta(days=today.weekday())
    interview_count = sum(status in INTERVIEW_STATES for status in statuses)
    offer_count = statuses.count("Offer")
    replied_count = sum(status in REPLIED_STATES for status in statuses)
    return {
        "total": total,
        "week_count": sum(isinstance(value, date) and week_start <= value <= today for value in dates),
        "month_count": sum(isinstance(value, date) and value.year == today.year and value.month == today.month for value in dates),
        "interview_count": interview_count,
        "offer_count": offer_count,
        "reply_rate": replied_count / total if total else 0,
        "interview_rate": interview_count / total if total else 0,
        "offer_rate": offer_count / total if total else 0,
        "by_status": Counter(statuses),
        "by_direction": Counter(str(row.get("岗位方向", "其他")) for row in rows),
        "by_channel": Counter(str(row.get("投递渠道", "未填写")) for row in rows),
        "by_priority": Counter(str(row.get("优先级", "未填写")) for row in rows),
    }
