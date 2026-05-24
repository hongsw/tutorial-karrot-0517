# Manus API 활용 조사 요약

## 1. 한 줄 결론

Manus API는 Claude Code/opencode에서 “외부 에이전트 실행기”로 붙일 수 있다. 단기 실습은 REST API 직접 호출이 가장 확실하고, 반복 업무 자동화는 MCP 서버로 감싸서 Claude Code/opencode의 도구처럼 호출하는 구성이 적합하다.

## 2. 공식 API 현황

Manus 공식 문서는 2026-05-11 기준 v2가 최신이며 v1은 deprecated로 표시된다. v2의 Base URL은 `https://api.manus.ai`이고, 인증 헤더는 `x-manus-api-key`이다.

주요 기능:

- Tasks: 태스크 생성, 후속 메시지, 결과 조회
- Projects: 공통 instruction과 connector 기본값을 묶는 작업 단위
- Files: PDF/CSV/이미지 등 첨부 파일 업로드
- Webhooks: 태스크 완료 또는 사용자 입력 필요 이벤트 수신
- Skills/Agents: Manus 내 커스텀 스킬과 에이전트 관리
- Connectors: Slack, Notion, Google Calendar, Linear, Anthropic, OpenAI, Vercel 등 OAuth 기반 외부 도구 연결

공식 문서상 `task.create`는 비동기로 동작한다. 요청 후 `task_id`를 받고, `task.detail` 또는 `task.listMessages`로 상태와 결과를 확인한다.

## 3. Claude Code/opencode에서 쓰는 두 가지 방식

### 방식 A. REST 직접 호출

Claude Code나 opencode 세션 안에서 셸 명령 또는 사내 CLI를 실행한다.

장점:

- 공식 v2 API를 그대로 사용하므로 추적과 디버깅이 쉽다.
- 사내 보안 기준에 맞춰 API 키, 로그, 프롬프트 템플릿을 통제하기 쉽다.
- 세미나 실습이 단순하다.

단점:

- Claude/opencode가 Manus 작업 상태를 “도구 목록”으로 자연스럽게 인식하지는 않는다.
- 결과 폴링, 파일 업로드, 웹훅 처리를 직접 구현해야 한다.

### 방식 B. MCP 서버 경유

Manus API를 MCP 서버가 감싸고, Claude Code/opencode가 그 MCP 서버를 호출한다.

장점:

- Claude Code/opencode 안에서 `create_task`, `get_task`, `list_messages` 같은 도구로 노출할 수 있다.
- 팀 단위로 표준 워크플로우를 만들기 쉽다.
- 여러 에이전트 도구를 같은 MCP 인터페이스로 묶을 수 있다.

단점:

- 커뮤니티 MCP 서버는 보안 검토와 v2 호환성 검증이 필요하다.
- 제3자 MCP 서버는 프롬프트, 파일 URL, API 키가 지나가는 경로가 되므로 사내 코드 리뷰 없이 바로 쓰면 위험하다.
- Claude Code 공식 문서도 서드파티 MCP 서버 사용 시 보안과 prompt injection 위험을 명시한다.

## 4. 실무 적용 시나리오

사업강화 AI에이전트팀 관점에서 유효한 초기 use case:

- 시장/경쟁사 조사: Claude Code에서 조사 프롬프트를 정리하고 Manus에 장시간 리서치 태스크 위임
- 영업/제휴 리포트 초안: CRM/Notion/Slack connector를 활용한 자료 수집과 요약
- 제품/운영 지표 리서치: CSV 첨부 후 분석 결과를 슬라이드/문서 형태로 생성
- 사내 반복 업무 자동화: Claude/opencode가 업무 정의와 검증을 맡고, Manus가 외부 서비스 탐색/작업을 수행

## 5. 추천 파일럿

1. Manus API 키 발급 및 팀 테스트 계정 준비
2. REST 직접 호출로 `task.create` -> `task.listMessages` 흐름 실습
3. 커뮤니티 `manus-mcp` 또는 사내 최소 MCP 래퍼로 Claude Code 연결
4. opencode에 동일 MCP 설정 적용
5. 보안 체크리스트 통과 후 팀 표준 템플릿화

## 6. 세미나에서 강조할 리스크

- v1/v2 혼재: 검색 결과와 일부 MCP 서버 README가 v1 기본값을 언급한다. 세미나에서는 공식 v2 기준으로 설명한다.
- 비동기 실행: 일반 LLM API처럼 한 번 호출하고 즉시 최종 답을 받는 구조가 아니다.
- 비용/크레딧: 장시간 태스크와 반복 폴링은 크레딧과 rate limit을 확인해야 한다.
- 데이터 경계: 고객 정보, 사내 문서, 채용/영업 데이터는 connector 권한과 공유 링크 설정을 제한해야 한다.
- MCP 공급망: `npx`로 바로 실행하는 MCP 서버는 패키지 소스와 버전을 고정하고 리뷰해야 한다.

## 7. 참고 출처

- Manus API v2 Introduction: https://open.manus.ai/docs/v2/introduction
- Manus `task.create`: https://open.manus.ai/docs/api-reference/create-task
- Manus `task.listMessages`: https://open.manus.im/docs/v2/list-messages
- Manus Connectors: https://open.manus.ai/docs/v2/connectors
- Manus `file.upload`: https://open.manus.ai/docs/v2/upload-file
- Claude Code MCP docs: https://code.claude.com/docs/en/mcp
- opencode CLI MCP docs: https://opencode.ai/docs/cli/
- opencode configuration docs: https://opencode-ai-opencode.mintlify.app/core-concepts/configuration
- Community Manus MCP repository: https://github.com/nanameru/Manus-MCP

