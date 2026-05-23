from datetime import datetime
from models.models import Transaction
from repositories.repositories import TransactionRepository, BudgetRepository, CategoryRepository


class TransactionService:
    def __init__(self):
        self.tx_repo = TransactionRepository()
        self.budget_repo = BudgetRepository()
        self.category_repo = CategoryRepository()

    # ── Thêm giao dịch ────────────────────────────────────

    def add_transaction(self, user_id, category_id, amount, type, note="", date=None):
        """
        Thêm giao dịch mới. Trả về tuple (transaction, alert).
        alert = None nếu không vượt budget.
        alert = dict nếu vượt budget: { category_name, spent, limit, exceeded_by }
        """
        if amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0.")
        if type not in ("income", "expense"):
            raise ValueError("Loại giao dịch phải là 'income' hoặc 'expense'.")

        tx = Transaction(
            id=0,
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            type=type,
            note=note,
            date=date or datetime.now().strftime("%Y-%m-%d"),
        )
        saved_tx = self.tx_repo.add(tx)

        alert = None
        if type == "expense":
            alert = self._check_budget(user_id, category_id, saved_tx.date)

        return saved_tx, alert

    def _check_budget(self, user_id, category_id, date):
        month = date[:7]  # "YYYY-MM-DD" → "YYYY-MM"
        budget = self.budget_repo.get_by_category_and_month(user_id, category_id, month)
        if budget is None:
            return None

        spent = self.tx_repo.get_expense_by_category_in_month(user_id, category_id, month)
        if spent <= budget.limit_amount:
            return None

        category = self.category_repo.get_by_id(category_id)
        return {
            "category_name": category.name if category else f"ID {category_id}",
            "spent": spent,
            "limit": budget.limit_amount,
            "exceeded_by": spent - budget.limit_amount,
        }

    # ── Sửa / Xoá ─────────────────────────────────────────

    def update_transaction(self, tx_id, user_id, **fields):
        tx = self.tx_repo.get_by_id(tx_id)
        if tx is None or tx.user_id != user_id:
            raise ValueError("Giao dịch không tồn tại hoặc không có quyền.")
        for key, value in fields.items():
            if hasattr(tx, key):
                setattr(tx, key, value)
        return self.tx_repo.update(tx_id, tx)

    def delete_transaction(self, tx_id, user_id):
        tx = self.tx_repo.get_by_id(tx_id)
        if tx is None or tx.user_id != user_id:
            raise ValueError("Giao dịch không tồn tại hoặc không có quyền.")
        return self.tx_repo.delete(tx_id)

    # ── Query ─────────────────────────────────────────────

    def get_all(self, user_id):
        return self.tx_repo.get_by_user(user_id)

    def get_by_date_range(self, user_id, start_date, end_date):
        return self.tx_repo.get_by_date_range(user_id, start_date, end_date)

    def get_by_category(self, user_id, category_id):
        return self.tx_repo.get_by_category(user_id, category_id)

    def get_by_month(self, user_id, month):
        return self.tx_repo.get_by_month(user_id, month)

    # ── Tính tổng ─────────────────────────────────────────

    def calc_total(self, user_id, start_date, end_date):
        """Trả về (total_income, total_expense, balance) trong khoảng ngày."""
        txs = self.tx_repo.get_by_date_range(user_id, start_date, end_date)
        total_income = 0.0
        total_expense = 0.0
        for t in txs:
            if t.type == "income":
                total_income += t.amount
            else:
                total_expense += t.amount
        return total_income, total_expense, total_income - total_expense

    def calc_by_category(self, user_id, start_date, end_date):
        """
        Trả về LinkedList các dict:
        { category_id, total_income, total_expense }
        """
        from models.linked_list import LinkedList

        txs = self.tx_repo.get_by_date_range(user_id, start_date, end_date)
        summary = {}  # tạm dùng dict nội bộ để nhóm

        for t in txs:
            if t.category_id not in summary:
                summary[t.category_id] = {"category_id": t.category_id,
                                           "total_income": 0.0,
                                           "total_expense": 0.0}
            if t.type == "income":
                summary[t.category_id]["total_income"] += t.amount
            else:
                summary[t.category_id]["total_expense"] += t.amount

        result = LinkedList()
        for item in summary.values():
            result.append(item)
        return result
