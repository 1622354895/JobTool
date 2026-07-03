from datetime import date
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, END, LEFT, X

from ..models import ApplicationDraft, Operation, ParseResult
from ..parser import parse_date, parse_message
from ..schema import CHANNELS, DIRECTIONS, JOB_TYPES, OPTION_GROUPS, PRIORITIES, STATUSES
from .theme import FONT, page_header


def drafts_are_valid(drafts: list[ApplicationDraft]) -> bool:
    return bool(drafts) and all(draft.company.strip() and draft.position.strip() for draft in drafts)


def batch_duplicate_indexes(drafts: list[ApplicationDraft]) -> set[int]:
    grouped: dict[tuple[str, str], list[int]] = {}
    for index, draft in enumerate(drafts):
        key = (" ".join(draft.company.split()).casefold(), " ".join(draft.position.split()).casefold())
        if all(key):
            grouped.setdefault(key, []).append(index)
    return {index for indexes in grouped.values() if len(indexes) > 1 for index in indexes}


def merge_add_draft(current_result: ParseResult | None, draft: ApplicationDraft) -> ParseResult:
    if current_result and current_result.operation is Operation.ADD:
        return ParseResult(
            operation=Operation.ADD,
            drafts=[*current_result.drafts, draft],
            warnings=list(current_result.warnings),
        )
    return ParseResult(operation=Operation.ADD, drafts=[draft])


