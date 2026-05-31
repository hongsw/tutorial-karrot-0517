"""
pipeline.py — 문의 메일 자동화 파이프라인 (통합 실행기)
─────────────────────────────────────────────────────────
앞에서 만든 4개의 부품(모듈)을 하나로 이어 붙여, 메일 한 통이 들어오면
"분류 → 담당자 배정 → 답장 생성 → 결과 저장"까지 한 번에 처리한다.

4단계 흐름(메일 1통 기준):
  1) classify(email)            : 카테고리·우선순위·요약을 정한다.
  2) Assigner.assign(category)  : 그 카테고리를 맡을 담당자를 라운드로빈으로 정한다.
  3) generate_reply(...)        : 카테고리 템플릿으로 답장 본문을 만든다.
  4) 결과 누적                  : 한 통의 처리 결과를 dict로 모아 둔다.

모든 메일을 처리한 뒤에는 reports/ 폴더에 타임스탬프가 붙은
리포트 3종(Markdown / CSV / JSON)을 저장한다.

비개발자 관점:
  - "지식"(카테고리/담당자/템플릿)은 전부 config.py 에 있다.
  - 이 파일은 그 지식을 이용해 메일을 줄 세워 처리하는 "컨베이어 벨트"다.
"""

import os
import csv
import json
from datetime import datetime

# 같은 폴더의 부품 모듈들을 가져온다.
from classifier import classify
from assigner import Assigner
from responder import generate_reply


# ── 경로 상수 ────────────────────────────────────────────
# 이 파일이 위치한 폴더를 기준으로 reports/ 폴더 경로를 만든다(절대경로).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


# ── 보기 좋은 콘솔 출력용 도우미 ─────────────────────────

def _priority_icon(priority: str) -> str:
    """우선순위에 어울리는 이모지를 붙여 한눈에 보이게 한다."""
    return {"높음": "🔴", "보통": "🟡", "낮음": "⚪"}.get(priority, "🟡")


def _print_one(index: int, total: int, email: dict, result: dict) -> None:
    """메일 1통의 처리 결과를 사람이 읽기 좋게 콘솔에 출력한다."""
    print("─" * 60)
    print(f"📩 [{index}/{total}] {email.get('subject', '(제목 없음)')}")
    print(f"   보낸이 : {email.get('sender', '(알 수 없음)')}")
    print(f"   분류   : {result['category']}  "
          f"{_priority_icon(result['priority'])} 우선순위 {result['priority']}  "
          f"(방식: {result['method']})")
    print(f"   요약   : {result['summary']}")
    print(f"   담당자 : 👤 {result['assignee']}")
    print("   ✉️  자동 답장 ─────────────")
    # 답장 본문은 줄마다 들여쓰기해서 보기 좋게 출력한다.
    for line in result["reply"].splitlines():
        print(f"     {line}")


# ── 메인 파이프라인 ──────────────────────────────────────

def run_pipeline(emails: list[dict], verbose: bool = True) -> list[dict]:
    """
    메일 목록을 받아 4단계 처리를 수행하고, 결과 리스트를 반환한다.

    Args:
        emails  : 이메일 레코드 dict 리스트 [{"subject","sender","date","body"}, ...]
        verbose : True면 각 메일의 처리 과정을 콘솔에 자세히 출력한다.

    Returns:
        결과 dict 리스트. 각 항목 형태:
          {subject, sender, category, priority, summary, method, assignee, reply}

    동작 주의:
        - Assigner 인스턴스는 한 번만 만들어 재사용한다.
          (매 메일마다 새로 만들면 라운드로빈이 항상 첫 담당자만 배정한다.)
    """
    results: list[dict] = []

    if not emails:
        if verbose:
            print("⚠️  처리할 메일이 없습니다. (빈 목록)")
        return results

    # 라운드로빈 상태를 유지하려면 Assigner 는 '한 번만' 생성해 공유해야 한다.
    assigner = Assigner()

    total = len(emails)
    if verbose:
        print("=" * 60)
        print(f"📨 문의 메일 자동화 시작 — 총 {total}건 처리")
        print("=" * 60)

    for i, email in enumerate(emails, start=1):
        # 1단계: 분류 (카테고리/우선순위/요약/방식)
        classification = classify(email)

        # 2단계: 담당자 배정 (카테고리별 라운드로빈)
        assignee = assigner.assign(classification["category"])

        # 3단계: 답장 생성 (카테고리 템플릿에 빈칸 채우기)
        reply = generate_reply(email, classification, assignee)

        # 4단계: 결과 누적
        record = {
            "subject": email.get("subject", ""),
            "sender": email.get("sender", ""),
            "category": classification["category"],
            "priority": classification["priority"],
            "summary": classification["summary"],
            "method": classification["method"],
            "assignee": assignee,
            "reply": reply,
        }
        results.append(record)

        if verbose:
            _print_one(i, total, email, record)

    if verbose:
        print("─" * 60)
        print(f"✅ 처리 완료: 총 {total}건")

    # 처리 결과를 파일로 저장(리포트 3종).
    saved = _save_reports(results)
    if verbose and saved:
        print("=" * 60)
        print("💾 리포트 저장 완료:")
        for path in saved:
            print(f"   - {path}")
        print("=" * 60)

    return results


# ── 집계(카테고리별 통계) ────────────────────────────────

