from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, LEFT, X, Y

from ..excel_store import ExcelStore
from ..settings import AppSettings
from .dashboard_page import DashboardPage
from .follow_up_page import FollowUpPage
from .message_page import MessagePage
from .records_page import RecordsPage
from .settings_page import SettingsPage
from .theme import COLORS, FONT


class MainWindow(ttk.Frame):
    def __init__(self, root, excel_path: Path, settings: AppSettings):
        super().__init__(root)
        self.root = root
        self.settings = settings
        self.store = ExcelStore(excel_path)
        self.pages = {}
        self.nav_buttons = {}
        self.pack(fill=BOTH, expand=True)
        self._configure_styles()
        self._build()
        self.show_page("message")

    def _configure_styles(self):
        style = ttk.Style()
        style.configure("TLabel", font=(FONT, 10))
        style.configure("TButton", font=(FONT, 10), padding=(12, 8))
        style.configure("Treeview", font=(FONT, 9), rowheight=32, borderwidth=0)
        style.configure("Treeview.Heading", font=(FONT, 9, "bold"), padding=9)
        style.configure("TNotebook.Tab", font=(FONT, 10, "bold"), padding=(18, 9))
        style.configure("TLabelframe.Label", font=(FONT, 10, "bold"))

    def _build(self):
        sidebar = ttk.Frame(self, width=220, padding=(18, 24), bootstyle="dark")
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="求职投递\n记录助手", font=(FONT, 18, "bold"), foreground="white", background=COLORS["navy"]).pack(anchor="w", pady=(0, 8))
        ttk.Label(sidebar, text="记录 · 跟进 · 复盘", font=(FONT, 9), foreground="#B8CBD9", background=COLORS["navy"]).pack(anchor="w", pady=(0, 28))
        nav = [
            ("message", "录入岗位"), ("records", "投递记录"), ("follow", "跟进中心"),
            ("dashboard", "数据看板"), ("settings", "文件设置"),
        ]
        for key, label in nav:
            button = ttk.Button(sidebar, text=label, command=lambda name=key: self.show_page(name), bootstyle="secondary", width=20)
            button.pack(fill=X, pady=5)
            self.nav_buttons[key] = button
        self.file_var = ttk.StringVar(value=self.store.path.name)
        ttk.Label(sidebar, text="当前数据文件", foreground="#7FA0B8", background=COLORS["navy"], font=(FONT, 8)).pack(side="bottom", anchor="w", pady=(0, 4))
        ttk.Label(sidebar, textvariable=self.file_var, wraplength=175, foreground="#DCE8F0", background=COLORS["navy"], font=(FONT, 8)).pack(side="bottom", anchor="w")

        self.content = ttk.Frame(self, bootstyle="light")
        self.content.pack(side=LEFT, fill=BOTH, expand=True)
        self.pages = {
            "message": MessagePage(self.content, self),
            "records": RecordsPage(self.content, self),
            "follow": FollowUpPage(self.content, self),
            "dashboard": DashboardPage(self.content, self),
            "settings": SettingsPage(self.content, self),
        }
        for page in self.pages.values():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_page(self, name: str):
        page = self.pages[name]
        page.tkraise()
        if hasattr(page, "refresh"):
            page.refresh()
        for key, button in self.nav_buttons.items():
            button.configure(bootstyle="primary" if key == name else "secondary")

    def show_records(self, criteria: dict[str, object]):
        self.pages["records"].set_query(criteria)
        self.show_page("records")

    def refresh_all(self):
        for key in ("records", "follow", "dashboard"):
            self.pages[key].refresh()

    def set_workbook(self, path: Path):
        store = ExcelStore(path)
        store.search({})
        self.store = store
        self.settings.save_excel_path(path)
        self.file_var.set(path.name)
        self.refresh_all()
