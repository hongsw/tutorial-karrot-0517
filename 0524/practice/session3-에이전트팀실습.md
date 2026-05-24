# SESSION 3 실습 — 에이전트 팀으로 일 시켜보기

**목표**: 콘텐츠 팀 (Researcher → Writer → Critic → Publisher) 5분 안에 만들기  
**도구**: harness (Claude Code) — 터미널 어렵다면 하단 대안 참고

---

## 방법 A · harness 사용 (Claude Code 있는 분 — 추천)

> [github.com/hongsw/harness](https://github.com/hongsw/harness) — Claude Code용 에이전트 팀 팩토리

### 설치

```bash
# Claude Code 이미 설치된 상태에서
# harness는 별도 설치 없이 Claude Code 안에서 실행됩니다

# 1. 프로젝트 폴더 만들기
mkdir ~/my-agent-team && cd ~/my-agent-team
claude  # Claude Code 실행
```

### 팀 만들기 (Claude Code 안에서 입력)

```
하네스 구성해줘.
나는 1인 콘텐츠 사업자야.
매주 블로그 포스트 1개를 자동으로 기획→작성→검수→발행하는 팀이 필요해.
```

harness가 자동으로 생성하는 것:
- `Researcher` — 주제 리서치 + 키워드 수집
- `Writer` — 초안 작성
- `Critic` — 논리·톤 검수
- `Publisher` — 발행 포맷 변환 (Markdown → HTML/Notion)

### 팀 실행

```
에이전트 팀 실행해줘.
주제: "1인 사업자가 AI로 고객 응대를 자동화하는 3가지 방법"
```

---

## 방법 B · Claude.ai 웹 (터미널 없이 — 비개발자 OK)

> claude.ai → 새 채팅 → 아래 프롬프트 붙여넣기

### 프롬프트: 콘텐츠 팀 시뮬레이션

```
당신은 4명의 전문가 에이전트 팀을 진행합니다.

[Researcher] 주제를 리서치하고 핵심 포인트 5개를 뽑습니다.
[Writer] Researcher의 결과로 블로그 초안을 작성합니다.
[Critic] Writer의 초안을 검수하고 개선점 3개를 제시합니다.
[Publisher] Critic의 피드백을 반영해 최종본을 완성합니다.

각 에이전트가 순서대로 자신의 역할을 수행해주세요.

주제: "1인 사업자가 AI로 고객 응대를 자동화하는 3가지 방법"
```

---

## 방법 C · n8n 노코드 에이전트 팀 (클릭만 — 가장 쉬움)

> n8n.io → 새 워크플로우 → 아래 순서로 노드 연결

```
[Trigger] Manual / Webhook
    ↓
[Claude] Researcher 프롬프트
    ↓
[Claude] Writer 프롬프트
    ↓
[Claude] Critic 프롬프트
    ↓
[Google Docs / Notion] 결과 저장
```

n8n Claude 노드 설정:
```json
{
  "model": "claude-sonnet-4-6",
  "prompt": "당신은 [역할]. 이전 에이전트 결과: {{$json.previous}}. 지금 할 일: ..."
}
```

---

## 방법 D · Cursor Background Agent (개발자)

```bash
# Cursor 열기 → Background Agents 탭
# "New Agent" → 아래 지시문 입력

"""
너는 콘텐츠 팀의 Conductor야.
다음 작업을 에이전트 3개에게 병렬로 분배해:
1. topic_researcher: 주제 "{{TOPIC}}" 리서치
2. competitor_analyzer: 경쟁 콘텐츠 분석
3. seo_researcher: 관련 키워드 20개 수집

결과를 합쳐서 Writer에게 전달해.
"""
```

---

## 오늘 할 일 1개

```
✅ 방법 A 또는 B 중 1개로 콘텐츠 팀 실행해보기
   주제는 본인 사업의 실제 콘텐츠 주제로
```

---

## 참고

- [harness 레포](https://github.com/hongsw/harness) — Apache 2.0, 한국어 지원
- [n8n.io](https://n8n.io) — 노코드 자동화 (self-host 무료)
- [claude.ai](https://claude.ai) — 웹 브라우저, 설치 불필요
