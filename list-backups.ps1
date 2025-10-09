# Script para listar backups disponibles
$BACKUPS_DIR = "C:\POS\backups"

if (!(Test-Path $BACKUPS_DIR)) {
    Write-Host "No se encontro el directorio de backups: $BACKUPS_DIR" -ForegroundColor Yellow
    exit 0
}

$backups = Get-ChildItem -Path $BACKUPS_DIR -Directory | Sort-Object Name -Descending

if ($backups.Count -eq 0) {
    Write-Host "No hay backups disponibles" -ForegroundColor Yellow
    Write-Host "Ejecuta .\backup.ps1 para crear uno" -ForegroundColor Cyan
    exit 0
}

Write-Host "=== BACKUPS DISPONIBLES ===" -ForegroundColor Green
Write-Host ""

foreach ($backup in $backups) {
    $infoPath = Join-Path $backup.FullName "backup_info.json"
    
    Write-Host "Backup: $($backup.Name)" -ForegroundColor Cyan
    
    if (Test-Path $infoPath) {
        $info = Get-Content $infoPath | ConvertFrom-Json
        Write-Host "  Fecha: $($info.date)" -ForegroundColor Gray
        Write-Host "  Modulos: $($info.modules)" -ForegroundColor Gray
    }
    
    $dbDump = Join-Path $backup.FullName "odoo_database.dump"
    if (Test-Path $dbDump) {
        $size = (Get-Item $dbDump).Length / 1MB
        $sizeRounded = [math]::Round($size, 2)
        Write-Host "  Tamano BD: $sizeRounded MB" -ForegroundColor Gray
    }
    
    Write-Host ""
}

Write-Host "Para restaurar un backup:" -ForegroundColor Yellow
Write-Host "  .\restore.ps1 <nombre_backup>" -ForegroundColor White
Write-Host "  .\restore.ps1                  (restaura el mas reciente)" -ForegroundColor White
