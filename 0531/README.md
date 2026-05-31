# 문의 메일 자동화 (당근모임 30회차 · 0531 실습)

고객 문의 메일을 받아서 **자동으로 분류 → 담당자 배정 → 답장 초안 생성 → 리포트 저장**까지
한 번에 처리하는 작은 프로그램입니다. Python 표준 라이브러리만 사용하므로 추가 설치가 필요 없습니다.

> 실습 핵심 포인트: "프로그램의 똑똑함"은 코드가 아니라 **`config.py`** 에 들어 있습니다.
> 비개발자도 `config.py` 의 키워드/담당자/템플릿만 고치면 동작이 바뀝니다.

---

## 1. 프로그램 개요

매일 쌓이는 문의 메일을 사람이 일일이 읽고 분류·배정·회신하는 일은 반복적이고 시간이 많이 듭니다.
이 프로그램은 그 과정을 자동화합니다.

- **분류(Classify)**: 제목+본문 키워드로 카테고리(환불/불만, 가격문의, 기술지원 등)와 우선순위를 판단
- **배정(Assign)**: 카테고리별 담당자 풀에서 라운드로빈(번갈아) 방식으로 담당자 지정
- **응답(Reply)**: 카테고리별 템플릿으로 답장 초안 자동 생성
- **리포트(Report)**: 처리 결과를 Markdown / CSV / JSON 3종 파일로 저장

---

## 2. 폴더 구조

```
0531/
├── config.py        # 🔧 "지식" 모음 (카테고리/담당자/템플릿/우선순위/LLM 설정)  ← 여기를 고치면 동작이 바뀜
├── mail_source.py   # 📥 메일 가져오기 (샘플 파일 또는 macOS Mail.app)
├── classifier.py    # 🏷️  메일 분류 (규칙 + LLM 폴백)
├── assigner.py      # 👤 담당자 라운드로빈 배정
├── responder.py     # ✉️  답장 초안 생성 (템플릿 채우기)
├── pipeline.py      # 🔗 위 부품들을 이어 붙인 처리 파이프라인 + 리포트 저장
├── run.py           # ▶️  실행 진입점 (CLI)
├── samples/
│   └── inbox.json   # 📨 실습용 샘플 문의 메일 7건
├── reports/         # 💾 실행 결과 리포트가 저장되는 곳(자동 생성)
├── README.md        # 📖 이 문서
└── WORKFLOW.md      # 🤖 이 코드를 "병렬 서브에이전트"로 만든 과정·효과 설명
```

> 이 프로그램이 **어떻게 만들어졌는지**(병렬 AI 에이전트 워크플로우)가 궁금하면
> [`WORKFLOW.md`](./WORKFLOW.md) 를 보세요.

---

## 3. 4단계 파이프라인 설명

메일 한 통이 들어오면 아래 순서로 처리됩니다 (`pipeline.py` 의 `run_pipeline`).

| 단계 | 모듈 / 함수 | 하는 일 |
|---|---|---|
| 1) 분류 | `classifier.classify(email)` | 카테고리·우선순위·요약 결정 (규칙 우선, '기타'면 LLM 폴백 시도) |
| 2) 배정 | `assigner.Assigner.assign(category)` | 카테고리 담당자 풀에서 라운드로빈으로 1명 선택 |
| 3) 응답 | `responder.generate_reply(...)` | 카테고리 템플릿의 빈칸을 채워 답장 초안 작성 |
| 4) 저장 | `pipeline._save_reports(...)` | 전체 결과를 `reports/` 에 MD/CSV/JSON 으로 저장 |

> ⚠️ **중요**: `Assigner` 인스턴스는 파이프라인 전체에서 **딱 한 번** 생성해 재사용합니다.
> 메일마다 새로 만들면 라운드로빈 상태가 초기화되어 항상 첫 담당자만 배정됩니다.

### 결과 레코드 형태
```python
{
  "subject":  "제목",
  "sender":   "보낸사람 <메일주소>",
  "category": "환불/불만",
  "priority": "높음" | "보통" | "낮음",
  "summary":  "한 줄 요약",
  "method":   "rule" | "llm",
  "assignee": "고객만족팀-김주임",
  "reply":    "자동 생성된 답장 본문",
}
```

---

## 4. 실행 방법

작업 디렉토리 기준으로 실행합니다. (프로젝트 가상환경 Python 사용)

### (A) 샘플 메일로 실습 — 가장 쉬움
```bash
cd /Users/hongmartin/dev/tutorial_karrot_0517
.venv/bin/python 0531/run.py --source sample
```
- `samples/inbox.json` 의 7건을 처리하고 콘솔에 결과를 보여준 뒤, `reports/` 에 파일 3종을 만듭니다.

