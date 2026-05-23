import tkinter as tk
from tkinter import ttk

# ── Bảng màu toàn app ─────────────────────────────────────
COLORS = {
    "bg":           "#F7F6F3",
    "surface":      "#FFFFFF",
    "border":       "#E2E0D9",
    "primary":      "#2D6A4F",
    "primary_dark": "#1B4332",
    "danger":       "#C0392B",
    "warning":      "#E67E22",
    "success":      "#27AE60",
    "text":         "#1A1A18",
    "text_muted":   "#6B6B66",
    "income":       "#1B6CA8",
    "expense":      "#C0392B",
}

FONTS = {
    "heading":  ("Georgia", 20, "bold"),
    "subhead":  ("Arial", 14, "bold"),
    "body":     ("Helvetica Neue", 11),
    "body_b":   ("Helvetica Neue", 11, "bold"),
    "small":    ("Helvetica Neue", 9),
    "mono":     ("Courier New", 11),
}

PAD = {"padx": 16, "pady": 10}


def apply_theme(root):
    """Áp dụng ttk style chung cho toàn bộ app."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"],
                    font=FONTS["body"])

    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Surface.TFrame", background=COLORS["surface"],
                    relief="flat")

    style.configure("TLabel", background=COLORS["bg"],
                    foreground=COLORS["text"], font=FONTS["body"])
    style.configure("Muted.TLabel", foreground=COLORS["text_muted"],
                    font=FONTS["small"])
    style.configure("Heading.TLabel", font=FONTS["heading"],
                    foreground=COLORS["text"])
    style.configure("Subhead.TLabel", font=FONTS["subhead"],
                    foreground=COLORS["text"])

    style.configure("TButton", background=COLORS["primary"],
                    foreground="#FFFFFF", font=FONTS["body_b"],
                    borderwidth=0, focusthickness=0, padding=(14, 8))
    style.map("TButton",
              background=[("active", COLORS["primary_dark"]),
                          ("disabled", COLORS["border"])])

    style.configure("Danger.TButton", background=COLORS["danger"])
    style.map("Danger.TButton",
              background=[("active", "#A93226")])

    style.configure("Ghost.TButton", background=COLORS["bg"],
                    foreground=COLORS["text"], relief="flat")
    style.map("Ghost.TButton",
              background=[("active", COLORS["border"])])

    style.configure("TEntry", fieldbackground=COLORS["surface"],
                    bordercolor=COLORS["border"], lightcolor=COLORS["border"],
                    darkcolor=COLORS["border"], padding=8)

    style.configure("TCombobox", fieldbackground=COLORS["surface"],
                    background=COLORS["surface"])

    style.configure("Treeview", background=COLORS["surface"],
                    fieldbackground=COLORS["surface"],
                    rowheight=32, font=FONTS["body"],
                    borderwidth=0)
    style.configure("Treeview.Heading", background=COLORS["bg"],
                    foreground=COLORS["text_muted"], font=FONTS["small"],
                    relief="flat")
    style.map("Treeview", background=[("selected", COLORS["primary"])],
              foreground=[("selected", "#FFFFFF")])

    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=COLORS["border"],
                    foreground=COLORS["text_muted"], padding=(16, 8),
                    font=FONTS["body"])
    style.map("TNotebook.Tab",
              background=[("selected", COLORS["surface"])],
              foreground=[("selected", COLORS["primary"])])

    style.configure("Horizontal.TProgressbar",
                    troughcolor=COLORS["border"],
                    background=COLORS["primary"], thickness=8)
    style.configure("Danger.Horizontal.TProgressbar",
                    troughcolor=COLORS["border"],
                    background=COLORS["danger"], thickness=8)
