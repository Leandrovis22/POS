# Script para restaurar backup de Odoo
param([string]$BackupName)

$BACKUPS_DIR = "C:\POS\backups"

if ([string]::IsNullOrEmpty($BackupName)) {
    $latestBackup = Get-ChildItem -Path $BACKUPS_DIR -Directory | Sort-Object Name -Descending | Select-Object -First 1
    if ($null -eq $latestBackup) {
        Write-Host "No se encontraron backups en $BACKUPS_DIR" -ForegroundColor Red
        exit 1
    }
    $BackupName = $latestBackup.Name
    Write-Host "Usando backup mas reciente: $BackupName" -ForegroundColor Cyan
}

$BACKUP_PATH = "$BACKUPS_DIR\$BackupName"

if (!(Test-Path $BACKUP_PATH)) {
    Write-Host "No se encontro el backup: $BACKUP_PATH" -ForegroundColor Red
    Write-Host "`nBackups disponibles:" -ForegroundColor Yellow
    Get-ChildItem -Path $BACKUPS_DIR -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }
    exit 1
}

Write-Host "=== RESTAURAR ODOO ===" -ForegroundColor Green
Write-Host "Backup: $BackupName" -ForegroundColor Cyan

Write-Host "`nADVERTENCIA: Esto eliminara todos los datos actuales de Odoo" -ForegroundColor Red
$confirm = Read-Host "Continuar? (si/no)"
if ($confirm -ne "si") {
    Write-Host "Operacion cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n[1/6] Deteniendo servicios..." -ForegroundColor Yellow
docker-compose down
Start-Sleep -Seconds 2
Write-Host "  Servicios detenidos" -ForegroundColor Green

Write-Host "`n[2/6] Limpiando datos actuales..." -ForegroundColor Yellow
$filestorePath = "C:\POS\odoo-data\filestore\odoo"
if (Test-Path $filestorePath) {
    Remove-Item -Path $filestorePath -Recurse -Force
    Write-Host "  Filestore limpiado" -ForegroundColor Green
}

$sessionsPath = "C:\POS\odoo-data\sessions"
if (Test-Path $sessionsPath) {
    Get-ChildItem -Path $sessionsPath -Recurse | Remove-Item -Force -Recurse
    Write-Host "  Sesiones limpiadas" -ForegroundColor Green
}

Write-Host "`n[3/6] Iniciando base de datos..." -ForegroundColor Yellow
docker-compose up -d db
Start-Sleep -Seconds 5
Write-Host "  Base de datos iniciada" -ForegroundColor Green

Write-Host "`n[4/6] Restaurando base de datos..." -ForegroundColor Yellow
docker exec pos-db-1 psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo;"
docker exec pos-db-1 psql -U odoo -d postgres -c "CREATE DATABASE odoo OWNER odoo;"
docker cp "$BACKUP_PATH\odoo_database.dump" pos-db-1:/tmp/odoo_backup.dump
docker exec pos-db-1 pg_restore -U odoo -d odoo -F c /tmp/odoo_backup.dump
docker exec pos-db-1 rm /tmp/odoo_backup.dump
Write-Host "  Base de datos restaurada" -ForegroundColor Green

Write-Host "`n[5/6] Restaurando archivos..." -ForegroundColor Yellow
$backupFilestore = "$BACKUP_PATH\filestore"
if (Test-Path $backupFilestore) {
    Copy-Item -Path $backupFilestore -Destination "C:\POS\odoo-data\filestore\odoo" -Recurse -Force
    Write-Host "  Filestore restaurado" -ForegroundColor Green
}

$backupSessions = "$BACKUP_PATH\sessions"
if (Test-Path $backupSessions) {
    Copy-Item -Path $backupSessions -Destination "C:\POS\odoo-data\sessions" -Recurse -Force
    Write-Host "  Sesiones restauradas" -ForegroundColor Green
}

Write-Host "`n[6/6] Iniciando Odoo..." -ForegroundColor Yellow
docker-compose up -d
Start-Sleep -Seconds 5

Write-Host "`n=== RESTAURACION COMPLETADA ===" -ForegroundColor Green
Write-Host "Odoo esta disponible en: http://localhost:8069" -ForegroundColor Cyan
Write-Host "Usuario: admin" -ForegroundColor Yellow
Write-Host "Contrasena: admin" -ForegroundColor Yellow

if (Test-Path "$BACKUP_PATH\backup_info.json") {
    Write-Host "`nInformacion del backup:" -ForegroundColor Cyan
    Get-Content "$BACKUP_PATH\backup_info.json" | ConvertFrom-Json | Format-List
}
