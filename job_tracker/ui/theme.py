import ttkbootstrap as ttk


FONT = "Microsoft YaHei UI"
COLORS = {
    "navy": "#17324D",
    "blue": "#1677D2",
    "green": "#2E8B57",
    "amber": "#D78A00",
    "red": "#C83F49",
    "text": "#203040",
    "muted": "#667786",
    "surface": "#FFFFFF",
    "canvas": "#F4F7FA",
    "line": "#D9E1E8",
}


def page_header(parent, title: str, subtitle: str):
    frame = ttk.Frame(parent)
    frame.pack(fill="x", pady=(0, 18))
    ttk.Label(frame, text=title, font=(FONT, 22, "bold"), bootstyle="dark").pack(anchor="w")
    ttk.Label(frame, text=subtitle, font=(FONT, 10), bootstyle="secondary").pack(anchor="w", pady=(4, 0))
    return frame


def section_title(parent, title: str, hint: str = ""):
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=(0, 8))
    ttk.Label(row, text=title, font=(FONT, 11, "bold"), bootstyle="dark").pack(side="left")
    if hint:
        ttk.Label(row, text=hint, font=(FONT, 9), bootstyle="secondary").pack(side="left", padx=(10, 0))
    return row
