from datetime import datetime
from models.models import Budget
from repositories.repositories import BudgetRepository, TransactionRepository, CategoryRepository


class BudgetService:
    def __init__(self):
        self.budget_repo = BudgetRepository()
        self.tx_repo = TransactionRepository()
        self.category_repo = CategoryRepository()

    # ── Xác thực tháng ────────────────────────────────────

    def _validate_month(self, month_str):
        """
        Xác thực tháng nhập vào.
        - Kiểm tra định dạng YYYY-MM
        - Kiểm tra năm hợp lệ
        - Kiểm tra tháng (1-12)
        Trả về (is_valid: bool, error_message: str)
        """
        if not month_str or not isinstance(month_str, str):
            return False, "Tháng không được để trống."
        
        month_str = month_str.strip()
        
        # Kiểm tra độ dài và định dạng
        if len(month_str) != 7 or month_str[4] != '-':
            return False, "Định dạng tháng phải là YYYY-MM (ví dụ: 2026-06)."
        
        try:
            year_str, month_part = month_str.split('-')
            year = int(year_str)
            month = int(month_part)
        except (ValueError, IndexError):
            return False, "Định dạng tháng phải là YYYY-MM (ví dụ: 2026-06)."
        
        # Kiểm tra tháng (1-12)
        if not (1 <= month <= 12):
            return False, "Tháng phải nằm trong khoảng 1-12."
        
        # Kiểm tra năm (hợp lệ, không quá tương lai)
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 10:
            return False, f"Năm không hợp lệ. Vui lòng nhập năm từ 2000 đến {current_year + 10}."
        
        return True, ""

    # ── Đặt / Cập nhật budget ─────────────────────────────

    def set_budget(self, user_id, category_id, limit_amount, month):
        """
        Nếu đã có budget cho danh mục + tháng đó → cập nhật.
        Chưa có → tạo mới.
        """
        if limit_amount <= 0:
            raise ValueError("Hạn mức phải lớn hơn 0.")

        # Xác thực tháng
        is_valid, error_msg = self._validate_month(month)
        if not is_valid:
            raise ValueError(error_msg)

        category = self.category_repo.get_by_id(category_id)
        if category is None or category.type != "expense":
            raise ValueError("Chỉ có thể đặt ngân sách cho danh mục chi tiêu.")

        existing = self.budget_repo.get_by_category_and_month(user_id, category_id, month)
        if existing:
            existing.limit_amount = limit_amount
            return self.budget_repo.update(existing.id, existing)

        budget = Budget(
            id=0,
            user_id=user_id,
            category_id=category_id,
            limit_amount=limit_amount,
            month=month,
        )
        return self.budget_repo.add(budget)

    def delete_budget(self, budget_id, user_id):
        budget = self.budget_repo.get_by_id(budget_id)
        if budget is None or budget.user_id != user_id:
            raise ValueError("Budget không tồn tại hoặc không có quyền.")
        return self.budget_repo.delete(budget_id)

    # ── Query ─────────────────────────────────────────────

    def get_by_month(self, user_id, month):
        """Query budget theo tháng (xác thực tháng trước)."""
        is_valid, error_msg = self._validate_month(month)
        if not is_valid:
            raise ValueError(error_msg)
        return self.budget_repo.get_by_month(user_id, month)

    # ── Kiểm tra toàn bộ budget trong tháng ──────────────

    def get_month_status(self, user_id, month):
        """
        Trả về LinkedList các dict, mỗi phần tử là trạng thái
        của 1 danh mục trong tháng:
        {
          category_id, category_name,
          limit_amount, spent, remaining,
          percent_used, over_budget
        }
        """
        from models.linked_list import LinkedList

        # Xác thực tháng
        is_valid, error_msg = self._validate_month(month)
        if not is_valid:
            raise ValueError(error_msg)

        budgets = self.budget_repo.get_by_month(user_id, month)
        result = LinkedList()

        for budget in budgets:
            spent = self.tx_repo.get_expense_by_category_in_month(
                user_id, budget.category_id, month
            )
            category = self.category_repo.get_by_id(budget.category_id)
            remaining = budget.limit_amount - spent
            percent_used = round((spent / budget.limit_amount) * 100, 1) if budget.limit_amount > 0 else 0.0

            result.append({
                "category_id": budget.category_id,
                "category_name": category.name if category else f"ID {budget.category_id}",
                "limit_amount": budget.limit_amount,
                "spent": spent,
                "remaining": remaining,
                "percent_used": percent_used,
                "over_budget": spent > budget.limit_amount,
            })

        return result

    def get_over_budget_categories(self, user_id, month):
        """Chỉ trả về các danh mục đã vượt hạn mức."""
        status = self.get_month_status(user_id, month)
        return status.filter(lambda s: s["over_budget"])
