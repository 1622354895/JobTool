import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, X

from ..manual import USER_MANUAL_TEXT
from .theme import FONT


def show_help_dialog(parent):
    dialog = ttk.Toplevel(parent)
    dialog.title("使用帮助")
    dialog.geometry("780x680")
    dialog.minsize(680, 560)
    dialog.transient(parent.winfo_toplevel())
    dialog.grab_set()

    body = ttk.Frame(dialog, padding=18)
    body.pack(fill=BOTH, expand=True)
    ttk.Label(body, text="使用帮助", font=(FONT, 18, "bold"), bootstyle="dark").pack(anchor="w", pady=(0, 10))

    text_frame = ttk.Frame(body)
    text_frame.pack(fill=BOTH, expand=True)
    text = ttk.Text(text_frame, wrap="word", font=(FONT, 10), padx=12, pady=12)
    text.insert("1.0", USER_MANUAL_TEXT)
    text.configure(state="disabled")
    scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview, bootstyle="round")
    text.configure(yscrollcommand=scroll.set)
    text.pack(side="left", fill=BOTH, expand=True)
    scroll.pack(side="right", fill="y")

    actions = ttk.Frame(body, padding=(0, 12, 0, 0))
    actions.pack(fill=X)
    ttk.Button(actions, text="关闭", command=dialog.destroy, bootstyle="primary", width=12).pack(side="right")
    return dialog
