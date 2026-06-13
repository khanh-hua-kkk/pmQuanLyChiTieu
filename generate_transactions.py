import json
import random
from datetime import datetime, timedelta

# Load existing transactions
with open('data/transactions.json', 'r', encoding='utf-8') as f:
    transactions = json.load(f)

# Load categories to see what categories exist
with open('data/categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

# Get category IDs for user_id 6 (49-64)
# Expense: 49-58, Income: 59-64
category_ids_expense = [49, 50, 51, 52, 53, 54, 55, 56, 57, 58]  # expense categories for user 6
category_ids_income = [59, 60, 61, 62, 63, 64]  # income categories for user 6

# Get the last ID
last_id = max(t['id'] for t in transactions)

# Generate 1000 new transactions
start_date = datetime.now() - timedelta(days=90)  # Last 3 months
notes = ["", "", "", "Mua đồ ăn", "Xăng xe", "Nhà hàng", "Thuốc", "Điện thoại", "Internet", "Sửa xe"]

for i in range(1000):
    new_id = last_id + i + 1
    
    # 80% expense, 20% income
    if random.random() < 0.8:
        transaction_type = "expense"
        category_id = random.choice(category_ids_expense)
        amount = random.uniform(10000, 2000000)
    else:
        transaction_type = "income"
        category_id = random.choice(category_ids_income)
        amount = random.uniform(500000, 5000000)
    
    # Generate random date within last 3 months
    random_date = start_date + timedelta(days=random.randint(0, 90))
    date_str = random_date.strftime('%Y-%m-%d')
    
    # Generate created_at timestamp
    created_at = random_date.strftime('%Y-%m-%d %H:%M:%S')
    
    transaction = {
        "id": new_id,
        "user_id": 6,
        "category_id": category_id,
        "amount": round(amount, 2),
        "type": transaction_type,
        "note": random.choice(notes),
        "date": date_str,
        "created_at": created_at
    }
    
    transactions.append(transaction)

# Save back to transactions.json
with open('data/transactions.json', 'w', encoding='utf-8') as f:
    json.dump(transactions, f, ensure_ascii=False, indent=2)

print(f"✓ Đã tạo 1000 transactions mới!")
print(f"Tổng transactions hiện tại: {len(transactions)}")
print(f"ID từ 12 đến {last_id + 1000}")
