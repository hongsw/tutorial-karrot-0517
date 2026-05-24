#!/usr/bin/env bash
# SESSION 3 실습 A: harness로 에이전트 팀 구성
# https://github.com/hongsw/harness
# 사전조건: Claude Code 설치 필요

set -euo pipefail

TEAM_DIR="$HOME/my-agent-team"
mkdir -p "$TEAM_DIR"

echo "▶ 에이전트 팀 디렉터리: $TEAM_DIR"
echo ""
echo "▶ Claude Code 실행 후 아래 메시지를 입력하세요:"
echo ""
echo "──────────────────────────────────────────"
cat << 'PROMPT'
하네스 구성해줘.

나는 1인 콘텐츠 사업자야.
매주 블로그 포스트 1개를 자동으로 기획→작성→검수→발행하는 팀이 필요해.
아래 4개 에이전트로 구성해줘:
- Researcher: 주제 리서치 + 키워드 수집
- Writer: 초안 작성 (SEO 고려)
- Critic: 논리·톤 검수, 개선점 3개 제시
- Publisher: Markdown → HTML 변환 후 파일 저장
PROMPT
echo "──────────────────────────────────────────"
echo ""

cd "$TEAM_DIR"
claude
