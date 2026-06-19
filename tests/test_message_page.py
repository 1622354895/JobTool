from job_tracker.models import ApplicationDraft, Operation, ParseResult
from job_tracker.ui.message_page import batch_duplicate_indexes, drafts_are_valid, merge_add_draft


def test_all_drafts_must_have_company_and_position():
    drafts = [
        ApplicationDraft(company="字节跳动", position="Agent开发实习生"),
        ApplicationDraft(company="", position="Java后端实习生"),
    ]

    assert drafts_are_valid(drafts) is False


def test_complete_batch_is_valid():
    drafts = [
        ApplicationDraft(company="字节跳动", position="Agent开发实习生"),
        ApplicationDraft(company="腾讯", position="大模型应用实习生"),
    ]

    assert drafts_are_valid(drafts) is True


def test_quick_form_draft_is_appended_to_existing_add_preview():
    current = ParseResult(
        operation=Operation.ADD,
        drafts=[ApplicationDraft(company="字节跳动", position="Agent开发实习生")],
    )

    result = merge_add_draft(current, ApplicationDraft(company="腾讯", position="大模型实习生"))

    assert [draft.company for draft in result.drafts] == ["字节跳动", "腾讯"]


def test_batch_duplicate_indexes_normalize_company_and_position():
    drafts = [
        ApplicationDraft(company="字节跳动", position="Agent开发实习生"),
        ApplicationDraft(company=" 字节跳动 ", position="agent开发实习生"),
        ApplicationDraft(company="腾讯", position="大模型实习生"),
    ]

    assert batch_duplicate_indexes(drafts) == {0, 1}
