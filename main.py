import tkinter as tk
from tkinter import ttk

from ui.theme import apply_theme, COLORS, FONTS
from ui.login_frame import LoginFrame
from ui.dashboard_frame import DashboardFrame
from ui.transaction_frame import AddTransactionFrame, TransactionListFrame
from ui.budget_report_frame import BudgetFrame, ReportFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quản Lý Chi Tiêu Cá Nhân")
        self.geometry("900x680")
        self.minsize(800, 600)
        self.configure(bg=COLORS["bg"])
        apply_theme(self)

        self.current_user = None
        self._show_login()

    # ── Điều hướng màn hình ───────────────────────────

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _show_login(self):
        self._clear()
        LoginFrame(self, on_login_success=self._on_login).pack(
            fill="both", expand=True)

    def _on_login(self, user):
        self.current_user = user
        self.title(f"Chi Tiêu Cá Nhân — {user.name}")
        self._show_main()

    def _show_main(self):
        self._clear()

        # ── Sidebar ──────────────────────────────────
        sidebar = tk.Frame(self, bg=COLORS["primary_dark"], width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Chi Tiêu\nCá Nhân",
                 font=FONTS["subhead"], fg="#FFFFFF",
                 bg=COLORS["primary_dark"],
                 justify="center").pack(pady=(32, 24))

        menu_items = [
            ("Dashboard",       "dashboard"),
            ("Thêm giao dịch",  "add_transaction"),
            ("Lịch sử",         "history"),
            ("Ngân sách",       "budget"),
            ("Báo cáo",         "report"),
        ]
        self._nav_btns = {}
        for label, key in menu_items:
            btn = tk.Button(
                sidebar, text=label,
                font=FONTS["body"],
                fg="#FFFFFF", bg=COLORS["primary_dark"],
                activeforeground="#FFFFFF",
                activebackground=COLORS["primary"],
                relief="flat", anchor="w",
                padx=20, pady=10,
                cursor="hand2",
                command=lambda k=key: self._navigate(k),
            )
            btn.pack(fill="x")
            self._nav_btns[key] = btn

        # Nút đăng xuất
        tk.Button(sidebar, text="Đăng xuất",
                  font=FONTS["small"],
                  fg=COLORS["border"], bg=COLORS["primary_dark"],
                  activeforeground="#FFFFFF",
                  activebackground=COLORS["danger"],
                  relief="flat", anchor="w",
                  padx=20, pady=8,
                  cursor="hand2",
                  command=self._logout).pack(side="bottom", fill="x",
                                             pady=(0, 16))

        # ── Content area ─────────────────────────────
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        self._navigate("dashboard")

    def _navigate(self, screen):
        # Highlight nút active
        for key, btn in self._nav_btns.items():
            btn.config(bg=COLORS["primary"] if key == screen
                       else COLORS["primary_dark"])

        # Xoá nội dung cũ
        for w in self.content.winfo_children():
            w.destroy()

        user = self.current_user

        if screen == "dashboard":
            frame = DashboardFrame(self.content, user,
                                   on_navigate=self._navigate)
        elif screen == "add_transaction":
            frame = AddTransactionFrame(
                self.content, user,
                on_save=lambda: self._navigate("dashboard"))
        elif screen == "history":
            frame = TransactionListFrame(self.content, user)
        elif screen == "budget":
            frame = BudgetFrame(self.content, user)
        elif screen == "report":
            frame = ReportFrame(self.content, user)
        else:
            return

        frame.pack(fill="both", expand=True)

    def _logout(self):
        self.current_user = None
        self.title("Quản Lý Chi Tiêu Cá Nhân")
        self._show_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()
