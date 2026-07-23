"""
수급 위험 추정 지수 계산 서비스

가격 데이터(PriceRecord 목록)를 받아 통계 분석과
수급 위험 추정 지수를 산출합니다.

계산 기준:
  - change_rate : 첫 유효가 대비 마지막 유효가의 변동률(%)
  - volatility  : pandas pct_change 기반 일별 변동률의 표준편차
  - 변동률 점수  : min(|change_rate| / 20, 1)
  - 변동성 점수  : min(volatility / 0.15, 1)
  - risk_score  : 변동률 점수 × 0.6 + 변동성 점수 × 0.4  (클램프 [0,1])
  - risk_level  : STABLE(0~0.35) / CAUTION(0.35~0.65) / RISK(0.65~1.0)
  - data_quality: GOOD(≥10) / LIMITED(5~9) / INSUFFICIENT(<5)

중요: 유효 데이터가 2개 미만이면 change_rate, volatility,
      risk_score, risk_level 은 None 으로 반환합니다.
"""
from typing import List, Optional, Tuple

import pandas as pd

from models.price import PriceRecord
from models.analysis import AnalysisResponse, DataQuality, RiskLevel

# 분석 한계 문구 (항상 포함)
_BASE_LIMITATIONS: List[str] = [
    "가격 데이터만 사용한 교육용 추정 결과입니다. 실제 수급 위험 판단에 그대로 적용하지 마십시오.",
    "실제 거래량·공급량 데이터가 포함되지 않아 '수급 위험 지수'가 아닌 '수급 위험 추정 지수'로 표시합니다.",
    "KAMIS 제공 가격은 전국 평균 기준이며, 지역별·등급별 실제 가격과 차이가 있을 수 있습니다.",
]


# ---------------------------------------------------------------------------
# 내부 헬퍼
# ---------------------------------------------------------------------------

def _classify_quality(count: int) -> str:
    if count >= 10:
        return DataQuality.GOOD
    if count >= 5:
        return DataQuality.LIMITED
    return DataQuality.INSUFFICIENT


def _classify_risk(score: float) -> str:
    if score < 0.35:
        return RiskLevel.STABLE
    if score < 0.65:
        return RiskLevel.CAUTION
    return RiskLevel.RISK


def _extract_valid_prices(records: List[PriceRecord]) -> pd.Series:
    """날짜 순 정렬 후 유효한(null 아닌) 가격만 추출한 Series 반환."""
    sorted_records = sorted(records, key=lambda r: r.date)
    prices = [r.price for r in sorted_records if r.price is not None]
    return pd.Series(prices, dtype=float)


# ---------------------------------------------------------------------------
# 공개 서비스 함수
# ---------------------------------------------------------------------------

def compute_analysis(
    product_name: str,
    start_date: str,
    end_date: str,
    records: List[PriceRecord],
    data_source: str = "KAMIS Open API (농산물유통정보)",
) -> AnalysisResponse:
    """
    PriceRecord 목록을 기반으로 수급 위험 추정 지수를 계산합니다.

    Parameters
    ----------
    product_name : 품목명 (str)
    start_date   : 분석 시작일 (YYYY-MM-DD)
    end_date     : 분석 종료일 (YYYY-MM-DD)
    records      : PriceRecord 목록
    data_source  : 데이터 출처 레이블

    Returns
    -------
    AnalysisResponse
    """
    prices = _extract_valid_prices(records)
    n = len(prices)

    # ── 기본 통계 ────────────────────────────────────────────────────────────
    current_price: Optional[int] = int(prices.iloc[-1]) if n > 0 else None
    average_price: Optional[float] = round(float(prices.mean()), 2) if n > 0 else None
    highest_price: Optional[int] = int(prices.max()) if n > 0 else None
    lowest_price: Optional[int] = int(prices.min()) if n > 0 else None

    # ── 변동성 지표 (유효 데이터 2개 이상 필요) ───────────────────────────────
    change_rate: Optional[float] = None
    volatility: Optional[float] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None

    limitations = list(_BASE_LIMITATIONS)

    if n < 2:
        limitations.append(
            f"유효 가격 데이터가 {n}개로 부족하여 변동률·변동성·위험 지수를 계산할 수 없습니다. "
            "최소 2개 이상의 유효 데이터가 필요합니다."
        )
    else:
        first_price = float(prices.iloc[0])
        last_price = float(prices.iloc[-1])

        # change_rate: 첫 유효가 대비 마지막 유효가 변동률 (%)
        change_rate = round(((last_price - first_price) / first_price) * 100, 4)

        # volatility: pct_change 일별 변동률의 표준편차
        daily_returns = prices.pct_change().dropna()
        volatility = round(float(daily_returns.std()), 6) if len(daily_returns) > 0 else 0.0

        # 위험 점수 계산
        change_score = min(abs(change_rate) / 20.0, 1.0)
        volatility_score = min(volatility / 0.15, 1.0)
        raw_score = change_score * 0.6 + volatility_score * 0.4
        risk_score = round(max(0.0, min(1.0, raw_score)), 4)
        risk_level = _classify_risk(risk_score)

    return AnalysisResponse(
        product=product_name,
        start_date=start_date,
        end_date=end_date,
        current_price=current_price,
        average_price=average_price,
        highest_price=highest_price,
        lowest_price=lowest_price,
        change_rate=change_rate,
        volatility=volatility,
        risk_score=risk_score,
        risk_level=risk_level,
        data_count=n,
        data_quality=_classify_quality(n),
        limitations=limitations,
        data_source=data_source,
    )
