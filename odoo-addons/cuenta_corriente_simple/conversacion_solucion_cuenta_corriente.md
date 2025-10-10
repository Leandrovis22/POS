# Conversación: Solución para Sistema de Cuenta Corriente
**Fecha:** 10 de Octubre, 2025

---

## Usuario:
ok pero tengo que poder ubicar facilmente y unificadamente todos los productos actualizados separado por cada compra de cada cliente, no se que hacer

---

## Asistente:

Entiendo perfectamente tu necesidad. El problema real es **TRAZABILIDAD**: Necesitas ver rápidamente qué productos tiene cada cliente de cada compra, especialmente después de cambios.

### ANÁLISIS DE TU NECESIDAD:

**Lo que necesitas:**
```
Cliente: Juan Pérez
  
  Compra 1 (15/09/2025): ORDER/00123
    Estado: Debe $4,950
    Productos actuales:
    - Producto A x10
    - Producto B x5
    - Producto C x3
    (Hubo cambios: originalmente eran 30 productos por $5,000)
  
  Compra 2 (20/09/2025): ORDER/00145
    Estado: Debe $2,300
    Productos actuales:
    - Producto D x15
    - Producto E x8
```

**Necesitas ver:**
1. ✅ Todas las compras de un cliente
2. ✅ Qué productos tiene ACTUALMENTE en cada compra
3. ✅ Cuánto debe de cada compra
4. ✅ Historial de cambios

### PROBLEMA FUNDAMENTAL:

El modelo `pos.order` en Odoo tiene un **límite técnico**:

```python
# Las líneas de orden son:
pos.order.line
  ├─ product_id
  ├─ qty
  ├─ price_unit
  └─ order_id

# Pero estas líneas son INMUTABLES después de confirmar
# Modificarlas puede romper reportes, inventario, etc.
```

### SOLUCIÓN: Sistema de "Versiones de Productos"

En lugar de modificar la orden original, crear un **registro paralelo** de "estado actual":

#### Nueva tabla: `pos.order.current.state`

```python
class PosOrderCurrentState(models.Model):
    _name = 'pos.order.current.state'
    
    order_id = fields.Many2one('pos.order')
    product_id = fields.Many2one('product.product')
    qty = fields.Float('Cantidad Actual')
    price_unit = fields.Float('Precio Unitario')
    price_subtotal = fields.Float(compute='_compute_subtotal')
    
    # Historial
    original_qty = fields.Float('Cantidad Original')
    changes_history = fields.Text('Historial de Cambios')
```

#### Vista unificada para el cliente:

```
┌──────────────────────────────────────────────────────┐
│  Cliente: Juan Pérez - Saldo Total: $7,250          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  📦 COMPRA: ORDER/00123 (15/09/2025)                │
│  Estado: Debe $4,950                                │
│  ──────────────────────────────────────────────────  │
│  PRODUCTOS ACTUALES:                                │
│  • Producto A x10  $1,500  [Editar]                 │
│  • Producto B x5   $2,500  [Editar]                 │
│  • Producto C x3   $950    [Editar]                 │
│                                                      │
│  💡 Cambios realizados:                             │
│    - 16/09: Quitó Producto D x5 (-$500)            │
│    - 18/09: Agregó Producto C x1 (+$450)           │
│  ──────────────────────────────────────────────────  │
│  [Ver Orden Original] [Editar Productos] [Cancelar]│
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  📦 COMPRA: ORDER/00145 (20/09/2025)                │
│  Estado: Debe $2,300                                │
│  ──────────────────────────────────────────────────  │
│  PRODUCTOS ACTUALES:                                │
│  • Producto D x15  $1,500  [Editar]                 │
│  • Producto E x8   $800    [Editar]                 │
│                                                      │
│  💡 Sin cambios                                      │
│  ──────────────────────────────────────────────────  │
│  [Ver Orden Original] [Editar Productos] [Cancelar]│
│                                                      │
└──────────────────────────────────────────────────────┘
```

