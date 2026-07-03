from collections.abc import Iterable

from .schema import OPTION_GROUPS


OPTION_CONFIG_VERSION = "2"
OPTION_META_HEADER = "__配置版本"
OPTION_GROUP_ORDER = list(OPTION_GROUPS)

OPTION_TARGETS = {
    "状态": ("投递记录", "当前状态"),
    "岗位类型": ("投递记录", "岗位类型"),
    "岗位方向": ("投递记录", "岗位方向"),
    "投递渠道": ("投递记录", "投递渠道"),
    "优先级": ("投递记录", "优先级"),
    "记录类型": ("跟进记录", "记录类型"),
}


def clean_option_values(values: Iterable[object]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        key = text.casefold()
        if not text or key in seen:
            continue
        cleaned.append(text)
        seen.add(key)
    return cleaned


def merge_option_values(primary: Iterable[object], extras: Iterable[object]) -> list[str]:
    return clean_option_values([*primary, *extras])


def normalize_option_groups(groups: dict[str, Iterable[object]] | None = None) -> dict[str, list[str]]:
    source = groups or {}
    normalized: dict[str, list[str]] = {}
    for group in OPTION_GROUP_ORDER:
        values = clean_option_values(source.get(group, []))
        normalized[group] = values or list(OPTION_GROUPS[group])
    return normalized


def merge_with_default_options(groups: dict[str, Iterable[object]]) -> dict[str, list[str]]:
    normalized = normalize_option_groups(groups)
    for group in OPTION_GROUP_ORDER:
        normalized[group] = merge_option_values(normalized[group], OPTION_GROUPS[group])
    return normalized
