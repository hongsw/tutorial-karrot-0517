# 29회차 당근모임 실습 코드 — 2026.05.24

각 세션 폴더 → 실행 가능한 코드 중심

```
0524/
├── session2-infra/          # miri.dev 배포 + n8n
│   ├── deploy.sh            # 사이트 파일 생성 → miri.dev 업로드 안내
│   └── n8n-start.sh         # Docker로 n8n 로컬 실행
│
├── session3-agent-team/     # 에이전트 팀 3가지 방법
│   ├── harness-setup.sh     # A: Claude Code + harness
│   ├── team-prompt.md       # B: Claude.ai 웹 복붙 프롬프트 (터미널 없이)
│   └── n8n-workflow.json    # C: n8n Import용 워크플로우
│
├── session4-build/          # 구축 옵션별 코드
│   ├── setup.sh             # A/B/C 선택형 설정 스크립트
│   ├── agent.py             # B: Claude API 이메일 분류 에이전트
│   └── crew.py              # C: CrewAI 콘텐츠 팀
│
└── session5-local-llm/      # 로컬 LLM + baryon.ai
    ├── baryon-test.sh        # baryon.ai TalkMode curl 테스트
    ├── opencode-baryon.json  # opencode provider 설정 (baryon)
    ├── ollama-start.sh       # Ollama 설치 + 모델 선택 실행
    └── opencode-ollama.json  # opencode provider 설정 (ollama)
```

---

## 세션별 첫 실행 명령

```bash
# SESSION 2: 사이트 만들기
bash 0524/session2-infra/deploy.sh

# SESSION 3-A: 에이전트 팀 (Claude Code 있는 분)
bash 0524/session3-agent-team/harness-setup.sh

# SESSION 3-B: 터미널 없이
# → session3-agent-team/team-prompt.md 열어서 claude.ai에 붙여넣기

# SESSION 4: 옵션 선택 후 실행
bash 0524/session4-build/setup.sh

# SESSION 5-1: baryon.ai (TalkMode) 테스트
bash 0524/session5-local-llm/baryon-test.sh

# SESSION 5-2: 로컬 Ollama
bash 0524/session5-local-llm/ollama-start.sh
```

---

## 오늘 할 일 1개씩

| 세션 | 즉시 실행 가능한 것 |
|------|--------------------|
| 2 | `deploy.sh` → miri.dev 드래그앤드롭 |
| 3 | `team-prompt.md` 프롬프트 → claude.ai |
| 4 | `setup.sh` B 선택 → `agent.py` 실행 |
| 5 | `baryon-test.sh` → TalkMode 응답 확인 |
