#!/usr/bin/env python3
"""
Script para recalcular los saldos de las cuentas corrientes
"""
import xmlrpc.client

# Configuración de conexión
url = "http://localhost:8069"
db = "odoo"
username = "admin"
password = "admin"

# Conectar
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✓ Conectado como usuario {uid}")
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Buscar todos los movimientos
    move_ids = models.execute_kw(db, uid, password,
        'customer.account.move', 'search', [[]])
    
    print(f"✓ Encontrados {len(move_ids)} movimientos")
    
    # Forzar recálculo
    if move_ids:
        # Leer y escribir para forzar recálculo del campo computed
        models.execute_kw(db, uid, password,
            'customer.account.move', 'write',
            [move_ids, {}])
        
        print(f"✓ Saldos recalculados para {len(move_ids)} movimientos")
        
        # Mostrar movimientos
        moves = models.execute_kw(db, uid, password,
            'customer.account.move', 'read',
            [move_ids, ['date', 'description', 'debit', 'credit', 'balance']])
        
        print("\nMovimientos:")
        for move in sorted(moves, key=lambda x: x['date']):
            print(f"  {move['date']}: {move['description']}")
            print(f"    Debe: {move['debit']}, Haber: {move['credit']}, Saldo: {move['balance']}")
    else:
        print("✗ No hay movimientos para recalcular")
        
else:
    print("✗ Error de autenticación")
