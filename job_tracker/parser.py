import re
from datetime import date, datetime, timedelta

from .classifier import RULES, classify_direction
from .models import ApplicationDraft, FollowUpDraft, Operation, ParseResult
from .schema import CHANNELS, CITIES, DIRECTIONS, JOB_TYPES, PRIORITIES, STATUSES


FIELD_ALIASES = {
    "公司": "company", "公司名称": "company", "岗位": "position", "职位": "position",
    "日期": "applied_date", "投递日期": "applied_date", "投递时间": "applied_date",
    "状态": "status", "进度": "status", "岗位类型": "job_type", "方向": "direction",
    "岗位方向": "direction", "渠道": "channel", "地点": "location", "城市": "location",
    "优先级": "priority", "截止日期": "deadline", "跟进日期": "next_follow_up",
    "下次跟进": "next_follow_up", "联系人": "contact", "联系方式": "contact_info",
    "简历版本": "resume_version", "薪资": "salary", "链接": "url", "网址": "url",
    "标签": "tags", "备注": "notes",
}


def detect_operation(text: str) -> Operation:
    lowered = text.lower().strip()
    if any(word in lowered for word in ("查询", "查找", "筛选", "列出")):
        return Operation.QUERY
    if any(word in lowered for word in ("更新为", "改为", "进度为", "状态为")):
        return Operation.UPDATE
    if lowered.startswith("记录") or any(word in lowered for word in ("添加跟进", "沟通记录", "面试复盘")):
        return Operation.FOLLOW_UP
    return Operation.ADD


