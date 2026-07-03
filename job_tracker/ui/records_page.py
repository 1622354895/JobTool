import webbrowser
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, END, LEFT, X

from ..schema import OPTION_GROUPS
from .theme import FONT, page_header


class RecordsPage(ttk.Frame):
    COLUMNS = ("编号", "公司", "岗位", "方向", "日期", "状态", "渠道", "地点", "优先级", "跟进")

    def __init__(self, master, app):
        super().__init__(master, padding=24)
        self.app = app
        self.rows_by_id = {}
        self.keyword = ttk.StringVar()
        self.status = ttk.StringVar()
        self.direction = ttk.StringVar()
        self.status_filter = None
        self.direction_filter = None
        self.new_status_filter = None
        self._build()

    def _options(self):
        try:
            return self.app.store.option_groups(include_record_values=True)
        except Exception:
            return {group: list(values) for group, values in OPTION_GROUPS.items()}

    def _refresh_option_values(self):
        options = self._options()
        statuses = ["全部状态", *options["状态"]]
        directions = ["全部方向", *options["岗位方向"]]
        if self.status.get() not in statuses:
            self.status.set("全部状态")
        if self.direction.get() not in directions:
            self.direction.set("全部方向")
        if self.new_status.get() not in options["状态"]:
            self.new_status.set(options["状态"][0])
        if self.status_filter:
            self.status_filter.configure(values=statuses)
        if self.direction_filter:
            self.direction_filter.configure(values=directions)
        if self.new_status_filter:
            self.new_status_filter.configure(values=options["状态"])

    def _build(self):
        page_header(self, "投递记录", "按公司、岗位、状态或方向快速定位记录；双击任意行查看完整详情。")
        toolbar = ttk.Labelframe(self, text="筛选条件", padding=12, bootstyle="secondary")
        toolbar.pack(fill=X)
        ttk.Label(toolbar, text="关键词", font=(FONT, 9), bootstyle="secondary").pack(side=LEFT, padx=(0, 6))
        keyword_entry = ttk.Entry(toolbar, textvariable=self.keyword, width=28)
        keyword_entry.pack(side=LEFT)
        keyword_entry.bind("<Return>", lambda _event: self.refresh())
        options = self._options()
        self.status_filter = ttk.Combobox(toolbar, textvariable=self.status, values=["全部状态", *options["状态"]], width=13, state="readonly")
        self.status_filter.pack(side=LEFT, padx=8)
        self.direction_filter = ttk.Combobox(toolbar, textvariable=self.direction, values=["全部方向", *options["岗位方向"]], width=14, state="readonly")
        self.direction_filter.pack(side=LEFT)
        self.status.set("全部状态")
        self.direction.set("全部方向")
        ttk.Button(toolbar, text="搜索", command=self.refresh, bootstyle="primary").pack(side=LEFT, padx=8)
        ttk.Button(toolbar, text="重置", command=self.reset, bootstyle="secondary-outline").pack(side=LEFT)
        ttk.Button(toolbar, text="删除", command=self.delete_selected, bootstyle="danger-outline").pack(side="right")
        ttk.Button(toolbar, text="打开链接", command=self.open_link, bootstyle="info-outline").pack(side="right", padx=8)

        table = ttk.Frame(self, padding=(0, 12, 0, 0))
        table.pack(fill=BOTH, expand=True)
        self.tree = ttk.Treeview(table, columns=self.COLUMNS, show="headings", bootstyle="primary")
        for column in self.COLUMNS:
            self.tree.heading(column, text=column)
            width = 185 if column == "岗位" else 150 if column == "公司" else 105
            self.tree.column(column, width=width, anchor="w")
        y_scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview, bootstyle="round")
        x_scroll = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview, bootstyle="round")
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", self.show_detail)

        footer = ttk.Frame(self, padding=(0, 12, 0, 0))
        footer.pack(fill=X)
        ttk.Label(footer, text="所选记录状态", bootstyle="secondary").pack(side=LEFT)
        self.new_status = ttk.StringVar(value="一面" if "一面" in options["状态"] else options["状态"][0])
        self.new_status_filter = ttk.Combobox(footer, textvariable=self.new_status, values=options["状态"], width=13, state="readonly")
        self.new_status_filter.pack(side=LEFT)
        ttk.Button(footer, text="更新", command=self.update_status, bootstyle="success").pack(side=LEFT, padx=8)
        self.count_var = ttk.StringVar()
        ttk.Label(footer, textvariable=self.count_var, bootstyle="secondary").pack(side="right")

    def reset(self):
        self.keyword.set("")
        self.status.set("全部状态")
        self.direction.set("全部方向")
        self.refresh()

    def set_query(self, criteria: dict[str, object]):
        self.keyword.set(str(criteria.get("keyword", "")))
        self.status.set(str(criteria.get("status", "全部状态")))
        self.direction.set(str(criteria.get("direction", "全部方向")))
        self.refresh(extra=criteria)

    def refresh(self, extra: dict[str, object] | None = None):
        self._refresh_option_values()
        criteria = dict(extra or {})
        if self.keyword.get().strip():
            criteria["keyword"] = self.keyword.get().strip()
        if self.status.get() and self.status.get() != "全部状态":
            criteria["status"] = self.status.get()
        if self.direction.get() and self.direction.get() != "全部方向":
            criteria["direction"] = self.direction.get()
        try:
            rows = self.app.store.search(criteria)
        except Exception as exc:
            messagebox.showerror("读取失败", str(exc))
            return
        self.tree.delete(*self.tree.get_children())
        self.rows_by_id = {row["投递编号"]: row for row in rows}
        for row in rows:
            applied = row.get("投递日期")
            applied_text = applied.strftime("%Y-%m-%d") if hasattr(applied, "strftime") else str(applied or "")
            self.tree.insert("", END, iid=row["投递编号"], values=(
                row["投递编号"], row["公司名称"], row["岗位名称"], row["岗位方向"], applied_text,
                row["当前状态"], row["投递渠道"], row["工作地点"], row["优先级"], row["跟进状态"],
            ))
        self.count_var.set(f"当前显示 {len(rows)} 条记录")

    def _selected_id(self):
        selected = self.tree.selection()
        return selected[0] if selected else None

    def update_status(self):
        application_id = self._selected_id()
        if not application_id:
            messagebox.showinfo("请选择记录", "请先选择一条投递记录。")
            return
        try:
            self.app.store.update_application(application_id, {"当前状态": self.new_status.get()})
            self.app.refresh_all()
        except Exception as exc:
            messagebox.showerror("更新失败", str(exc))

    def delete_selected(self):
        application_id = self._selected_id()
        if not application_id:
            return
        row = self.rows_by_id[application_id]
        if not messagebox.askyesno("确认删除", f"确定删除“{row['公司名称']} - {row['岗位名称']}”及其跟进记录吗？"):
            return
        try:
            self.app.store.delete_application(application_id)
            self.app.refresh_all()
        except Exception as exc:
            messagebox.showerror("删除失败", str(exc))

    def open_link(self):
        application_id = self._selected_id()
        if not application_id:
            return
        url = self.rows_by_id[application_id].get("招聘链接")
        if url:
            webbrowser.open(str(url))
        else:
            messagebox.showinfo("没有链接", "该记录没有招聘链接。")

    def show_detail(self, _event=None):
        application_id = self._selected_id()
        if not application_id:
            return
        row = self.rows_by_id[application_id]
        fields = ["公司名称", "岗位名称", "岗位方向", "当前状态", "投递日期", "投递渠道", "工作地点", "优先级", "联系人", "联系方式", "薪资信息", "标签", "备注"]
        messagebox.showinfo("投递详情", "\n".join(f"{field}：{row.get(field) or '-'}" for field in fields))
