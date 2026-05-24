# 29회차 당근모임 실습 코드

세션별 즉시 실행 가능한 코드 모음  
각 파일을 열고 본인 수준에 맞는 방법(A/B/C) 1개 선택

---

| 파일 | 세션 | 핵심 도구 | 소요 |
|------|------|-----------|------|
| [session2-인프라실습.md](session2-인프라실습.md) | 2. 1인 사업 기반 | **miri.dev** 배포 | 10분 |
| [session3-에이전트팀실습.md](session3-에이전트팀실습.md) | 3. 에이전트 팀 | **harness** / Claude.ai / n8n | 15분 |
| [session4-구축방법실습.md](session4-구축방법실습.md) | 4. 구축 방법 | n8n / Claude Code / CrewAI | 15~60분 |
| [session5-로컬LLM실습.md](session5-로컬LLM실습.md) | 5. 로컬 LLM | **baryon.ai(TalkMode)** / Ollama | 20분 |

---

## 빠른 시작 (복붙 가능)

### 오늘 저녁 가능한 것 (10분)

```bash
# 1. miri.dev에 내 소개 페이지 올리기
open https://www.miri.dev

# 2. baryon.ai TalkMode 테스트
uuidgen | tr 'A-Z' 'a-z' > ~/.config/opencode/baryon-device-id
DEVICE_ID=$(cat ~/.config/opencode/baryon-device-id)
curl -sS https://llm.baryon.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: $DEVICE_ID" \
  -d '{"model":"baryon-1","messages":[{"role":"user","content":"이름이 뭐야?"}],"stream":false}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

### 이번 주말 (30분)

```bash
# harness로 에이전트 팀 구성 (Claude Code 필요)
mkdir ~/my-agent-team && cd ~/my-agent-team
claude
# → "하네스 구성해줘. 나는 1인 콘텐츠 사업자야."
```

---

## 참고 링크

- [miri.dev](https://www.miri.dev) — 무료 사이트 배포 (드래그앤드롭)
- [miri.dev/hosting-guide](https://www.miri.dev/hosting-guide) — 20개 호스팅 비교
- [github.com/hongsw/harness](https://github.com/hongsw/harness) — 에이전트 팀 팩토리
- [baryon.ai](https://baryon.ai) — 오늘 후원사, LLM 인프라
- [llm.baryon.ai](https://llm.baryon.ai) — TalkMode LLM 엔드포인트
- [opencode.ai](https://opencode.ai) — 터미널 AI 코딩 도구
