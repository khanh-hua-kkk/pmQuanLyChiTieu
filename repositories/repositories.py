from repositories.base_repository import BaseRepository
from models.models import User, Category, Transaction, Budget, Report


class UserRepository(BaseRepository):
    file_path = "data/users.json"
    model_class = User

    def get_by_email(self, email):
        email = email.strip().lower()
        return self._data.find(lambda u: u.email.strip().lower() == email)


# ─────────────────────────────────────────────


class CategoryRepository(BaseRepository):
    file_path = "data/categories.json"
    model_class = Category

    DEFAULT_EXPENSE_CATEGORIES = [
        "Ăn uống",
        "Chi tiêu hàng ngày",
        "Quần áo",
        "Mỹ phẩm",
        "Phí giao lưu",
        "Y tế",
        "Giáo dục",
        "Tiền điện",
        "Đi lại",
        "Phí liên lạc",
        "Tiền nhà",
    ]

    DEFAULT_INCOME_CATEGORIES = [
        "Tiền lương",
        "Tiền phụ cấp",
        "Tiền thưởng",
        "Thu nhập phụ",
        "Đầu tư",
    ]

    def get_all(self):
        if self._data.head is None:
            self._create_default_categories()
        return self._data

    def get_by_user(self, user_id):
        """Legacy alias: categories are global, not per-user."""
        return self.get_all()

    def get_by_type(self, type):
        if type == "both":
            return self.get_all()
        return self.get_all().filter(lambda c: c.type in (type, "both"))

    def get_by_user_and_type(self, user_id, type):
        """Legacy alias: categories are global, not per-user."""
        return self.get_by_type(type)

    def _create_default_categories(self):
        categories = []
        for name in self.DEFAULT_EXPENSE_CATEGORIES:
            categories.append(Category(id=0, name=name, type="expense"))
        for name in self.DEFAULT_INCOME_CATEGORIES:
            categories.append(Category(id=0, name=name, type="income"))

        for category in categories:
            category.id = self._next_id()
            self._data.append(category)
        self._save_all()


# ─────────────────────────────────────────────


class TransactionRepository(BaseRepository):
    file_path = "data/transactions.json"
    model_class = Transaction

    def get_by_user(self, user_id):
        return self._data.filter(lambda t: t.user_id == user_id)

    def get_by_user_and_type(self, user_id, type):
        """type: 'income' | 'expense'"""
        return self._data.filter(
            lambda t: t.user_id == user_id and t.type == type
        )

    def get_by_date_range(self, user_id, start_date, end_date):
        """start_date, end_date: chuỗi 'YYYY-MM-DD'"""
        return self._data.filter(
            lambda t: (
                t.user_id == user_id
                and start_date <= t.date <= end_date
            )
        )

    def get_by_category(self, user_id, category_id):
        return self._data.filter(
            lambda t: t.user_id == user_id and t.category_id == category_id
        )

    def get_by_month(self, user_id, month):
        """month: 'YYYY-MM'"""
        return self._data.filter(
            lambda t: t.user_id == user_id and t.date.startswith(month)
        )

    def get_expense_by_category_in_month(self, user_id, category_id, month):
        """Tổng chi của 1 danh mục trong 1 tháng — dùng để kiểm tra budget."""
        transactions = self._data.filter(
            lambda t: (
                t.user_id == user_id
                and t.category_id == category_id
                and t.type == "expense"
                and t.date.startswith(month)
            )
        )
        total = 0.0
        for t in transactions:
            total += t.amount
        return total


# ─────────────────────────────────────────────


class BudgetRepository(BaseRepository):
    file_path = "data/budgets.json"
    model_class = Budget

    def get_by_user(self, user_id):
        return self._data.filter(lambda b: b.user_id == user_id)

    def get_by_month(self, user_id, month):
        """Lấy tất cả budget của user trong tháng đó."""
        return self._data.filter(
            lambda b: b.user_id == user_id and b.month == month
        )

    def get_by_category_and_month(self, user_id, category_id, month):
        """Lấy 1 budget cụ thể — dùng khi thêm transaction để kiểm tra."""
        return self._data.find(
            lambda b: (
                b.user_id == user_id
                and b.category_id == category_id
                and b.month == month
            )
        )


# ─────────────────────────────────────────────


class ReportRepository(BaseRepository):
    file_path = "data/reports.json"
    model_class = Report

    def get_by_user(self, user_id):
        return self._data.filter(lambda r: r.user_id == user_id)

    def get_by_period_type(self, user_id, period_type):
        return self._data.filter(
            lambda r: r.user_id == user_id and r.period_type == period_type
        )

    def get_by_date_range(self, user_id, start_date, end_date):
        return self._data.find(
            lambda r: (
                r.user_id == user_id
                and r.start_date == start_date
                and r.end_date == end_date
            )
        )
