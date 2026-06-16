import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import COLORS, FONTS, PAD
from services.user_service import UserService, _validate_email


class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.user_service = UserService()
        self._build()

    def _build(self):
        self.configure(style="TFrame")
        self.columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────────────
        header = ttk.Frame(self, style="TFrame")
        header.grid(row=0, column=0, pady=(60, 40))
        ttk.Label(header, text="Chi Tiêu Cá Nhân",
                  style="Heading.TLabel").pack()
        ttk.Label(header, text="Quản lý tài chính thông minh",
                  style="Muted.TLabel").pack(pady=(4, 0))

        # ── Card ────────────────────────────────────────
        card = ttk.Frame(self, style="Surface.TFrame",
                         padding=32, width=380)
        card.grid(row=1, column=0)
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Đăng nhập",
                  style="Subhead.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 20)) 

        # Email
        ttk.Label(card, text="Email").grid(
            row=1, column=0, sticky="w", pady=(0, 4))
        self.email_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.email_var,
                  width=38).grid(row=2, column=0, sticky="ew", pady=(0, 12))

        # Password
        ttk.Label(card, text="Mật khẩu").grid(
            row=3, column=0, sticky="w", pady=(0, 4))
        self.pw_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.pw_var,
                  show="•", width=38).grid(
            row=4, column=0, sticky="ew", pady=(0, 24))

        # Buttons
        btn_frame = ttk.Frame(card, style="Surface.TFrame")
        btn_frame.grid(row=5, column=0, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        ttk.Button(btn_frame, text="Đăng nhập",
                   command=self._login).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btn_frame, text="Đăng ký",
                   style="Ghost.TButton",
                   command=self._open_register).grid(
            row=0, column=1, sticky="ew", padx=(6, 0))

        self.bind("<Return>", lambda e: self._login())

    def _login(self):
        email = self.email_var.get().strip()
        password = self.pw_var.get()
        if not _validate_email(email):
            messagebox.showerror("Email không hợp lệ", "Email không hợp lệ, vui lòng nhập lại.")
            return
        try:
            user = self.user_service.login(email, password)
            self.on_login_success(user)
        except ValueError as e:
            messagebox.showerror("Lỗi đăng nhập", str(e))

    def _open_register(self):
        win = tk.Toplevel(self)
        win.title("Đăng ký tài khoản")
        win.resizable(False, False)

        def _on_register_success():
            # Reload user data after a new account is created,
            # vì RegisterFrame sử dụng UserService riêng và ghi file.
            self.user_service = UserService()
            win.destroy()

        RegisterFrame(win, on_success=_on_register_success).pack(
            fill="both", expand=True)


class RegisterFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=32)
        self.on_success = on_success
        self.user_service = UserService()
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Tạo tài khoản",
                  style="Subhead.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 20))

        fields = [
            ("Họ tên", "name_var", False),
            ("Email", "email_var", False),
            ("Mật khẩu", "pw_var", True),
            ("Xác nhận mật khẩu", "pw2_var", True),
        ]
        for i, (label, attr, secret) in enumerate(fields):
            ttk.Label(self, text=label).grid(
                row=i * 2 + 1, column=0, sticky="w", pady=(0, 4))
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(self, textvariable=var,
                      show="•" if secret else "",
                      width=36).grid(
                row=i * 2 + 2, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(self, text="Tạo tài khoản",
                   command=self._register).grid(
            row=10, column=0, sticky="ew", pady=(10, 0))

    def _register(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        pw = self.pw_var.get()
        pw2 = self.pw2_var.get()

        if not name or not email or not pw:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ.")
            return
        if not _validate_email(email):
            messagebox.showerror("Email không hợp lệ", "Email không hợp lệ, vui lòng nhập lại.")
            return
        if pw != pw2:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp.")
            return
        try:
            self.user_service.register(name, email, pw)
            messagebox.showinfo("Thành công", "Tài khoản đã được tạo!")
            self.on_success()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
