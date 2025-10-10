# Ejemplos de Uso - POS Customer Credit

Este documento contiene ejemplos prácticos de uso del módulo de Cuenta Corriente.

## 📌 Caso de Uso 1: Venta Simple a Crédito

**Situación**: Cliente compra $5,000 en productos y paga todo con cuenta corriente.

### Proceso:
1. **En POS**:
   - Agregar productos (total: $5,000)
   - Seleccionar cliente "Juan Pérez"
   - Ir a Pago
   - Click en botón "Cuenta Corriente" → muestra saldo actual: $0
   - Seleccionar método de pago "Cuenta Corriente"
   - Ingresar $5,000
   - Validar

2. **Resultado**:
   - Cliente debe: $5,000
   - Se crea 1 movimiento de tipo "Venta a Crédito"
   - La orden queda registrada con `has_credit_payment = True`

### Verificación en Backend:
```
Cliente "Juan Pérez"
├── Saldo CC: $5,000 (Debe)
├── Total órdenes: 1
└── Movimientos:
    └── Venta a Crédito: +$5,000
```

---

## 📌 Caso de Uso 2: Venta con Pago Combinado

**Situación**: Cliente compra $10,000. Paga $4,000 en efectivo y $6,000 con cuenta corriente.

### Proceso:
1. **En POS**:
   - Agregar productos (total: $10,000)
   - Seleccionar cliente "María García"
   - Ir a Pago
   - Seleccionar "Efectivo" → Ingresar $4,000
   - Seleccionar "Cuenta Corriente" → Ingresar $6,000
   - Validar

2. **Resultado**:
   - Cliente debe: $6,000
   - Orden tiene:
     - `has_credit_payment = True`
     - `credit_amount = $6,000`
     - `cash_amount = $4,000`

### Cálculos Importantes:
- Proporción de CC: 60% ($6,000 / $10,000)
- Si se agregan $1,000 de productos → Deuda aumenta $600
- Si se quitan $1,000 de productos → Deuda reduce $600

---

## 📌 Caso de Uso 3: Cliente Quita Productos (Orden con CC)

**Situación**: Cliente compró $5,000 con CC. Ahora devuelve productos por $2,000.

### Proceso:
1. **En Backend**:
   - Ir a la orden del cliente
   - Click en "Modificar Orden"
   - En la lista de productos, identificar los que se devuelven
   - Cambiar cantidad a 0 o usar wizard de modificación
   - Guardar

2. **Cálculo Automático**:
   ```
   Monto original: $5,000
   Productos devueltos: $2,000
   
   Movimiento creado:
   - Tipo: "Productos Removidos"
   - Monto: -$2,000 (reduce deuda)
   
   Nuevo saldo de la orden: $3,000
   ```

3. **Resultado**:
   - `current_products_value = $3,000`
   - `credit_amount_due = $3,000`
   - `is_modified = True`
   - Inventario se devuelve automáticamente

---

## 📌 Caso de Uso 4: Cliente Agrega Productos (Orden con CC)

**Situación**: Cliente compró $5,000 con CC. Ahora quiere agregar $1,500 más.

### Proceso:
1. **En Backend**:
   - Ir a la orden del cliente
   - Click en "Modificar Orden"
   - Agregar nuevos productos por $1,500
   - Guardar

2. **Cálculo Automático**:
   ```
   Monto original: $5,000 (100% CC)
   Productos agregados: $1,500
   
   Movimiento creado:
   - Tipo: "Productos Agregados"
   - Monto: +$1,500 (aumenta deuda)
   
   Nuevo saldo de la orden: $6,500
   ```

3. **Resultado**:
   - `current_products_value = $6,500`
   - `credit_amount_due = $6,500`
   - Inventario se reduce automáticamente

---

## 📌 Caso de Uso 5: Orden 100% Efectivo - Solo Puede Quitar

**Situación**: Cliente pagó $3,000 en efectivo. Devuelve productos por $1,000.