### ARQUITECTURA PROPUESTA:

#### 1. Al crear orden POS:
```python
def _process_order(self, order, existing_order):
    # ... código existente ...
    
    # Crear snapshot del estado actual
    for line in pos_order.lines:
        self.env['pos.order.current.state'].create({
            'order_id': pos_order.id,
            'product_id': line.product_id.id,
            'qty': line.qty,
            'original_qty': line.qty,
            'price_unit': line.price_unit,
        })
```

#### 2. Al editar productos:
```python
class PosOrderEditWizard(models.TransientModel):
    
    current_products = fields.One2many(
        'pos.order.current.state', 
        related='order_id.current_state_ids'
    )
    
    def action_update_products(self):
        # Actualizar pos.order.current.state
        # NO tocar pos.order.lines (queda como histórico)
        # Crear ajuste en CC por la diferencia
        # Registrar cambio en historial
```

#### 3. Vista del cliente:
```xml
<page string="Compras con Cuenta Corriente (LV)">
    <field name="pos_order_ids" domain="[('is_credit_sale', '=', True)]">
        <tree>
            <field name="name"/>
            <field name="date_order"/>
            <field name="amount_total_current"/> <!-- Monto actual -->
            <field name="amount_total"/> <!-- Monto original -->
            <button name="action_view_current_products" 
                    string="Ver Productos Actuales"
                    type="object"/>
        </tree>
    </field>
</page>
```

### VENTAJAS DE ESTE SISTEMA:

✅ **Orden original INTACTA:** No rompe nada de Odoo
✅ **Estado actual CLARO:** Ves productos actualizados fácilmente
✅ **Historial completo:** Sabes qué cambió y cuándo
✅ **Por cliente:** Vista unificada de todas sus compras
✅ **Por compra:** Productos actuales de cada orden
✅ **Auditable:** Mantienes registro de todo
✅ **Sin conflictos:** Facturas pueden existir o no

### FLUJO COMPLETO:

```
Día 1: Cliente compra 30 productos
    ↓
pos.order.lines: 30 líneas (INMUTABLE)
pos.order.current.state: 30 líneas (EDITABLE)
CC: Débito $5,000
    ↓
Día 3: Cliente cambia 3 productos
    ↓
Usuario: "Editar Productos" desde la orden
Wizard muestra: current.state (30 productos)
Usuario: Quita 3, agrega 2
    ↓
current.state: Actualizado a 29 productos
pos.order.lines: SIN TOCAR (30 productos originales)
CC: Crédito $200 (ajuste)
Historial: Registra cambio
    ↓
Vista del cliente muestra:
- Orden ORDER/00123
- Productos ACTUALES: 29 (desde current.state)
- Saldo: $4,800
- Historial: "Cambio 3 productos el 03/10"
```

### ¿TE GUSTA ESTA SOLUCIÓN?

**Características:**
- ✅ **Unificado:** Todo en un solo lugar por cliente
- ✅ **Actualizado:** Siempre ves productos actuales
- ✅ **Histórico:** Puedes ver qué cambió
- ✅ **Seguro:** No rompe estructura de Odoo
- ✅ **Visual:** Fácil de entender y usar

**Tiempo de implementación:** 60-90 minutos

---

## Usuario:
en retrospectiva mirando atras en todo lo que hicimos, cual crees que seria la mejor solucion a lo que quiero desde el inicio? como lo recrearias desde el inicio?

---

## Asistente:

Excelente pregunta. Déjame analizar **TODO** lo que necesitas y diseñar la solución óptima desde cero:

### TUS NECESIDADES REALES (según toda nuestra conversación):

1. ✅ Clientes compran a crédito sin límite por defecto
2. ✅ ~15 ventas/día, 30-50 productos por venta
3. ✅ **NO quieres facturar todo** (hace el POS lento)
4. ✅ Clientes vuelven a **cambiar productos** frecuentemente
5. ✅ Necesitas ver **productos actuales** por compra
6. ✅ Necesitas saber **cuánto debe cada cliente**
7. ✅ Eventual facturación AFIP para algunos casos
8. ✅ **Simplicidad** (no sistema contable complejo)
9. ✅ **Velocidad** en el punto de venta

