"""
seed_data.py
------------
로컬에서 돌아가고 있는 백엔드(http://127.0.0.1:8000)에
샘플 시계열 데이터 100개를 자동으로 채워 넣는 스크립트.

예시 주제: 하루 걸음 수 기록 (2026-06-01부터 100일치)
다른 주제로 바꾸고 싶으면 generate_value() 함수만 고치면 된다.

실행 방법 (backend 폴더 안에서):
    venv/bin/python scripts/seed_data.py
"""

import random
import requests
from datetime import date, timedelta

API_BASE = "http://127.0.0.1:8000"
START_DATE = date(2026, 6, 1)
DAYS = 100


def generate_value(day_index: int) -> int:
    """
    하루 걸음 수를 그럴듯하게 생성한다.
    - 기본 7000보에서 시작해서 서서히 늘어나는 추세(운동 습관이 느는 상황을 가정)
    - 매일 랜덤한 변동(+-1500)을 더해서 실제 기록처럼 들쭉날쭉하게 만든다
    """
    base = 7000 + day_index * 15          # 완만한 증가 추세
    noise = random.randint(-1500, 1500)    # 하루하루의 변동
    return max(1000, base + noise)          # 너무 작은 값 방지


def main():
    success_count = 0
    for i in range(DAYS):
        current_date = START_DATE + timedelta(days=i)
        payload = {
            "date": current_date.isoformat(),
            "value": generate_value(i),
            "memo": "seed_data.py로 생성된 샘플 데이터",
        }
        response = requests.post(f"{API_BASE}/api/data", json=payload)
        if response.status_code == 200:
            success_count += 1
        else:
            print(f"실패: {current_date} -> {response.status_code} {response.text}")

    print(f"완료: {success_count}/{DAYS}개 데이터 추가됨")


if __name__ == "__main__":
    main()