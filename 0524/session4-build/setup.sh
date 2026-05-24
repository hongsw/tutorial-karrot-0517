#!/usr/bin/env bash
# SESSION 4 실습: 환경 설정 + 실행
set -euo pipefail

echo "=== SESSION 4 실습 환경 설정 ==="
echo ""
echo "어떤 옵션으로 시작하시겠습니까?"
echo "  A) 노코드 — n8n 로컬 실행"
echo "  B) Vibe-coding — Claude API 에이전트 (Python)"
echo "  C) 프레임워크 — CrewAI"
echo ""
read -rp "선택 (A/B/C): " CHOICE

case "${CHOICE^^}" in
  A)
    echo "▶ n8n 시작..."
    docker run -d --name n8n-sess4 -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
    echo "✅ http://localhost:5678 열기"
    echo "   workflows/ 폴더의 JSON 파일을 n8n에서 Import하세요."
    ;;
  B)
    echo "▶ Python 환경 설정..."
    python3 -m venv .venv && source .venv/bin/activate
    pip install anthropic -q
    if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
      read -rp "ANTHROPIC_API_KEY 입력: " KEY
      export ANTHROPIC_API_KEY="$KEY"
    fi
    python3 agent.py
    ;;
  C)
    echo "▶ CrewAI 설치..."
    python3 -m venv .venv && source .venv/bin/activate
    pip install crewai -q
    if [[ -z "${OPENAI_API_KEY:-}" ]]; then
      read -rp "OPENAI_API_KEY 입력: " KEY
      export OPENAI_API_KEY="$KEY"
    fi
    python3 crew.py
    ;;
  *)
    echo "A, B, C 중 하나를 입력하세요."
    exit 1
    ;;
esac
