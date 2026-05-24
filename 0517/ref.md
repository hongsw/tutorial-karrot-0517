## LiteLLM 프록시를 활용한 Manus API 연동 가이드

질문하신 내용이 맞습니다! **LiteLLM v1.80.15**부터 Manus API가 공식 지원 제공자로 추가되었으며, 이를 활용하면 Manus API를 OpenAI 호환 API로 변환하여 **Claude Code, opencode, Codex** 등에서 사용할 수 있습니다.

또한 공유해주신 `openclaw-skill-manus` 레포지토리는 OpenClaw/Clawdbot 환경에서 Manus API를 직접 호출하는 파이썬 스크립트 모음입니다. 이 두 가지 접근 방식을 종합하여, 터미널 기반 AI 코딩 도구에서 Manus API를 활용하는 방법을 상세히 설명해 드립니다.

---

### 1. LiteLLM 프록시를 통한 연동 원리

Manus API는 기본적으로 비동기 에이전트 태스크 방식(`POST /v2/tasks`)으로 동작하며, 일반적인 LLM의 실시간 스트리밍 응답(Chat Completions)과는 구조가 다릅니다.

하지만 **LiteLLM AI Gateway(Proxy)**를 중간에 두면 이 문제를 해결할 수 있습니다. LiteLLM은 클라이언트(opencode 등)로부터 OpenAI 형식의 요청을 받아 Manus API의 `/responses` 엔드포인트로 전달하고, 비동기 폴링을 내부적으로 처리한 뒤 결과를 다시 OpenAI 형식으로 클라이언트에게 반환합니다.

#### 설정 방법

**1. LiteLLM 설치**

```bash
pip install 'litellm[proxy]'
```

**2. `config.yaml` 작성**

```yaml
model_list:
  - model_name: manus-agent
    litellm_params:
      model: manus/manus-1.6-agent
      api_key: os.environ/MANUS_API_KEY
```

**3. 프록시 서버 실행**

```bash
export MANUS_API_KEY="your-manus-api-key"
litellm --config config.yaml --port 4000
```

이제 `http://localhost:4000` 주소에서 완벽한 OpenAI 호환 API가 제공됩니다.

---

### 2. 각 도구별 연동 방법

LiteLLM 프록시가 실행 중인 상태(`http://localhost:4000`)에서 각 도구를 연결하는 방법입니다.

#### A. opencode CLI 연동

opencode는 `opencode.json`을 통해 커스텀 OpenAI 호환 제공자를 쉽게 추가할 수 있습니다.

`~/.config/opencode/opencode.json` 파일에 다음을 추가합니다:

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

이후 opencode 터미널에서 `/models` 명령어를 입력하면 `Manus 1.6 Agent`를 선택하여 코딩 작업을 지시할 수 있습니다.

#### B. Claude Code 연동

Claude Code는 환경 변수를 통해 커스텀 엔드포인트를 지원합니다.

```bash
# LiteLLM 프록시 주소 설정
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="dummy-key"

# Claude Code 실행 시 모델 지정
claude --model manus-agent
```

---

### 3. OpenClaw 스킬 방식 (`openclaw-skill-manus`)

공유해주신 GitHub 레포지토리는 프록시를 거치지 않고, Manus API의 본래 목적인 **"자율 에이전트 작업(Autonomous Agent Task)"**을 터미널에서 직접 실행하기 위한 파이썬 스크립트 모음입니다.

이 방식은 코딩 보조(자동 완성 등)보다는 **독립적인 백그라운드 작업 지시**에 적합합니다.

**주요 스크립트 활용:**

- `run_task.py`: "이 레포지토리의 코드를 분석해서 README.md를 작성해줘"와 같은 복잡한 작업을 지시하고 완료될 때까지 대기합니다.
- `upload_file.py`: 로컬의 로그 파일이나 데이터 CSV를 Manus 에이전트에게 업로드하여 분석 컨텍스트로 제공합니다.
- **커넥터 활용**: "내 Gmail을 읽고 오늘 할 일을 정리해줘"처럼 Manus의 외부 서비스 연동 기능(Connectors)을 터미널에서 바로 트리거할 수 있습니다.

---

### 요약 및 추천 아키텍처

| 목적                                   | 추천 방식                    | 장점                                                                                   |
| -------------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------- |
| **코드 자동완성 및 인라인 편집**       | **LiteLLM Proxy + opencode** | 기존 코딩 워크플로우에 Manus의 강력한 추론 능력을 그대로 이식할 수 있음                |
| **대규모 리서치 및 백그라운드 자동화** | **OpenClaw 스킬 스크립트**   | Manus의 비동기 에이전트 특성과 파일 업로드, 외부 앱 연동(커넥터) 기능을 100% 활용 가능 |

결론적으로, **LiteLLM v1.80.15 업데이트 덕분에 Manus API를 일반적인 LLM처럼 프록시하여 opencode나 Claude Code에 물리는 것이 완벽하게 가능해졌습니다.** 코딩 작업 시에는 LiteLLM 프록시를 띄워두고 사용하시고, 무거운 백그라운드 작업이 필요할 때는 파이썬 스크립트로 직접 태스크를 생성하는 투트랙(Two-track) 전략을 추천합니다.
