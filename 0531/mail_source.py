"""
mail_source.py
==============

문의 메일을 가져오는(읽어오는) 모듈입니다.

두 가지 방법으로 메일을 가져올 수 있어요.
  1) source="sample" : 미리 준비된 샘플 파일(samples/inbox.json)을 읽습니다.
                       (인터넷 연결이나 Mail 앱 없이도 실습할 수 있어요.)
  2) source="mail"   : macOS의 기본 "Mail.app"을 osascript(AppleScript)로 직접 읽습니다.
                       (실제 받은 편지함의 메일을 가져옵니다.)

이 모듈이 돌려주는 메일 한 통(레코드)의 모양은 다음과 같습니다.
  {
    "subject": "제목",
    "sender":  "보낸사람 이름 <이메일주소>",
    "date":    "받은 날짜(문자열)",
    "body":    "본문 내용",
  }
"""

import json
import os
import subprocess


# ----------------------------------------------------------------------------
# 파일 경로(절대경로)를 미리 계산해 둡니다.
#   - 이 파일이 위치한 폴더를 기준으로 samples/inbox.json 을 찾습니다.
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_PATH = os.path.join(BASE_DIR, "samples", "inbox.json")

# AppleScript 결과를 파싱할 때 쓰는 구분자(눈에 안 보이는 특수문자)입니다.
#   - 필드(제목/보낸이/날짜/본문) 사이를 나눌 때:  ASCII 31 (Unit Separator)
#   - 메일(레코드)과 메일 사이를 나눌 때:        ASCII 30 (Record Separator)
# 일반 텍스트에는 거의 등장하지 않는 문자라서 안전하게 쪼갤 수 있습니다.
FIELD_SEP = chr(31)   # 필드 구분자
RECORD_SEP = chr(30)  # 레코드 구분자


def fetch_emails(source: str = "sample", limit: int = 10,
                 unread_only: bool = False, mailbox: str = "inbox") -> list[dict]:
    """
    문의 메일을 가져옵니다.

    매개변수(인자)
      source      : "sample"이면 샘플 JSON 파일을, "mail"이면 macOS Mail.app을 읽습니다.
      limit       : 최대 몇 통까지 가져올지 (기본 10통).
      unread_only : True면 '읽지 않은' 메일만 가져옵니다. (source="mail"에서만 의미 있음)
      mailbox     : 어느 사서함(폴더)에서 읽을지. 기본은 "inbox"(받은 편지함).

    반환값
      메일 레코드(dict)들의 리스트. (위 docstring의 모양을 따릅니다.)
      문제가 생기면 빈 리스트([])를 돌려줍니다.
    """
    if source == "sample":
        return _fetch_from_sample(limit=limit)
    elif source == "mail":
        return _fetch_from_mail(limit=limit, unread_only=unread_only, mailbox=mailbox)
    else:
        # 알 수 없는 source가 들어오면 친절히 알려주고 빈 리스트를 돌려줍니다.
        print(f"[안내] 알 수 없는 source 값입니다: '{source}'. "
              f"'sample' 또는 'mail' 중에서 선택해 주세요.")
        return []


def _fetch_from_sample(limit: int = 10) -> list[dict]:
    """
    샘플 파일(samples/inbox.json)에서 메일을 읽어 limit 개만큼 돌려줍니다.

    - 파일이 없거나 형식이 잘못된 경우에도 프로그램이 죽지 않도록
      친절한 한국어 안내 메시지를 출력하고 빈 리스트를 돌려줍니다.
    """
    try:
        with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[안내] 샘플 파일을 찾을 수 없습니다: {SAMPLE_PATH}")
        return []
    except json.JSONDecodeError as e:
        print(f"[안내] 샘플 파일의 형식(JSON)이 올바르지 않습니다: {e}")
        return []

    # 혹시 리스트가 아니면(예: 객체 하나만 들어있으면) 안전하게 처리합니다.
    if not isinstance(data, list):
        print("[안내] 샘플 파일은 메일 목록(배열) 형태여야 합니다.")
        return []

    # 앞에서부터 limit 개만 잘라서 돌려줍니다.
    return data[:limit]