### ERRORES EN EL ENFOQUE ACTUAL:

❌ **Usar Odoo POS como base:** POS está diseñado para ventas rápidas cerradas, no para crédito con cambios frecuentes
❌ **Separar orden/factura:** Genera dos fuentes de verdad que se dessincronizan
❌ **Intentar modificar órdenes POS:** Son inmutables por diseño
❌ **Cuenta Corriente separada de productos:** Sabes cuánto debe pero no QUÉ tiene

### LA SOLUCIÓN ÓPTIMA DESDE CERO:

#### Concepto: "Sistema de Pedidos a Crédito"

NO es POS tradicional, es un **módulo de gestión de crédito** integrado con POS.

### ARQUITECTURA IDEAL:

#### Modelo Principal: `credit.sale.order` (Pedido a Crédito)

```python
class CreditSaleOrder(models.Model):
    _name = 'credit.sale.order'
    _description = 'Pedido de Venta a Crédito'
    
    # Identificación
    name = fields.Char('Número', default=lambda self: _('Nuevo'))
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True)
    date_order = fields.Datetime('Fecha', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('partial', 'Entrega Parcial'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado')
    ])
    
    # Líneas de productos (EDITABLES siempre)
    line_ids = fields.One2many('credit.sale.order.line', 'order_id')
    
    # Totales
    amount_total = fields.Float(compute='_compute_totals', store=True)
    amount_paid = fields.Float(compute='_compute_paid')
    amount_due = fields.Float(compute='_compute_due')
    
    # Referencias
    pos_order_id = fields.Many2one('pos.order', 'Orden POS Original')
    invoice_ids = fields.One2many('account.move', 'credit_order_id')
    
    # Historial
    change_history = fields.One2many('credit.order.change', 'order_id')
    
    @api.depends('line_ids.price_subtotal')
    def _compute_totals(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('price_subtotal'))
    
    def action_confirm(self):
        """Confirmar el pedido y registrar en cuenta corriente"""
        self.state = 'confirmed'
        # Crear movimiento en CC
        self.env['customer.account.move'].create({
            'partner_id': self.partner_id.id,
            'credit_order_id': self.id,
            'debit': self.amount_total,
            'description': f'Pedido a crédito {self.name}',
        })
```

#### Líneas: `credit.sale.order.line` (Siempre editables)

```python
class CreditSaleOrderLine(models.Model):
    _name = 'credit.sale.order.line'
    
    order_id = fields.Many2one('credit.sale.order')
    product_id = fields.Many2one('product.product', 'Producto')
    qty_ordered = fields.Float('Cantidad Pedida')
    qty_delivered = fields.Float('Cantidad Entregada')
    price_unit = fields.Float('Precio')
    price_subtotal = fields.Float(compute='_compute_subtotal')
    
    # Historial de cambios
    original_qty = fields.Float('Cantidad Original')
    is_modification = fields.Boolean()
    
    @api.depends('qty_ordered', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.qty_ordered * line.price_unit
```

#### Historial: `credit.order.change`

```python
class CreditOrderChange(models.Model):
    _name = 'credit.order.change'
    
    order_id = fields.Many2one('credit.sale.order')
    date = fields.Datetime(default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    change_type = fields.Selection([
        ('add', 'Producto Agregado'),
        ('remove', 'Producto Quitado'),
        ('modify', 'Cantidad Modificada'),
    ])
    product_id = fields.Many2one('product.product')
    qty_change = fields.Float()
    amount_change = fields.Float()
    description = fields.Text()
```

### FLUJO DESDE EL POS:

#### 1. Venta en POS:

