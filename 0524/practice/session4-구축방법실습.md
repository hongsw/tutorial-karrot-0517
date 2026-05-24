# SESSION 4 실습 — 에이전트 팀 구축 방법

**목표**: 본인 수준에 맞는 옵션 1개 선택 → 오늘 저녁 첫 실행  
**소요**: 옵션별 15~60분

---

## 옵션 A · 노코드 — n8n (코딩 0줄)

> "오늘 저녁부터 시작 가능"

```bash
# 로컬 설치 (Docker 있는 분)
docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n

# 브라우저: http://localhost:5678
```

**클라우드 (설치 없이)**: [app.n8n.io](https://app.n8n.io) → Free plan

### 첫 자동화: 이메일 → Claude → Notion

```
[Gmail Trigger] 새 이메일 수신
  ↓
[Claude] 요약 + 카테고리 분류
  ↓
[Notion] 분류된 결과 저장
```

n8n Claude 노드 System Prompt:
```
당신은 이메일 분류 에이전트입니다.
이메일을 받으면:
1. 한 줄 요약
2. 카테고리: [문의/계약/스팸/기타]
3. 우선순위: [높음/보통/낮음]
을 JSON으로 반환하세요.
```

---

## 옵션 B · Vibe-coding — Claude Code / Cursor

> "이번 주말에 첫 프로토타입"

```bash
# Claude Code 설치
curl -fsSL https://claude.ai/install.sh | bash
# 또는: npm install -g @anthropic-ai/claude-code

# 프로젝트 시작
mkdir ~/my-agent && cd ~/my-agent
claude

# Claude Code 안에서:
# "나는 1인 컨설팅 사업자야. 고객 문의 이메일을 받으면
#  자동으로 분류하고 답장 초안을 만드는 에이전트를 만들어줘."
```

### 빠른 에이전트 스크립트 (Python)

```python
# agent.py — Claude API로 간단한 이메일 분류 에이전트
import anthropic

client = anthropic.Anthropic()

def classify_email(email_text: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system="당신은 이메일 분류 에이전트입니다. JSON으로만 응답하세요.",
        messages=[{
            "role": "user",
            "content": f"이메일 분류:\n\n{email_text}"
        }]
    )
    return response.content[0].text

# 테스트
email = "안녕하세요, 컨설팅 서비스 가격이 궁금합니다. 연락 부탁드립니다."
print(classify_email(email))
```

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-..."
python agent.py
```

---

## 옵션 C · 프레임워크 — LangGraph / CrewAI (개발자)

> "한 달 학습 후 프로덕션"

```bash
pip install crewai

# crew.py
```

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="리서처",
    goal="주어진 주제에 대해 핵심 정보 5개를 수집한다",
    backstory="1인 사업자를 위한 전문 리서처",
    verbose=True
)

writer = Agent(
    role="라이터",
    goal="리서처의 결과로 블로그 포스트 초안을 작성한다",
    backstory="SEO와 독자 경험을 아는 콘텐츠 전문가",
    verbose=True
)

task1 = Task(description="'AI 고객응대 자동화' 리서치", agent=researcher)
task2 = Task(description="리서치 결과로 포스트 작성", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
result = crew.kickoff()
print(result)
```

```bash
pip install crewai
export OPENAI_API_KEY="..."  # 또는 Claude 설정
python crew.py
```

---

## 옵션 D · Agent Work OS — harness + MCP (중급)

> "본인 도메인의 영구 자산화"

```bash
# Claude Code + harness로 시작
cd ~/my-business-os
claude

# 안에서:
# "하네스 구성해줘.
#  나는 [사업 설명]. 
#  [반복 업무 설명]을 자동화하고 싶어."
```

→ harness가 CLAUDE.md + 에이전트 스킬 파일 자동 생성  
→ MCP 서버 연결로 Notion/Slack/Linear 직접 호출

---

## 결정 트리

```
코딩 0줄도 안 써봤다          → 옵션 A (n8n 오늘 시작)
AI랑 대화하며 만들어본 적 있다 → 옵션 B (Claude Code 이번 주말)
백엔드 경험 있다               → 옵션 C (CrewAI 한 달)
본인 도메인 자산화 원한다      → 옵션 D (harness + MCP)
```

---

## 오늘 할 일 1개

```
✅ 위 4개 옵션 중 1개 골라서 "Hello World" 에이전트 실행
   (결과 스크린샷 → 그룹 채팅에 공유)
```
