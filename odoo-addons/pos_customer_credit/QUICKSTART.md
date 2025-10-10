# ⚡ Inicio Rápido - POS Customer Credit

## 🎯 En 5 Minutos

### 1️⃣ Instalar (1 minuto)
```powershell
cd c:\POS
.\install-pos-credit.ps1 install
```

### 2️⃣ Configurar POS (2 minutos)
1. Ir a **Punto de Venta → Configuración → Punto de Venta**
2. Abrir tu POS
3. Pestaña **Cuenta Corriente**:
   - ✅ Habilitar Cuenta Corriente
   - Seleccionar: Cuenta Corriente
4. **Guardar**

### 3️⃣ Prueba Rápida (2 minutos)
1. Abrir POS
2. Agregar productos ($1,000)
3. Seleccionar cliente
4. Click botón **Cuenta Corriente** (ver saldo)
5. Ir a **Pago**
6. Seleccionar **Cuenta Corriente** ($1,000)
7. **Validar**
8. ✅ Cliente ahora debe $1,000

---


## ✅ Funcionalidades Clave

### En POS
- **Ver Saldo**: Botón CC muestra saldo actual
- **Vender a Crédito**: Método de pago "Cuenta Corriente"
- **Pago Mixto**: Combina efectivo + CC

### En Backend
- **Ver Todo**: Cliente → Pestaña "Cuenta Corriente"
- **Modificar Orden**: Agregar/quitar productos
- **Registrar Pago**: Cliente → "Registrar Pago"
- **PDF con Saldo**: Orden → "PDF con Saldo"

---

## 🎮 Ejemplo Completo

### Escenario: Cliente compra $5,000 a crédito

```
1. POS: Agregar productos ($5,000)
2. POS: Seleccionar cliente "Juan"
3. POS: Ver saldo actual (botón CC)
4. POS: Pago → Cuenta Corriente $5,000
5. POS: Validar

✅ Juan ahora debe: $5,000
```

### Cliente devuelve productos por $1,000

```
1. Backend: Órdenes → Abrir orden de Juan
2. Backend: Click "Modificar Orden"
3. Backend: Quitar productos ($1,000)
4. Backend: Guardar

✅ Juan ahora debe: $4,000
```

### Cliente paga $2,000

```
1. Backend: Contactos → Juan
2. Backend: "Cuenta Corriente" → "Registrar Pago"
3. Backend: Monto: -$2,000
4. Backend: Confirmar

✅ Juan ahora debe: $2,000
```

### Generar PDF para cliente

```
1. Backend: Órdenes → Orden de Juan
2. Backend: Click "PDF con Saldo"
3. Se descarga PDF con:
   - Productos actuales
   - Saldo de esta orden
   - Saldo total de Juan
   
✅ Enviar PDF al cliente
```