```python
# En POS, cuando detectas pago "Cuenta Corriente"
def _process_order(self, order, existing_order):
    # ... código normal de POS ...
    
    if has_credit_payment:
        # Crear pedido a crédito desde la orden POS
        credit_order = self.env['credit.sale.order'].create({
            'partner_id': pos_order.partner_id.id,
            'pos_order_id': pos_order.id,
            'state': 'confirmed',
        })
        
        # Copiar líneas
        for line in pos_order.lines:
            self.env['credit.sale.order.line'].create({
                'order_id': credit_order.id,
                'product_id': line.product_id.id,
                'qty_ordered': line.qty,
                'qty_delivered': line.qty,
                'original_qty': line.qty,
                'price_unit': line.price_unit,
            })
        
        # Confirmar y registrar en CC
        credit_order.action_confirm()
```

**Resultado:**
- ✅ Orden POS queda como "recibo/comprobante"
- ✅ Credit Sale Order es la "fuente de verdad" EDITABLE
- ✅ CC registra la deuda

### EDICIÓN DE PRODUCTOS:

#### Desde el pedido a crédito (NO desde POS order):

```xml
<record id="view_credit_sale_order_form" model="ir.ui.view">
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_edit_products" string="Editar Productos (LV)"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <group>
                    <field name="partner_id"/>
                    <field name="date_order"/>
                    <field name="amount_total"/>
                    <field name="amount_due"/>
                </group>
                
                <notebook>
                    <page string="Productos Actuales">
                        <field name="line_ids" editable="bottom">
                            <tree editable="bottom">
                                <field name="product_id"/>
                                <field name="qty_ordered"/>
                                <field name="price_unit"/>
                                <field name="price_subtotal"/>
                                <button name="remove_line" icon="fa-trash"/>
                            </tree>
                        </field>
                        <button name="add_product_line" string="+ Agregar Producto"/>
                    </page>
                    
                    <page string="Historial de Cambios">
                        <field name="change_history">
                            <tree>
                                <field name="date"/>
                                <field name="change_type"/>
                                <field name="product_id"/>
                                <field name="qty_change"/>
                                <field name="amount_change"/>
                                <field name="description"/>
                            </tree>
                        </field>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

#### Al modificar líneas:

```python
def write(self, vals):
    result = super().write(vals)
    
    if 'line_ids' in vals:
        for order in self:
            # Calcular diferencia
            old_total = order.amount_total
            order._compute_totals()
            new_total = order.amount_total
            difference = new_total - old_total
            
            if difference != 0:
                # Registrar cambio
                self.env['credit.order.change'].create({
                    'order_id': order.id,
                    'change_type': 'modify',
                    'amount_change': difference,
                    'description': f'Monto cambiado de {old_total} a {new_total}',
                })
                
                # Ajustar CC
                self.env['customer.account.move'].create({
                    'partner_id': order.partner_id.id,
                    'credit_order_id': order.id,
                    'debit': difference if difference > 0 else 0,
                    'credit': abs(difference) if difference < 0 else 0,
                    'description': f'Ajuste de {order.name}',
                })
    
    return result
```

### VISTA DEL CLIENTE:

```xml
<page string="Pedidos a Crédito (LV)">
    <field name="credit_order_ids">
        <tree>
            <field name="name"/>
            <field name="date_order"/>
            <field name="amount_total"/>
            <field name="amount_due" decoration-danger="amount_due > 0"/>
            <field name="state"/>
            <button name="action_view_products" string="Ver Productos" icon="fa-list"/>
        </tree>
    </field>
    
    <group>
        <field name="account_balance" widget="monetary"/>
        <button name="action_register_payment" string="Registrar Pago (LV)"/>
    </group>
</page>
```

### FACTURACIÓN (cuando sea necesaria):

```python
def action_create_invoice(self):
    """Crear factura desde pedido a crédito"""
    invoice = self.env['account.move'].create({
        'partner_id': self.partner_id.id,
        'move_type': 'out_invoice',
        'credit_order_id': self.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': line.product_id.id,
            'quantity': line.qty_ordered,
            'price_unit': line.price_unit,
        }) for line in self.line_ids],
    })
    
    # NO afecta CC (ya está registrado)
    # La factura es solo el documento fiscal
    return invoice
