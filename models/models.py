from datetime import datetime
from models.linked_list import LinkedList


class User:
    def __init__(self, id, name, email, password, currency="VND", created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.currency = currency
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "currency": self.currency,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            password=data["password"],
            currency=data.get("currency", "VND"),
            created_at=data.get("created_at"),
        )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"


# ─────────────────────────────────────────────


class Category:
    # type: "income" | "expense" | "both"
    def __init__(self, id, user_id, name, type="both"):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.type = type

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            name=data["name"],
            type=data.get("type", "both"),
        )

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name}, type={self.type})"


# ─────────────────────────────────────────────


class Transaction:
    # type: "income" | "expense"
    def __init__(self, id, user_id, category_id, amount, type, note="", date=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.category_id = category_id
        self.amount = float(amount)
        self.type = type
        self.note = note
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "amount": self.amount,
            "type": self.type,
            "note": self.note,
            "date": self.date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            category_id=data["category_id"],
            amount=data["amount"],
            type=data["type"],
            note=data.get("note", ""),
            date=data.get("date"),
            created_at=data.get("created_at"),
        )

    def __repr__(self):
        return f"Transaction(id={self.id}, type={self.type}, amount={self.amount})"


# ─────────────────────────────────────────────


class Budget:
    # month: "YYYY-MM"  vd "2026-05"
    def __init__(self, id, user_id, category_id, limit_amount, month, created_at=None):
        self.id = id
        self.user_id = user_id
        self.category_id = category_id
        self.limit_amount = float(limit_amount)
        self.month = month
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "limit_amount": self.limit_amount,
            "month": self.month,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            category_id=data["category_id"],
            limit_amount=data["limit_amount"],
            month=data["month"],
            created_at=data.get("created_at"),
        )

    def __repr__(self):
        return f"Budget(id={self.id}, month={self.month}, limit={self.limit_amount})"


# ─────────────────────────────────────────────


class Report:
    # period_type: "day" | "week" | "month" | "quarter" | "year" | "custom"
    def __init__(self, id, user_id, start_date, end_date, period_type,
                 total_income=0.0, total_expense=0.0, created_at=None):
        self.id = id
        self.user_id = user_id
        self.start_date = start_date          # "YYYY-MM-DD"
        self.end_date = end_date              # "YYYY-MM-DD"
        self.period_type = period_type
        self.total_income = float(total_income)
        self.total_expense = float(total_expense)
        self.balance = self.total_income - self.total_expense
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Danh sách tên danh mục vượt budget — tự cài LinkedList
        self.over_budget_categories = LinkedList()

        # Chi tiết từng danh mục: LinkedList chứa dict
        # { category_name, spent, budget_limit, percentage }
        self.category_summaries = LinkedList()

    def add_category_summary(self, category_name, spent, budget_limit):
        percentage = round((spent / self.total_expense * 100), 2) if self.total_expense > 0 else 0.0
        over = spent > budget_limit if budget_limit > 0 else False
        summary = {
            "category_name": category_name,
            "spent": spent,
            "budget_limit": budget_limit,
            "percentage": percentage,
            "over_budget": over,
        }
        self.category_summaries.append(summary)
        if over:
            self.over_budget_categories.append(category_name)

    def recalculate_balance(self):
        self.balance = self.total_income - self.total_expense

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "period_type": self.period_type,
            "total_income": self.total_income,
            "total_expense": self.total_expense,
            "balance": self.balance,
            "created_at": self.created_at,
            # Chuyển LinkedList → list để lưu JSON
            "over_budget_categories": self.over_budget_categories.to_list(),
            "category_summaries": self.category_summaries.to_list(),
        }

    @classmethod
    def from_dict(cls, data):
        report = cls(
            id=data["id"],
            user_id=data["user_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            period_type=data["period_type"],
            total_income=data.get("total_income", 0.0),
            total_expense=data.get("total_expense", 0.0),
            created_at=data.get("created_at"),
        )
        # Khôi phục LinkedList từ JSON list
        for name in data.get("over_budget_categories", []):
            report.over_budget_categories.append(name)
        for summary in data.get("category_summaries", []):
            report.category_summaries.append(summary)
        return report

    def __repr__(self):
        return (f"Report(id={self.id}, period={self.period_type}, "
                f"{self.start_date} → {self.end_date})")
