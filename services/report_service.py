from datetime import datetime, timedelta
from models.models import Report
from repositories.repositories import (
    ReportRepository, TransactionRepository,
    BudgetRepository, CategoryRepository,
)


def _get_date_range(period_type, ref_date=None):
    """
    Tính start_date, end_date theo period_type.
    ref_date: datetime object, mặc định hôm nay.
    Trả về tuple (start_str, end_str) dạng 'YYYY-MM-DD'.
    """
    d = ref_date or datetime.now()

    if period_type == "day":
        start = end = d

    elif period_type == "week":
        # Tuần bắt đầu từ thứ Hai
        start = d - timedelta(days=d.weekday())
        end = start + timedelta(days=6)

    elif period_type == "month":
        start = d.replace(day=1)
        # Ngày cuối tháng: ngày 1 tháng sau - 1 ngày
        if d.month == 12:
            end = d.replace(year=d.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = d.replace(month=d.month + 1, day=1) - timedelta(days=1)

    elif period_type == "quarter":
        quarter_start_month = ((d.month - 1) // 3) * 3 + 1
        start = d.replace(month=quarter_start_month, day=1)
        end_month = quarter_start_month + 2
        if end_month == 12:
            end = d.replace(month=12, day=31)
        else:
            end = d.replace(month=end_month + 1, day=1) - timedelta(days=1)

    elif period_type == "year":
        start = d.replace(month=1, day=1)
        end = d.replace(month=12, day=31)

    else:
        raise ValueError(f"period_type không hợp lệ: {period_type}")

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


class ReportService:
    def __init__(self):
        self.report_repo = ReportRepository()
        self.tx_repo = TransactionRepository()
        self.budget_repo = BudgetRepository()
        self.category_repo = CategoryRepository()

    # ── Sinh báo cáo ──────────────────────────────────────

    def generate(self, user_id, period_type, ref_date=None, custom_range=None):
        """
        Sinh báo cáo và lưu vào file.
        custom_range: tuple ('YYYY-MM-DD', 'YYYY-MM-DD') khi period_type='custom'.
        Trả về Report object đã được lưu.
        """
        if period_type == "custom":
            if not custom_range or len(custom_range) != 2:
                raise ValueError("custom_range phải là tuple (start_date, end_date).")
            start_date, end_date = custom_range
        else:
            start_date, end_date = _get_date_range(period_type, ref_date)

        # Tính tổng thu / chi
        txs = self.tx_repo.get_by_date_range(user_id, start_date, end_date)
        total_income = 0.0
        total_expense = 0.0
        for t in txs:
            if t.type == "income":
                total_income += t.amount
            else:
                total_expense += t.amount

        report = Report(
            id=0,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            period_type=period_type,
            total_income=total_income,
            total_expense=total_expense,
        )

        # Nhóm chi tiêu theo danh mục
        self._fill_category_summaries(report, user_id, start_date, end_date, period_type)

        return self.report_repo.add(report)

    def _fill_category_summaries(self, report, user_id, start_date, end_date, period_type):
        """Tính chi tiêu từng danh mục và so sánh với budget (nếu có)."""
        categories = self.category_repo.get_by_user(user_id)

        # Xác định month để lấy budget (chỉ áp dụng khi period_type == month)
        month = start_date[:7] if period_type == "month" else None

        for cat in categories:
            txs_cat = self.tx_repo.get_by_date_range(user_id, start_date, end_date)
            spent = 0.0
            for t in txs_cat:
                if t.category_id == cat.id and t.type == "expense":
                    spent += t.amount

            if spent == 0.0:
                continue  # bỏ qua danh mục không có chi tiêu

            budget_limit = 0.0
            if month:
                budget = self.budget_repo.get_by_category_and_month(user_id, cat.id, month)
                if budget:
                    budget_limit = budget.limit_amount

            report.add_category_summary(cat.name, spent, budget_limit)

    # ── Lấy báo cáo đã lưu ───────────────────────────────

    def get_all(self, user_id):
        return self.report_repo.get_by_user(user_id)

    def get_by_period_type(self, user_id, period_type):
        return self.report_repo.get_by_period_type(user_id, period_type)

    # ── Tóm tắt nhanh (không lưu) ────────────────────────

    def quick_summary(self, user_id, period_type, ref_date=None):
        """
        Trả về dict tóm tắt nhanh — không lưu vào file.
        Dùng để hiển thị dashboard.
        """
        start_date, end_date = _get_date_range(period_type, ref_date)
        txs = self.tx_repo.get_by_date_range(user_id, start_date, end_date)

        total_income = 0.0
        total_expense = 0.0
        for t in txs:
            if t.type == "income":
                total_income += t.amount
            else:
                total_expense += t.amount

        return {
            "period_type": period_type,
            "start_date": start_date,
            "end_date": end_date,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
        }
