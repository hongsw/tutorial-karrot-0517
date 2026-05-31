"""
담당자 배정 모듈 (assigner.py)
─────────────────────────────────────────────────────────
문의 메일이 어떤 카테고리로 분류되면, 그 카테고리를 맡은 팀의
담당자 중 한 명에게 일감을 "골고루" 나눠 주는 역할을 한다.

핵심 아이디어 = 라운드로빈(round-robin):
  같은 카테고리에 담당자가 여러 명일 때, 한 사람에게만 몰리지 않도록
  "다음 사람 → 다음 사람 → 다시 처음" 순서로 번갈아 배정한다.

  예) 기술지원 = [최엔지니어, 정엔지니어]
      1번째 문의 → 최엔지니어
      2번째 문의 → 정엔지니어
      3번째 문의 → 최엔지니어 (다시 처음으로)

배정 규칙(담당자 풀)은 config.ASSIGNEES 에 들어 있다.
이 파일을 고칠 필요 없이 config.py 만 수정하면 배정 대상이 바뀐다.
"""

import config  # 카테고리별 담당자 풀(ASSIGNEES)을 가져온다.


class Assigner:
    """
    카테고리별로 담당자를 라운드로빈 방식으로 배정하는 클래스.

    동작 방식:
      - 카테고리마다 "지금 몇 번째 사람 차례인지"를 가리키는 인덱스를
        내부 dict(_indices)에 저장해 둔다.
      - assign()을 호출할 때마다 현재 차례의 담당자를 돌려주고,
        인덱스를 1 증가시킨다(끝에 도달하면 모듈로 연산으로 처음으로 회귀).

    상태(인덱스)는 인스턴스가 살아 있는 동안 계속 유지되므로,
    같은 Assigner 객체로 여러 번 배정해야 골고루 분배된다.
    """

    def __init__(self):
        """
        Assigner 초기화.
        _indices: { 카테고리명: 다음에 배정할 담당자 인덱스 } 형태의 상태 저장소.
        처음에는 비어 있고, 카테고리가 처음 등장할 때 0으로 채워진다.
        """
        # 카테고리별 라운드로빈 인덱스(현재 차례)를 보관하는 사전.
        self._indices: dict[str, int] = {}

    def assign(self, category: str) -> str:
        """
        주어진 카테고리에 대해 다음 담당자를 배정해 반환한다.

        Args:
            category: 분류 결과 카테고리명(예: "기술지원", "환불/불만").

        Returns:
            배정된 담당자 이름 문자열(예: "기술지원팀-최엔지니어").

        규칙:
            - config.ASSIGNEES 에 해당 카테고리가 있으면 그 담당자 풀을 사용.
            - 카테고리가 없으면 '기타' 풀(config.DEFAULT_CATEGORY)을 사용.
            - 풀에서 현재 인덱스의 담당자를 고른 뒤, 인덱스를 1 증가시켜
              다음 호출 때는 그다음 사람이 나오도록 한다(모듈로로 순환).
        """
        # 1) 카테고리에 맞는 담당자 풀을 찾는다. 없으면 '기타' 풀로 대체.
        if category in config.ASSIGNEES:
            pool_key = category
        else:
            pool_key = config.DEFAULT_CATEGORY  # 보통 "기타"

        pool = config.ASSIGNEES[pool_key]

        # 안전장치: 혹시 풀이 비어 있으면 배정 불가 안내를 반환(예외로 죽지 않게).
        if not pool:
            return "(배정 대상 없음)"

        # 2) 이 카테고리의 현재 차례 인덱스를 가져온다(처음이면 0).
        #    pool_key 기준으로 상태를 관리해야 '기타'로 합쳐진 경우도 함께 순환된다.
        current = self._indices.get(pool_key, 0)

        # 3) 현재 차례의 담당자를 선택한다.
        assignee = pool[current]

        # 4) 다음 사람을 가리키도록 인덱스를 1 증가시킨다.
        #    풀 크기로 나눈 나머지(모듈로)를 써서 끝에 도달하면 처음으로 되돌린다.
        self._indices[pool_key] = (current + 1) % len(pool)

        return assignee


# ── 이 파일을 직접 실행했을 때만 동작하는 테스트 블록 ──────────
# 사용법: python assigner.py
# '기술지원'을 3번 배정해서, 엔지니어 두 명이 번갈아 나오는지(라운드로빈) 확인한다.
if __name__ == "__main__":
    print("=== Assigner 라운드로빈 테스트 ===")
    print(f"기술지원 담당자 풀: {config.ASSIGNEES['기술지원']}\n")

    assigner = Assigner()

    # '기술지원'을 3번 연속 배정 → 최 → 정 → 최 순서로 나와야 정상.
    for i in range(1, 4):
        picked = assigner.assign("기술지원")
        print(f"{i}번째 기술지원 배정 → {picked}")

    print("\n=== 카테고리가 없을 때 '기타' 풀로 대체되는지 확인 ===")
    # 존재하지 않는 카테고리를 넣으면 '기타' 풀(대표문의-운영팀)이 나와야 한다.
    print(f"알수없는카테고리 배정 → {assigner.assign('알수없는카테고리')}")
