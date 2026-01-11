#!/usr/bin/env bash

export USE_MOCK_DATA=False

PORT=5123
WORKERS=3
APP_MODULE="app:app"
LOGFILE="app.log"

fuser -k ${PORT}/tcp 2>/dev/null || true

nohup gunicorn \
  -w ${WORKERS} \
  -b 127.0.0.1:${PORT} \
  ${APP_MODULE} \
  > ${LOGFILE} 2>&1 &

disown