### Proceso:
1. **En Backend**:
   - Ir a la orden
   - Click en "Modificar Orden" → Mensaje indica "Solo puede quitar productos"
   - Quitar productos por $1,000
   - Guardar

2. **Cálculo Automático**:
   ```
   Pago original: $3,000 efectivo
   Productos devueltos: $1,000
   
   Movimiento creado:
   - Tipo: "Productos Removidos"
   - Monto: -$1,000 (genera crédito A FAVOR)
   
   Saldo del cliente: -$1,000 (A favor)
   ```

3. **Resultado**:
   - Cliente tiene $1,000 a favor para próxima compra
   - `credit_amount_due = -$1,000`

### ⚠️ Importante:
Si intenta AGREGAR productos a orden 100% efectivo:
- ❌ **ERROR**: "No se pueden agregar productos a orden pagada 100% en efectivo"
- ✅ **Solución**: Crear nueva venta

---

## 📌 Caso de Uso 6: Pago Combinado - Agregar Productos

**Situación**: Cliente pagó $10,000 ($4,000 efectivo + $6,000 CC). Agrega $2,000 de productos.

### Cálculo de Proporción:
```
Pago original:
- Efectivo: $4,000 (40%)
- CC: $6,000 (60%)

Productos agregados: $2,000

Distribución proporcional:
- Aumento en CC: $2,000 × 60% = $1,200
- (Efectivo no cambia)

Nueva deuda CC: $6,000 + $1,200 = $7,200
```

---

## 📌 Caso de Uso 7: Registrar Pago del Cliente

**Situación**: Cliente debe $8,500. Paga $5,000.

### Proceso:
1. **Desde el Cliente**:
   - Ir a Contactos → Abrir cliente
   - Pestaña "Cuenta Corriente"
   - Click en "Registrar Pago"
   
2. **En el Formulario**:
   ```
   Cliente: Juan Pérez
   Tipo: Pago Recibido
   Monto: -$5,000 (negativo para reducir deuda)
   Descripción: "Pago parcial - Efectivo"
   ```
   - Click en "Confirmar"

3. **Resultado**:
   ```
   Saldo anterior: $8,500
   Pago recibido: -$5,000
   Nuevo saldo: $3,500
   ```

### Pago Total:
Para saldar completamente:
```
Monto: -$8,500
Descripción: "Pago total - Transferencia"
Nuevo saldo: $0
```

---

## 📌 Caso de Uso 8: Generar PDF de Orden

**Situación**: Necesitas enviar al cliente el detalle de su compra con saldo actual.

### Proceso:
1. **En Backend**:
   - Ir a Punto de Venta → Órdenes
   - Abrir la orden del cliente
   - Click en "PDF con Saldo"

2. **El PDF incluye**:
   - Número de orden y fecha
   - Datos del cliente
   - **Alerta si está modificada** (muestra monto original)
   - Productos actuales (solo qty > 0)
   - Totales:
     - Total actual
     - Pagado en efectivo
     - Pagado con CC
     - Saldo de esta orden
     - Saldo total del cliente
   - Historial de modificaciones (si aplica)

---

## 📌 Caso de Uso 9: Facturación Opcional

**Situación**: Cliente pide factura después de la venta.

### Proceso:
1. **Generar Factura**:
   - Ir a la orden POS
   - Click en "Factura" (método estándar de Odoo)
   - Confirmar factura

2. **Modificar Orden Después**:
   - Cliente agrega productos por $1,000
   - Sistema detecta que factura está desactualizada
   - Muestra alerta: ⚠️ "Factura Desactualizada"

3. **Regenerar Factura**:
   - Cancelar factura anterior
   - Generar nueva factura desde orden actualizada

### ⚠️ Reglas Importantes:
- ✅ Factura NO modifica saldo CC
- ✅ Saldo se calcula solo desde movimientos de crédito
- ⚠️ Si orden se modifica, factura queda desactualizada
- ❌ No se puede editar factura vinculada a orden modificada

---

## 📌 Caso de Uso 10: Ver Todo lo que Debe un Cliente

