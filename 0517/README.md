# 당근 사업강화 AI에이전트팀 세미나 자료

주제: Manus API를 Claude Code 또는 opencode에서 활용하는 방법

작성일: 2026-05-11

## 파일 구성

- [docs/research-brief.md](docs/research-brief.md): 조사 요약과 도입 판단
- [docs/seminar-slides.md](docs/seminar-slides.md): 30분 세미나 발표안
- [docs/setup-guide.md](docs/setup-guide.md): MCP 서버 방식 설정 가이드 (Claude Code/opencode)
- [docs/litellm-proxy-guide.md](docs/litellm-proxy-guide.md): LiteLLM 프록시 방식 연동 가이드 (전체 테스트 체크리스트 포함)
- [examples/manus-task-create.json](examples/manus-task-create.json): Manus v2 task.create 요청 예시
- [scripts/manus_create_task.sh](scripts/manus_create_task.sh): API 키로 태스크 생성 테스트 스크립트

## 세미나 핵심 결론

Manus API는 “모델 호출 API”라기보다 비동기 AI 에이전트 실행 API에 가깝습니다. Claude Code나 opencode 안에서 쓰는 방법은 두 가지입니다.

1. 직접 REST 호출: `curl`, 사내 래퍼 CLI, 간단한 스크립트로 Manus 태스크를 만들고 결과를 폴링합니다.
2. MCP 서버 경유: Claude Code/opencode가 MCP 클라이언트 역할을 하고, Manus API를 감싼 MCP 서버를 도구로 붙입니다.

권장 파일럿은 “REST 직접 호출 1회 실습 + MCP 서버 PoC”입니다. 커뮤니티 MCP 서버는 편하지만 제3자 코드와 v1/v2 호환성 확인이 필요합니다.

