"""
SESSION 30 (0531) - 자동 응답 생성기 (responder)
─────────────────────────────────────────────────────────
역할: 분류 결과에 맞는 '답장 본문'을 만들어 준다.

흐름:
  1) 분류 결과(classification)에서 카테고리를 꺼낸다.
  2) config.TEMPLATES 에서 그 카테고리에 맞는 답장 템플릿을 고른다.
  3) 템플릿 안의 빈칸({name}, {summary}, {assignee}, {category})을 실제 값으로 채운다.

비개발자 관점:
  - 답장 문구를 바꾸고 싶으면 config.py 의 TEMPLATES 만 고치면 된다.
  - 이 파일은 "빈칸 채우기" 기계라고 생각하면 쉽다.
"""

import re

import config


def _display_name(sender: str) -> str:
    """
    보낸사람(sender) 문자열에서 '표시 이름'만 뽑아낸다.

    예시:
      "김민수 <minsu.kim@example.com>"  ->  "김민수"
      "<minsu.kim@example.com>"         ->  "minsu.kim"   (이름이 없으면 이메일 로컬파트)
      "minsu.kim@example.com"           ->  "minsu.kim"
      ""                                ->  "고객"          (아무것도 없으면 기본값)

    동작 설명(비개발자용):
      - 보통 "이름 <이메일>" 형태로 들어온다. 꺾쇠(< >) 앞부분이 이름이다.
      - 이름이 없으면 이메일의 @ 앞부분(로컬파트)을 대신 쓴다.
    """
    if not sender:
        return "고객"

    sender = sender.strip()

    # 1) "이름 <이메일>" 형태에서 꺾쇠 앞의 이름 부분을 분리
    #    re.match 로 '<' 앞쪽(name_part)과 '<...>' 안쪽(email_part)을 나눈다.
    match = re.match(r"^(.*?)<([^>]*)>\s*$", sender)
    if match:
        name_part = match.group(1).strip().strip('"').strip()
        email_part = match.group(2).strip()
        if name_part:
            # 표시 이름이 있으면 그대로 사용
            return name_part
        # 표시 이름이 없으면 이메일 로컬파트(@ 앞)를 사용
        if "@" in email_part:
            local = email_part.split("@", 1)[0].strip()
            if local:
                return local
        if email_part:
            return email_part
        return "고객"

    # 2) 꺾쇠가 없는 경우: 그냥 이메일 주소만 온 형태일 수 있다.
    if "@" in sender:
        local = sender.split("@", 1)[0].strip()
        if local:
            return local

    # 3) 그 외에는 받은 문자열을 이름으로 간주
    return sender or "고객"


class _SafeDict(dict):
    """
    문자열 포맷팅용 안전 사전.

    템플릿에 {알수없는키} 가 들어있어도 에러로 죽지 않고,
    그 자리를 그대로 "{알수없는키}" 로 남겨 둔다.
    (누락 키가 있어도 안전하게 처리하기 위함)
    """

    def __missing__(self, key):
        return "{" + key + "}"


def generate_reply(email: dict, classification: dict, assignee: str) -> str:
    """
    이메일 1건에 대한 답장 본문을 만들어 반환한다.

    매개변수:
      email          : {"subject","sender","date","body"} 형태의 이메일 레코드
      classification : {"category","priority","summary","method"} 형태의 분류 결과
      assignee       : 배정된 담당자 이름(문자열)

    반환:
      빈칸이 모두 채워진 답장 본문(문자열)

    주의:
      - 카테고리에 맞는 템플릿이 없으면 '기타' 템플릿을 사용한다.
      - 스팸처럼 치환자({name} 등)가 아예 없는 템플릿도 그대로 처리된다.
      - 템플릿에 알 수 없는 빈칸이 있어도 안전하게 둔다(죽지 않음).
    """
    email = email or {}
    classification = classification or {}

    # 1) 카테고리 결정 (없으면 기본 카테고리)
    category = classification.get("category") or config.DEFAULT_CATEGORY

    # 2) 카테고리에 맞는 템플릿 선택 (없으면 '기타' 템플릿)
    template = config.TEMPLATES.get(category)
    if template is None:
        template = config.TEMPLATES.get(
            config.DEFAULT_CATEGORY,
            "{name}님, 문의 주셔서 감사합니다. 담당자 {assignee}가 확인 후 회신드리겠습니다.",
        )

    # 3) 빈칸에 채워 넣을 값 준비
    name = _display_name(email.get("sender", ""))
    summary = classification.get("summary") or "문의 내용"
    assignee = assignee or "운영팀"

    values = _SafeDict(
        name=name,
        summary=summary,
        assignee=assignee,
        category=category,
    )

    # 4) 빈칸 치환.
    #    str.format_map 은 템플릿에 {name} 같은 자리가 있으면 채우고,
    #    스팸 템플릿처럼 자리가 없으면 원문을 그대로 돌려준다.
    #    혹시 모를 포맷 오류(잘못된 중괄호 등)에도 죽지 않도록 방어한다.
    try:
        return template.format_map(values)
    except (ValueError, KeyError, IndexError):
        # 템플릿 문법이 깨진 경우엔 원문 템플릿을 그대로 반환(서비스 중단 방지)
        return template


# ── 단독 실행 테스트 ─────────────────────────────────────
# 이 파일을 직접 실행(python responder.py)하면 가짜 데이터로 답장 1건을 만들어 출력한다.
if __name__ == "__main__":
    # 가짜 이메일
    sample_email = {
        "subject": "결제 오류로 환불 요청드립니다",
        "sender": "김민수 <minsu.kim@example.com>",
        "date": "2026-05-31",
        "body": "결제가 두 번 됐어요. 환불 부탁드립니다. 너무 불편합니다.",
    }
    # 가짜 분류 결과
    sample_classification = {
        "category": "환불/불만",
        "priority": "높음",
        "summary": "결제가 두 번 되어 환불 요청",
        "method": "rule",
    }
    # 가짜 담당자
    sample_assignee = "고객만족팀-김주임"

    print("=" * 50)
    print("[발신자 이름 추출 테스트]")
    print(' "김민수 <a@b.com>"  ->', _display_name("김민수 <a@b.com>"))
    print(' "<a@b.com>"          ->', _display_name("<a@b.com>"))
    print(' "a@b.com"            ->', _display_name("a@b.com"))
    print("=" * 50)
    print("[답장 생성 테스트]")
    reply = generate_reply(sample_email, sample_classification, sample_assignee)
    print(reply)
    print("=" * 50)
    print("[스팸 템플릿(치환자 없음) 테스트]")
    spam_reply = generate_reply(
        {"sender": "광고 <ad@spam.com>"},
        {"category": "스팸", "summary": "당첨 안내"},
        "(자동처리-담당자없음)",
    )
    print(spam_reply)
