import xmlrpc.client

url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Find TEMP_POS product
product_ids = models.execute_kw(db, uid, password, 'product.template', 'search',
    [[('default_code', '=', 'TEMP_POS')]])

if product_ids:
    # Update taxes_id to include tax ID 56
    result = models.execute_kw(db, uid, password, 'product.template', 'write',
        [product_ids, {'taxes_id': [(6, 0, [56])]}])
    
    print(f"✅ Product updated: {result}")
    
    # Verify the update
    product = models.execute_kw(db, uid, password, 'product.template', 'read',
        [product_ids, ['name', 'default_code', 'taxes_id']])
    print(f"Product after update: {product}")
else:
    print("❌ TEMP_POS product not found")
