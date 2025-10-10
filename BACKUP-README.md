# Sistema de Backup y Restore para Odoo POS

Este directorio contiene scripts para hacer backup y restaurar el servidor completo de Odoo.

## 📦 ¿Qué se respalda?

- ✅ Base de datos PostgreSQL completa (estructura + datos)
- ✅ Filestore (imágenes, archivos adjuntos)
- ✅ Sesiones de usuarios
- ✅ Configuración y metadata

## 🚀 Comandos disponibles

### 1. Crear Backup

```powershell
.\backup.ps1
```

Esto crea un backup completo con timestamp en `C:\POS\backups\`.

**Ejemplo de salida:**
```
=== BACKUP DE ODOO ===
Creando backup en: C:\POS\backups\20251009_174246

[1/3] Haciendo backup de la base de datos...
  Base de datos guardada: 4.74 MB

[2/3] Haciendo backup del filestore...
  Filestore guardado: 401 archivos

[3/3] Haciendo backup de sesiones...
  Sesiones guardadas

=== BACKUP COMPLETADO ===
```

### 2. Listar Backups

```powershell
.\list-backups.ps1
```

Muestra todos los backups disponibles con su información.

### 3. Restaurar Backup

```powershell
# Restaurar el backup más reciente automáticamente
.\restore.ps1

# Restaurar un backup específico
.\restore.ps1 20251009_174246
```

⚠️ **ADVERTENCIA**: La restauración eliminará todos los datos actuales de Odoo.

## 📁 Estructura de Backups

```
C:\POS\backups\
├── 20251009_174246\              ← Backup del 9 de octubre a las 17:42:46
│   ├── odoo_database.dump        ← Base de datos PostgreSQL
│   ├── filestore\                ← Archivos adjuntos e imágenes
│   ├── sessions\                 ← Sesiones de usuarios
│   └── backup_info.json          ← Información del backup
├── 20251010_093000\              ← Otro backup
│   └── ...
```

## 🔄 Flujo recomendado

### Antes de cambios importantes:

```powershell
# 1. Crear backup del estado actual
.\backup.ps1

# 2. Hacer tus cambios en Odoo
# (instalar módulos, configurar, etc.)

# 3. Si algo sale mal, restaurar:
.\restore.ps1
```

### Respaldo periódico:

Se recomienda crear backups:
- ✅ Antes de actualizar módulos
- ✅ Antes de cambios importantes en configuración
- ✅ Diariamente (si el negocio lo requiere)
- ✅ Después de configurar el sistema como deseas

## 🛠️ Solución de problemas

### Error: "No se encontró el backup"
```powershell
# Verifica los backups disponibles
.\list-backups.ps1
```

### Error: "Cannot connect to Docker"
```powershell
# Asegúrate de que Docker esté corriendo
docker ps

# Si no está corriendo, inicia los servicios
docker-compose up -d
```

### Backup muy grande
Los backups incluyen:
- Base de datos (tamaño varía según datos)
- Filestore (puede crecer con imágenes de productos)

Para reducir tamaño:
- Limpia archivos innecesarios del filestore
- Elimina backups antiguos de `C:\POS\backups\`

## 📌 Notas importantes

1. **Los backups son locales**: Se guardan en `C:\POS\backups\`
2. **Mantén backups externos**: Copia la carpeta `backups\` a otro disco o nube
3. **Espacio en disco**: Cada backup ocupa ~5-50 MB dependiendo de datos
4. **Tiempo de restauración**: ~30 segundos - 2 minutos

## 🔐 Seguridad

- Los backups contienen **TODOS** los datos de Odoo
- Incluyen contraseñas hasheadas de usuarios
- **NO compartas** los archivos .dump públicamente
- Considera cifrar la carpeta `backups\` si contiene datos sensibles

## 📞 Soporte

Si encuentras problemas con los scripts de backup/restore, verifica:
1. Docker está corriendo: `docker ps`
2. Contenedores activos: `pos-db-1` y `pos-odoo-1`
3. Permisos de escritura en `C:\POS\backups\`
