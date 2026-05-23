import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui.theme import COLORS, FONTS
from services.budget_service import BudgetService
from services.report_service import ReportService
from repositories.repositories import CategoryRepository
from models.models import Budget


# ═══════════════════════════════════════════════════════
#  BudgetFrame
# ═══════════════════════════════════════════════════════

class BudgetFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master, padding=24)
        self.user = user
        self.budget_service = BudgetService()
        self.cat_repo = CategoryRepository()
        self._build()
        self.refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Quản lý ngân sách",
                  style="Subhead.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 16))

        # ── Chọn tháng ──────────────────────────────────
        top = ttk.Frame(self)
        top.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(top, text="Tháng (YYYY-MM):").pack(side="left", padx=(0, 8))
        self.month_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m"))
        ttk.Entry(top, textvariable=self.month_var,
                  width=10).pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Xem",
                   command=self.refresh).pack(side="left")

        # ── Form đặt budget ──────────────────────────────
        form = ttk.Frame(self, style="Surface.TFrame", padding=16)
        form.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Đặt hạn mức mới",
                  style="Subhead.TLabel",
                  background=COLORS["surface"]).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        ttk.Label(form, text="Danh mục:",
                  background=COLORS["surface"]).grid(
            row=1, column=0, sticky="w", padx=(0, 8))
        self.cat_var = tk.StringVar()
        cats = self.cat_repo.get_by_user_and_type(self.user.id, "expense")
        self._cat_list = list(cats)
        self.cat_combo = ttk.Combobox(
            form, textvariable=self.cat_var, state="readonly",
            values=[c.name for c in self._cat_list], width=18)
        self.cat_combo.grid(row=1, column=1, padx=(0, 16))
        if self._cat_list:
            self.cat_combo.current(0)

        ttk.Label(form, text="Hạn mức (₫):",
                  background=COLORS["surface"]).grid(
            row=1, column=2, sticky="w", padx=(0, 8))
        self.limit_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.limit_var,
                  width=14).grid(row=1, column=3, padx=(0, 12))

        ttk.Button(form, text="Đặt ngân sách",
                   command=self._set_budget).grid(row=1, column=4)

        # ── Danh sách budget tháng ───────────────────────
        ttk.Label(self, text="Ngân sách tháng",
                  style="Subhead.TLabel",
                  background=COLORS["bg"]).grid(
            row=3, column=0, sticky="w", pady=(0, 8))

        self.budget_container = ttk.Frame(self)
        self.budget_container.grid(row=4, column=0, sticky="ew")
        self.budget_container.columnconfigure(0, weight=1)

    def _set_budget(self):
        cat_name = self.cat_var.get()
        cat = next((c for c in self._cat_list if c.name == cat_name), None)
        if cat is None:
            messagebox.showerror("Lỗi", "Chọn danh mục.")
            return
        try:
            limit = float(self.limit_var.get().replace(",", ""))
        except ValueError:
            messagebox.showerror("Lỗi", "Hạn mức không hợp lệ.")
            return
        month = self.month_var.get().strip()
        try:
            self.budget_service.set_budget(
                self.user.id, cat.id, limit, month)
            messagebox.showinfo("OK", "Đã đặt ngân sách.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def refresh(self):
        for w in self.budget_container.winfo_children():
            w.destroy()
        month = self.month_var.get().strip()
        statuses = self.budget_service.get_month_status(self.user.id, month)

        if len(statuses) == 0:
            ttk.Label(self.budget_container,
                      text="Chưa có ngân sách nào cho tháng này.",
                      style="Muted.TLabel").grid(row=0, column=0, sticky="w")
            return

        for i, s in enumerate(statuses):
            over = s["over_budget"]
            card = tk.Frame(self.budget_container, bg=COLORS["surface"],
                            highlightthickness=1,
                            highlightbackground=(
                                COLORS["danger"] if over else COLORS["border"]))
            card.grid(row=i, column=0, sticky="ew", pady=4)
            card.columnconfigure(1, weight=1)

            inner = tk.Frame(card, bg=COLORS["surface"], padx=14, pady=10)
            inner.pack(fill="both")
            inner.columnconfigure(1, weight=1)

            tk.Label(inner, text=s["category_name"],
                     font=FONTS["body_b"], bg=COLORS["surface"],
                     fg=COLORS["text"]).grid(row=0, column=0, sticky="w")

            status_text = (f"⚠ Vượt {s['spent'] - s['limit_amount']:,.0f} ₫"
                           if over else f"Còn {s['remaining']:,.0f} ₫")
            tk.Label(inner, text=status_text, font=FONTS["small"],
                     bg=COLORS["surface"],
                     fg=COLORS["danger"] if over else COLORS["success"]).grid(
                row=0, column=2, sticky="e")

            style = ("Danger.Horizontal.TProgressbar"
                     if over else "Horizontal.TProgressbar")
            pb = ttk.Progressbar(inner, orient="horizontal",
                                 length=500, mode="determinate", style=style)
            pb["value"] = min(s["percent_used"], 100)
            pb.grid(row=1, column=0, columnspan=3,
                    sticky="ew", pady=(6, 2))

            tk.Label(inner,
                     text=f"{s['spent']:,.0f} / {s['limit_amount']:,.0f} ₫  "
                          f"({s['percent_used']}%)",
                     font=FONTS["small"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).grid(
                row=2, column=0, sticky="w")


# ═══════════════════════════════════════════════════════
#  ReportFrame
# ═══════════════════════════════════════════════════════

class ReportFrame(ttk.Frame):
    def __init__(self, master, user):
        super().__init__(master, padding=24)
        self.user = user
        self.report_service = ReportService()
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Báo cáo thống kê",
                  style="Subhead.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 16))

        # ── Chọn kỳ ─────────────────────────────────────
        ctrl = ttk.Frame(self)
        ctrl.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        ttk.Label(ctrl, text="Kỳ:").pack(side="left", padx=(0, 8))
        self.period_var = tk.StringVar(value="month")
        for val, label in [("day", "Ngày"), ("week", "Tuần"),
                           ("month", "Tháng"), ("quarter", "Quý"),
                           ("year", "Năm"), ("custom", "Tùy chọn")]:
            ttk.Radiobutton(ctrl, text=label,
                            variable=self.period_var, value=val,
                            command=self._on_period_change).pack(
                side="left", padx=4)

        ttk.Button(ctrl, text="Tạo báo cáo",
                   command=self._generate).pack(side="left", padx=(16, 0))

        # ── Khoảng thời gian tùy chọn ────────────────────
        self.custom_range_frame = ttk.Frame(self)
        self.custom_range_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.custom_range_frame.columnconfigure(1, weight=1)

        ttk.Label(self.custom_range_frame, text="Từ ngày:").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 4))
        self.start_date_var = tk.StringVar(
            value=datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_range_frame, textvariable=self.start_date_var,
                  width=12).grid(row=0, column=1, sticky="w")

        ttk.Label(self.custom_range_frame, text="Đến ngày:").grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=(4, 0))
        self.end_date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_range_frame, textvariable=self.end_date_var,
                  width=12).grid(row=1, column=1, sticky="w")

        ttk.Label(self.custom_range_frame, text="Định dạng: YYYY-MM-DD",
                  style="Muted.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.custom_range_frame.grid_remove()

        # ── Kết quả văn bản ─────────────────────────────
        self.text_frame = ttk.Frame(self, style="Surface.TFrame", padding=16)
        self.text_frame.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        self.text_frame.columnconfigure(0, weight=1)

        self.summary_text = tk.Text(self.text_frame, height=8,
                                    font=FONTS["mono"],
                                    bg=COLORS["surface"],
                                    fg=COLORS["text"],
                                    relief="flat", state="disabled")
        self.summary_text.pack(fill="both")

        # ── Biểu đồ matplotlib ──────────────────────────
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.grid(row=4, column=0, sticky="nsew")
        self._canvas = None

    def _on_period_change(self):
        if self.period_var.get() == "custom":
            self.custom_range_frame.grid()
        else:
            self.custom_range_frame.grid_remove()

    def _generate(self):
        period = self.period_var.get()
        try:
            if period == "custom":
                start_date = self.start_date_var.get().strip()
                end_date = self.end_date_var.get().strip()
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Định dạng ngày phải là YYYY-MM-DD.")
                if start_date > end_date:
                    raise ValueError("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.")
                report = self.report_service.generate(
                    self.user.id,
                    period,
                    custom_range=(start_date, end_date),
                )
            else:
                report = self.report_service.generate(self.user.id, period)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            return

        self._render_text(report)
        self._render_chart(report)

    def _render_text(self, report):
        lines = [
            f"Kỳ: {report.period_type.upper()}  "
            f"({report.start_date} → {report.end_date})",
            f"{'─' * 48}",
            f"Tổng thu    : {report.total_income:>16,.0f} ₫",
            f"Tổng chi    : {report.total_expense:>16,.0f} ₫",
            f"Số dư       : {report.balance:>16,.0f} ₫",
            f"{'─' * 48}",
            "Chi tiết theo danh mục:",
        ]
        for s in report.category_summaries:
            over_mark = " ⚠" if s["over_budget"] else ""
            lines.append(
                f"  {s['category_name']:<18} "
                f"{s['spent']:>12,.0f} ₫  "
                f"({s['percentage']:.1f}%){over_mark}"
            )
        if len(report.over_budget_categories) > 0:
            lines.append(f"{'─' * 48}")
            lines.append("Vượt ngân sách:")
            for name in report.over_budget_categories:
                lines.append(f"  ⚠ {name}")

        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", "\n".join(lines))
        self.summary_text.config(state="disabled")

    def _render_chart(self, report):
        # Xoá chart cũ
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
        for w in self.chart_frame.winfo_children():
            w.destroy()

        summaries = list(report.category_summaries)
        if not summaries:
            ttk.Label(self.chart_frame,
                      text="Không có dữ liệu chi tiêu để vẽ biểu đồ.",
                      style="Muted.TLabel").pack()
            return

        labels = [s["category_name"] for s in summaries]
        sizes = [s["spent"] for s in summaries]
        colors_pie = ["#2D6A4F", "#40916C", "#52B788",
                      "#74C69D", "#95D5B2", "#B7E4C7",
                      "#D8F3DC"][:len(labels)]

        fig = Figure(figsize=(6, 3.5), dpi=96,
                     facecolor=COLORS["bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["bg"])

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors_pie,
            autopct="%1.1f%%", startangle=140,
            wedgeprops={"linewidth": 1, "edgecolor": COLORS["bg"]},
            textprops={"fontsize": 9, "color": COLORS["text"]},
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color(COLORS["surface"])

        ax.set_title(
            f"Tỷ lệ chi tiêu — {report.period_type}",
            fontsize=11, color=COLORS["text"], pad=12)

        fig.tight_layout()
        self._canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