def _aggregate(results: list[dict]) -> dict[str, dict]:
    """
    카테고리별 건수와 우선순위 분포를 집계한다(리포트의 표용).

    반환 예:
      {"환불/불만": {"count": 1, "높음": 1, "보통": 0, "낮음": 0}, ...}
    """
    agg: dict[str, dict] = {}
    for r in results:
        cat = r["category"]
        if cat not in agg:
            agg[cat] = {"count": 0, "높음": 0, "보통": 0, "낮음": 0}
        agg[cat]["count"] += 1
        # 우선순위 키가 표준 3종 중 하나면 카운트(혹시 모를 값은 무시)
        if r["priority"] in ("높음", "보통", "낮음"):
            agg[cat][r["priority"]] += 1
    return agg


# ── 리포트 저장 ──────────────────────────────────────────

def _save_reports(results: list[dict]) -> list[str]:
    """
    결과 리스트를 reports/ 폴더에 3가지 형식으로 저장한다.
      - report_<ts>.md   : 사람이 읽는 요약 + 카테고리별 집계 표
      - results_<ts>.csv  : 표 계산 프로그램(엑셀 등)에서 열기 좋은 형식
      - results_<ts>.json : 프로그램이 다시 읽기 좋은 형식

    Returns:
        저장한 파일들의 절대경로 리스트.
    """
    # reports/ 폴더가 없으면 만든다(이미 있으면 그대로 둔다).
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 타임스탬프(예: 20260531_152300) — 파일명이 겹치지 않도록 사용.
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    md_path = os.path.join(REPORTS_DIR, f"report_{ts}.md")
    csv_path = os.path.join(REPORTS_DIR, f"results_{ts}.csv")
    json_path = os.path.join(REPORTS_DIR, f"results_{ts}.json")

    # 1) JSON 저장 — 원본 결과를 그대로 보존(한글 깨짐 방지 ensure_ascii=False).
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 2) CSV 저장 — 답장은 줄바꿈이 많으므로 한 줄로 정리해 칸에 넣는다.
    fieldnames = ["subject", "sender", "category", "priority",
                  "summary", "method", "assignee", "reply"]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = dict(r)
            # 답장 본문의 줄바꿈은 CSV 한 칸에서 보기 좋게 ' / ' 로 합친다.
            row["reply"] = " / ".join(r["reply"].splitlines())
            writer.writerow(row)

    # 3) Markdown 저장 — 사람이 읽는 요약 보고서.
    _write_markdown(md_path, results, ts)

    return [md_path, csv_path, json_path]


def _write_markdown(md_path: str, results: list[dict], ts: str) -> None:
    """사람이 읽기 좋은 Markdown 리포트를 작성한다(요약 + 집계 표 + 상세)."""
    agg = _aggregate(results)
    total = len(results)
    high_count = sum(1 for r in results if r["priority"] == "높음")
    llm_count = sum(1 for r in results if r["method"] == "llm")

    lines: list[str] = []
    lines.append(f"# 문의 메일 자동화 리포트 ({ts})")
    lines.append("")
    lines.append("> 당근모임 30회차(0531) 실습 — 문의 메일 자동 분류·배정·응답 결과")
    lines.append("")

    # ── 요약 섹션 ──
    lines.append("## 📊 요약")
    lines.append("")
    lines.append(f"- 총 처리 건수: **{total}건**")
    lines.append(f"- 높음 우선순위: **{high_count}건**")
    lines.append(f"- LLM 폴백 분류: **{llm_count}건** (나머지는 규칙 분류)")
    lines.append("")

    # ── 카테고리별 집계 표 ──
    lines.append("## 📁 카테고리별 집계")
    lines.append("")
    lines.append("| 카테고리 | 건수 | 높음 | 보통 | 낮음 |")
    lines.append("|---|---:|---:|---:|---:|")
    # 건수가 많은 카테고리부터 정렬해 보여준다.
    for cat, stat in sorted(agg.items(), key=lambda kv: kv[1]["count"], reverse=True):
        lines.append(
            f"| {cat} | {stat['count']} | {stat['높음']} | "
            f"{stat['보통']} | {stat['낮음']} |"
        )
    lines.append("")

    # ── 메일별 상세 ──
    lines.append("## 📨 메일별 상세")
    lines.append("")
    for i, r in enumerate(results, start=1):
        lines.append(f"### {i}. {r['subject'] or '(제목 없음)'}")
        lines.append("")
        lines.append(f"- 보낸이: {r['sender']}")
        lines.append(f"- 분류: **{r['category']}** / 우선순위: **{r['priority']}** "
                     f"/ 방식: {r['method']}")
        lines.append(f"- 담당자: {r['assignee']}")
        lines.append(f"- 요약: {r['summary']}")
        lines.append("")
        lines.append("**자동 답장**")
        lines.append("")
        # 답장 본문은 코드블록으로 감싸 원문 줄바꿈을 그대로 보존한다.
        lines.append("```")
        lines.append(r["reply"])
        lines.append("```")
        lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── 단독 실행 테스트 ─────────────────────────────────────
# python pipeline.py 로 실행하면 샘플 메일을 직접 읽어 파이프라인을 돌린다.
if __name__ == "__main__":
    # mail_source 를 통해 샘플 메일을 읽어 온다(없어도 동작하도록 방어).
    try:
        from mail_source import fetch_emails
        sample_emails = fetch_emails("sample")
    except Exception as e:  # noqa: BLE001  (테스트 편의를 위해 폭넓게 잡음)
        print(f"[안내] 샘플 메일을 불러오지 못했습니다: {e}")
        sample_emails = []

    run_pipeline(sample_emails, verbose=True)
