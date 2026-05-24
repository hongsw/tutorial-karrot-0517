# LiteLLM 프록시를 통한 Manus API 연동 가이드

대상: 당근 사업강화 AI에이전트팀  
기준: LiteLLM v1.80.15 이상 / Manus API v2

---

## 개요

LiteLLM v1.80.15부터 Manus API가 공식 지원 제공자로 추가되었습니다.  
LiteLLM 프록시를 중간에 두면 Manus API를 **완전한 OpenAI 호환 API**로 변환할 수 있어  
Claude Code, opencode, Codex 등 어떤 OpenAI 호환 클라이언트에서도 Manus를 바로 사용할 수 있습니다.

### 동작 원리

```
클라이언트 (Claude Code / opencode)
       ↓  OpenAI Chat Completions 요청
LiteLLM 프록시 (localhost:4000)
       ↓  Manus /responses 엔드포인트로 변환
Manus API (비동기 폴링 내부 처리)
       ↑  OpenAI 형식 응답 반환
LiteLLM 프록시
       ↑  결과 전달
클라이언트
```

Manus API의 비동기 에이전트 태스크 구조(`POST /v2/tasks`)를 LiteLLM이 내부적으로 폴링·변환하여  
클라이언트에는 표준 스트리밍 응답처럼 반환합니다.

---

## 1. 사전 준비

- Python 3.8 이상
- Manus API 키 (`MANUS_API_KEY`)
- Claude Code 또는 opencode 설치

```bash
# API 키를 환경변수로 설정
export MANUS_API_KEY="your-manus-api-key"
```

---

## 2. LiteLLM 설치 및 설정

### 2-1. 설치

```bash
pip install 'litellm[proxy]'
```

### 2-2. 설치 확인 테스트

```bash
litellm --version
# 출력 예: litellm v1.80.15 이상인지 확인
```

### 2-3. config.yaml 작성

프로젝트 루트 또는 홈 디렉터리에 파일 생성:

```yaml
# litellm_config.yaml
model_list:
  - model_name: manus-agent
    litellm_params:
      model: manus/manus-1.6-agent
      api_key: os.environ/MANUS_API_KEY
```

`os.environ/MANUS_API_KEY` 표기는 LiteLLM이 런타임에 환경변수를 참조하는 방식입니다.  
API 키를 파일에 직접 쓰지 않습니다.

### 2-4. 프록시 서버 실행

```bash
litellm --config litellm_config.yaml --port 4000
```

정상 실행 시 아래와 같이 출력됩니다:

```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:4000
```

---

## 3. 프록시 동작 테스트

서버 실행 상태에서 별도 터미널을 열어 다음을 순서대로 확인합니다.

### 3-1. 헬스체크

```bash
curl -sS http://localhost:4000/health | jq .
# 기대값: {"status": "healthy"} 또는 모델 상태 JSON
```

### 3-2. 사용 가능한 모델 목록 확인

```bash
curl -sS http://localhost:4000/v1/models \
  -H "Authorization: Bearer dummy-key" | jq '.data[].id'
# 기대값: "manus-agent" 출력
```

### 3-3. 단순 Chat Completions 호출 테스트

```bash
curl -sS http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy-key" \
  -d '{
    "model": "manus-agent",
    "messages": [{"role": "user", "content": "안녕하세요. 테스트입니다."}],
    "max_tokens": 100
  }' | jq '{id: .id, content: .choices[0].message.content}'
# 기대값: id와 Manus 응답 content 출력
```

---

## 4. opencode CLI 연동

### 4-1. 설정 파일 작성

`~/.config/opencode/opencode.json` 파일에 추가:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "litellm-manus": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Manus via LiteLLM",
      "options": {
        "baseURL": "http://localhost:4000/v1",
        "apiKey": "dummy-key"
      },
      "models": {
        "manus-agent": {
          "name": "Manus 1.6 Agent"
        }
      }
    }
  }
}
```

기존 설정이 없다면 디렉터리를 먼저 생성합니다:

```bash
mkdir -p ~/.config/opencode
```

### 4-2. opencode 연동 테스트

```bash
# 설정 파일 JSON 유효성 검사
jq . ~/.config/opencode/opencode.json

# opencode 실행 후 모델 목록 확인
opencode
# 터미널 안에서 /models 명령 입력 → "Manus 1.6 Agent" 표시 확인
```

### 4-3. 실제 작업 지시 테스트

opencode 세션 내에서 모델을 `Manus 1.6 Agent`로 선택한 후:

```
당근마켓 경쟁사 앱 3개의 주요 기능을 한 문장씩 정리해줘.
```

- LiteLLM 프록시 터미널에 요청 로그가 찍히는지 확인
- opencode에 응답이 반환되는지 확인

---

## 5. Claude Code 연동

### 5-1. 환경변수 설정 및 실행

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="dummy-key"

claude --model manus-agent
```

### 5-2. Claude Code 연동 테스트

```bash
# 환경변수가 올바르게 설정되었는지 확인
echo "BASE_URL: $ANTHROPIC_BASE_URL"
echo "TOKEN: $ANTHROPIC_AUTH_TOKEN"

# Claude Code 실행 후 간단한 테스트
claude --model manus-agent -p "안녕하세요. 연동 테스트입니다. 한 문장으로 응답해주세요."
```

- 응답이 터미널에 출력되면 연동 성공
- LiteLLM 프록시 로그에도 요청이 찍히는지 교차 확인

### 5-3. 인터랙티브 세션 테스트

