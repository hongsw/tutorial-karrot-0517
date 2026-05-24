# SESSION 5 실습 — 로컬 LLM + baryon.ai 사례

**목표**: 토큰 비용 걱정 없는 나만의 LLM 환경 구축  
**보너스**: baryon.ai가 실제로 어떻게 LLM을 구축했는지 살펴보기

---

## PART 1 · 오늘 후원사 baryon.ai 이야기

오늘 세션의 후원사인 **baryon.ai**는 실제로 자체 LLM 서비스를 구축·운영 중인 팀입니다.

### baryon.ai가 만든 것

| 구성 요소 | 내용 |
|-----------|------|
| 모델 | Qwen3-Coder 기반 파인튜닝 |
| 인프라 | RTX 4090 + SGLang 백엔드 |
| 서비스 | `llm.baryon.ai` — OpenAI 호환 엔드포인트 |
| 인터페이스 | **TalkMode** — 한국어 AI 코딩 어시스턴트 |

**TalkMode**는 baryon.ai 인프라 위에서 동작하는 AI 어시스턴트입니다.  
opencode, Claude Code, curl 어디서든 바로 연결할 수 있습니다.

---

## PART 2 · TalkMode (llm.baryon.ai) — opencode에서 쓰기

### 사전 정보

| 항목 | 값 |
|------|-----|
| Base URL | `https://llm.baryon.ai/v1` |
| 모델 | `baryon-1` (Qwen3-Coder 기반, 한국어) |
| API Key | 불필요 (더미값 `not-used` 입력) |
| 필수 헤더 | `X-Device-Id: <UUID>` |
| 무료 한도 | 디바이스 ID당 lifetime 30회 / IP당 분당 10회 |

### STEP 1 · 디바이스 ID 생성 (한 번만)

```bash
# UUID 생성 후 파일에 저장 (고정 필수 — 매번 바꾸면 30회 소진)
mkdir -p ~/.config/opencode
uuidgen | tr 'A-Z' 'a-z' > ~/.config/opencode/baryon-device-id
cat ~/.config/opencode/baryon-device-id
# 예: 3f5a2b1c-9e44-4d6f-8b21-7c0a1d4e9f88
```

### STEP 2 · curl로 먼저 확인 (opencode 없어도 OK)

```bash
DEVICE_ID=$(cat ~/.config/opencode/baryon-device-id)

curl -sS https://llm.baryon.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: $DEVICE_ID" \
  -d '{
    "model": "baryon-1",
    "messages": [{"role": "user", "content": "이름이 뭐야?"}],
    "stream": false
  }' | jq '.choices[0].message.content'
```

기대 응답: `"저는 바리온랩스AI 입니다."`

### STEP 3 · opencode에 provider 등록

```bash
# opencode 설치 (없는 경우)
curl -fsSL https://opencode.ai/install | bash

# 설정 파일 열기
nano ~/.config/opencode/opencode.json
```

`opencode.json` 내용 (기존 설정 있으면 `provider` 블록 안에 추가):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "baryon": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "TalkMode (baryon.ai)",
      "options": {
        "baseURL": "https://llm.baryon.ai/v1",
        "apiKey": "not-used",
        "headers": {
          "X-Device-Id": "여기에-본인-UUID",
          "User-Agent": "opencode/baryon"
        }
      },
      "models": {
        "baryon-1": {
          "name": "Baryon Labs AI — Qwen3-Coder (한국어)"
        }
      }
    }
  },
  "model": "baryon/baryon-1"
}
```

### STEP 4 · JSON 검증 + 실행

```bash
# JSON 문법 확인
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null && echo "✅ valid"

# 모델 등록 확인
opencode models | grep baryon

# 테스트
opencode run -m baryon/baryon-1 "안녕, 간단하게 자기소개 해줘"
```

### 에러 대응

| 에러 | 원인 | 해결 |
|------|------|------|
| 400 | X-Device-Id 누락 | opencode.json headers 확인 |
| 429 | 30회 한도 소진 | 로컬 LLM(Ollama)으로 전환 |
| 502 | GPU 백엔드 다운 | 잠시 후 재시도 |

---

## PART 3 · 로컬 LLM — Ollama (토큰 0원, 무제한)

### 설치 (Mac/Linux)

```bash
# Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 또는 Mac:
brew install ollama
```

**LM Studio** (GUI, 비개발자 추천): [lmstudio.ai](https://lmstudio.ai) 다운로드

### 모델 받아서 실행

```bash
# 가벼운 시작 (RAM 8GB)
ollama pull llama3.2:3b
ollama run llama3.2:3b

# 코딩 작업 (RAM 16GB)
ollama pull qwen3:14b
ollama run qwen3:14b

# 한국어 양호 (RAM 32GB)
ollama pull gemma3:27b
ollama run gemma3:27b
```

### opencode에서 Ollama 사용

```json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Local Ollama",
      "options": {
        "baseURL": "http://localhost:11434/v1",
        "apiKey": "ollama"
      },
      "models": {
        "qwen3:14b": { "name": "Qwen3 14B (로컬)" }
      }
    }
  }
}
```

---

## PART 4 · 하이브리드 전략 (권장)

```
민감 데이터 / 대량 처리  → Ollama 로컬 (토큰 0원)
고난이도 추론              → Claude Opus / Sonnet (클라우드)
일상 코딩 자동완성         → Cursor + Sonnet 4.6
빠른 한국어 질문           → baryon.ai TalkMode (무료 30회)
```

```bash
# opencode에서 모델 스위치 (TUI 안에서)
/model
# → baryon/baryon-1 또는 ollama/qwen3:14b 선택 가능
```

---

## baryon.ai 아키텍처 참고

```
사용자 요청
    ↓
TalkMode 인터페이스 (UX 레이어)
    ↓
llm.baryon.ai (OpenAI 호환 API)
    ↓
SGLang 서빙 엔진
    ↓
RTX 4090 × N (GPU 클러스터)
    ↓
Qwen3-Coder (파인튜닝 모델)
```

→ 이 스택이 월 수십만원대로 팀이 직접 운영 가능  
→ 1인 사업자도 중고 4090 (150~200만원) + Ollama로 유사 환경 구축 가능

---

## 오늘 할 일 1개

```
✅ 둘 중 하나:
   A. curl로 baryon.ai (TalkMode) 30회 중 1회 테스트
   B. ollama pull llama3.2:3b 실행하고 첫 대화
```

---

## 참고 링크

- [baryon.ai](https://baryon.ai) — 후원사, LLM 인프라 구축·운영
- [llm.baryon.ai](https://llm.baryon.ai) — TalkMode 엔드포인트
- [ollama.com](https://ollama.com) — 로컬 LLM 실행
- [lmstudio.ai](https://lmstudio.ai) — GUI 로컬 LLM (비개발자 추천)
- [opencode.ai](https://opencode.ai) — 터미널 AI 코딩 에디터