def parse_date(value: str, today: date) -> date | None:
    text = value.strip().replace(" ", "")
    relative = {"今天": today, "昨天": today - timedelta(days=1), "明天": today + timedelta(days=1)}
    if text in relative:
        return relative[text]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    match = re.search(r"(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日?", text)
    if match:
        year = int(match.group(1) or today.year)
        try:
            return date(year, int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    return None


def _scan_choice(text: str, choices: list[str]) -> str:
    for choice in sorted(choices, key=len, reverse=True):
        if choice.lower() in text.lower():
            return choice
    return ""


def _choices(options: dict[str, list[str]] | None, group: str, defaults: list[str]) -> list[str]:
    if not options:
        return defaults
    return options.get(group) or defaults


def _split_target(text: str) -> tuple[str, str]:
    cleaned = re.sub(r"^(把|记录)", "", text).strip(" ：:,，")
    if " " in cleaned:
        company, position = cleaned.split(None, 1)
        return company.strip(), position.strip()
    position_terms = [term for _, terms in RULES for term in terms] + ["后端", "算法", "测试", "产品"]
    indices = [cleaned.lower().find(term.lower()) for term in position_terms if cleaned.lower().find(term.lower()) > 0]
    if indices:
        index = min(indices)
        return cleaned[:index].strip(), cleaned[index:].strip()
    return "", cleaned


def _parse_key_value_line(line: str, today: date) -> tuple[ApplicationDraft, list[str]]:
    values: dict[str, object] = {}
    warnings: list[str] = []
    for part in re.split(r"[；;]", line):
        if not part.strip() or not re.search(r"[:：]", part):
            continue
        key, value = re.split(r"[:：]", part, maxsplit=1)
        field = FIELD_ALIASES.get(key.strip())
        if not field:
            continue
        raw = value.strip()
        if field in {"applied_date", "deadline", "next_follow_up"}:
            parsed = parse_date(raw, today)
            if parsed is None:
                warnings.append(f"无法识别日期：{raw}")
            values[field] = parsed
        else:
            values[field] = raw
    draft = ApplicationDraft(**values)
    if not draft.applied_date:
        draft.applied_date = today
        warnings.append("未提供投递日期，已使用今天")
    if not draft.direction:
        draft.direction = classify_direction(draft.position, draft.tags)
    if not draft.company:
        warnings.append("缺少公司名称")
    if not draft.position:
        warnings.append("缺少岗位名称")
    return draft, warnings


def _parse_natural_add(text: str, today: date, options: dict[str, list[str]] | None = None) -> tuple[ApplicationDraft, list[str]]:
    warnings: list[str] = []
    relative = "今天" if "今天" in text else "昨天" if "昨天" in text else "明天" if "明天" in text else ""
    applied_date = parse_date(relative, today) if relative else today
    match = re.search(r"(?:今天|昨天|明天)?\s*投(?:递)?了?\s*(.+?)的\s*(.+?)(?:[，,。]|$)", text)
    company = match.group(1).strip() if match else ""
    position = match.group(2).strip() if match else ""
    location = _scan_choice(text, CITIES)
    if location and company.endswith(location):
        company = company[:-len(location)].strip()
    if position.endswith("岗位") and len(position) > len("岗位"):
        position = position[:-len("岗位")].strip()
    if not match:
        warnings.append("无法可靠识别公司和岗位，请使用“公司：...；岗位：...”格式")
    draft = ApplicationDraft(
        company=company,
        position=position,
        applied_date=applied_date,
        status=_scan_choice(text, _choices(options, "状态", STATUSES)) or "已投递",
        job_type=_scan_choice(text, _choices(options, "岗位类型", JOB_TYPES)),
        direction=classify_direction(position, text),
        location=location,
        channel=_scan_choice(text, _choices(options, "投递渠道", CHANNELS)),
        priority="高" if re.search(r"优先级\s*高", text) else "低" if re.search(r"优先级\s*低", text) else "中",
        url=(re.search(r"https?://\S+", text).group(0).rstrip("，,。") if re.search(r"https?://\S+", text) else ""),
    )
    direction = _scan_choice(text, _choices(options, "岗位方向", DIRECTIONS))
    if direction:
        draft.direction = direction
    return draft, warnings


def _parse_query(text: str, options: dict[str, list[str]] | None = None) -> ParseResult:
    query: dict[str, object] = {}
    direction = _scan_choice(text, _choices(options, "岗位方向", DIRECTIONS))
    if direction:
        query["direction"] = direction
    else:
        for direction, _ in RULES:
            if direction in text or classify_direction(text) == direction:
                query["direction"] = direction
                break
    if "正在面试" in text or "面试中" in text:
        query["statuses"] = ["一面", "二面", "终面"]
    elif "需要跟进" in text or "待跟进" in text:
        query["follow_up_statuses"] = ["已逾期", "今日跟进"]
    else:
        status = _scan_choice(text, _choices(options, "状态", STATUSES))
        if status:
            query["status"] = status
    if "本周" in text:
        query["date_scope"] = "this_week"
    return ParseResult(operation=Operation.QUERY, query=query)


def _parse_update(text: str, today: date, options: dict[str, list[str]] | None = None) -> ParseResult:
    match = re.search(r"把(.+?)(?:更新为|改为|进度为|状态为)([^，,。]+)", text)
    warnings: list[str] = []
    if not match:
        return ParseResult(operation=Operation.UPDATE, warnings=["无法识别需要更新的岗位"])
    company, position = _split_target(match.group(1))
    status = _scan_choice(match.group(2), _choices(options, "状态", STATUSES)) or match.group(2).strip()
    if not company or not position:
        warnings.append("无法可靠识别目标公司和岗位")
    changes: dict[str, object] = {"status": status}
    date_match = re.search(r"(?:面试时间|时间)(?:是|为)?\s*([^，,。]+)", text)
    if date_match:
        parsed = parse_date(date_match.group(1), today)
        if parsed:
            changes["next_follow_up"] = parsed
    return ParseResult(
        operation=Operation.UPDATE,
        target={"company": company, "position": position},
        changes=changes,
        warnings=warnings,
    )


def _parse_follow_up(text: str, today: date) -> ParseResult:
    match = re.match(r"记录(.+?)[：:]\s*(.+)", text.strip())
    if not match:
        return ParseResult(operation=Operation.FOLLOW_UP, warnings=["无法识别跟进岗位和内容"])
    company, position = _split_target(match.group(1))
    content = match.group(2).strip()
    warnings = [] if company and position else ["无法可靠识别目标公司和岗位"]
    next_action = ""
    action_match = re.search(r"下一步(.+)$", content)
    if action_match:
        next_action = action_match.group(1).strip(" ：:,，")
    return ParseResult(
        operation=Operation.FOLLOW_UP,
        target={"company": company, "position": position},
        follow_up=FollowUpDraft(
            record_type="HR沟通" if "HR" in content.upper() or "沟通" in content else "主动跟进",
            occurred_date=today if "今天" in content else today,
            content=content,
            next_action=next_action,
        ),
        warnings=warnings,
    )


def parse_message(text: str, today: date | None = None, options: dict[str, list[str]] | None = None) -> ParseResult:
    today = today or date.today()
    cleaned = text.strip()
    operation = detect_operation(cleaned)
    if operation is Operation.QUERY:
        return _parse_query(cleaned, options)
    if operation is Operation.UPDATE:
        return _parse_update(cleaned, today, options)
    if operation is Operation.FOLLOW_UP:
        return _parse_follow_up(cleaned, today)
    drafts: list[ApplicationDraft] = []
    warnings: list[str] = []
    for line_no, line in enumerate((line.strip() for line in cleaned.splitlines()), start=1):
        if not line:
            continue
        draft, line_warnings = (
            _parse_key_value_line(line, today)
            if re.search(r"(?:公司|岗位|职位)\s*[:：]", line)
            else _parse_natural_add(line, today, options)
        )
        drafts.append(draft)
        warnings.extend(f"第{line_no}行：{warning}" for warning in line_warnings)
    if not drafts:
        warnings.append("没有可解析的内容")
    return ParseResult(operation=Operation.ADD, drafts=drafts, warnings=warnings)
