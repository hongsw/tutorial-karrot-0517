"""
run.py — 문의 메일 자동화 실행 진입점 (CLI)
─────────────────────────────────────────────────────────
명령줄(터미널)에서 이 프로그램을 실행하는 "시작 버튼"이다.
메일을 가져와서(mail_source) 파이프라인(pipeline)에 흘려보낸다.

사용법(예시):
  # 1) 샘플 메일로 실습(기본값) — Mail 앱/인터넷 없이 바로 동작
  python run.py
  python run.py --source sample

  # 2) 실제 macOS Mail.app 받은 편지함에서 읽기 (macOS + 자동화 권한 필요)
  python run.py --source mail
  python run.py --source mail --limit 20
  python run.py --source mail --unread-only          # 읽지 않은 메일만
  python run.py --source mail --mailbox "고객문의"     # 특정 사서함 이름

  # 3) 콘솔 출력을 줄이고 조용히 실행(리포트 파일만 생성)
  python run.py --quiet

옵션 설명:
  --source       sample | mail   (기본 sample)
  --limit        최대 가져올 메일 수 (기본 10)
  --unread-only  읽지 않은 메일만 (source=mail 일 때 의미 있음)
  --mailbox      읽을 사서함 이름 (기본 inbox=받은 편지함)
  --quiet        처리 과정 콘솔 출력을 끈다(요약만 표시)

주의(Mail.app 사용 시):
  - 처음 실행하면 macOS가 "Mail 제어 권한"을 물어볼 수 있다. 허용해야 한다.
  - 권한 위치: 시스템 설정 > 개인정보 보호 및 보안 > 자동화 > (사용 중인 터미널) > Mail
"""

import argparse

from mail_source import fetch_emails
from pipeline import run_pipeline


def main() -> None:
    """명령줄 인자를 해석해 메일을 수집하고 파이프라인을 실행한다."""
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="문의 메일 자동 분류·담당자 배정·답장 생성 프로그램 "
                    "(당근모임 30회차 실습)",
    )
    parser.add_argument(
        "--source", choices=["sample", "mail"], default="sample",
        help="메일 출처: sample(샘플 파일) 또는 mail(macOS Mail.app). 기본 sample",
    )
    parser.add_argument(
        "--limit", type=int, default=10,
        help="최대 가져올 메일 수 (기본 10)",
    )
    parser.add_argument(
        "--unread-only", action="store_true",
        help="읽지 않은 메일만 가져온다 (source=mail 일 때 의미 있음)",
    )
    parser.add_argument(
        "--mailbox", default="inbox",
        help="읽을 사서함 이름 (기본 inbox = 받은 편지함)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="처리 과정 콘솔 출력을 끄고 요약만 표시한다",
    )

    args = parser.parse_args()

    # verbose 는 --quiet 의 반대.
    verbose = not args.quiet

    if verbose:
        print(f"🔎 메일 수집 중 ... (source={args.source}, limit={args.limit}, "
              f"unread_only={args.unread_only}, mailbox={args.mailbox})")

    # 1) 메일 수집
    emails = fetch_emails(
        source=args.source,
        limit=args.limit,
        unread_only=args.unread_only,
        mailbox=args.mailbox,
    )

    if not emails:
        # 수집된 메일이 없으면 친절히 알리고 종료(에러로 죽지 않음).
        print("ℹ️  가져온 메일이 없습니다. "
              "(--source mail 인 경우 Mail 앱 실행/자동화 권한을 확인해 주세요.)")
        return

    if verbose:
        print(f"✅ 메일 {len(emails)}건 수집 완료. 파이프라인을 시작합니다.\n")

    # 2) 파이프라인 실행(분류 → 배정 → 답장 → 리포트 저장)
    results = run_pipeline(emails, verbose=verbose)

    # --quiet 모드에서도 마지막 한 줄 요약은 보여 준다.
    if not verbose:
        high = sum(1 for r in results if r["priority"] == "높음")
        print(f"처리 완료: 총 {len(results)}건 (높음 {high}건). "
              f"리포트는 reports/ 폴더를 확인하세요.")


if __name__ == "__main__":
    main()
