import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search for tax ID 56 specifically
tax_56 = models.execute_kw(db, uid, password, 'account.tax', 'search_read', 
    [[('id', '=', 56)]], 
    {'fields': ['id', 'name', 'type_tax_use', 'amount', 'company_id']})

print("Tax ID 56:")
for t in tax_56:
    print(f"  ID: {t['id']}, Name: {t['name']}, Type: {t['type_tax_use']}, Amount: {t['amount']}, Company: {t['company_id']}")

# Now search for TEMP_POS product
product = models.execute_kw(db, uid, password, 'product.template', 'search_read',
    [[('default_code', '=', 'TEMP_POS')]],
    {'fields': ['id', 'name', 'default_code', 'taxes_id']})

print("\nTEMP_POS product:")
for p in product:
    print(f"  ID: {p['id']}, Name: {p['name']}, Code: {p['default_code']}, Taxes: {p['taxes_id']}")
