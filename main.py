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


def load_data(path="data.json"):
    """data.json을 읽어 dict로 반환한다. 실패하면 안내 문구를 출력하고 None을 반환한다."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"오류: {path} 파일을 찾을 수 없습니다. main.py와 같은 폴더에 두세요.")
    except json.JSONDecodeError as e:
        print(f"오류: {path} 형식이 올바르지 않습니다. ({e})")
    except OSError as e:
        print(f"오류: {path} 파일을 읽을 수 없습니다. ({e})")
    return None


def extract_size(key):
    """'size_13_2' 또는 'size_13' 형태의 키에서 N(13)을 추출한다."""
    parts = str(key).split("_")
    if len(parts) not in (2, 3) or parts[0] != "size" or not parts[1].isdigit():
        raise ValueError(f"키 형식 오류: {key!r} (size_N 또는 size_N_idx 형태여야 함)")
    return int(parts[1])


def validate_matrix(matrix, n, name):
    """matrix가 숫자로 된 n x n 2차원 배열인지 검증한다. 아니면 ValueError."""
    if not isinstance(matrix, list) or not all(isinstance(r, list) for r in matrix):
        raise ValueError(f"{name}: 2차원 배열이 아닙니다")
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    if rows != n or any(len(r) != n for r in matrix):
        raise ValueError(f"크기 불일치: {name} (기대 {n}×{n}, 실제 {rows}×{cols})")
    for r in matrix:
        for v in r:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ValueError(f"{name}: 숫자가 아닌 값 {v!r}")


def load_filters(data):
    """filters 섹션을 읽어 ({N: {라벨: 행렬}}, {키: 오류 사유})를 반환한다.

    필터 키(cross, x)는 표준 라벨로 정규화해서 저장한다.
    오류가 있는 필터는 건너뛰고 사유만 기록한다. (프로그램은 계속 진행)
    """
    filters, errors = {}, {}
    raw_filters = data.get("filters")
    if not isinstance(raw_filters, dict):
        print("✗ data.json에 filters 항목이 없거나 형식이 올바르지 않습니다.")
        return filters, errors

    for key, group in raw_filters.items():
        try:
            n = extract_size(key)
            if not isinstance(group, dict):
                raise ValueError("필터 묶음이 객체가 아닙니다")
            by_label = {}
            for raw_label, matrix in group.items():
                label = normalize_label(raw_label)
                validate_matrix(matrix, n, f"{key}/{raw_label}")
                by_label[label] = matrix
            missing = [lb for lb in (LABEL_CROSS, LABEL_X) if lb not in by_label]
            if missing:
                raise ValueError(f"필터 누락: {', '.join(missing)}")
            filters[n] = by_label
            print(f"✓ {key:<8} 필터 로드 완료 ({LABEL_CROSS}, {LABEL_X})")
        except ValueError as e:
            errors[str(key)] = str(e)
            print(f"✗ {key:<8} 필터 오류: {e}")
    return filters, errors


def analyze_case(key, case, filters, filter_errors):
    """패턴 1건을 분석해 결과 dict를 반환한다.

    어떤 오류가 나도 예외를 밖으로 던지지 않고 FAIL + 사유로 기록한다.
    """
    result = {
        "key": key, "status": "FAIL", "reason": "",
        "score_cross": None, "score_x": None,
        "judgment": None, "expected": None,
    }
    try:
        n = extract_size(key)
        filter_key = f"size_{n}"
        if n not in filters:
            if filter_key in filter_errors:
                raise ValueError(f"{filter_key} 필터 오류: {filter_errors[filter_key]}")
            raise ValueError(f"{filter_key} 필터가 data.json에 없습니다")
        if not isinstance(case, dict) or "input" not in case or "expected" not in case:
            raise ValueError("스키마 오류: input, expected 키가 필요합니다")

        pattern = case["input"]
        validate_matrix(pattern, n, f"{key} 패턴")
        expected = normalize_label(case["expected"])
        result["expected"] = expected

        result["score_cross"] = mac(pattern, filters[n][LABEL_CROSS])
        result["score_x"] = mac(pattern, filters[n][LABEL_X])
        judgment = judge(result["score_cross"], result["score_x"])
        result["judgment"] = judgment

        if judgment == expected:
            result["status"] = "PASS"
        elif judgment == LABEL_UNDECIDED:
            result["reason"] = "동점(UNDECIDED) 규칙"
        else:
            result["reason"] = "판정 불일치"
    except ValueError as e:
        result["reason"] = str(e)
    except Exception as e:  # 예상 못한 오류도 케이스 단위로 처리
        result["reason"] = f"예상치 못한 오류: {e}"
    return result


def print_case_result(r):
    """케이스 1건의 결과를 출력한다."""
    print(f"--- {r['key']} ---")
    if r["score_cross"] is not None:
        print(f"Cross 점수: {r['score_cross']}")
        print(f"X 점수: {r['score_x']}")
        tail = f" ({r['reason']})" if r["reason"] else ""
        print(f"판정: {r['judgment']} | expected: {r['expected']} | {r['status']}{tail}")
    else:
        print(f"FAIL | 사유: {r['reason']}")


def mode_json_analysis():
    """모드 2: data.json 분석"""
    line = "#" + "-" * 39

    data = load_data()
    if data is None:
        return None

    print(f"\n{line}\n# [1] 필터 로드\n{line}")
    filters, filter_errors = load_filters(data)

    print(f"\n{line}\n# [2] 패턴 분석 (라벨 정규화 적용)\n{line}")
    patterns = data.get("patterns")
    if not isinstance(patterns, dict):
        print("✗ data.json에 patterns 항목이 없거나 형식이 올바르지 않습니다.")
        return []

    results = []
    for key, case in patterns.items():
        r = analyze_case(key, case, filters, filter_errors)
        print_case_result(r)
        results.append(r)

    # TODO 6단계: 성능 분석 표 / 7단계: 결과 요약
    return results


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