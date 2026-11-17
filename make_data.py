"""테스트용 data.json 생성 스크립트 (모드 2 검증용)."""
import json


def cross(n):
    c = n // 2
    return [[1 if (i == c or j == c) else 0 for j in range(n)] for i in range(n)]


def x_shape(n):
    return [[1 if (i == j or i + j == n - 1) else 0 for j in range(n)] for i in range(n)]


data = {
    "filters": {
        f"size_{n}": {"cross": cross(n), "x": x_shape(n)} for n in (5, 13, 25)
    },
    "patterns": {
        "size_5_1": {"input": x_shape(5), "expected": "x"},
        "size_5_2": {"input": cross(5), "expected": "+"},
        "size_13_1": {"input": x_shape(13), "expected": "x"},
        "size_13_2": {"input": cross(13), "expected": "+"},
        "size_25_1": {"input": x_shape(25), "expected": "x"},
        "size_25_2": {"input": cross(25), "expected": "+"},
        # --- 오류/실패 확인용 케이스 ---
        "size_5_3": {"input": [[0] * 5 for _ in range(5)], "expected": "x"},   # 동점 -> FAIL
        "size_13_3": {"input": x_shape(5), "expected": "x"},                   # 크기 불일치
        "size_5_4": {"input": x_shape(5), "expected": "circle"},               # 알 수 없는 라벨
        "size_7_1": {"input": x_shape(7), "expected": "x"},                    # size_7 필터 없음
    },
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
print("data.json 생성 완료")