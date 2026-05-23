from models.models import Budget
from repositories.repositories import BudgetRepository, TransactionRepository, CategoryRepository


class BudgetService:
    def __init__(self):
        self.budget_repo = BudgetRepository()
        self.tx_repo = TransactionRepository()
        self.category_repo = CategoryRepository()

    # ── Đặt / Cập nhật budget ─────────────────────────────

    def set_budget(self, user_id, category_id, limit_amount, month):
        """
        Nếu đã có budget cho danh mục + tháng đó → cập nhật.
        Chưa có → tạo mới.
        """
        if limit_amount <= 0:
            raise ValueError("Hạn mức phải lớn hơn 0.")

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
