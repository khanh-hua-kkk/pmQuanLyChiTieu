import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.theme import COLORS, FONTS
from services.transaction_service import TransactionService
from services.budget_service import BudgetService
from repositories.repositories import CategoryRepository


class DashboardFrame(ttk.Frame):
    def __init__(self, master, user, on_navigate):
        super().__init__(master)
        self.user = user
        self.on_navigate = on_navigate  # callback(screen_name)
        self.tx_service = TransactionService()
        self.budget_service = BudgetService()
        self.cat_repo = CategoryRepository()
        self._build()
        self.refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # ── Greeting ────────────────────────────────────
        top = ttk.Frame(self, padding=(24, 20, 24, 0))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        ttk.Label(top, text=f"Xin chào, {self.user.name}",
                  style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        now = datetime.now().strftime("%B %Y")
        ttk.Label(top, text=now,
                  style="Muted.TLabel").grid(row=1, column=0, sticky="w")

        # ── Summary cards ───────────────────────────────
        cards = ttk.Frame(self, padding=(24, 16))
        cards.grid(row=1, column=0, sticky="ew")
        for i in range(3):
            cards.columnconfigure(i, weight=1)

        self.income_lbl = self._make_card(cards, 0, "Tổng thu", "0 ₫",
                                          COLORS["income"])
        self.expense_lbl = self._make_card(cards, 1, "Tổng chi", "0 ₫",
                                           COLORS["expense"])
        self.balance_lbl = self._make_card(cards, 2, "Số dư", "0 ₫",
                                           COLORS["primary"])

        # ── Quick actions ────────────────────────────────
        actions = ttk.Frame(self, padding=(24, 0))
        actions.grid(row=2, column=0, sticky="ew")

        ttk.Button(actions, text="+ Thêm giao dịch",
                   command=lambda: self.on_navigate("add_transaction")).pack(
            side="left", padx=(0, 8))
        ttk.Button(actions, text="Xem báo cáo",
                   style="Ghost.TButton",
                   command=lambda: self.on_navigate("report")).pack(
            side="left")

        # ── Budget status ────────────────────────────────
        ttk.Label(self, text="Ngân sách tháng này",
                  style="Subhead.TLabel",
                  background=COLORS["bg"]).grid(
            row=3, column=0, sticky="w", padx=24, pady=(20, 8))

        self.budget_frame = ttk.Frame(self, padding=(24, 0))
        self.budget_frame.grid(row=4, column=0, sticky="ew")
        self.budget_frame.columnconfigure(0, weight=1)

        # ── Recent transactions ──────────────────────────
        ttk.Label(self, text="Giao dịch gần đây",
                  style="Subhead.TLabel",
                  background=COLORS["bg"]).grid(
            row=5, column=0, sticky="w", padx=24, pady=(20, 8))

        tree_frame = ttk.Frame(self, padding=(24, 0, 24, 24))
        tree_frame.grid(row=6, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)

        cols = ("date", "note", "category", "type", "amount")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=8)
        headers = {"date": ("Ngày", 90),
                   "note": ("Ghi chú", 200),
                   "category": ("Danh mục", 120),
                   "type": ("Loại", 70),
                   "amount": ("Số tiền", 110)}
        for col, (label, width) in headers.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width,
                             anchor="e" if col == "amount" else "w")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

    def _make_card(self, parent, col, title, value, accent):
        card = tk.Frame(parent, bg=COLORS["surface"],
                        highlightthickness=1,
                        highlightbackground=COLORS["border"])
        card.grid(row=0, column=col, sticky="ew",
                  padx=(0 if col == 0 else 8, 0), pady=4)
        card.columnconfigure(0, weight=1)

        accent_bar = tk.Frame(card, bg=accent, height=3)
        accent_bar.pack(fill="x")

        inner = tk.Frame(card, bg=COLORS["surface"], padx=16, pady=14)
        inner.pack(fill="both")

        tk.Label(inner, text=title, font=FONTS["small"],
                 fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")
        lbl = tk.Label(inner, text=value, font=FONTS["subhead"],
                       fg=accent, bg=COLORS["surface"])
        lbl.pack(anchor="w", pady=(4, 0))
        return lbl

    def refresh(self):
        """Tải lại toàn bộ dữ liệu lên dashboard."""
        month = datetime.now().strftime("%Y-%m")
        today = datetime.now()
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

        income, expense, balance = self.tx_service.calc_total(
            self.user.id, start, end)

        def fmt(n): return f"{n:,.0f} ₫"
        self.income_lbl.config(text=fmt(income))
        self.expense_lbl.config(text=fmt(expense))
        self.balance_lbl.config(
            text=fmt(balance),
            fg=COLORS["success"] if balance >= 0 else COLORS["danger"])

        self._refresh_budget(month)
        self._refresh_transactions()

    def _refresh_budget(self, month):
        for w in self.budget_frame.winfo_children():
            w.destroy()

        statuses = self.budget_service.get_month_status(self.user.id, month)
        if len(statuses) == 0:
            ttk.Label(self.budget_frame, text="Chưa đặt ngân sách tháng này.",
                      style="Muted.TLabel").grid(row=0, column=0, sticky="w")
            return

        for i, s in enumerate(statuses):
            row = ttk.Frame(self.budget_frame, style="Surface.TFrame",
                            padding=(12, 8))
            row.grid(row=i, column=0, sticky="ew", pady=3)
            row.columnconfigure(1, weight=1)

            over = s["over_budget"]
            color = COLORS["danger"] if over else COLORS["primary"]

            tk.Label(row, text=s["category_name"], font=FONTS["body_b"],
                     bg=COLORS["surface"], fg=COLORS["text"]).grid(
                row=0, column=0, sticky="w")

            pct_text = f"{s['percent_used']}%"
            if over:
                pct_text += " ⚠"
            tk.Label(row, text=pct_text, font=FONTS["small"],
                     bg=COLORS["surface"],
                     fg=COLORS["danger"] if over else COLORS["text_muted"]).grid(
                row=0, column=2, sticky="e", padx=(8, 0))

            style = "Danger.Horizontal.TProgressbar" if over else "Horizontal.TProgressbar"
            pb = ttk.Progressbar(row, orient="horizontal", length=300,
                                 mode="determinate", style=style)
            pb["value"] = min(s["percent_used"], 100)
            pb.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 0))

            tk.Label(row,
                     text=f"{s['spent']:,.0f} / {s['limit_amount']:,.0f} ₫",
                     font=FONTS["small"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).grid(
                row=2, column=0, sticky="w", pady=(2, 0))

    def _refresh_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        txs = self.tx_service.get_all(self.user.id)
        # Lấy 10 giao dịch mới nhất (duyệt LinkedList, lưu tạm)
        all_txs = []
        for t in txs:
            all_txs.append(t)

        # Sắp xếp giảm dần theo ngày (tự cài, không dùng sorted())
        for i in range(len(all_txs)):
            for j in range(i + 1, len(all_txs)):
                if all_txs[i].date < all_txs[j].date:
                    all_txs[i], all_txs[j] = all_txs[j], all_txs[i]

        for t in all_txs[:10]:
            sign = "+" if t.type == "income" else "-"
            tag = t.type
            category = self.cat_repo.get_by_id(t.category_id)
            category_name = category.name if category else f"#{t.category_id}"
            self.tree.insert("", "end",
                             values=(t.date, t.note or "—",
                                     category_name,
                                     "Thu" if t.type == "income" else "Chi",
                                     f"{sign}{t.amount:,.0f} ₫"),
                             tags=(tag,))

        self.tree.tag_configure("income", foreground=COLORS["income"])
        self.tree.tag_configure("expense", foreground=COLORS["expense"])