```

### VENTAJAS DE ESTE DISEÑO:

✅ **Una sola fuente de verdad:** `credit.sale.order`
✅ **Siempre editable:** No hay límites técnicos
✅ **Productos visibles:** Siempre sabes QUÉ tiene el cliente
✅ **Historial completo:** Cada cambio registrado
✅ **Por cliente:** Vista unificada de todos sus pedidos
✅ **CC sincronizado:** Ajustes automáticos
✅ **Facturación opcional:** Generas cuando necesites
✅ **POS rápido:** No genera facturas automáticamente
✅ **Escalable:** Soporta volumen y modificaciones

### COMPARACIÓN:

#### Sistema Actual (POS-based):
```
POS Order (inmutable) → ¿Cómo edito?
  ↓
Factura (opcional) → Otra fuente de verdad
  ↓
CC separada → Solo monto, no productos
```
**Problema:** 3 fuentes de verdad desincronizadas

#### Sistema Ideal (Credit-based):
```
Credit Sale Order (editable) → Fuente única
  ├─ Productos: Siempre actualizados
  ├─ CC: Auto-sincronizado
  ├─ Historial: Completo
  └─ Factura: Opcional, generada cuando se necesita
```
**Ventaja:** Una sola fuente, todo sincronizado

### RESUMEN:

**Si empezara desde cero, haría:**

1. **Módulo independiente:** `credit_sales` (no extender POS)
2. **Modelo central:** `credit.sale.order` (siempre editable)
3. **Integración con POS:** Crear credit order desde POS, pero gestionar desde su propio módulo
4. **CC integrada:** Parte del mismo módulo
5. **Facturación on-demand:** Generas factura cuando la pidas, se vincula al pedido
6. **Vista unificada por cliente:** Todos sus pedidos con productos actuales

**Tiempo de desarrollo:** 2-3 días completo y probado

### ¿QUÉ HACEMOS AHORA?

**Opción A:** Continuar con el sistema actual y agregar solo el wizard simple

**Opción B:** Recrear desde cero con el diseño ideal (módulo nuevo `credit_sales`)

**Opción C:** Migrar gradualmente: Mantener lo actual, ir creando el nuevo módulo en paralelo

---

## Usuario:
y cambiaria la cosa si facturamos todo? estoy viendo que otras cosas podemos cambiar de las restricciones para poder ayudarte a encontrar una solucion mas simple u optima

---

## Asistente:

¡EXCELENTE pregunta! Esto cambia **RADICALMENTE** la solución. Déjame analizar:

### SI FACTURAS TODO automáticamente:

#### VENTAJAS ENORMES:

✅ **Factura = Fuente única de verdad**
✅ **Ya es editable** (borrador → editar → confirmar)
✅ **Sistema nativo de Odoo** (probado, estable)
✅ **account_move.py ya funciona** (detecta cambios)
✅ **NO necesitas módulo nuevo**
✅ **Productos siempre visibles** en la factura
✅ **Historial automático** (Odoo lo lleva)

### SOLUCIÓN SIMPLIFICADA CON FACTURACIÓN AUTOMÁTICA:

#### Arquitectura:

```
Venta POS → Factura automática → CC
     ↓              ↓              ↓
  (recibo)    (FUENTE ÚNICA)   (saldo)
```

**Una sola fuente de verdad:** La FACTURA

### TU PREOCUPACIÓN: "El POS se pone lento"

Déjame analizar **POR QUÉ** se pone lento:

#### Posibles causas:

1. **Facturación electrónica (AFIP/SAT):** Si cada factura requiere autorización online
2. **Secuencia de números:** Si usa secuencia bloqueante
3. **Reglas contables complejas:** Muchos asientos automáticos
4. **Impresión de factura:** Si imprime PDF automáticamente
5. **Cálculo de impuestos:** Si tiene muchas reglas fiscales

### SOLUCIONES PARA LA LENTITUD:

#### Opción 1: Facturación "interna" rápida

```python
# Configuración de facturación
- NO usar facturación electrónica para todas
- Secuencia simple sin validación externa
- Generar factura "interna" (no fiscal)
- Solo cuando cliente pida, convertir a fiscal
```

**Resultado:** Factura instantánea

#### Opción 2: Facturación asíncrona

```python
# Al confirmar venta en POS:
1. Orden se confirma inmediatamente
2. Factura se genera en SEGUNDO PLANO
3. Cliente no espera

