#!/usr/bin/env bash
set -euo pipefail

PORT=5123
WORKERS=3
APP_MODULE="app:app"
LOGFILE="/var/log/personalblog/app.log"
VENV="/home/vps_webs/personal-blog/venv"

mkdir -p /var/log/personalblog

pkill -f "gunicorn.*127.0.0.1:${PORT}" || true

export USE_MOCK_DATA=False

exec ${VENV}/bin/gunicorn \
  --workers ${WORKERS} \
  --bind 127.0.0.1:${PORT} \
  --access-logfile ${LOGFILE} \
  --error-logfile ${LOGFILE} \
  ${APP_MODULE}