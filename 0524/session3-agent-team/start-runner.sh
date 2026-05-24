#!/usr/bin/env bash
# Deepagent Code Runner Server 시작
# n8n Docker에서 host.docker.internal:8899 로 접근
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v uvicorn &>/dev/null; then
  echo "▶ 의존성 설치..."
  pip install fastapi uvicorn 2>/dev/null || pip3 install fastapi uvicorn
fi

echo "🚀 Deepagent Code Runner 시작 (포트 8899)"
echo "   n8n 워크플로우 → POST http://localhost:8899/run"
echo "   테스트: curl -X POST localhost:8899/run -H 'Content-Type: application/json' -d '{\"script\":\"print(42)\",\"lang\":\"python\"}'"
echo ""
python3 code-runner-server.py
