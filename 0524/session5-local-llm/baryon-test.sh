#!/usr/bin/env bash
# SESSION 5 실습: baryon.ai (TalkMode) 연결 테스트
# 사전조건: jq 설치 (brew install jq)
set -euo pipefail

DEVICE_FILE="$HOME/.config/opencode/baryon-device-id"
mkdir -p "$(dirname "$DEVICE_FILE")"

# 디바이스 ID 생성 (한 번만)
if [[ ! -f "$DEVICE_FILE" ]]; then
  uuidgen | tr 'A-Z' 'a-z' > "$DEVICE_FILE"
  echo "✅ 새 Device ID 생성: $(cat "$DEVICE_FILE")"
else
  echo "✅ 기존 Device ID 사용: $(cat "$DEVICE_FILE")"
fi

DEVICE_ID=$(cat "$DEVICE_FILE")

echo ""
echo "▶ baryon.ai (TalkMode) 연결 테스트..."
RESPONSE=$(curl -sS https://llm.baryon.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: $DEVICE_ID" \
  -d '{
    "model": "baryon-1",
    "messages": [{"role": "user", "content": "이름이 뭐야? 한 문장으로만."}],
    "stream": false
  }')

echo ""
echo "응답: $(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$RESPONSE")"
echo ""
echo "─────────────────────────────────────"
echo "남은 무료 횟수: 30회 기준 (lifetime/device)"
echo "에러 코드:"
echo "  400 → X-Device-Id 확인"
echo "  429 → 30회 소진 또는 분당 10회 초과 → Ollama로 전환"
echo "  502 → GPU 백엔드 일시 장애 → 잠시 후 재시도"
