import ttkbootstrap as ttk

from job_tracker.ui.follow_up_page import FollowUpPage


class DummyStore:
    def search(self, criteria):
        return []

    def option_groups(self, include_record_values=False):
        return {"记录类型": ["主动跟进"]}


class DummyApp:
    store = DummyStore()

    def refresh_all(self):
        pass


def test_follow_up_tree_is_parented_by_table_frame():
    root = ttk.Window(themename="flatly")
    root.withdraw()
    try:
        page = FollowUpPage(root, DummyApp())

        assert page.tree.master is not page
    finally:
        root.destroy()
