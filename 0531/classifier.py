"""
classifier.py — 문의 메일 자동 분류기
─────────────────────────────────────────────────────────
문의 메일 한 통(dict)을 받아서 아래 정보를 돌려준다.

  {"category": 카테고리, "priority": "높음"|"보통"|"낮음",
   "summary": 한줄요약, "method": "rule"|"llm"}

동작 방식 (2단계):
  1) 규칙 분류  : config.CATEGORIES 의 키워드로 제목+본문을 검사.
                 위에서부터 검사해 처음 걸리는 카테고리로 정한다.
                 어디에도 안 걸리면 '기타'.
  2) LLM 폴백   : 규칙 결과가 '기타'이고 LLM_FALLBACK_ENABLED 면
                 Claude(anthropic)로 한 번 더 분류를 시도한다.
                 단, anthropic 미설치 / API 키 없음 / 호출 실패 시에는
                 조용히 규칙 결과를 그대로 사용한다(절대 예외로 죽지 않음).

비개발자 관점: "분류의 똑똑함"은 config.py 의 키워드만 고쳐도 바뀐다.
"""

import os
import json

import config  # 같은 폴더의 config.py (카테고리/우선순위 등 '지식')


# ── 도우미 함수들 ────────────────────────────────────────

def _build_text(email: dict) -> str:
    """제목과 본문을 한 덩어리 문자열로 합친다(키워드 검사용)."""
    subject = email.get("subject", "") or ""
    body = email.get("body", "") or ""
    return f"{subject}\n{body}"


def _match_category(text: str) -> str:
    """
    config.CATEGORIES 를 위에서부터 검사해
    처음으로 키워드가 걸리는 카테고리 이름을 반환한다.
    아무것도 안 걸리면 config.DEFAULT_CATEGORY('기타').
    """
    for category in config.CATEGORIES:
        name = category["name"]
        for keyword in category["keywords"]:
            if keyword in text:
                return name  # 첫 매칭 즉시 채택
    return config.DEFAULT_CATEGORY


def _decide_priority(text: str, category: str) -> str:
    """
    우선순위를 정한다.
      - URGENT_KEYWORDS 중 하나라도 본문/제목에 있으면 '높음'
      - 또는 카테고리가 HIGH_PRIORITY_CATEGORIES(예: 환불/불만)면 '높음'
      - 스팸은 '낮음'
      - 그 외에는 '보통'
    """
    if category == "스팸":
        return "낮음"

    # 긴급 키워드가 들어있으면 높음
    for keyword in config.URGENT_KEYWORDS:
        if keyword in text:
            return "높음"

    # 자동으로 높은 우선순위로 다루는 카테고리(예: 환불/불만)
    if category in config.HIGH_PRIORITY_CATEGORIES:
        return "높음"

    return "보통"


def _make_summary(body: str, max_len: int = 60) -> str:
    """
    본문에서 한 줄 요약을 만든다(규칙 기반).
      - 첫 번째 문장(마침표/물음표/느낌표/줄바꿈 기준)을 우선 사용
      - 그래도 길면 max_len 글자로 자르고 '…' 표시
    """
    body = (body or "").strip()
    if not body:
        return "(본문 없음)"

    # 문장 구분 기호가 처음 나오는 위치를 찾아 첫 문장만 추출
    first_sentence = body
    for sep in ["다.", ".", "?", "!", "\n"]:
        idx = body.find(sep)
        if idx != -1:
            # 구분 기호까지 포함해서 자른다(예: "…요청합니다.")
            cut = idx + len(sep) if sep in ("다.", ".") else idx + 1
            candidate = body[:cut].strip()
            if candidate:
                first_sentence = candidate
                break

    # 너무 길면 max_len 으로 줄임
    if len(first_sentence) > max_len:
        return first_sentence[:max_len].rstrip() + "…"
    return first_sentence


