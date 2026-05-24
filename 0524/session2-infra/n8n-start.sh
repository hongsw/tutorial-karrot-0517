#!/usr/bin/env bash
# SESSION 2 실습: n8n 로컬 실행 (L4 자동화 계층)
# 사전조건: Docker 설치 필요

set -euo pipefail

if ! command -v docker &>/dev/null; then
  echo "❌ Docker 미설치. https://docs.docker.com/get-docker/ 참고"
  exit 1
fi

echo "▶ n8n 시작 중..."
docker run -d \
  --name n8n-local \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

echo "✅ http://localhost:5678 에서 n8n 확인"
echo "   (중지: docker stop n8n-local)"
