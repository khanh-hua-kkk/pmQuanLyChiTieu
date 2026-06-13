import json

with open('data/categories.json', encoding='utf-8') as f:
    categories = json.load(f)

with open('data/transactions.json', encoding='utf-8') as f:
    transactions = json.load(f)

print('═ CATEGORIES DISTRIBUTION ═')
user_categories = {}
for cat in categories:
    uid = cat['user_id']
    if uid not in user_categories:
        user_categories[uid] = []
    user_categories[uid].append({
        'id': cat['id'], 
        'name': cat['name'], 
        'type': cat['type']
    })

for uid in sorted(user_categories.keys()):
    cats = user_categories[uid]
    print(f'\n👤 User {uid}: {len(cats)} categories')
    for cat in cats[:5]:
        print(f'   • {cat["id"]}: {cat["name"]} ({cat["type"]})')
    if len(cats) > 5:
        print(f'   ... và {len(cats) - 5} categories khác')

print('\n═ TRANSACTIONS ANALYSIS ═')
user_txs = {}
for tx in transactions:
    uid = tx['user_id']
    if uid not in user_txs:
        user_txs[uid] = {'count': 0, 'categories': set()}
    user_txs[uid]['count'] += 1
    user_txs[uid]['categories'].add(tx['category_id'])

for uid in sorted(user_txs.keys()):
    data = user_txs[uid]
    print(f'\n👤 User {uid}:')
    print(f'   📊 Transactions: {data["count"]}')
    print(f'   📂 Categories used: {sorted(data["categories"])}')
    
    # Check if categories exist
    used_cats = [c for c in user_categories.get(uid, []) if c['id'] in data['categories']]
    print(f'   ✓ Categories found in DB: {len(used_cats)}')
    for cat in used_cats[:5]:
        print(f'      • {cat["id"]}: {cat["name"]}')
    if len(used_cats) > 5:
        print(f'      ... và {len(used_cats) - 5} categories khác')