### Opción 1: Vista Rápida en POS
1. En POS, seleccionar cliente
2. Click en botón "Cuenta Corriente"
3. Ver:
   - Saldo total actual
   - Últimos 10 movimientos
   - Total de órdenes

### Opción 2: Vista Completa en Backend
1. Ir a Contactos → Cliente
2. Pestaña "Cuenta Corriente"
3. Ver:
   - Saldo total
   - Deuda pendiente
   - Total de órdenes a crédito
   - Todos los movimientos con filtros

### Opción 3: Ver Órdenes Específicas
1. Desde el cliente, click en "Ver Órdenes a Crédito"
2. Lista de todas las órdenes con CC
3. Para cada orden ver:
   - Productos actuales
   - Saldo de esa orden
   - Si fue modificada

---

## 📌 Caso de Uso 11: Cambio de Productos

**Situación**: Cliente cambió de opinión, quiere cambiar producto A por producto B.

### Método 1: Quitar + Nueva Venta (100% Efectivo)
1. Quitar producto A de orden original
2. Crear nueva venta con producto B
3. Cliente tiene crédito a favor de orden original

### Método 2: Quitar + Agregar (Con CC)
1. Abrir orden original (debe tener CC)
2. Quitar producto A (reduce deuda)
3. Agregar producto B (aumenta deuda)
4. Todo en la misma orden

---

## 📊 Reportes y Análisis

### Ver Todos los Movimientos de Crédito
```
Punto de Venta → Cuenta Corriente → Movimientos de Crédito

Filtros disponibles:
- Por tipo (Ventas, Pagos, Modificaciones)
- Por estado (Confirmados, Borradores)
- Por fecha (Este mes, etc.)
- Por cliente
- Por orden

Agrupar por:
- Cliente
- Orden
- Tipo de movimiento
- Fecha
```

### Ver Clientes con Deuda
```
1. Ir a Contactos
2. Buscar clientes
3. Ordenar por "Saldo CC" (descendente)
4. Los primeros son los que más deben
```

### Ver Órdenes Modificadas
```
Punto de Venta → Órdenes
Filtro: "Órdenes Modificadas"

Muestra:
- Todas las órdenes que fueron modificadas
- Cuáles tienen facturas desactualizadas
```

---

## 🎯 Tips y Mejores Prácticas

### 1. Siempre Seleccionar Cliente
- Activa "Requiere Cliente para CC" en configuración
- Evita errores y mejora trazabilidad

### 2. Revisar Saldo Antes de Vender
- Click en botón "Cuenta Corriente" antes de confirmar venta
- Ver si cliente ya tiene deuda acumulada

### 3. Documentar Pagos
- Usar descripción clara: "Pago efectivo", "Transferencia", etc.
- Facilita auditorías y seguimiento

### 4. Generar PDF para Cliente
- Al entregar productos, genera PDF con saldo
- Cliente tiene registro claro de su deuda

### 5. Revisar Movimientos Regularmente
- Verificar que todos los movimientos estén confirmados
- Usar filtros para detectar anomalías

### 6. Backup Regular
- El saldo se calcula desde los movimientos
- Importante tener backups de la base de datos

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo establecer un límite de crédito por cliente?**
R: El módulo permite crédito sin límite por defecto. Si necesitas límites, puedes agregar validación en el código.

**P: ¿Qué pasa si borro una orden con CC?**
R: Los movimientos de crédito asociados se mantienen por trazabilidad. Debes crear un ajuste manual si necesitas corregir el saldo.

**P: ¿Puedo usar múltiples monedas?**
R: El módulo usa la moneda de la compañía. Soporte multi-moneda requeriría modificaciones.

**P: ¿Se integra con módulos de facturación AFIP?**
R: La facturación es independiente del saldo CC. El módulo AFIP genera la factura, pero el saldo se maneja por separado.

**P: ¿Cómo afecta al inventario?**
R: El módulo implementa lógica básica. Para control de inventario completo, se recomienda integrar con módulos de stock de Odoo.
