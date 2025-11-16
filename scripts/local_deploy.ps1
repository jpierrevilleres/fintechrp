# Local deployment script for Windows - Run in virtual environment
# Test changes locally before pushing to production

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting LOCAL deployment: $(Get-Date)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$PROJECT_DIR = "F:\WEBSITE\fintechrp"
$BACKUP_DIR = "$PROJECT_DIR\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

Set-Location $PROJECT_DIR

# Create backup directory
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

Write-Host ""
Write-Host "Step 1: Backing up database..." -ForegroundColor Yellow
if (Test-Path "$PROJECT_DIR\db.sqlite3") {
    Copy-Item "$PROJECT_DIR\db.sqlite3" "$BACKUP_DIR\db.sqlite3.backup.$TIMESTAMP"
    Compress-Archive -Path "$BACKUP_DIR\db.sqlite3.backup.$TIMESTAMP" -DestinationPath "$BACKUP_DIR\db.sqlite3.backup.$TIMESTAMP.zip" -Force
    Remove-Item "$BACKUP_DIR\db.sqlite3.backup.$TIMESTAMP"
    Write-Host "OK Database backed up to: $BACKUP_DIR\db.sqlite3.backup.$TIMESTAMP.zip" -ForegroundColor Green
    
    Get-ChildItem "$BACKUP_DIR\db.sqlite3.backup.*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 10 | Remove-Item
    Write-Host "OK Cleaned old backups (keeping last 10)" -ForegroundColor Green
} else {
    Write-Host "WARNING: Database file not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 2: Installing/updating dependencies..." -ForegroundColor Yellow
& "$PROJECT_DIR\.venv\Scripts\pip.exe" install -r requirements.txt --quiet
Write-Host "OK Dependencies updated" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Updating CKEditor to secure 4.25.1-lts..." -ForegroundColor Yellow
$CKEDITOR_DIR = "$PROJECT_DIR\static\ckeditor"
$versionFile = "$CKEDITOR_DIR\ckeditor\.version-4.25.1"

if (-not (Test-Path $versionFile)) {
    Write-Host "Downloading CKEditor 4.25.1-lts (secure version)..." -ForegroundColor Cyan
    
    if (-not (Test-Path $CKEDITOR_DIR)) {
        New-Item -ItemType Directory -Path $CKEDITOR_DIR | Out-Null
    }
    
    $zipPath = "$CKEDITOR_DIR\ckeditor.zip"
    $downloadUrl = "https://cdn.ckeditor.com/4.25.1-lts/standard/ckeditor_4.25.1-lts_standard.zip"
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
    
    if (Test-Path "$CKEDITOR_DIR\ckeditor") {
        $backupName = "ckeditor.backup.$TIMESTAMP"
        Rename-Item "$CKEDITOR_DIR\ckeditor" $backupName
        Write-Host "OK Old CKEditor backed up to $backupName" -ForegroundColor Green
    }
    
    Expand-Archive -Path $zipPath -DestinationPath $CKEDITOR_DIR -Force
    Remove-Item $zipPath
    
    "4.25.1-lts" | Out-File $versionFile -Encoding utf8
    
    Write-Host "OK CKEditor updated to 4.25.1-lts" -ForegroundColor Green
} else {
    Write-Host "OK CKEditor 4.25.1-lts already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Running database migrations..." -ForegroundColor Yellow
& "$PROJECT_DIR\.venv\Scripts\python.exe" manage.py migrate --noinput
Write-Host "OK Migrations applied" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Collecting static files..." -ForegroundColor Yellow
& "$PROJECT_DIR\.venv\Scripts\python.exe" manage.py collectstatic --noinput
Write-Host "OK Static files collected" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Local deployment completed successfully!" -ForegroundColor Green
Write-Host "Deployment time: $(Get-Date)" -ForegroundColor Cyan
Write-Host "Backup: $BACKUP_DIR\db.sqlite3.backup.$TIMESTAMP.zip" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host ""
Write-Host "To start the local development server:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Then visit:" -ForegroundColor White
Write-Host "  Homepage: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Admin: http://localhost:8000/control-panel-72d3/" -ForegroundColor Cyan
