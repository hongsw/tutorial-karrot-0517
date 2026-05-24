#!/usr/bin/env bash
# SESSION 5 실습: Ollama 로컬 LLM 시작
set -euo pipefail

# 설치 확인
if ! command -v ollama &>/dev/null; then
  echo "▶ Ollama 설치 중..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "모델 선택:"
echo "  1) llama3.2:3b   — 빠름, RAM 8GB, 가볍게 시작"
echo "  2) qwen3:14b     — 코딩 양호, RAM 16GB (추천)"
echo "  3) gemma3:27b    — 한국어 양호, RAM 32GB"
echo ""
read -rp "선택 (1/2/3): " CHOICE

case "$CHOICE" in
  1) MODEL="llama3.2:3b" ;;
  2) MODEL="qwen3:14b" ;;
  3) MODEL="gemma3:27b" ;;
  *) echo "잘못된 선택"; exit 1 ;;
esac

echo ""
echo "▶ $MODEL 다운로드 + 실행..."
ollama pull "$MODEL"
ollama run "$MODEL"
