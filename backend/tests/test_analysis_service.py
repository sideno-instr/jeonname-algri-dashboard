"""
analysis_service 단위 테스트

테스트 케이스:
  1. 가격이 거의 일정한 데이터       → STABLE, risk_score 낮음
  2. 가격이 급격히 상승한 데이터     → RISK, change_rate 양수
  3. 가격이 급격히 하락한 데이터     → RISK, change_rate 음수
  4. 데이터가 부족한 경우 (0~1개)   → change_rate / volatility / risk_score 모두 None
  5. 위험 점수가 항상 0~1 사이인지  → clamp 검증

실행 방법:
  (backend 디렉터리에서)
  python -m pytest tests/test_analysis_service.py -v
  또는
  python tests/test_analysis_service.py
"""
import sys
import os

# backend 루트를 경로에 추가 (pytest 없이도 직접 실행 가능)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.price import PriceRecord
from models.analysis import DataQuality, RiskLevel
from services.analysis_service import compute_analysis


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def _make_records(prices: list[float], start: str = "2024-01-01") -> list[PriceRecord]:
    """날짜를 하루씩 증가시켜 PriceRecord 목록을 생성합니다."""
    from datetime import date, timedelta
    base = date.fromisoformat(start)
    return [
        PriceRecord(date=(base + timedelta(days=i)).isoformat(), price=int(p))
        for i, p in enumerate(prices)
    ]


# ---------------------------------------------------------------------------
# 테스트 케이스
# ---------------------------------------------------------------------------

def test_stable_prices():
    """가격이 거의 일정한 경우 → risk_score가 낮고 STABLE 등급이어야 한다."""
    print("\n[TEST 1] 가격이 거의 일정한 데이터")
    prices = [1000, 1002, 998, 1001, 1003, 999, 1000, 1001, 998, 1002]
    records = _make_records(prices)
    result = compute_analysis("테스트품목", "2024-01-01", "2024-01-10", records)

    print(f"  change_rate : {result.change_rate}%")
    print(f"  volatility  : {result.volatility}")
    print(f"  risk_score  : {result.risk_score}")
    print(f"  risk_level  : {result.risk_level}")
    print(f"  data_quality: {result.data_quality}")

    assert result.change_rate is not None
    assert result.risk_score is not None
    assert result.risk_score < 0.35, f"STABLE 기대, 실제 risk_score={result.risk_score}"
    assert result.risk_level == RiskLevel.STABLE
    assert result.data_quality == DataQuality.GOOD
    print("  ✅ PASS")


def test_sharp_rise():
    """가격이 급격히 상승한 경우 → change_rate 양수, RISK 등급 기대."""
    print("\n[TEST 2] 가격이 급격히 상승한 데이터")
    prices = [1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800]
    records = _make_records(prices)
    result = compute_analysis("테스트품목", "2024-01-01", "2024-01-10", records)

    print(f"  change_rate : {result.change_rate}%")
    print(f"  volatility  : {result.volatility}")
    print(f"  risk_score  : {result.risk_score}")
    print(f"  risk_level  : {result.risk_level}")

    assert result.change_rate is not None and result.change_rate > 0
    assert result.risk_score is not None and result.risk_score >= 0.65
    assert result.risk_level == RiskLevel.RISK
    print("  ✅ PASS")


def test_sharp_fall():
    """가격이 급격히 하락한 경우 → change_rate 음수, RISK 등급 기대."""
    print("\n[TEST 3] 가격이 급격히 하락한 데이터")
    prices = [3000, 2700, 2400, 2100, 1800, 1500, 1200, 900, 600, 300]
    records = _make_records(prices)
    result = compute_analysis("테스트품목", "2024-01-01", "2024-01-10", records)

    print(f"  change_rate : {result.change_rate}%")
    print(f"  volatility  : {result.volatility}")
    print(f"  risk_score  : {result.risk_score}")
    print(f"  risk_level  : {result.risk_level}")

    assert result.change_rate is not None and result.change_rate < 0
    assert result.risk_score is not None and result.risk_score >= 0.65
    assert result.risk_level == RiskLevel.RISK
    print("  ✅ PASS")


