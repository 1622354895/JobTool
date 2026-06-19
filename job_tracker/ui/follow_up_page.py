from datetime import date
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, END, LEFT, X

from ..models import FollowUpDraft
from ..parser import parse_date
from ..schema import LOG_TYPES
from .theme import page_header


class FollowUpPage(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=24)
        self.app = app
        self.rows_by_id = {}
        self._build()

    def _build(self):
        page_header(self, "跟进中心", "集中查看已逾期、今日和未来 7 天需要处理的岗位。")
        columns = ("公司", "岗位", "状态", "跟进日期", "跟进状态")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle="warning")
        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=220 if column == "岗位" else 150, anchor="w")
        table = ttk.Frame(self)
        table.pack(fill=BOTH, expand=True)
        self.tree.pack(in_=table, side=LEFT, fill=BOTH, expand=True)
        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview, bootstyle="round")
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        footer = ttk.Frame(self, padding=(0, 12, 0, 0))
        footer.pack(fill=X)
        ttk.Button(footer, text="刷新", command=self.refresh, bootstyle="secondary-outline").pack(side=LEFT)
        ttk.Button(footer, text="添加跟进记录", command=self.add_follow_up, bootstyle="primary").pack(side=LEFT, padx=8)
        self.count_var = ttk.StringVar(value="0 条待处理")
        ttk.Label(footer, textvariable=self.count_var, bootstyle="secondary").pack(side="right")

    def refresh(self):
        rows = self.app.store.search({})
        rows = [row for row in rows if row.get("跟进状态") in {"已逾期", "今日跟进", "未来7天"}]
        self.rows_by_id = {row["投递编号"]: row for row in rows}
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            follow_date = row.get("下次跟进日期")
            self.tree.insert("", END, iid=row["投递编号"], values=(
                row["公司名称"], row["岗位名称"], row["当前状态"],
                follow_date.strftime("%Y-%m-%d") if hasattr(follow_date, "strftime") else "", row["跟进状态"],
            ))
        self.count_var.set(f"{len(rows)} 条待处理")

    def add_follow_up(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("请选择记录", "请先选择一个岗位。")
            return
        application_id = selected[0]
        dialog = ttk.Toplevel(self)
        dialog.title("添加跟进记录")
        dialog.geometry("560x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=True)
        type_var = ttk.StringVar(value="主动跟进")
        ttk.Label(frame, text="记录类型").pack(anchor="w")
        ttk.Combobox(frame, textvariable=type_var, values=LOG_TYPES, state="readonly").pack(fill=X, pady=(4, 12))
        ttk.Label(frame, text="过程内容").pack(anchor="w")
        content = ttk.Text(frame, height=7, wrap="word")
        content.pack(fill=BOTH, expand=True, pady=(4, 12))
        ttk.Label(frame, text="下一步行动").pack(anchor="w")
        action_var = ttk.StringVar()
        ttk.Entry(frame, textvariable=action_var).pack(fill=X, pady=(4, 14))
        ttk.Label(frame, text="下一步日期（可选）").pack(anchor="w")
        next_date_var = ttk.StringVar()
        ttk.Entry(frame, textvariable=next_date_var).pack(fill=X, pady=(4, 4))
        ttk.Label(frame, text="支持 YYYY-MM-DD、今天、明天；填写后会同步到跟进提醒。", bootstyle="secondary").pack(anchor="w", pady=(0, 14))

        def save():
            value = content.get("1.0", END).strip()
            if not value:
                messagebox.showwarning("内容为空", "请输入跟进内容。", parent=dialog)
                return
            next_date_text = next_date_var.get().strip()
            parsed_next_date = parse_date(next_date_text, date.today()) if next_date_text else None
            if next_date_text and not parsed_next_date:
                messagebox.showwarning("日期无效", "下一步日期请使用 YYYY-MM-DD、今天或明天。", parent=dialog)
                return
            try:
                self.app.store.append_follow_up(
                    application_id,
                    FollowUpDraft(
                        record_type=type_var.get(), occurred_date=date.today(), content=value,
                        next_action=action_var.get().strip(), next_date=parsed_next_date,
                    ),
                )
                dialog.destroy()
                self.app.refresh_all()
            except Exception as exc:
                messagebox.showerror("保存失败", str(exc), parent=dialog)

        ttk.Button(frame, text="保存记录", command=save, bootstyle="success").pack(anchor="e")
