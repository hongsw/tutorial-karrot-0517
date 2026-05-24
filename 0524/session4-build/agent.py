"""
SESSION 4 실습 B: Claude API로 간단한 이메일 분류 에이전트
사용법:
  pip install anthropic
  export ANTHROPIC_API_KEY="sk-..."
  python agent.py
"""

import anthropic
import json

client = anthropic.Anthropic()

SYSTEM = """당신은 이메일 분류 에이전트입니다.
이메일을 받으면 반드시 아래 JSON 형식으로만 응답하세요.
{
  "summary": "한 줄 요약",
  "category": "문의|계약|불만|스팸|기타",
  "priority": "높음|보통|낮음",
  "draft_reply": "답장 초안 (100자 이내)"
}"""

EMAILS = [
    "안녕하세요, 컨설팅 서비스 가격이 궁금합니다. 연락 부탁드립니다.",
    "지난주 구매한 서비스가 전혀 작동하지 않아요. 환불 요청합니다.",
    "축하합니다! 당신이 당첨되었습니다. 지금 바로 클릭하세요.",
]

def classify(email: str) -> dict:
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"이메일:\n{email}"}],
    )
    return json.loads(resp.content[0].text)

if __name__ == "__main__":
    for i, email in enumerate(EMAILS, 1):
        print(f"\n[이메일 {i}] {email[:40]}...")
        result = classify(email)
        print(f"  카테고리: {result['category']} / 우선순위: {result['priority']}")
        print(f"  요약: {result['summary']}")
        print(f"  답장 초안: {result['draft_reply']}")