# Implementación:
def _process_order(self, order, existing_order):
    order_id = super()._process_order(order, existing_order)
    
    if has_credit_payment:
        # Programar factura en cola
        self.env['pos.order'].browse(order_id).with_delay().create_invoice()
    
    return order_id
```

**Resultado:** POS no se enlentece

#### Opción 3: Facturación por lotes al cerrar caja

```python
# Durante el día: Solo órdenes POS
# Al cerrar sesión: Generar todas las facturas juntas
```

**Resultado:** Rapidez en ventas, facturas después

### AHORA, SI FACTURAS TODO:

#### Sistema ULTRA SIMPLIFICADO:

```
┌─────────────────────────────────────────────────┐
│  FLUJO COMPLETO                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Venta en POS con Cuenta Corriente          │
│     ↓                                           │
│  2. Factura generada automáticamente            │
│     (interna, rápida)                           │
│     ↓                                           │
│  3. account_move.py registra en CC              │
│     (código que YA EXISTE)                      │
│     ↓                                           │
│  4. Cliente vuelve a cambiar productos          │
│     ↓                                           │
│  5. Editas LA FACTURA:                          │
│     - Restablecer a borrador (verde)            │
│     - Editar líneas                             │
│     - Confirmar (verde)                         │
│     ↓                                           │
│  6. account_move.py detecta cambio              │
│     y ajusta CC automáticamente                 │
│     ↓                                           │
│  ✓ TODO SINCRONIZADO                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### LO QUE NECESITAS AGREGAR:

#### Solo 2 cosas:

##### 1. Vista del cliente mejorada:

```xml
<page string="Facturas a Crédito (LV)">
    <field name="invoice_ids" domain="[('payment_method', '=', 'cuenta_corriente')]">
        <tree>
            <field name="name"/>
            <field name="invoice_date"/>
            <field name="amount_total"/>
            <field name="state"/>
            <button name="action_view_products" string="Ver Productos" icon="fa-list"/>
            <button name="button_draft" string="Editar" 
                    invisible="state != 'posted'"
                    class="btn-success"/>
        </tree>
    </field>
</page>
```

##### 2. Registro automático en CC (ya lo tienes):

El `account_move.py` ya hace todo:
- ✅ Detecta cambios en facturas
- ✅ Crea ajustes en CC
- ✅ Cancela movimientos si cancelas factura

### CONFIGURACIÓN PARA VELOCIDAD:

#### A. Factura interna rápida:

```python
# En pos.payment.method "Cuenta Corriente":
{
    'name': 'Cuenta Corriente',
    'split_transactions': True,
    'journal_id': journal_simple,  # Journal sin validaciones complejas
}

# En configuración POS:
{
    'auto_invoice': True,  # Factura automática
    'invoice_journal_id': journal_simple,  # Journal rápido
}
```

#### B. Deshabilitar validaciones lentas:

```python
# En account.move (heredar):
def _post(self):
    # Si es factura de CC, simplificar
    if self.payment_method_cuenta_corriente:
        # Saltear validaciones complejas
        # No enviar a AFIP (solo internas)
        # No imprimir automáticamente
    
    return super()._post()
```

### COMPARACIÓN DE VELOCIDAD:

#### Facturación completa (lenta):
```
Venta → Validar stock → Validar impuestos → 
Crear asientos contables → Enviar a AFIP → 
Generar PDF → Enviar email
= 5-10 segundos
```

#### Facturación simplificada (rápida):
```
Venta → Crear factura simple → Registrar en CC
= 0.5-1 segundo
```