```bash
claude --model manus-agent
# 세션 진입 후
> 이번 주 한국 e-커머스 시장의 주요 이슈를 3줄로 요약해줘.
```

---

## 6. openclaw-skill-manus 방식 (프록시 없이 직접 호출)

LiteLLM 프록시를 거치지 않고 Manus API를 직접 비동기 태스크로 실행하는 방식입니다.  
코딩 보조보다 **독립적인 장시간 백그라운드 작업**에 적합합니다.

### 6-1. 기존 스크립트 활용

이 레포의 `scripts/manus_create_task.sh`가 동일한 방식입니다:

```bash
# 태스크 생성 및 task_id 획득
export MANUS_API_KEY="your-api-key"
./scripts/manus_create_task.sh "한국어로 당근 신규 사업 기회 5개를 조사해줘"
```

### 6-2. 태스크 상태 조회 테스트

```bash
# task_id를 변수로 저장 후 상태 조회
TASK_ID="앞 단계에서 받은 task_id"

curl -sS "https://api.manus.ai/v2/task.detail?task_id=$TASK_ID" \
  -H "x-manus-api-key: $MANUS_API_KEY" | jq '{status: .status, title: .title}'
```

### 6-3. 결과 메시지 조회 테스트

```bash
curl -sS "https://api.manus.ai/v2/task.listMessages?task_id=$TASK_ID&order=asc&limit=50" \
  -H "x-manus-api-key: $MANUS_API_KEY" | jq '.messages[-1].content'
```

상태가 `running`이면 잠시 기다렸다가 재조회합니다. `stopped`가 되면 결과를 확인합니다.

---

## 7. 방식 비교 및 선택 기준

| 목적 | 추천 방식 | 장점 |
|------|-----------|------|
| 코딩 세션 인라인 질의/편집 | **LiteLLM Proxy + Claude Code/opencode** | 기존 워크플로우 그대로 사용, 추가 설정 최소화 |
| 장시간 리서치·백그라운드 자동화 | **직접 REST 호출 (스크립트)** | 비동기 특성 100% 활용, 폴링·파일 업로드·커넥터 완전 제어 |
| 팀 표준 워크플로우 | **MCP 서버 경유** | Claude/opencode가 도구로 인식, 여러 에이전트 통합 용이 |

---

## 8. 전체 테스트 체크리스트

세미나 전 또는 팀 온보딩 시 아래 항목을 순서대로 확인합니다.

### 환경 준비
- [ ] `MANUS_API_KEY` 환경변수 설정 확인 (`echo $MANUS_API_KEY`)
- [ ] LiteLLM v1.80.15 이상 설치 확인 (`litellm --version`)
- [ ] `litellm_config.yaml` 파일 존재 및 YAML 문법 이상 없음

### LiteLLM 프록시
- [ ] `litellm --config litellm_config.yaml --port 4000` 오류 없이 실행됨
- [ ] `/health` 엔드포인트 200 응답 확인
- [ ] `/v1/models` 에서 `manus-agent` 모델 목록 확인
- [ ] `curl` Chat Completions 테스트 정상 응답 수신

### opencode 연동
- [ ] `~/.config/opencode/opencode.json` JSON 유효성 통과 (`jq .`)
- [ ] opencode `/models` 에서 `Manus 1.6 Agent` 표시 확인
- [ ] 간단한 질문에 정상 응답 수신 및 프록시 로그 확인

### Claude Code 연동
- [ ] `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` 환경변수 설정 확인
- [ ] `claude --model manus-agent -p "테스트"` 정상 응답 수신
- [ ] 인터랙티브 세션에서 응답 수신 확인

### REST 직접 호출
- [ ] `./scripts/manus_create_task.sh` 실행 시 `task_id` 반환 확인
- [ ] `task.detail` 조회로 상태 확인
- [ ] `task.listMessages` 조회로 최종 결과 수신 확인

### 보안
- [ ] API 키가 config 파일에 직접 쓰이지 않음 (환경변수 방식 사용)
- [ ] `share_visibility` 기본값 `private` 유지 확인
- [ ] MCP 서버 사용 시 버전 고정 및 소스 확인 (`npm audit`)

---

## 9. 자주 발생하는 오류와 해결책

| 증상 | 원인 | 해결 |
|------|------|------|
| `MANUS_API_KEY is required` | 환경변수 미설정 | `export MANUS_API_KEY=...` 실행 후 재시도 |
| 프록시 `Connection refused` | LiteLLM 서버 미실행 | `litellm --config ...` 먼저 실행 |
| `model not found` | config.yaml 모델명 불일치 | `model_name` 값이 호출 시 사용한 이름과 일치하는지 확인 |
| Manus 태스크 `running` 상태 지속 | 복잡한 요청은 수 분 소요 | `task.detail` 반복 조회, `status`가 `stopped`가 될 때까지 대기 |
| opencode에서 모델 미표시 | JSON 설정 오류 | `jq . ~/.config/opencode/opencode.json` 으로 파싱 오류 확인 |

---

## 10. 관련 문서

- [research-brief.md](./research-brief.md): Manus API 도입 조사 요약
- [setup-guide.md](./setup-guide.md): MCP 서버 방식 설정 가이드
- [seminar-slides.md](./seminar-slides.md): 30분 세미나 발표안
- [../examples/manus-task-create.json](../examples/manus-task-create.json): task.create 요청 예시 JSON
- [../scripts/manus_create_task.sh](../scripts/manus_create_task.sh): REST 직접 호출 스크립트
