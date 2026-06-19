from datetime import datetime
from models.models import Transaction
from repositories.repositories import TransactionRepository, BudgetRepository, CategoryRepository


class TransactionService:
    def __init__(self):
        self.tx_repo = TransactionRepository()
        self.budget_repo = BudgetRepository()
        self.category_repo = CategoryRepository()

    # ── Xác thực ngày tháng ────────────────────────────────

    def _validate_date(self, date_str):
        """
        Xác thực ngày nhập vào.
        Trả về (is_valid: bool, error_message: str)
        """
        # Kiểm tra định dạng
        if not date_str or not isinstance(date_str, str):
            return False, "Ngày không được để trống."
        
        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            return False, "Định dạng ngày phải là YYYY-MM-DD."
        
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Ngày không hợp lệ."
        
        return True, ""

    # ── Xác thực số tiền ───────────────────────────────────

    def _validate_and_normalize_amount(self, amount):
        """
        Xác thực và chuẩn hóa số tiền.
        - Chuyển đổi thành float
        - Kiểm tra > 0
        - Làm tròn 2 chữ số thập phân
        Trả về (is_valid: bool, amount_normalized: float, error_message: str)
        """
        if not amount:
            return False, None, "Số tiền không được để trống."
        
        try:
            # Chuyển đổi thành float (đã được chuẩn hóa từ UI)
            amount_float = float(amount)
        except (ValueError, TypeError):
            return False, None, "Số tiền không hợp lệ. Vui lòng nhập số."
        
        # Kiểm tra > 0
        if amount_float <= 0:
            return False, None, "Số tiền phải lớn hơn 0."
        
        # Làm tròn 2 chữ số thập phân
        amount_normalized = round(amount_float, 2)
        
        return True, amount_normalized, ""

    # ── Thêm giao dịch ────────────────────────────────────

    def add_transaction(self, user_id, category_id, amount, type, note="", date=None):
        """
        Thêm giao dịch mới. Trả về tuple (transaction, alert).
        alert = None nếu không vượt budget.
        alert = dict nếu vượt budget: { category_name, spent, limit, exceeded_by }
        """
        # Xác thực và chuẩn hóa số tiền
        is_valid, amount_normalized, error_msg = self._validate_and_normalize_amount(amount)
        if not is_valid:
            raise ValueError(error_msg)
        
        if type not in ("income", "expense"):
            raise ValueError("Loại giao dịch phải là 'income' hoặc 'expense'.")
        
        # Xác thực ngày
        date_to_use = date or datetime.now().strftime("%Y-%m-%d")
        is_valid, error_msg = self._validate_date(date_to_use)
        if not is_valid:
            raise ValueError(error_msg)

        tx = Transaction(
            id=0,
            user_id=user_id,
            category_id=category_id,
            amount=amount_normalized,
            type=type,
            note=note,
            date=date_to_use,
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
        """
        Cập nhật giao dịch. Xác thực số tiền và ngày nếu được cập nhật.
        """
        tx = self.tx_repo.get_by_id(tx_id)
        if tx is None or tx.user_id != user_id:
            raise ValueError("Giao dịch không tồn tại hoặc không có quyền.")
        
        # Xác thực số tiền nếu được cập nhật
        if "amount" in fields and fields["amount"] is not None:
            is_valid, amount_normalized, error_msg = self._validate_and_normalize_amount(fields["amount"])
            if not is_valid:
                raise ValueError(error_msg)
            fields["amount"] = amount_normalized
        
        # Xác thực ngày nếu được cập nhật
        if "date" in fields and fields["date"] is not None:
            is_valid, error_msg = self._validate_date(fields["date"])
            if not is_valid:
                raise ValueError(error_msg)
        
        # Cập nhật các trường
        for key, value in fields.items():
            if hasattr(tx, key) and value is not None:
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