def _fetch_from_mail(limit: int = 10, unread_only: bool = False,
                     mailbox: str = "inbox") -> list[dict]:
    """
    macOS의 Mail.app을 osascript(AppleScript)로 읽어 메일을 가져옵니다.

    동작 방식
      1) AppleScript를 만들어 Mail.app의 받은 편지함 메일을 읽습니다.
      2) 각 메일의 제목/보낸이/날짜/본문을 FIELD_SEP(특수문자)로 이어 붙이고,
         메일과 메일 사이는 RECORD_SEP(특수문자)로 구분한 '하나의 긴 문자열'을 받습니다.
      3) Python에서 그 문자열을 쪼개어 메일 레코드(dict) 리스트로 만듭니다.

    실패(권한 없음 / Mail 미실행 등) 시
      - 무엇이 문제인지 친절한 한국어 안내를 출력하고 빈 리스트를 돌려줍니다.
    """
    applescript = _build_applescript(limit=limit, unread_only=unread_only,
                                     mailbox=mailbox)

    try:
        # osascript 명령으로 AppleScript를 실행합니다.
        #   -e 옵션으로 스크립트 문자열을 직접 전달합니다.
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,   # 표준출력/표준에러를 잡아둡니다.
            text=True,             # 결과를 (바이트가 아닌) 문자열로 받습니다.
            timeout=60,            # 메일이 많으면 시간이 걸리므로 넉넉히 60초.
        )
    except FileNotFoundError:
        # osascript 자체가 없는 경우 (보통 macOS가 아닐 때)
        print("[안내] 'osascript'를 실행할 수 없습니다. "
              "이 기능은 macOS에서만 동작합니다.")
        return []
    except subprocess.TimeoutExpired:
        print("[안내] Mail.app에서 메일을 읽는 데 시간이 너무 오래 걸려 중단했습니다. "
              "메일 수를 줄이거나(limit) 잠시 후 다시 시도해 주세요.")
        return []

    # 종료 코드가 0이 아니면 실행 중 오류가 난 것입니다.
    if result.returncode != 0:
        print("[안내] Mail.app에서 메일을 읽지 못했습니다.")
        print("       다음을 확인해 주세요:")
        print("       1) Mail 앱이 실행되어 있는지")
        print("       2) '시스템 설정 > 개인정보 보호 및 보안 > 자동화'에서")
        print("          터미널(또는 사용 중인 앱)에 Mail 제어 권한이 켜져 있는지")
        # AppleScript가 남긴 오류 메시지도 함께 보여줍니다.
        err = (result.stderr or "").strip()
        if err:
            print(f"       (상세 오류: {err})")
        return []

    # 정상 출력이 비어 있으면(메일이 없거나 조건에 맞는 메일이 없으면) 빈 리스트.
    raw = (result.stdout or "").strip()
    if not raw:
        return []

    return _parse_mail_output(raw)


