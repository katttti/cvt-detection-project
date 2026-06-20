#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="/Users/katykim/Desktop/Finnect-challenge/cvt-detection-project"
ENV_FILE="$ROOT_DIR/backend/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE"
  echo "Copy backend/.env.example to backend/.env and fill in the values first."
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

pm2 delete cvt-api cvt-ops >/dev/null 2>&1 || true

CVT_SHARED_PASSWORD="$CVT_SHARED_PASSWORD" \
CVT_OPS_USERNAME="$CVT_OPS_USERNAME" \
pm2 start "$ROOT_DIR/backend/ecosystem.config.cjs" --cwd "$ROOT_DIR"

pm2 save
pm2 status