class MessagePage(ttk.Frame):
    PREVIEW_COLUMNS = ("公司", "岗位", "日期", "状态", "方向", "地点", "渠道", "优先级")

    def __init__(self, master, app):
        super().__init__(master, padding=24)
        self.app = app
        self.current_result = None
        self.option_widgets = {group: [] for group in OPTION_GROUPS}
        self.edit_vars = {name: ttk.StringVar() for name in self.PREVIEW_COLUMNS}
        self.quick_vars = {
            "公司": ttk.StringVar(), "岗位": ttk.StringVar(), "日期": ttk.StringVar(value=date.today().isoformat()),
            "状态": ttk.StringVar(value="已投递"), "类型": ttk.StringVar(), "方向": ttk.StringVar(),
            "地点": ttk.StringVar(), "渠道": ttk.StringVar(), "优先级": ttk.StringVar(value="中"),
            "链接": ttk.StringVar(), "备注": ttk.StringVar(),
        }
        self._build()

    def _option_groups(self, include_record_values: bool = False) -> dict[str, list[str]]:
        try:
            return self.app.store.option_groups(include_record_values=include_record_values)
        except Exception:
            return {group: list(values) for group, values in OPTION_GROUPS.items()}

    def _option_values(self, group: str, include_record_values: bool = False) -> list[str]:
        return self._option_groups(include_record_values=include_record_values).get(group, list(OPTION_GROUPS[group]))

    def refresh(self):
        groups = self._option_groups(include_record_values=True)
        for group, widgets in self.option_widgets.items():
            for widget in widgets:
                widget.configure(values=groups.get(group, list(OPTION_GROUPS[group])))

    def _build(self):
        page_header(self, "录入岗位", "单条记录用快速表单，批量记录或自然语言用智能消息。确认后才会写入 Excel。")

        notebook = ttk.Notebook(self, bootstyle="primary")
        notebook.pack(fill=X)
        quick_tab = ttk.Frame(notebook, padding=14)
        message_tab = ttk.Frame(notebook, padding=14)
        notebook.add(quick_tab, text="快速表单")
        notebook.add(message_tab, text="智能消息 / 批量录入")
        self._build_quick_form(quick_tab)
        self._build_message_input(message_tab)

        status_row = ttk.Frame(self, padding=(0, 12, 0, 8))
        status_row.pack(fill=X)
        self.warning_var = ttk.StringVar(value="等待录入")
        ttk.Label(status_row, textvariable=self.warning_var, font=(FONT, 9), bootstyle="secondary").pack(side=LEFT)
        self.preview_count_var = ttk.StringVar(value="0 条待确认")
        ttk.Label(status_row, textvariable=self.preview_count_var, font=(FONT, 9, "bold"), bootstyle="primary").pack(side="right")

        preview_frame = ttk.Labelframe(self, text="写入前预览", padding=12, bootstyle="secondary")
        preview_frame.pack(fill=BOTH, expand=True)
        table_frame = ttk.Frame(preview_frame)
        table_frame.pack(fill=BOTH, expand=True)
        self.tree = ttk.Treeview(table_frame, columns=self.PREVIEW_COLUMNS, show="headings", height=5, bootstyle="primary")
        widths = {"公司": 130, "岗位": 170, "日期": 88, "状态": 82, "方向": 92, "地点": 68, "渠道": 86, "优先级": 64}
        for column in self.PREVIEW_COLUMNS:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=widths[column], minwidth=55, anchor="w", stretch=column in {"公司", "岗位"})
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, bootstyle="round")
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview, bootstyle="round")
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.tag_configure("invalid", background="#FDEBEC")
        self.tree.tag_configure("duplicate", background="#FFF3D6")
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self._load_selected)

        footer = ttk.Frame(self, padding=(0, 14, 0, 0))
        footer.pack(fill=X)
        ttk.Button(footer, text="编辑选中记录", command=self.edit_selected, bootstyle="secondary-outline").pack(side=LEFT)
        ttk.Button(footer, text="清空预览", command=self.clear_preview, bootstyle="light").pack(side=LEFT, padx=8)
        self.confirm_button = ttk.Button(footer, text="确认写入 Excel", command=self.confirm, bootstyle="success", state="disabled", width=18)
        self.confirm_button.pack(side="right")

    def _build_quick_form(self, parent):
        fields = [
            ("公司", None, None), ("岗位", None, None), ("日期", None, None), ("状态", "状态", STATUSES),
            ("类型", "岗位类型", JOB_TYPES), ("方向", "岗位方向", DIRECTIONS), ("地点", None, None), ("渠道", "投递渠道", CHANNELS),
            ("优先级", "优先级", PRIORITIES), ("链接", None, None), ("备注", None, None),
        ]
        for index, (label, group, defaults) in enumerate(fields):
            field = ttk.Frame(parent)
            field.grid(row=index // 4, column=index % 4, sticky="ew", padx=(0, 12), pady=(0, 10))
            required = " *" if label in {"公司", "岗位"} else ""
            ttk.Label(field, text=label + required, font=(FONT, 9), bootstyle="secondary").pack(anchor="w", pady=(0, 3))
            if group:
                values = self._option_values(group, include_record_values=True)
                state = "readonly" if label in {"状态", "类型", "优先级"} else "normal"
                widget = ttk.Combobox(field, textvariable=self.quick_vars[label], values=values, state=state, width=16)
                self.option_widgets[group].append(widget)
            else:
                widget = ttk.Entry(field, textvariable=self.quick_vars[label], width=16)
            widget.pack(fill=X)
            parent.columnconfigure(index % 4, weight=1)
        actions = ttk.Frame(parent)
        actions.grid(row=3, column=3, sticky="e", pady=(2, 0))
        ttk.Button(actions, text="重置", command=self.reset_quick_form, bootstyle="secondary-outline").pack(side=LEFT)
        ttk.Button(actions, text="加入预览", command=self.preview_quick_form, bootstyle="primary", width=14).pack(side=LEFT, padx=(8, 0))

    def _build_message_input(self, parent):
        body = ttk.Frame(parent)
        body.pack(fill=X)
        self.input_text = ttk.Text(body, height=5, font=(FONT, 10), wrap="word", padx=12, pady=10, undo=True)
        self.input_text.pack(side=LEFT, fill=X, expand=True)
        actions = ttk.Frame(body, padding=(12, 0, 0, 0))
        actions.pack(side=LEFT, fill="y")
        ttk.Button(actions, text="解析到预览", command=self.parse, bootstyle="primary", width=14).pack(fill=X)
        ttk.Button(actions, text="查看示例", command=self.fill_example, bootstyle="info-outline", width=14).pack(fill=X, pady=(8, 0))
        ttk.Button(actions, text="清空输入", command=lambda: self.input_text.delete("1.0", END), bootstyle="secondary-outline", width=14).pack(fill=X, pady=(8, 0))
        ttk.Label(parent, text="一行一条记录；推荐格式：公司：…；岗位：…；日期：今天；状态：已投递", font=(FONT, 8), bootstyle="secondary").pack(anchor="w", pady=(8, 0))

    def preview_quick_form(self):
        parsed = parse_date(self.quick_vars["日期"].get(), date.today())
        if not parsed:
            messagebox.showerror("日期无效", "日期请使用 YYYY-MM-DD、今天、昨天或明天。")
            return
        draft = ApplicationDraft(
            company=self.quick_vars["公司"].get().strip(), position=self.quick_vars["岗位"].get().strip(),
            applied_date=parsed, status=self.quick_vars["状态"].get() or "已投递",
            job_type=self.quick_vars["类型"].get().strip(), direction=self.quick_vars["方向"].get().strip(),
            location=self.quick_vars["地点"].get().strip(), channel=self.quick_vars["渠道"].get().strip(),
            priority=self.quick_vars["优先级"].get() or "中", url=self.quick_vars["链接"].get().strip(),
            notes=self.quick_vars["备注"].get().strip(),
        )
        if not draft.company or not draft.position:
            messagebox.showwarning("信息不完整", "公司和岗位为必填项。")
            return
        if not draft.direction:
            from ..classifier import classify_direction
            draft.direction = classify_direction(draft.position, draft.tags)
        self._set_result(merge_add_draft(self.current_result, draft))
        self.reset_quick_form()

    def reset_quick_form(self):
        for name, variable in self.quick_vars.items():
            variable.set("")
        self.quick_vars["日期"].set(date.today().isoformat())
        self.quick_vars["状态"].set("已投递")
        self.quick_vars["优先级"].set("中")

    def fill_example(self):
        self.input_text.delete("1.0", END)
        self.input_text.insert("1.0", "公司：字节跳动；岗位：Agent开发实习生；日期：今天；状态：已投递；渠道：Boss直聘；地点：北京；优先级：高")

    def clear_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.current_result = None
        for variable in self.edit_vars.values():
            variable.set("")
        self.warning_var.set("等待录入")
        self.preview_count_var.set("0 条待确认")
        self.confirm_button.configure(text="确认写入 Excel", state="disabled")

    def clear(self):
        self.input_text.delete("1.0", END)
        self.clear_preview()

    def parse(self):
        text = self.input_text.get("1.0", END).strip()
        if not text:
            messagebox.showinfo("请输入信息", "请先输入求职信息。")
            return
        self._set_result(parse_message(text, options=self._option_groups(include_record_values=True)))

    def _set_result(self, result: ParseResult):
        self.current_result = result
        self.tree.delete(*self.tree.get_children())
        if result.operation is Operation.ADD:
            duplicate_indexes = batch_duplicate_indexes(result.drafts)
            for index, draft in enumerate(result.drafts):
                tags = ("invalid",) if not draft.company.strip() or not draft.position.strip() else ("duplicate",) if index in duplicate_indexes else ()
                self.tree.insert("", END, iid=str(index), values=(
                    draft.company, draft.position, draft.applied_date.isoformat() if draft.applied_date else "",
                    draft.status, draft.direction, draft.location, draft.channel, draft.priority,
                ), tags=tags)
            self.preview_count_var.set(f"{len(result.drafts)} 条待确认")
            self.confirm_button.configure(text="确认写入 Excel", state="normal" if drafts_are_valid(result.drafts) else "disabled")
            warnings = list(result.warnings)
            if duplicate_indexes:
                warnings.append(f"同批次有 {len(duplicate_indexes)} 条重复记录，已用黄色标记")
            self.warning_var.set("；".join(warnings) if warnings else "解析完成，请核对预览内容")
        elif result.operation is Operation.QUERY:
            self.preview_count_var.set("查询操作")
            self.warning_var.set("已识别为查询，将在投递记录页显示结果")
            self.confirm_button.configure(text="执行查询", state="normal")
        elif result.operation is Operation.UPDATE:
            self.preview_count_var.set("更新操作")
            self.warning_var.set("；".join(result.warnings) if result.warnings else f"更新目标：{result.target.get('company', '')} {result.target.get('position', '')}")
            self.confirm_button.configure(text="确认更新进度", state="disabled" if result.warnings else "normal")
        else:
            self.preview_count_var.set("跟进操作")
            self.warning_var.set("；".join(result.warnings) if result.warnings else f"跟进目标：{result.target.get('company', '')} {result.target.get('position', '')}")
            self.confirm_button.configure(text="确认添加跟进", state="disabled" if result.warnings else "normal")

    def _load_selected(self, _event=None):
        selected = self.tree.selection()
        if selected:
            for name, value in zip(self.PREVIEW_COLUMNS, self.tree.item(selected[0], "values")):
                self.edit_vars[name].set(value)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected or not self.current_result or self.current_result.operation is not Operation.ADD:
            messagebox.showinfo("请选择记录", "请先在预览表中选择一条记录。")
            return
        self._load_selected()
        dialog = ttk.Toplevel(self)
        dialog.title("编辑预览记录")
        dialog.geometry("620x430")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        body = ttk.Frame(dialog, padding=22)
        body.pack(fill=BOTH, expand=True)
        ttk.Label(body, text="编辑预览记录", font=(FONT, 16, "bold"), bootstyle="dark").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))
        for index, name in enumerate(self.PREVIEW_COLUMNS):
            field = ttk.Frame(body)
            field.grid(row=index // 2 + 1, column=index % 2, sticky="ew", padx=(0, 12), pady=(0, 10))
            ttk.Label(field, text=name, font=(FONT, 9), bootstyle="secondary").pack(anchor="w", pady=(0, 3))
            if name == "状态":
                widget = ttk.Combobox(field, textvariable=self.edit_vars[name], values=self._option_values("状态", include_record_values=True), state="readonly")
            elif name == "方向":
                widget = ttk.Combobox(field, textvariable=self.edit_vars[name], values=self._option_values("岗位方向", include_record_values=True))
            elif name == "渠道":
                widget = ttk.Combobox(field, textvariable=self.edit_vars[name], values=self._option_values("投递渠道", include_record_values=True))
            elif name == "优先级":
                widget = ttk.Combobox(field, textvariable=self.edit_vars[name], values=self._option_values("优先级", include_record_values=True), state="readonly")
            else:
                widget = ttk.Entry(field, textvariable=self.edit_vars[name])
            widget.pack(fill=X)
            body.columnconfigure(index % 2, weight=1)

        def save_and_close():
            if self.apply_edit(show_selection_warning=False):
                dialog.destroy()

        actions = ttk.Frame(body)
        actions.grid(row=5, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(actions, text="取消", command=dialog.destroy, bootstyle="secondary-outline").pack(side=LEFT)
        ttk.Button(actions, text="保存修改", command=save_and_close, bootstyle="primary").pack(side=LEFT, padx=(8, 0))

    def apply_edit(self, show_selection_warning=True):
        selected = self.tree.selection()
        if not selected or not self.current_result or self.current_result.operation is not Operation.ADD:
            if show_selection_warning:
                messagebox.showinfo("请选择记录", "请先在预览表中选择一条记录。")
            return False
        draft = self.current_result.drafts[int(selected[0])]
        parsed = parse_date(self.edit_vars["日期"].get(), date.today())
        if not parsed:
            messagebox.showerror("日期无效", "日期请使用 YYYY-MM-DD 格式。")
            return False
        draft.company = self.edit_vars["公司"].get().strip()
        draft.position = self.edit_vars["岗位"].get().strip()
        draft.applied_date = parsed
        draft.status = self.edit_vars["状态"].get().strip() or "已投递"
        draft.direction = self.edit_vars["方向"].get().strip() or "其他"
        draft.location = self.edit_vars["地点"].get().strip()
        draft.channel = self.edit_vars["渠道"].get().strip()
        draft.priority = self.edit_vars["优先级"].get().strip() or "中"
        self.tree.item(selected[0], values=(draft.company, draft.position, draft.applied_date.isoformat(), draft.status, draft.direction, draft.location, draft.channel, draft.priority))
        valid = drafts_are_valid(self.current_result.drafts)
        self.confirm_button.configure(state="normal" if valid else "disabled")
        self.warning_var.set("修改已应用" if valid else "仍有记录缺少公司或岗位")
        return True

    def confirm(self):
        result = self.current_result
        if not result:
            return
        try:
            if result.operation is Operation.QUERY:
                self.app.show_records(result.query)
                return
            if result.operation is Operation.ADD:
                if not drafts_are_valid(result.drafts):
                    messagebox.showwarning("信息不完整", "每条记录都必须填写公司和岗位。")
                    return
                duplicates = []
                for draft in result.drafts:
                    duplicates.extend(self.app.store.find_duplicates(draft.company, draft.position))
                batch_duplicates = batch_duplicate_indexes(result.drafts)
                duplicate_count = len(duplicates) + len(batch_duplicates)
                if duplicate_count and not messagebox.askyesno("发现重复投递", f"发现 {duplicate_count} 条相同公司和岗位记录，仍要继续写入吗？"):
                    return
                created = self.app.store.append_applications(result.drafts)
                messagebox.showinfo("写入成功", f"已向 Excel 追加 {len(created)} 条记录。")
            else:
                matches = self.app.store.search(result.target)
                if len(matches) != 1:
                    messagebox.showwarning("目标不唯一", f"匹配到 {len(matches)} 条记录，请在投递记录页选择具体记录。")
                    return
                application_id = matches[0]["投递编号"]
                if result.operation is Operation.UPDATE:
                    self.app.store.update_application(application_id, result.changes)
                    messagebox.showinfo("更新成功", "投递进度已更新。")
                else:
                    self.app.store.append_follow_up(application_id, result.follow_up)
                    messagebox.showinfo("记录成功", "跟进记录已追加。")
            self.app.refresh_all()
            self.clear_preview()
        except Exception as exc:
            messagebox.showerror("操作失败", str(exc))
