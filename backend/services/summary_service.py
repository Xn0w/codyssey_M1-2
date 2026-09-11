"""
summary_service.py
-------------------
저장된 시계열 데이터를 받아서 "요약 정보"를 계산하는 곳.
이 요약본이 나중에 AI 시스템 프롬프트에 그대로 들어간다.
GPT는 숫자 100개를 직접 세고 평균 내는 걸 잘 못하니,
계산은 여기서 파이썬(정확한 산수)으로 미리 끝내고 결과만 넘겨준다.
"""


def calculate_summary(items: list[dict]) -> dict:
    """
    items: [{"date": "...", "value": ..., "memo": "..."}, ...]
    반환: 기간 / 개수 / 평균 / 최댓값 / 최솟값 / 최근 추세
    """
    if not items:
        return {
            "period": {"start": None, "end": None},
            "count": 0,
            "average": None,
            "max": None,
            "min": None,
            "recent_trend": "데이터 없음",
        }

    # 날짜순 정렬 (문자열 "YYYY-MM-DD" 형식이면 문자열 정렬 = 날짜순 정렬과 동일)
    sorted_items = sorted(items, key=lambda x: x["date"])
    values = [item["value"] for item in sorted_items]
    dates = [item["date"] for item in sorted_items]

    # 최근 5개(또는 전체가 5개 미만이면 전체)를 기준으로 추세 판단
    recent = values[-5:] if len(values) >= 5 else values
    if len(recent) < 2:
        trend = "판단 불가 (데이터 부족)"
    elif recent[-1] > recent[0]:
        trend = "증가"
    elif recent[-1] < recent[0]:
        trend = "감소"
    else:
        trend = "유지"

    return {
        "period": {"start": dates[0], "end": dates[-1]},
        "count": len(values),
        "average": round(sum(values) / len(values), 2),
        "max": max(values),
        "min": min(values),
        "recent_trend": trend,
    }
