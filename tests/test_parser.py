from datetime import date

from job_tracker.models import ApplicationDraft, FollowUpDraft, Operation, ParseResult
from job_tracker.parser import parse_message


def test_application_draft_has_safe_defaults():
    draft = ApplicationDraft(company="字节跳动", position="Agent开发实习生")
    assert draft.status == "已投递"
    assert draft.priority == "中"


def test_parse_key_value_add_message():
    result = parse_message(
        "公司：字节跳动；岗位：Agent开发实习生；日期：今天；状态：已投递；渠道：Boss直聘；地点：北京；优先级：高",
        today=date(2026, 6, 18),
    )
    draft = result.drafts[0]
    assert result.operation is Operation.ADD
    assert draft.company == "字节跳动"
    assert draft.position == "Agent开发实习生"
    assert draft.applied_date == date(2026, 6, 18)
    assert draft.direction == "Agent开发"
    assert draft.priority == "高"


def test_parse_multiple_lines_as_multiple_drafts():
    result = parse_message(
        "公司：腾讯；岗位：大模型实习；日期：今天\n公司：美团；岗位：Java后端实习；日期：昨天",
        today=date(2026, 6, 18),
    )
    assert len(result.drafts) == 2
    assert result.drafts[1].applied_date == date(2026, 6, 17)


def test_parse_common_natural_language_message():
    result = parse_message(
        "今天投了字节跳动的 Agent开发实习生，北京，Boss直聘，已投递，优先级高",
        today=date(2026, 6, 18),
    )
    draft = result.drafts[0]
    assert draft.company == "字节跳动"
    assert draft.position == "Agent开发实习生"
    assert draft.location == "北京"
    assert draft.channel == "Boss直聘"


def test_parse_natural_message_with_channel_before_action_and_city_after_company():
    result = parse_message(
        "今天通过Boss直聘投递了字节跳动北京的Agent开发实习生岗位，优先级高",
        today=date(2026, 6, 19),
    )

    draft = result.drafts[0]
    assert draft.company == "字节跳动"
    assert draft.position == "Agent开发实习生"
    assert draft.location == "北京"
    assert draft.channel == "Boss直聘"
    assert draft.priority == "高"


def test_parse_query_update_and_follow_up_messages():
    query = parse_message("查询所有Agent开发岗位", today=date(2026, 6, 18))
    assert query.operation is Operation.QUERY
    assert query.query["direction"] == "Agent开发"

    update = parse_message(
        "把字节跳动 Agent开发实习生更新为一面，面试时间是6月21日",
        today=date(2026, 6, 18),
    )
    assert update.operation is Operation.UPDATE
    assert update.target["company"] == "字节跳动"
    assert update.changes["status"] == "一面"

    follow_up = parse_message(
        "记录腾讯大模型应用实习：今天HR电话沟通，下一步等待笔试通知",
        today=date(2026, 6, 18),
    )
    assert follow_up.operation is Operation.FOLLOW_UP
    assert isinstance(follow_up.follow_up, FollowUpDraft)
    assert follow_up.follow_up.occurred_date == date(2026, 6, 18)


def test_missing_company_or_position_produces_warning():
    result = parse_message("岗位：Agent开发实习；日期：今天", today=date(2026, 6, 18))
    assert result.warnings


def test_parse_result_supports_update_fields():
    result = ParseResult(
        operation=Operation.UPDATE,
        target={"company": "腾讯"},
        changes={"status": "一面"},
    )
    assert result.changes["status"] == "一面"
