import json
from collections import OrderedDict

CATEGORY_DEFS = [
    {"name": "Ăn uống", "type": "expense"},
    {"name": "Chi tiêu hàng ngày", "type": "expense"},
    {"name": "Quần áo", "type": "expense"},
    {"name": "Mỹ phẩm", "type": "expense"},
    {"name": "Phí giao lưu", "type": "expense"},
    {"name": "Y tế", "type": "expense"},
    {"name": "Giáo dục", "type": "expense"},
    {"name": "Tiền điện", "type": "expense"},
    {"name": "Đi lại", "type": "expense"},
    {"name": "Phí liên lạc", "type": "expense"},
    {"name": "Tiền nhà", "type": "expense"},
    {"name": "Tiền lương", "type": "income"},
    {"name": "Tiền phụ cấp", "type": "income"},
    {"name": "Tiền thưởng", "type": "income"},
    {"name": "Thu nhập phụ", "type": "income"},
    {"name": "Đầu tư", "type": "income"},
]

# Load old categories to build mapping
with open('data/categories.json', 'r', encoding='utf-8') as f:
    old_categories = json.load(f)

old_category_map = {(c['name'], c['type']): c['id'] for c in old_categories}
reverse_map = {c['id']: (c['name'], c['type']) for c in old_categories}

new_categories = []
new_id_map = {}
for new_id, cat in enumerate(CATEGORY_DEFS, start=1):
    new_categories.append({"id": new_id, "name": cat['name'], "type": cat['type']})
    old_id = old_category_map.get((cat['name'], cat['type']))
    if old_id is not None:
        # If there are multiple old IDs, choose the first one
        new_id_map[old_id] = new_id

# Handle duplicated old IDs for same name/type if there are several per user
for old_id, info in reverse_map.items():
    if info in old_category_map and new_id_map.get(old_id) is None:
        new_id_map[old_id] = [nid for nid, cat in enumerate(CATEGORY_DEFS, start=1)
                              if (cat['name'], cat['type']) == info][0]

# Save categories.json as global categories
with open('data/categories.json', 'w', encoding='utf-8') as f:
    json.dump(new_categories, f, ensure_ascii=False, indent=2)

print('Saved data/categories.json with', len(new_categories), 'global categories.')

# Helper for category ID translation
category_id_mapping = {}
for old_cat in old_categories:
    key = (old_cat['name'], old_cat['type'])
    new_id = next((n['id'] for n in new_categories if n['name'] == key[0] and n['type'] == key[1]), None)
    if new_id is None:
        raise ValueError(f'No mapping for old category {key}')
    category_id_mapping[old_cat['id']] = new_id

# Update transactions
with open('data/transactions.json', 'r', encoding='utf-8') as f:
    transactions = json.load(f)
updated_transactions = []
missing = set()
for tx in transactions:
    old_id = tx['category_id']
    if old_id in category_id_mapping:
        tx['category_id'] = category_id_mapping[old_id]
    else:
        missing.add(old_id)
    updated_transactions.append(tx)

with open('data/transactions.json', 'w', encoding='utf-8') as f:
    json.dump(updated_transactions, f, ensure_ascii=False, indent=2)

print('Updated transactions: total', len(updated_transactions), 'missing category_ids:', sorted(missing))

# Update budgets
with open('data/budgets.json', 'r', encoding='utf-8') as f:
    budgets = json.load(f)
updated_budgets = []
missing_budget = set()
for b in budgets:
    old_id = b['category_id']
    if old_id in category_id_mapping:
        b['category_id'] = category_id_mapping[old_id]
    else:
        missing_budget.add(old_id)
    updated_budgets.append(b)

with open('data/budgets.json', 'w', encoding='utf-8') as f:
    json.dump(updated_budgets, f, ensure_ascii=False, indent=2)

print('Updated budgets: total', len(updated_budgets), 'missing category_ids:', sorted(missing_budget))