### SOLUCIÓN FINAL SI FACTURAS TODO:

#### Arquitectura mínima:

```
┌──────────────────────────────────────────────┐
│  MÓDULO: cuenta_corriente_simple             │
├──────────────────────────────────────────────┤
│                                              │
│  1. pos_order.py                             │
│     → _process_order(): Crear factura        │
│                                              │
│  2. account_move.py (YA EXISTE)              │
│     → write(): Detectar cambios              │
│     → Ajustar CC                             │
│                                              │
│  3. res_partner.py                           │
│     → Vista de facturas a crédito            │
│     → Saldo total                            │
│                                              │
│  4. customer_account.py (YA EXISTE)          │
│     → Movimientos de CC                      │
│                                              │
└──────────────────────────────────────────────┘
```

**NO necesitas:**
- ❌ credit.sale.order
- ❌ Wizard de edición
- ❌ Sincronización compleja
- ❌ Historial separado

**TODO lo hace la factura nativa de Odoo**

### ¿QUÉ MODIFICAR EN RESTRICCIONES?

Te pregunto:

#### 1. ¿Puedes facturar todo pero como "factura interna"?
   - No fiscal, solo registro interno
   - Convertir a fiscal solo cuando cliente la pida
   - **Si SÍ:** Solución ultra simple

#### 2. ¿El problema de velocidad es SOLO con facturación electrónica?
   - AFIP/SAT/SRI demora 2-5 segundos por factura
   - **Si SÍ:** Facturación interna resuelve todo

#### 3. ¿Cuánto demora actualmente generar una factura en tu sistema?
   - Si es <1 segundo: No hay problema
   - Si es >3 segundos: Necesitamos optimizar o facturar asíncrono

#### 4. ¿El cajero puede esperar 1-2 segundos por venta?
   - **Si SÍ:** Factura todo, solución simple
   - **Si NO:** Factura asíncrona en segundo plano

### MI RECOMENDACIÓN DEFINITIVA:

**Si puedes facturar TODO con facturas internas rápidas:**

✅ **Mantén el addon actual**
✅ **Activa facturación automática** en POS
✅ **Configura journal simple** (sin validaciones lentas)
✅ **Editas facturas** cuando haya cambios
✅ **account_move.py ya hace todo** el resto

**Desarrollo adicional: 0 minutos** (ya funciona)

---

**¿Cuánto demora actualmente generar una factura en tu Odoo? Probemos activar facturación automática y medir la velocidad.**

---

**FIN DE LA CONVERSACIÓN CAPTURADA**

---

## RESUMEN EJECUTIVO:

### Problema Principal:
- Necesitas editar productos de compras a crédito frecuentemente
- Clientes vuelven a cambiar productos
- Necesitas ver productos actuales por cliente y por compra
- ~15 ventas/día, 30-50 productos por venta

### Soluciones Propuestas (en orden de complejidad):

1. **SOLUCIÓN MÁS SIMPLE (Si facturas todo):**
   - Activar facturación automática en POS
   - Usar facturas internas rápidas (no fiscales)
   - Editar facturas cuando haya cambios
   - account_move.py ya ajusta CC automáticamente
   - **Desarrollo: 0 minutos (ya está listo)**

2. **SOLUCIÓN INTERMEDIA (Sistema actual + wizard):**
   - Crear wizard de edición de órdenes
   - Bloquear si tiene factura (redirigir a factura)
   - Sistema de "estado actual" paralelo
   - **Desarrollo: 60-90 minutos**

3. **SOLUCIÓN COMPLETA (Desde cero):**
   - Módulo nuevo `credit_sales`
   - Modelo `credit.sale.order` siempre editable
   - Integración con POS
   - **Desarrollo: 2-3 días**

### Preguntas Pendientes:
- ¿Cuánto demora generar una factura actualmente?
- ¿Puedes usar facturas internas (no fiscales)?
- ¿El cajero puede esperar 1-2 segundos por venta?
