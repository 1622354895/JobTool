import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import X

from ..excel_builder import save_template
from .theme import FONT, page_header


def open_path(path: Path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


class SettingsPage(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=24)
        self.app = app
        self.path_var = ttk.StringVar(value=str(app.store.path))
        self._build()

    def _build(self):
        page_header(self, "文件设置", "选择 Excel 数据文件、创建新工作簿或打开自动备份。")
        panel = ttk.Labelframe(self, text="当前数据文件", padding=18, bootstyle="secondary")
        panel.pack(fill=X)
        ttk.Entry(panel, textvariable=self.path_var, state="readonly").pack(fill=X, pady=(0, 14))
        actions = ttk.Frame(panel)
        actions.pack(fill=X)
        ttk.Button(actions, text="选择已有文件", command=self.choose, bootstyle="primary-outline").pack(side="left")
        ttk.Button(actions, text="新建文件", command=self.create, bootstyle="success-outline").pack(side="left", padx=8)
        ttk.Button(actions, text="打开 Excel", command=lambda: open_path(self.app.store.path), bootstyle="info-outline").pack(side="left")
        ttk.Button(actions, text="打开备份目录", command=self.open_backups, bootstyle="secondary-outline").pack(side="left", padx=8)
        ttk.Label(self, text="隐私说明", font=(FONT, 12, "bold"), bootstyle="dark").pack(anchor="w", pady=(28, 6))
        ttk.Label(self, text="求职记录只保存在所选 Excel 和本地备份中，不会上传网络。", bootstyle="secondary").pack(anchor="w")

    def choose(self):
        path = filedialog.askopenfilename(title="选择求职记录 Excel", filetypes=[("Excel 工作簿", "*.xlsx")])
        if not path:
            return
        try:
            self.app.set_workbook(Path(path))
            self.path_var.set(path)
        except Exception as exc:
            messagebox.showerror("文件不可用", str(exc))

    def create(self):
        path = filedialog.asksaveasfilename(title="创建求职记录 Excel", defaultextension=".xlsx", filetypes=[("Excel 工作簿", "*.xlsx")], initialfile="求职投递管理工具.xlsx")
        if not path:
            return
        try:
            save_template(path)
            self.app.set_workbook(Path(path))
            self.path_var.set(path)
        except Exception as exc:
            messagebox.showerror("创建失败", str(exc))

    def open_backups(self):
        self.app.store.backup_dir.mkdir(parents=True, exist_ok=True)
        open_path(self.app.store.backup_dir)
