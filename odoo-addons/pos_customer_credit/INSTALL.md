### 4. Configurar el Punto de Venta

1. Ir a **Punto de Venta → Configuración → Punto de Venta**
2. Abrir tu configuración de POS existente
3. Ir a la pestaña **Cuenta Corriente**
4. Activar ✅ **Habilitar Cuenta Corriente**
5. En **Método de Pago CC**, seleccionar "Cuenta Corriente"
6. Activar ✅ **Requiere Cliente para CC** (recomendado)
7. Guardar

### 5. Configurar Métodos de Pago

1. Ir a **Punto de Venta → Configuración → Métodos de Pago**
2. Buscar "Cuenta Corriente" (se crea automáticamente)
3. Verificar que está marcado como ✅ **Es Pago con Cuenta Corriente**
4. Ir a tu configuración de POS
5. En la pestaña **Pagos**, agregar el método "Cuenta Corriente" si no está

## 🔧 Actualización del Módulo

Si ya tienes el módulo instalado y necesitas actualizar:

```powershell
# Actualizar el módulo
docker exec -it pos-odoo-1 odoo --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons -d odoo -u pos_customer_credit --stop-after-init

# Reiniciar Odoo
docker-compose restart odoo
```

## ✅ Verificación de la Instalación

### 1. Verificar que el módulo está instalado
- Ir a **Aplicaciones**
- Filtrar por "Instaladas"
- Buscar "POS Customer Credit"
- Debe aparecer con estado "Instalado"

### 2. Verificar menús
- Ir a **Punto de Venta**
- Debe aparecer un nuevo menú **Cuenta Corriente** con:
  - Movimientos de Crédito
  - Clientes con CC

### 3. Verificar en un cliente
- Ir a **Contactos**
- Abrir cualquier cliente
- Debe aparecer una nueva pestaña **Cuenta Corriente**

### 4. Verificar en POS
- Abrir el POS
- Agregar productos
- Seleccionar un cliente
- Ir a pantalla de **Pago**
- Debe aparecer:
  - Botón de **Cuenta Corriente** con el saldo del cliente
  - Método de pago "Cuenta Corriente" disponible

## 🎯 Prueba Rápida

### Crear una venta a crédito:

1. Abrir POS
2. Agregar productos (ej: 3 productos por $1000)
3. Seleccionar un cliente
4. Ir a **Pago**
5. Click en botón **Cuenta Corriente** para ver el saldo actual
6. Seleccionar método de pago **Cuenta Corriente**
7. Ingresar monto (puede ser parcial, ej: $500)
8. Agregar pago en **Efectivo** por el resto ($500)
9. **Validar**

### Verificar el resultado:

1. En **Contactos**, abrir el cliente
2. Ir a pestaña **Cuenta Corriente**
3. Debe mostrar:
   - Saldo: $500 (Debe)
   - 1 orden a crédito
   - Movimiento de venta por $500

### Registrar un pago:

1. Desde el cliente, click en **Registrar Pago**
2. El monto por defecto es -$500 (para saldar)
3. Puedes cambiarlo si es pago parcial
4. Click en **Confirmar**
5. El saldo se actualiza automáticamente

## 🐛 Solución de Problemas

### Error: "Module not found"
```powershell
# Verificar que el módulo está en el path correcto
docker exec -it pos-odoo-1 ls -la /mnt/extra-addons/pos_customer_credit

# Debe mostrar todos los archivos del módulo
```

### Error: "Access Denied"
```powershell
# Actualizar permisos de seguridad
docker exec -it pos-odoo-1 odoo --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons -d odoo -i pos_customer_credit --stop-after-init
```

### El módulo no aparece en Aplicaciones
1. Verificar que el modo desarrollador está activo
2. Actualizar lista de aplicaciones
3. Limpiar caché del navegador (Ctrl+F5)
4. Reiniciar Odoo

### JavaScript no carga en POS
```powershell
# Limpiar assets y reiniciar
docker-compose restart odoo
```
Luego en Odoo:
1. Ir a **Configuración → Técnico → Base de datos → Limpiar Assets**
2. Refrescar el navegador (Ctrl+F5)

## 📚 Documentación Adicional

- **README.md**: Documentación completa del módulo
- **Modelos**: Ver código en `models/`
- **Vistas**: Ver código en `views/`
- **JavaScript**: Ver código en `static/src/app/`

## 🔐 Usuarios y Permisos

El módulo usa los grupos estándar de POS:
- **Usuario POS**: Puede usar cuenta corriente, ver movimientos
- **Manager POS**: Acceso completo, puede modificar órdenes, ajustes manuales

## 📞 Soporte

Si encuentras algún problema:
1. Revisar logs: `docker logs pos-odoo-1`
2. Verificar configuración de POS
3. Consultar README.md para troubleshooting
