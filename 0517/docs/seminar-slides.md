# 세미나 발표안: Manus API를 Claude Code/opencode에서 활용하기

대상: 당근 사업강화 AI에이전트팀  
시간: 30분 발표 + 15분 Q&A

---

## 1. 오늘의 목표

- Manus API가 일반 LLM API와 어떻게 다른지 이해한다.
- Claude Code/opencode에서 Manus를 호출하는 두 가지 방식을 비교한다.
- 금주 파일럿으로 실행할 최소 PoC 범위를 정한다.

---

## 2. Manus API의 포지션

Manus API는 “텍스트 생성 API”보다 “비동기 AI 에이전트 작업 API”에 가깝다.

- 입력: 작업 지시, 파일, connector, skill, agent profile
- 실행: Manus가 계획 수립, 도구 사용, 웹/데이터 접근, 산출물 생성
- 출력: 메시지 히스토리, 파일/슬라이드/웹사이트, 상태 이벤트

---

## 3. v2 기준 핵심 엔드포인트

- `POST /v2/task.create`: 새 작업 생성
- `GET /v2/task.detail`: 작업 상태와 메타데이터 조회
- `GET /v2/task.listMessages`: 대화/이벤트/결과 조회
- `POST /v2/task.sendMessage`: 후속 메시지 또는 사용자 질문 응답
- `POST /v2/file.upload`: 첨부 파일 업로드 URL 발급
- `GET /v2/connector.list`: 사용 가능한 connector 확인
- `GET /v2/usage.*`: 사용량/크레딧 확인

---

## 4. 기본 호출 흐름

1. API 키를 `MANUS_API_KEY`로 설정한다.
2. `task.create`로 작업을 생성한다.
3. 응답의 `task_id`를 저장한다.
4. `task.listMessages` 또는 `task.detail`을 주기적으로 조회한다.
5. `running`, `waiting`, `stopped`, `error` 상태에 맞게 처리한다.
6. 필요하면 `task.sendMessage` 또는 `task.confirmAction`으로 재개한다.

---

## 5. Claude Code 연동 방식

### 직접 REST 호출

Claude Code 안에서 셸 스크립트 또는 사내 CLI를 실행한다.

```bash
MANUS_API_KEY=... ./scripts/manus_create_task.sh "이번 주 경쟁사 프로모션을 조사해줘"
```

### MCP 경유

Manus API wrapper를 MCP 서버로 붙인다.

```bash
claude mcp add --transport stdio --scope user \
  --env MANUS_MCP_API_KEY="$MANUS_API_KEY" \
  manus-mcp -- npx -y manus-mcp
```

Claude Code 안에서는 `/mcp`로 연결 상태를 확인한다.

---

## 6. opencode 연동 방식

opencode는 CLI로 MCP 서버를 추가하거나 JSON 설정에 `mcp` 블록을 둘 수 있다.

```bash
opencode mcp add
opencode mcp list
```

설정 예시:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "manus-mcp": {
      "type": "local",
      "command": ["npx", "-y", "manus-mcp"],
      "enabled": true,
      "env": {
        "MANUS_MCP_API_KEY": "${MANUS_API_KEY}"
      }
    }
  }
}
```

---

## 7. MCP를 붙이면 무엇이 좋아지는가

- Claude/opencode가 Manus를 “도구”로 인식한다.
- 반복 업무를 자연어 워크플로우로 만들기 쉽다.
- 태스크 생성, 상태 조회, 결과 회수 같은 작업을 한 세션에서 묶을 수 있다.
- 여러 도구와 Manus를 함께 조합할 수 있다.

---

## 8. 그래도 REST부터 해야 하는 이유

- 공식 v2 API의 실제 동작을 먼저 확인해야 한다.
- 커뮤니티 MCP 서버가 v1 기본값을 쓰는 경우가 있다.
- 사내 보안 기준상 API 키와 첨부 파일 처리 경로를 명확히 해야 한다.
- 문제가 생겼을 때 REST 로그가 가장 디버깅하기 쉽다.

---

## 9. 사업강화팀 파일럿 과제

추천 과제: “경쟁사/지역별 신규 사업 신호 리서치”

입력:

- 조사 대상 업종/지역
- 경쟁사 리스트
- 원하는 산출물 형식: 1페이지 요약, 표, 액션 아이템

출력:

- 요약 리포트
- 근거 링크
- 영업/제휴 후보 리스트
- 다음 주 실험 제안

---

## 10. 운영 체크리스트

- API 키는 개인 로컬 설정 또는 secret manager에만 둔다.
- public share link는 기본 비활성화한다.
- 고객/파트너/지원자 개인정보는 파일럿 데이터에서 제외한다.
- `npx` MCP 서버는 버전 고정과 코드 리뷰 후 사용한다.
- 실패/대기/장시간 실행 상태를 처리하는 룰을 만든다.

---

## 11. 이번 주 실행 계획

Day 1:

- API 키 발급
- REST `task.create` 실습
- 결과 폴링 확인

Day 2:

- Claude Code MCP 연결
- opencode MCP 연결
- 커뮤니티 MCP 서버 v2 호환성 점검

Day 3:

- 사업강화 use case 1개로 end-to-end 실행
- 비용, 속도, 품질, 보안 이슈 기록

Day 4-5:

- 팀 표준 프롬프트와 운영 가이드 작성
- 세미나 데모 진행

---

## 12. 결론

Manus API는 Claude/opencode를 대체하는 도구가 아니라, 두 코딩 에이전트가 장시간 외부 조사와 작업을 위임할 수 있는 실행 레이어다. 금주는 REST 직접 호출로 기준선을 만들고, MCP는 팀 워크플로우로 확장할 때 채택하는 순서가 가장 실용적이다.

