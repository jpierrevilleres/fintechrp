#!/bin/bash
set -e  # Exit on any error

# Configuration
PROJECT_DIR="/home/ubuntu/fintechrp"
BRANCH="${DEPLOY_BRANCH:-main}"

cd "$PROJECT_DIR"

# This script pulls its own latest version from git. If the rest of the
# steps below ran in the same process, bash could read a mix of the old
# and new file off disk mid-execution. So: sync the code first, then
# re-exec into the freshly-pulled copy of this script for everything else.
if [ -z "$DEPLOY_SCRIPT_REEXECED" ]; then
    echo "Syncing code from $BRANCH before running deploy..."
    git fetch origin
    git checkout "$BRANCH"
    git pull --ff-only origin "$BRANCH"
    export DEPLOY_SCRIPT_REEXECED=1
    exec bash "$PROJECT_DIR/scripts/deploy.sh"
fi

echo "=========================================="
echo "Starting deployment: $(date)"
echo "=========================================="

BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}✓ Code up to date: $(git rev-parse --short HEAD) on $BRANCH${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}Step 1: Backing up database...${NC}"
# Backup SQLite database
if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    DB_BACKUP="$BACKUP_DIR/db.sqlite3.backup.$TIMESTAMP"
    "$PROJECT_DIR/.venv/bin/python" - "$PROJECT_DIR/db.sqlite3" "$DB_BACKUP" <<'PY'
import sqlite3
import sys

with sqlite3.connect(sys.argv[1]) as source:
    with sqlite3.connect(sys.argv[2]) as backup:
        source.backup(backup)
PY
    gzip "$DB_BACKUP"
    echo "Database backup created: $DB_BACKUP.gz"
    ls -t "$BACKUP_DIR"/db.sqlite3.backup.*.gz | tail -n +11 | xargs -r rm
else
    echo -e "${RED}✗ Warning: Database file not found!${NC}"
fi

if [ -d "$PROJECT_DIR/media" ]; then
    tar -czf "$BACKUP_DIR/media.backup.$TIMESTAMP.tar.gz" -C "$PROJECT_DIR" media
    echo "Media backup created: $BACKUP_DIR/media.backup.$TIMESTAMP.tar.gz"
    ls -t "$BACKUP_DIR"/media.backup.*.tar.gz | tail -n +6 | xargs -r rm
fi

echo -e "${YELLOW}Step 2: Activating virtual environment...${NC}"
source "$PROJECT_DIR/.venv/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo -e "${YELLOW}Step 3: Installing/updating dependencies...${NC}"
"$PROJECT_DIR/.venv/bin/pip" install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies updated${NC}"

echo -e "${YELLOW}Step 4: Running database migrations...${NC}"
"$PROJECT_DIR/.venv/bin/python" manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations applied${NC}"

echo -e "${YELLOW}Step 5: Collecting static files...${NC}"
"$PROJECT_DIR/.venv/bin/python" manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

echo -e "${YELLOW}Step 5.5: Updating CKEditor to secure LTS version...${NC}"
CKEDITOR_DIR="$PROJECT_DIR/static/ckeditor"
if [ ! -f "$CKEDITOR_DIR/ckeditor/.version-4.25.1" ]; then
    echo "Downloading CKEditor 4.25.1-lts (secure version)..."
    mkdir -p "$CKEDITOR_DIR"
    cd "$CKEDITOR_DIR"

    # Download CKEditor 4.25.1-lts standard package
    wget -q https://cdn.ckeditor.com/4.25.1-lts/standard/ckeditor_4.25.1-lts_standard.zip -O ckeditor.zip

    # Backup old version if exists
    if [ -d "ckeditor" ]; then
        mv ckeditor "ckeditor.backup.$(date +%Y%m%d_%H%M%S)"
    fi

    # Extract new version
    unzip -q ckeditor.zip
    rm ckeditor.zip

    # Mark version
    echo "4.25.1-lts" > ckeditor/.version-4.25.1

    echo -e "${GREEN}✓ CKEditor updated to 4.25.1-lts${NC}"
else
    echo -e "${GREEN}✓ CKEditor 4.25.1-lts already installed${NC}"
fi
cd "$PROJECT_DIR"

echo -e "${YELLOW}Step 5.6: Re-collecting static files with new CKEditor...${NC}"
"$PROJECT_DIR/.venv/bin/python" manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files re-collected${NC}"

echo -e "${YELLOW}Step 6: Restarting Gunicorn...${NC}"
sudo systemctl restart gunicorn
sleep 2
if sudo systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✓ Gunicorn restarted successfully${NC}"
else
    echo -e "${RED}✗ Error: Gunicorn failed to start!${NC}"
    echo "Check logs: sudo journalctl -u gunicorn -n 50"
    exit 1
fi

echo -e "${YELLOW}Step 7: Reloading Nginx...${NC}"
sudo systemctl reload nginx
echo -e "${GREEN}✓ Nginx reloaded${NC}"

echo -e "${YELLOW}Step 8: Checking service status...${NC}"
sudo systemctl status gunicorn --no-pager -l | head -20

echo "=========================================="
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "Deployment time: $(date)"
echo "Backup location: $BACKUP_DIR/db.sqlite3.backup.$TIMESTAMP.gz"
echo "=========================================="