### (B) 실제 macOS Mail.app 에서 읽기
```bash
.venv/bin/python 0531/run.py --source mail --limit 20
.venv/bin/python 0531/run.py --source mail --unread-only        # 읽지 않은 메일만
.venv/bin/python 0531/run.py --source mail --mailbox "고객문의"  # 특정 사서함
```

### (C) 조용히 실행 (리포트만 생성)
```bash
.venv/bin/python 0531/run.py --quiet
```

### CLI 옵션
| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--source` | `sample` 또는 `mail` | `sample` |
| `--limit` | 가져올 최대 메일 수 | `10` |
| `--unread-only` | 읽지 않은 메일만 (mail 전용) | 꺼짐 |
| `--mailbox` | 읽을 사서함 이름 | `inbox` |
| `--quiet` | 처리 과정 출력 끄기 | 꺼짐 |

---

## 5. macOS Mail.app 자동화 권한 안내

`--source mail` 은 AppleScript(osascript)로 Mail.app 을 읽습니다. 처음 실행 시 권한이 필요합니다.

1. Mail 앱이 **실행 중**인지 확인합니다.
2. 처음 실행하면 macOS 가 "터미널이 Mail 을 제어하려 합니다" 라고 물어봅니다 → **허용**.
3. 권한이 거부됐다면 다음 경로에서 직접 켜 줍니다.
   - **시스템 설정 → 개인정보 보호 및 보안 → 자동화 → (사용 중인 터미널/앱) → Mail 체크**
4. 권한이 없거나 macOS 가 아니면 프로그램은 **에러로 죽지 않고** 안내 메시지를 출력한 뒤 빈 결과로 종료합니다.

---

## 6. config.py 커스터마이즈 방법

코드를 건드리지 않고 `config.py` 만 수정하면 동작이 바뀝니다.

- **분류 규칙 바꾸기** → `CATEGORIES`
  - 카테고리는 **위에서부터** 검사하며 **처음 걸린 키워드**로 분류됩니다(first-match-wins).
  - ★ **순서가 결과를 바꾼다 (핵심 실습 포인트)**: 처음엔 `[광고] 무료 당첨` 스팸이
    `제휴/파트너십`(키워드 `광고`)으로, "API 에러" 문의가 `환불/불만`(키워드 `에러`)으로
    엉뚱하게 분류됐습니다. **코드는 한 줄도 안 고치고** `config.py`에서
    ① `스팸`을 맨 위로 올리고 ② `에러/오류`를 `기술지원` 키워드로 옮기자 7건 모두 올바르게 분류됐습니다.
  - 직접 실험: `스팸`을 다시 아래로 내리거나 키워드를 옮겨 보고 `python run.py --source sample` 로
    결과가 어떻게 달라지는지 비교해 보세요.
- **담당자 바꾸기** → `ASSIGNEES`
  - 카테고리별 담당자 목록. 여러 명이면 라운드로빈으로 골고루 배정됩니다.
- **답장 문구 바꾸기** → `TEMPLATES`
  - `{name}` `{summary}` `{assignee}` `{category}` 자리표시자를 자유롭게 사용하세요.
- **우선순위 규칙** → `URGENT_KEYWORDS`, `HIGH_PRIORITY_CATEGORIES`
  - 긴급 키워드가 들어 있거나 고우선 카테고리면 `높음`으로 판정됩니다.

---

## 7. LLM 폴백 사용법 (선택)

규칙으로 분류했을 때 결과가 **`기타`** 인 경우에만, Claude(anthropic)로 한 번 더 분류를 시도합니다(비용 절약).

- 활성화 조건: `config.LLM_FALLBACK_ENABLED = True` (기본값)
- 사용 모델: `config.LLM_MODEL` (기본 `claude-haiku-4-5-...`)
- **필요한 것**:
  1. `pip install anthropic` (가상환경에)
  2. 환경변수 설정:
     ```bash
     export ANTHROPIC_API_KEY="sk-ant-..."
     ```
- **없어도 괜찮습니다**: anthropic 미설치 또는 API 키가 없으면 LLM 호출을 건너뛰고
  **조용히 규칙 결과를 그대로 사용**합니다(에러로 죽지 않음). `method` 값으로 `rule`/`llm` 을 구분할 수 있습니다.

---

## 8. 모듈별 단독 테스트

각 부품은 `python <파일>` 로 단독 실행해 동작을 확인할 수 있습니다.

```bash
.venv/bin/python 0531/mail_source.py   # 샘플 메일 읽기 확인
.venv/bin/python 0531/classifier.py    # 첫 메일 분류 확인
.venv/bin/python 0531/assigner.py      # 라운드로빈 배정 확인
.venv/bin/python 0531/responder.py     # 답장 생성/이름추출 확인
.venv/bin/python 0531/pipeline.py      # 샘플 전체 파이프라인 실행
```

---

당근모임 30회차(2026-05-31) 실습 자료입니다. 즐거운 자동화 되세요! 🥕
