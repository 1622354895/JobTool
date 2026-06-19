import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams

from ..statistics import calculate_metrics, pending_follow_ups
from .theme import COLORS, FONT, page_header


rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
rcParams["axes.unicode_minus"] = False


class DashboardPage(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=24)
        self.app = app
        self.metric_vars = {}
        self.pending_rows = {}
        self.canvas = None
        self._build()

    def _build(self):
        page_header(self, "数据看板", "指标从当前 Excel 实时计算，帮助你观察投递节奏和转化情况。")
        metrics_frame = ttk.Frame(self)
        metrics_frame.pack(fill="x")
        labels = [("total", "累计投递"), ("week_count", "本周投递"), ("month_count", "本月投递"), ("interview_count", "面试阶段"), ("offer_count", "Offer"), ("interview_rate", "面试转化")]
        for index, (key, label) in enumerate(labels):
            panel = ttk.Labelframe(metrics_frame, padding=12, bootstyle="secondary")
            panel.grid(row=0, column=index, sticky="ew", padx=(0, 8))
            metrics_frame.columnconfigure(index, weight=1)
            ttk.Label(panel, text=label, bootstyle="secondary", font=(FONT, 9)).pack(anchor="w")
            var = ttk.StringVar(value="0")
            self.metric_vars[key] = var
            ttk.Label(panel, textvariable=var, bootstyle="dark", font=(FONT, 18, "bold")).pack(anchor="w", pady=(5, 0))
        workspace = ttk.Frame(self, padding=(0, 18, 0, 0))
        workspace.pack(fill="both", expand=True)
        workspace.columnconfigure(0, weight=0, minsize=340)
        workspace.columnconfigure(1, weight=1)
        workspace.rowconfigure(0, weight=1)

        pending_panel = ttk.Labelframe(workspace, text="近期待办", padding=12, bootstyle="warning")
        pending_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        pending_panel.columnconfigure(0, weight=1)
        pending_panel.rowconfigure(1, weight=1)
        self.pending_count_var = ttk.StringVar(value="暂无待办")
        ttk.Label(pending_panel, textvariable=self.pending_count_var, font=(FONT, 9), bootstyle="secondary").grid(row=0, column=0, sticky="w", pady=(0, 8))
        columns = ("日期", "状态", "公司", "岗位")
        self.pending_tree = ttk.Treeview(pending_panel, columns=columns, show="headings", height=10, bootstyle="warning")
        widths = {"日期": 82, "状态": 76, "公司": 105, "岗位": 145}
        for column in columns:
            self.pending_tree.heading(column, text=column)
            self.pending_tree.column(column, width=widths[column], minwidth=60, anchor="w", stretch=column in {"公司", "岗位"})
        self.pending_tree.tag_configure("overdue", background="#FDEBEC")
        self.pending_tree.tag_configure("today", background="#FFF3D6")
        pending_scroll = ttk.Scrollbar(pending_panel, orient="vertical", command=self.pending_tree.yview, bootstyle="round")
        self.pending_tree.configure(yscrollcommand=pending_scroll.set)
        self.pending_tree.grid(row=1, column=0, sticky="nsew")
        pending_scroll.grid(row=1, column=1, sticky="ns")

        self.chart_frame = ttk.Frame(workspace)
        self.chart_frame.grid(row=0, column=1, sticky="nsew")

    def refresh(self):
        rows = self.app.store.search({})
        metrics = calculate_metrics(rows)
        for key, var in self.metric_vars.items():
            value = metrics[key]
            var.set(f"{value:.1%}" if key.endswith("rate") else str(value))
        pending = pending_follow_ups(rows, limit=20)
        self.pending_tree.delete(*self.pending_tree.get_children())
        self.pending_rows = {row["投递编号"]: row for row in pending}
        for row in pending:
            follow_date = row["下次跟进日期"]
            state = row["待办状态"]
            tag = "overdue" if state == "已逾期" else "today" if state == "今日跟进" else ""
            self.pending_tree.insert(
                "", "end", iid=row["投递编号"],
                values=(follow_date.strftime("%m-%d"), state, row.get("公司名称", ""), row.get("岗位名称", "")),
                tags=(tag,) if tag else (),
            )
        self.pending_count_var.set(f"{len(pending)} 条待处理" if pending else "暂无待办安排")

        figure = Figure(figsize=(7.2, 5.8), dpi=100, facecolor=COLORS["canvas"])
        axes = [figure.add_subplot(221), figure.add_subplot(222), figure.add_subplot(223), figure.add_subplot(224)]
        datasets = [
            (metrics["by_status"], "状态分布", COLORS["blue"]),
            (metrics["by_direction"], "岗位方向", COLORS["green"]),
            (metrics["by_channel"], "投递渠道", COLORS["amber"]),
            (metrics["by_priority"], "优先级分布", COLORS["navy"]),
        ]
        for axis, (data, title, color) in zip(axes, datasets):
            axis.set_title(title, loc="left", fontsize=11, fontweight="bold", fontfamily="Microsoft YaHei")
            axis.set_facecolor("#FFFFFF")
            axis.spines[["top", "right", "left"]].set_visible(False)
            axis.tick_params(labelsize=8)
            if data:
                axis.barh(list(data.keys()), list(data.values()), color=color, alpha=0.88)
                axis.grid(axis="x", alpha=0.15)
            else:
                axis.text(0.5, 0.5, "暂无数据", ha="center", va="center", color=COLORS["muted"], transform=axis.transAxes)
                axis.set_xticks([])
                axis.set_yticks([])
                axis.spines["bottom"].set_visible(False)
        figure.tight_layout(pad=2)
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
