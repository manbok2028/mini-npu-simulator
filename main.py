"""Mini NPU Simulator"""
import json  # data.json 로드에 사용
import math  # 숫자 유효성(유한값) 검사에 사용
import time  # 성능 측정에 사용

EPSILON = 1e-9  # 점수 비교 허용오차
REPEAT = 10  # 성능 측정 반복 횟수

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

def read_matrix(title, n=3):
    """n줄을 입력받아 n x n 숫자 행렬을 반환한다.

    줄의 숫자 개수가 n이 아니거나 숫자가 아닌 값이 있으면
    안내 문구를 출력하고 처음부터 다시 입력받는다.
    """
    print(f"{title} ({n}줄 입력, 공백 구분)")
    while True:
        matrix = []
        for _ in range(n):
            parts = input().split()
            if len(parts) != n:
                print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
                break
            try:
                row = [float(p) for p in parts]
            except ValueError:
                print("입력 형식 오류: 숫자만 입력하세요.")
                break
            if not all(math.isfinite(v) for v in row):
                print("입력 형식 오류: 유한한 숫자만 입력하세요.")
                break
            matrix.append(row)
        else:
            return matrix
        print(f"{title}을(를) 처음부터 다시 입력하세요.")


def measure_mac(pattern, filt, repeat=REPEAT):
    """MAC 연산 구간만 repeat회 측정해 평균 시간(ms)을 반환한다. (I/O 제외)"""
    total = 0.0
    for _ in range(repeat):
        start = time.perf_counter()
        mac(pattern, filt)
        total += time.perf_counter() - start
    return total / repeat * 1000


def mode_user_input():
    """모드 1: 사용자 입력 (3x3)"""
    line = "#" + "-" * 39

    print(f"\n{line}\n# [1] 필터 입력\n{line}")
    filter_a = read_matrix("필터 A")
    print()
    filter_b = read_matrix("필터 B")
    print("\n✓ 필터 A, B 저장 완료")

    print(f"\n{line}\n# [2] 패턴 입력\n{line}")
    pattern = read_matrix("패턴")
    print("\n✓ 패턴 저장 완료")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    result = judge(score_a, score_b, "A", "B")
    avg_ms = measure_mac(pattern, filter_a)

    print(f"\n{line}\n# [3] MAC 결과\n{line}")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{REPEAT}회): {avg_ms:.3f} ms")
    if result == LABEL_UNDECIDED:
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {result}")

    print(f"\n{line}\n# [4] 성능 분석 (평균/{REPEAT}회)\n{line}")
    print(f"{'크기':<8}{'평균 시간(ms)':<16}{'연산 횟수'}")
    print("-" * 36)
    print(f"{'3×3':<8}{avg_ms:<16.3f}{9}")
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