def _llm_classify(email: dict) -> dict | None:
    """
    Claude(anthropic SDK)로 메일을 재분류한다.

    성공하면 {"category", "priority", "summary"} dict 반환,
    실패하면 None 반환(규칙 결과 유지용).

    아래 어떤 경우에도 예외를 밖으로 던지지 않는다:
      - anthropic 패키지 미설치
      - ANTHROPIC_API_KEY 환경변수 없음
      - 네트워크/응답 오류, JSON 파싱 실패 등
    """
    try:
        # API 키가 없으면 LLM 호출 자체를 하지 않는다(비용/오류 방지)
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return None

        # anthropic 미설치면 ImportError → 아래 except 에서 조용히 None
        import anthropic

        client = anthropic.Anthropic()

        # 선택 가능한 카테고리 목록(규칙과 동일한 이름 + 기타)
        category_names = [c["name"] for c in config.CATEGORIES] + [config.DEFAULT_CATEGORY]

        subject = email.get("subject", "")
        body = email.get("body", "")

        prompt = (
            "너는 고객 문의 메일 분류기다. 아래 메일을 읽고 JSON 으로만 답하라.\n"
            f"가능한 category 값: {', '.join(category_names)}\n"
            "priority 값은 '높음', '보통', '낮음' 중 하나.\n"
            "summary 는 한국어 한 줄(60자 이내) 요약.\n"
            "반드시 아래 형식의 JSON 만 출력(설명 문장 금지):\n"
            '{"category": "...", "priority": "...", "summary": "..."}\n\n'
            f"제목: {subject}\n"
            f"본문: {body}\n"
        )

        response = client.messages.create(
            model=config.LLM_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        # 응답 텍스트 모으기
        raw = "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        ).strip()

        # 혹시 코드블록(```json ... ```)으로 감싸져 오면 안쪽만 추출
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)

        # 카테고리 검증: 모르는 값이면 기타로 보정
        category = data.get("category", config.DEFAULT_CATEGORY)
        if category not in category_names:
            category = config.DEFAULT_CATEGORY

        priority = data.get("priority", "보통")
        if priority not in ("높음", "보통", "낮음"):
            priority = "보통"

        summary = (data.get("summary") or "").strip() or _make_summary(body)

        return {"category": category, "priority": priority, "summary": summary}

    except Exception:
        # 어떤 오류든 조용히 무시하고 규칙 결과를 쓰게 한다.
        return None


# ── 메인 함수 ────────────────────────────────────────────

def classify(email: dict) -> dict:
    """
    메일 한 통을 분류한다.

    Args:
        email: {"subject", "sender", "date", "body"} 형태의 dict

    Returns:
        {"category", "priority", "summary", "method"} dict
        - method: "rule"(규칙 분류) 또는 "llm"(Claude 폴백 분류)
    """
    text = _build_text(email)
    body = email.get("body", "")

    # 1차: 규칙 기반 분류
    category = _match_category(text)
    priority = _decide_priority(text, category)
    summary = _make_summary(body)
    method = "rule"

    result = {
        "category": category,
        "priority": priority,
        "summary": summary,
        "method": method,
    }

    # 2차: 규칙으로 '기타'가 나왔고 LLM 폴백이 켜져 있으면 Claude 시도
    if category == config.DEFAULT_CATEGORY and config.LLM_FALLBACK_ENABLED:
        llm = _llm_classify(email)
        if llm is not None:
            # LLM 결과로 교체. priority 는 규칙 보강(긴급 키워드 등) 한번 더 적용.
            llm_category = llm["category"]
            llm_priority = _decide_priority(text, llm_category)
            # 규칙상 높음이 아니면 LLM 이 판단한 priority 를 존중
            if llm_priority != "높음":
                llm_priority = llm["priority"]
            result = {
                "category": llm_category,
                "priority": llm_priority,
                "summary": llm["summary"],
                "method": "llm",
            }

    return result


# ── 단독 실행 테스트 ─────────────────────────────────────
if __name__ == "__main__":
    # samples/inbox.json 의 첫 번째 메일을 분류해 본다.
    samples_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "samples", "inbox.json"
    )
    with open(samples_path, "r", encoding="utf-8") as f:
        emails = json.load(f)

    first = emails[0]
    print("── 입력 메일 ─────────────────────────")
    print(f"제목 : {first.get('subject')}")
    print(f"보낸이: {first.get('sender')}")
    print(f"본문 : {first.get('body')}")
    print()

    result = classify(first)
    print("── 분류 결과 ─────────────────────────")
    print(f"카테고리 : {result['category']}")
    print(f"우선순위 : {result['priority']}")
    print(f"요약     : {result['summary']}")
    print(f"방식     : {result['method']}")
