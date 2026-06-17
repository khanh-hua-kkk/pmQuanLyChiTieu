import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.theme import COLORS, FONTS
from services.transaction_service import TransactionService
from services.budget_service import BudgetService
from repositories.repositories import CategoryRepository


class AddTransactionFrame(ttk.Frame):
    def __init__(self, master, user, on_save):
        super().__init__(master, padding=24)
        self.user = user
        self.on_save = on_save
        self.tx_service = TransactionService()
        self.cat_repo = CategoryRepository()
        self._categories = []
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Thêm giao dịch",
                  style="Subhead.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Loại giao dịch
        ttk.Label(self, text="Loại").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 16))
        self.type_var = tk.StringVar(value="expense")
        type_frame = ttk.Frame(self)
        type_frame.grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(type_frame, text="Chi tiêu",
                        variable=self.type_var, value="expense",
                        command=self._on_type_change).pack(side="left", padx=(0, 16))
        ttk.Radiobutton(type_frame, text="Thu nhập",
                        variable=self.type_var, value="income",
                        command=self._on_type_change).pack(side="left")

        # Số tiền
        ttk.Label(self, text="Số tiền (₫)").grid(
            row=2, column=0, sticky="w", pady=6, padx=(0, 16))
        self.amount_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.amount_var).grid(
            row=2, column=1, sticky="ew")

        # Danh mục
        ttk.Label(self, text="Danh mục").grid(
            row=3, column=0, sticky="w", pady=6, padx=(0, 16))
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(self, textvariable=self.cat_var,
                                      state="readonly")
        self.cat_combo.grid(row=3, column=1, sticky="ew")
        self._load_categories("expense")

        # Ngày
        ttk.Label(self, text="Ngày").grid(
            row=4, column=0, sticky="w", pady=6, padx=(0, 16))
        self.date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self, textvariable=self.date_var).grid(
            row=4, column=1, sticky="ew")
        ttk.Label(self, text="Định dạng: YYYY-MM-DD",
                  style="Muted.TLabel").grid(
            row=5, column=1, sticky="w")

        # Ghi chú
        ttk.Label(self, text="Ghi chú").grid(
            row=6, column=0, sticky="w", pady=6, padx=(0, 16))
        self.note_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.note_var).grid(
            row=6, column=1, sticky="ew")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=7, column=0, columnspan=2,
                       sticky="e", pady=(24, 0))
        ttk.Button(btn_frame, text="Lưu",
                   command=self._save).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="Huỷ",
                   style="Ghost.TButton",
                   command=self.on_save).pack(side="right")

        # Alert label (hiện khi vượt budget)
        self.alert_lbl = tk.Label(self, text="", font=FONTS["body"],
                                  fg=COLORS["danger"],
                                  bg=COLORS["bg"], wraplength=400,
                                  justify="left")
        self.alert_lbl.grid(row=8, column=0, columnspan=2,
                            sticky="w", pady=(12, 0))

    def _on_type_change(self):
        self._load_categories(self.type_var.get())

    def _load_categories(self, type):
        cats = self.cat_repo.get_by_user_and_type(self.user.id, type)
        self._categories = list(cats)
        names = [c.name for c in self._categories]
        self.cat_combo["values"] = names
        if names:
            self.cat_combo.current(0)

    def _save(self):
        self.alert_lbl.config(text="")
        try:
            amount = float(self.amount_var.get().replace(",", ""))
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền không hợp lệ.")
            return

        cat_name = self.cat_var.get()
        cat = next((c for c in self._categories if c.name == cat_name), None)
        if cat is None:
            messagebox.showerror("Lỗi", "Vui lòng chọn danh mục.")
            return

        date = self.date_var.get().strip()
        note = self.note_var.get().strip()
        type_ = self.type_var.get()

        try:
            tx, alert = self.tx_service.add_transaction(
                user_id=self.user.id,
                category_id=cat.id,
                amount=amount,
                type=type_,
                note=note,
                date=date,
            )
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
            return

        if alert:
            msg = (f"⚠ Vượt ngân sách [{alert['category_name']}]!\n"
                   f"Đã chi: {alert['spent']:,.0f} ₫  |  "
                   f"Hạn mức: {alert['limit']:,.0f} ₫  |  "
                   f"Vượt: {alert['exceeded_by']:,.0f} ₫")
            self.alert_lbl.config(text=msg)
            messagebox.showwarning("Cảnh báo ngân sách", msg)

        messagebox.showinfo("Thành công", "Đã lưu giao dịch.")
        self.on_save()


# ─────────────────────────────────────────────


class TransactionListFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master, padding=24)
        self.user = user
        self.tx_service = TransactionService()
        self.cat_repo = CategoryRepository()
        self._build()
        self.refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="Lịch sử giao dịch",
                  style="Subhead.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 16))

        # ── Filter bar ──────────────────────────────────
        filter_bar = ttk.Frame(self)
        filter_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(filter_bar, text="Từ:").pack(side="left", padx=(0, 4))
        self.start_var = tk.StringVar(
            value=datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        ttk.Entry(filter_bar, textvariable=self.start_var,
                  width=12).pack(side="left", padx=(0, 12))

        ttk.Label(filter_bar, text="Đến:").pack(side="left", padx=(0, 4))
        self.end_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(filter_bar, textvariable=self.end_var,
                  width=12).pack(side="left", padx=(0, 12))

        ttk.Label(filter_bar, text="Loại:").pack(side="left", padx=(0, 4))
        self.type_labels = {"Tất cả": "both", "Thu nhập": "income", "Chi tiêu": "expense"}
        self.type_var = tk.StringVar(value="Tất cả")
        self.type_combo = ttk.Combobox(filter_bar, textvariable=self.type_var,
                                       values=list(self.type_labels.keys()),
                                       state="readonly", width=10)
        self.type_combo.pack(side="left", padx=(0, 12))

        ttk.Label(filter_bar, text="Sắp xếp:").pack(side="left", padx=(0, 4))
        self.sort_labels = {"Ngày": "date", "Số tiền": "amount"}
        self.sort_var = tk.StringVar(value="Ngày")
        self.sort_combo = ttk.Combobox(filter_bar, textvariable=self.sort_var,
                                       values=list(self.sort_labels.keys()),
                                       state="readonly", width=10)
        self.sort_combo.pack(side="left", padx=(0, 12))

        self.order_labels = {"Giảm dần": True, "Tăng dần": False}
        self.order_var = tk.StringVar(value="Giảm dần")
        self.order_combo = ttk.Combobox(filter_bar, textvariable=self.order_var,
                                        values=list(self.order_labels.keys()),
                                        state="readonly", width=10)
        self.order_combo.pack(side="left", padx=(0, 12))

        ttk.Button(filter_bar, text="Lọc",
                   command=self.refresh).pack(side="left", padx=(0, 8))
        ttk.Button(filter_bar, text="Xoá giao dịch",
                   style="Danger.TButton",
                   command=self._delete_selected).pack(side="right")

        # ── Treeview ────────────────────────────────────
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        cols = ("id", "date", "note", "category_id", "type", "amount")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=16)
        widths = {"id": 40, "date": 100, "note": 220,
                  "category_id": 100, "type": 70, "amount": 120}
        labels = {"id": "ID", "date": "Ngày", "note": "Ghi chú",
                  "category_id": "Danh mục", "type": "Loại",
                  "amount": "Số tiền"}
        for col in cols:
            self.tree.heading(col, text=labels[col])
            self.tree.column(col, width=widths[col],
                             anchor="e" if col in ("id", "amount") else "w")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        # ── Tổng kết ────────────────────────────────────
        summary = ttk.Frame(self)
        summary.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        self.summary_lbl = ttk.Label(summary, text="", style="Muted.TLabel")
        self.summary_lbl.pack(side="right")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        txs = self.tx_service.get_by_date_range(self.user.id, start, end)

        selected_type = self.type_labels[self.type_var.get()]
        if selected_type != "both":
            txs = [t for t in txs if t.type == selected_type]

        sort_key = self.sort_labels[self.sort_var.get()]
        reverse = self.order_labels[self.order_var.get()]
        txs = sorted(txs, key=lambda t: getattr(t, sort_key), reverse=reverse)

        income = expense = 0.0
        for t in txs:
            sign = "+" if t.type == "income" else "-"
            tag = t.type
            if t.type == "income":
                income += t.amount
            else:
                expense += t.amount

            category = self.cat_repo.get_by_id(t.category_id)
            category_name = category.name if category else f"#{t.category_id}"

            self.tree.insert("", "end",
                             values=(t.id, t.date, t.note or "—",
                                     category_name,
                                     "Thu" if t.type == "income" else "Chi",
                                     f"{sign}{t.amount:,.0f} ₫"),
                             tags=(tag,))

        self.tree.tag_configure("income", foreground=COLORS["income"])
        self.tree.tag_configure("expense", foreground=COLORS["expense"])
        balance = income - expense
        sign = "+" if balance >= 0 else ""
        self.summary_lbl.config(
            text=f"Thu: {income:,.0f} ₫  |  Chi: {expense:,.0f} ₫  |  "
                 f"Số dư: {sign}{balance:,.0f} ₫")

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Chưa chọn giao dịch nào.")
            return
        if not messagebox.askyesno("Xác nhận", "Xoá giao dịch đã chọn?"):
            return
        for item in selected:
            tx_id = int(self.tree.item(item, "values")[0])
            try:
                self.tx_service.delete_transaction(tx_id, self.user.id)
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e))
        self.refresh()