def test_insufficient_data_zero():
    """데이터가 0개인 경우 → 계산 불가 필드는 None, INSUFFICIENT 품질."""
    print("\n[TEST 4a] 데이터 0개")
    result = compute_analysis("테스트품목", "2024-01-01", "2024-01-10", [])

    print(f"  current_price: {result.current_price}")
    print(f"  change_rate  : {result.change_rate}")
    print(f"  risk_score   : {result.risk_score}")
    print(f"  risk_level   : {result.risk_level}")
    print(f"  data_quality : {result.data_quality}")

    assert result.current_price is None
    assert result.change_rate is None
    assert result.volatility is None
    assert result.risk_score is None
    assert result.risk_level is None
    assert result.data_quality == DataQuality.INSUFFICIENT
    # limitations에 부족 안내 포함 여부
    assert any("부족" in s for s in result.limitations)
    print("  ✅ PASS")


def test_insufficient_data_one():
    """데이터가 1개인 경우 → 변동률 계산 불가, None 반환."""
    print("\n[TEST 4b] 데이터 1개")
    records = _make_records([1500])
    result = compute_analysis("테스트품목", "2024-01-01", "2024-01-01", records)

    print(f"  change_rate : {result.change_rate}")
    print(f"  risk_score  : {result.risk_score}")
    print(f"  data_quality: {result.data_quality}")

    assert result.current_price == 1500
    assert result.change_rate is None
    assert result.risk_score is None
    assert result.risk_level is None
    assert result.data_quality == DataQuality.INSUFFICIENT
    print("  ✅ PASS")


def test_risk_score_clamp():
    """위험 점수가 항상 [0, 1] 범위 내에 있어야 한다."""
    print("\n[TEST 5] 위험 점수 클램프 검증 (극단값 포함)")
    # 극단적인 상승 케이스
    prices_up = [100] + [100_000] * 9
    records_up = _make_records(prices_up)
    result_up = compute_analysis("테스트품목", "2024-01-01", "2024-01-10", records_up)

    # 극단적인 하락 케이스
    prices_down = [100_000] + [100] * 9
    records_down = _make_records(prices_down)
    result_down = compute_analysis("테스트품목", "2024-01-01", "2024-01-10", records_down)

    for label, result in [("급등", result_up), ("급락", result_down)]:
        score = result.risk_score
        print(f"  [{label}] risk_score={score}")
        assert score is not None
        assert 0.0 <= score <= 1.0, f"범위 초과: {score}"

    print("  ✅ PASS")


def test_data_quality_boundaries():
    """데이터 품질 경계값 검증."""
    print("\n[TEST 6] 데이터 품질 경계값")

    cases = [
        (4,  DataQuality.INSUFFICIENT),
        (5,  DataQuality.LIMITED),
        (9,  DataQuality.LIMITED),
        (10, DataQuality.GOOD),
    ]
    for count, expected in cases:
        records = _make_records([1000] * count)
        result = compute_analysis("테스트품목", "2024-01-01", "2024-01-10", records)
        print(f"  count={count} → {result.data_quality} (기대: {expected})")
        assert result.data_quality == expected, f"count={count}: {result.data_quality} != {expected}"

    print("  ✅ PASS")


def test_limitations_always_present():
    """limitations 에 '가격 데이터만 사용한 교육용 추정 결과' 문구가 포함되어야 한다."""
    print("\n[TEST 7] limitations 필수 문구 포함 여부")
    records = _make_records([1000, 1100, 1200])
    result = compute_analysis("테스트품목", "2024-01-01", "2024-01-03", records)
    combined = " ".join(result.limitations)
    assert "교육용 추정" in combined, "교육용 추정 문구 누락"
    assert "수급 위험 추정 지수" in combined, "수급 위험 추정 지수 문구 누락"
    print(f"  limitations: {result.limitations}")
    print("  ✅ PASS")


# ---------------------------------------------------------------------------
# 직접 실행 지원
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_stable_prices,
        test_sharp_rise,
        test_sharp_fall,
        test_insufficient_data_zero,
        test_insufficient_data_one,
        test_risk_score_clamp,
        test_data_quality_boundaries,
        test_limitations_always_present,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"결과: {passed} passed / {failed} failed")
    if failed:
        sys.exit(1)
