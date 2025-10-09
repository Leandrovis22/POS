# Script para crear backup completo de Odoo
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_DIR = "C:\POS\backups\$TIMESTAMP"

Write-Host "=== BACKUP DE ODOO ===" -ForegroundColor Green
Write-Host "Creando backup en: $BACKUP_DIR"

New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null

Write-Host "`n[1/3] Haciendo backup de la base de datos..." -ForegroundColor Yellow
docker exec pos-db-1 pg_dump -U odoo -d odoo -F c -f /tmp/odoo_backup.dump
docker cp pos-db-1:/tmp/odoo_backup.dump "$BACKUP_DIR\odoo_database.dump"
docker exec pos-db-1 rm /tmp/odoo_backup.dump

if (Test-Path "$BACKUP_DIR\odoo_database.dump") {
    $dbSize = (Get-Item "$BACKUP_DIR\odoo_database.dump").Length / 1MB
    Write-Host "  Base de datos guardada: $([math]::Round($dbSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  Error al guardar la base de datos" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/3] Haciendo backup del filestore..." -ForegroundColor Yellow
$filestorePath = "C:\POS\odoo-data\filestore\odoo"
if (Test-Path $filestorePath) {
    Copy-Item -Path $filestorePath -Destination "$BACKUP_DIR\filestore" -Recurse -Force
    $fileCount = (Get-ChildItem -Path "$BACKUP_DIR\filestore" -Recurse -File).Count
    Write-Host "  Filestore guardado: $fileCount archivos" -ForegroundColor Green
} else {
    Write-Host "  No se encontro filestore" -ForegroundColor Yellow
}

Write-Host "`n[3/3] Haciendo backup de sesiones..." -ForegroundColor Yellow
$sessionsPath = "C:\POS\odoo-data\sessions"
if (Test-Path $sessionsPath) {
    Copy-Item -Path $sessionsPath -Destination "$BACKUP_DIR\sessions" -Recurse -Force
    Write-Host "  Sesiones guardadas" -ForegroundColor Green
} else {
    Write-Host "  No se encontraron sesiones" -ForegroundColor Yellow
}

$backupInfo = @{
    timestamp = $TIMESTAMP
    date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    odoo_version = "18.0"
    postgres_version = "15"
    modules = "cuenta_corriente_simple, pos_temporary_product"
} | ConvertTo-Json

$backupInfo | Out-File "$BACKUP_DIR\backup_info.json" -Encoding UTF8

Write-Host "`n=== BACKUP COMPLETADO ===" -ForegroundColor Green
Write-Host "Ubicacion: $BACKUP_DIR" -ForegroundColor Cyan
Write-Host "Para restaurar: .\restore.ps1 $TIMESTAMP" -ForegroundColor Yellow
