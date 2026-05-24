#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${MANUS_API_KEY:-}" ]]; then
  echo "MANUS_API_KEY is required" >&2
  exit 1
fi

PROMPT="${1:-한국어로 당근 사업강화팀을 위한 신규 사업 기회 5개를 조사하고 표로 정리해줘.}"

curl -sS --request POST \
  --url "https://api.manus.ai/v2/task.create" \
  --header "Content-Type: application/json" \
  --header "x-manus-api-key: ${MANUS_API_KEY}" \
  --data "$(jq -n --arg prompt "$PROMPT" '{
    message: {
      content: [
        {
          type: "text",
          text: $prompt
        }
      ]
    },
    locale: "ko",
    interactive_mode: false,
    hide_in_task_list: false,
    share_visibility: "private",
    agent_profile: "manus-1.6"
  }')"