def _build_applescript(limit: int, unread_only: bool, mailbox: str) -> str:
    """
    Mail.app을 읽는 AppleScript 문자열을 만들어 돌려줍니다.

    - 최신 메일부터 limit 개를 읽습니다.
    - unread_only=True 이면 '읽지 않은(read status가 false)' 메일만 모읍니다.
    - 각 필드는 FIELD_SEP, 각 메일은 RECORD_SEP로 이어 붙입니다.
    """
    # AppleScript 안에서 특수문자를 표현하기 위해 ASCII 코드 번호로 만듭니다.
    #   (ASCII character 31) = 필드 구분자, (ASCII character 30) = 레코드 구분자
    field_sep_code = ord(FIELD_SEP)    # 31
    record_sep_code = ord(RECORD_SEP)  # 30

    # mailbox 이름을 AppleScript용으로 매핑합니다.
    #   "inbox"는 Mail.app에서 전체 받은 편지함을 뜻하는 'inbox'로 처리합니다.
    if mailbox == "inbox":
        mailbox_ref = "inbox"
    else:
        # 그 외 이름은 계정 안의 특정 사서함 이름으로 시도합니다.
        # 사서함 이름에 큰따옴표가 섞여 깨지지 않도록 간단히 정리합니다.
        safe_name = mailbox.replace('"', "")
        mailbox_ref = f'mailbox "{safe_name}"'

    # 읽지 않은 메일만 모을지 결정하는 조건문(AppleScript)을 만듭니다.
    if unread_only:
        # read status가 false(아직 안 읽음)인 메일만 messageList에 담습니다.
        gather_block = (
            "    repeat with m in (messages of targetBox)\n"
            "      if (read status of m) is false then\n"
            "        set end of messageList to m\n"
            "      end if\n"
            "    end repeat\n"
        )
    else:
        # 조건 없이 모든 메일을 담습니다.
        gather_block = (
            "    repeat with m in (messages of targetBox)\n"
            "      set end of messageList to m\n"
            "    end repeat\n"
        )

    # 아래가 실제 실행되는 AppleScript입니다.
    #   - fieldSep / recordSep : 위에서 정한 특수 구분자
    #   - 최신 메일이 보통 앞쪽에 있으므로 앞에서부터 limit 개만 사용합니다.
    script = f"""
set fieldSep to (ASCII character {field_sep_code})
set recordSep to (ASCII character {record_sep_code})
set theLimit to {limit}
set outputText to ""

tell application "Mail"
  set targetBox to {mailbox_ref}
  set messageList to {{}}
{gather_block}
  set msgCount to count of messageList
  if msgCount is 0 then
    return ""
  end if

  set takeCount to theLimit
  if msgCount < takeCount then set takeCount to msgCount

  repeat with i from 1 to takeCount
    set m to item i of messageList
    set theSubject to ""
    set theSender to ""
    set theDate to ""
    set theBody to ""
    try
      set theSubject to (subject of m) as string
    end try
    try
      set theSender to (sender of m) as string
    end try
    try
      set theDate to (date received of m) as string
    end try
    try
      set theBody to (content of m) as string
    end try

    set thisRecord to theSubject & fieldSep & theSender & fieldSep & theDate & fieldSep & theBody
    if i is 1 then
      set outputText to thisRecord
    else
      set outputText to outputText & recordSep & thisRecord
    end if
  end repeat
end tell

return outputText
"""
    return script


def _parse_mail_output(raw: str) -> list[dict]:
    """
    AppleScript가 돌려준 '하나의 긴 문자열'을 메일 레코드(dict) 리스트로 바꿉니다.

    - RECORD_SEP로 메일 단위로 자르고,
    - 각 메일은 FIELD_SEP로 4개 필드(subject, sender, date, body)로 자릅니다.
    - 필드 개수가 모자란(깨진) 레코드는 안전하게 건너뜁니다.
    """
    emails: list[dict] = []

    # 메일 단위로 자릅니다.
    for record in raw.split(RECORD_SEP):
        if not record.strip():
            continue  # 빈 조각은 건너뜀

        # 필드 단위로 자릅니다. body 안에 FIELD_SEP가 끼어드는 일은 거의 없지만,
        # 혹시 모를 상황을 대비해 최대 3번만 나눠 마지막 조각을 본문으로 둡니다.
        parts = record.split(FIELD_SEP, 3)
        if len(parts) < 4:
            # 형식이 깨진 레코드는 무시합니다.
            continue

        subject, sender, date, body = parts
        emails.append({
            "subject": subject.strip(),
            "sender": sender.strip(),
            "date": date.strip(),
            # 본문은 앞뒤 공백/줄바꿈만 정리하고 내용은 그대로 둡니다.
            "body": body.strip(),
        })

    return emails


# ----------------------------------------------------------------------------
# 이 파일을 직접 실행했을 때 동작하는 간단한 테스트입니다.
#   예) python mail_source.py
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("샘플 메일을 읽어옵니다...")
    sample_emails = fetch_emails("sample")
    print(f"가져온 샘플 메일 건수: {len(sample_emails)}건")

    # 첫 번째 메일의 제목만 살짝 보여줍니다(잘 읽혔는지 확인용).
    if sample_emails:
        print(f"첫 번째 메일 제목: {sample_emails[0]['subject']}")
