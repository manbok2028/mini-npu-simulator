"""Mini NPU Simulator"""

import json  # data.json 로드에 사용
import time  # 성능 측정에 사용

EPSILON = 1e-9  # 점수 비교 허용오차


def mac(pattern, filt):
    """MAC(Multiply-Accumulate) 연산.

    패턴과 필터의 같은 위치 값끼리 곱하고(Multiply),
    그 결과를 모두 누적해서 더한(Accumulate) 점수를 반환한다.
    외부 라이브러리 없이 이중 반복문으로 직접 구현한다.
    """
    n = len(pattern)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


# 표준 라벨: 프로그램 내부에서는 이 두 가지만 사용한다.
LABEL_CROSS = "Cross"
LABEL_X = "X"
LABEL_UNDECIDED = "UNDECIDED"

# 입력 표기 -> 표준 라벨 (expected 값 '+', 'x' / filter 키 'cross', 'x')
_LABEL_MAP = {
    "+": LABEL_CROSS,
    "cross": LABEL_CROSS,
    "x": LABEL_X,
}


def normalize_label(raw):
    """다양한 표기를 표준 라벨(Cross / X)로 통일한다.

    알 수 없는 표기는 ValueError를 발생시킨다.
    (호출하는 쪽에서 케이스 단위로 잡아 FAIL 처리한다.)
    """
    key = str(raw).strip().lower()
    if key not in _LABEL_MAP:
        raise ValueError(f"알 수 없는 라벨: {raw!r}")
    return _LABEL_MAP[key]


def judge(score_a, score_b, label_a=LABEL_CROSS, label_b=LABEL_X):
    """두 점수를 epsilon 기반으로 비교해 판정한다.

    |a - b| < EPSILON 이면 동점으로 보고 UNDECIDED를 반환한다.
    그렇지 않으면 점수가 높은 쪽의 라벨을 반환한다.
    """
    if abs(score_a - score_b) < EPSILON:
        return LABEL_UNDECIDED
    return label_a if score_a > score_b else label_b


def mode_user_input():
    """모드 1: 사용자 입력 (3x3)"""
    print("\n[모드 1] 사용자 입력 (3x3) - 아직 구현 전입니다.")


def mode_json_analysis():
    """모드 2: data.json 분석"""
    print("\n[모드 2] data.json 분석 - 아직 구현 전입니다.")


def main():
    print("=== Mini NPU Simulator ===\n")
    print("[모드 선택]\n")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    while True:
        choice = input("선택: ").strip()
        if choice == "1":
            mode_user_input()
            break
        if choice == "2":
            mode_json_analysis()
            break
        print("입력 형식 오류: 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()