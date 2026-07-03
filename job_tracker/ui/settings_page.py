import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, X

from ..excel_builder import save_template
from ..schema import OPTION_GROUPS
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
        self.option_group_var = ttk.StringVar(value="岗位方向")
        self.option_value_var = ttk.StringVar()
        self.options = {}
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
        self._build_options_panel()
        ttk.Label(self, text="隐私说明", font=(FONT, 12, "bold"), bootstyle="dark").pack(anchor="w", pady=(28, 6))
        ttk.Label(self, text="求职记录只保存在所选 Excel 和本地备份中，不会上传网络。", bootstyle="secondary").pack(anchor="w")

    def _build_options_panel(self):
        panel = ttk.Labelframe(self, text="选项管理", padding=18, bootstyle="secondary")
        panel.pack(fill=BOTH, expand=True, pady=(18, 0))
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(1, weight=1)
        ttk.Label(panel, text="选项类型", font=(FONT, 9), bootstyle="secondary").grid(row=0, column=0, sticky="w", padx=(0, 10))
        group_box = ttk.Combobox(
            panel,
            textvariable=self.option_group_var,
            values=list(OPTION_GROUPS),
            state="readonly",
            width=14,
        )
        group_box.grid(row=1, column=0, sticky="new", padx=(0, 14))
        group_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_option_values())

        self.option_tree = ttk.Treeview(panel, columns=("值",), show="headings", height=7, bootstyle="primary")
        self.option_tree.heading("值", text="当前选项")
        self.option_tree.column("值", width=260, anchor="w")
        self.option_tree.grid(row=1, column=1, sticky="nsew")
        self.option_tree.bind("<<TreeviewSelect>>", self.load_selected_option)
        scroll = ttk.Scrollbar(panel, orient="vertical", command=self.option_tree.yview, bootstyle="round")
        scroll.grid(row=1, column=2, sticky="ns")
        self.option_tree.configure(yscrollcommand=scroll.set)

        editor = ttk.Frame(panel)
        editor.grid(row=1, column=3, sticky="new", padx=(14, 0))
        ttk.Label(editor, text="选项名称", font=(FONT, 9), bootstyle="secondary").pack(anchor="w")
        ttk.Entry(editor, textvariable=self.option_value_var, width=22).pack(fill=X, pady=(4, 10))
        ttk.Button(editor, text="新增", command=self.add_option, bootstyle="success-outline").pack(fill=X)
        ttk.Button(editor, text="重命名", command=self.rename_option, bootstyle="primary-outline").pack(fill=X, pady=(8, 0))
        ttk.Button(editor, text="删除", command=self.delete_option, bootstyle="danger-outline").pack(fill=X, pady=(8, 0))
        ttk.Label(
            editor,
            text="修改会同步 Excel 下拉和看板；删除选项不会删除已有投递记录。",
            wraplength=190,
            font=(FONT, 8),
            bootstyle="secondary",
        ).pack(anchor="w", pady=(12, 0))
        self.refresh()

    def refresh(self):
        self.path_var.set(str(self.app.store.path))
        try:
            self.options = self.app.store.option_groups()
        except Exception:
            self.options = {group: list(values) for group, values in OPTION_GROUPS.items()}
        if self.option_group_var.get() not in self.options:
            self.option_group_var.set("岗位方向")
        self.refresh_option_values()

    def refresh_option_values(self):
        if not hasattr(self, "option_tree"):
            return
        self.option_tree.delete(*self.option_tree.get_children())
        group = self.option_group_var.get()
        for index, value in enumerate(self.options.get(group, [])):
            self.option_tree.insert("", "end", iid=str(index), values=(value,))
        self.option_value_var.set("")

    def load_selected_option(self, _event=None):
        selected = self.option_tree.selection()
        if selected:
            self.option_value_var.set(self.option_tree.item(selected[0], "values")[0])

    def _selected_option(self) -> str | None:
        selected = self.option_tree.selection()
        if not selected:
            return None
        return str(self.option_tree.item(selected[0], "values")[0])

    def _save_options(self):
        self.app.store.save_option_groups(self.options)
        self.app.refresh_all()

    def add_option(self):
        group = self.option_group_var.get()
        value = self.option_value_var.get().strip()
        if not value:
            messagebox.showwarning("名称为空", "请输入选项名称。")
            return
        if value in self.options[group]:
            messagebox.showinfo("选项已存在", "该选项已经在列表中。")
            return
        self.options[group].append(value)
        try:
            self._save_options()
        except Exception as exc:
            messagebox.showerror("保存失败", str(exc))

    def rename_option(self):
        group = self.option_group_var.get()
        old_value = self._selected_option()
        new_value = self.option_value_var.get().strip()
        if not old_value:
            messagebox.showinfo("请选择选项", "请先选择要重命名的选项。")
            return
        if not new_value:
            messagebox.showwarning("名称为空", "请输入新的选项名称。")
            return
        if old_value == new_value:
            return
        if new_value in self.options[group]:
            messagebox.showinfo("选项已存在", "新名称已经在列表中。")
            return
        try:
            self.app.store.rename_option_value(group, old_value, new_value)
            self.app.refresh_all()
        except Exception as exc:
            messagebox.showerror("保存失败", str(exc))

    def delete_option(self):
        group = self.option_group_var.get()
        value = self._selected_option()
        if not value:
            messagebox.showinfo("请选择选项", "请先选择要删除的选项。")
            return
        if len(self.options[group]) <= 1:
            messagebox.showwarning("至少保留一项", "每组选项至少需要保留一个值。")
            return
        if not messagebox.askyesno("确认删除", f"从“{group}”中删除“{value}”？已有记录中的该值会保留。"):
            return
        self.options[group] = [item for item in self.options[group] if item != value]
        try:
            self._save_options()
        except Exception as exc:
            messagebox.showerror("保存失败", str(exc))

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
