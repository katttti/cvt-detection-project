#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "설치 완료. 서버 실행:"
echo "  source venv/bin/activate"
echo "  uvicorn app:app --host 0.0.0.0 --port 8000"
