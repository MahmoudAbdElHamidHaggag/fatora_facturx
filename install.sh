#!/bin/bash
set -e

SITE=${1:-erp.erpnext.support}

echo "================================================"
echo "  Installing fatora_facturx dependencies..."
echo "================================================"

echo "[1/3] Installing Python packages..."
bench pip install factur-x pypdf playwright --break-system-packages

echo "[2/3] Installing Chromium..."
python3 -m playwright install chromium
python3 -m playwright install-deps chromium

echo "[3/3] Running migrations and clearing cache..."
bench --site $SITE migrate
bench --site $SITE clear-cache

echo ""
echo "Done! fatora_facturx is ready."
echo "================================================"
