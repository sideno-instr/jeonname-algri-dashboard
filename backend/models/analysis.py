"""
분석 결과 Pydantic 모델 정의

수급 위험 추정 지수 응답 스키마를 포함합니다.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 내부 열거형 상수 (Enum 대신 Literal 사용 → JSON 직렬화 편의)
# ---------------------------------------------------------------------------
class RiskLevel:
    STABLE = "STABLE"       # 0.0 ≤ score < 0.35
    CAUTION = "CAUTION"     # 0.35 ≤ score < 0.65
    RISK = "RISK"           # 0.65 ≤ score ≤ 1.0


class DataQuality:
    GOOD = "GOOD"                   # 유효 데이터 10개 이상
    LIMITED = "LIMITED"             # 5개 이상 10개 미만
    INSUFFICIENT = "INSUFFICIENT"   # 5개 미만


# ---------------------------------------------------------------------------
# 분석 요청 파라미터 (서비스 내부용)
# ---------------------------------------------------------------------------
class AnalysisRequest(BaseModel):
    product_key: str = Field(..., description="품목 키")
    start_date: str = Field(..., description="분석 시작일 (YYYY-MM-DD)")
    end_date: str = Field(..., description="분석 종료일 (YYYY-MM-DD)")


# ---------------------------------------------------------------------------
# 분석 응답 스키마
# ---------------------------------------------------------------------------
class AnalysisResponse(BaseModel):
    """수급 위험 추정 지수 분석 결과"""

    product: str = Field(..., description="품목명")
    start_date: str = Field(..., description="분석 시작일")
    end_date: str = Field(..., description="분석 종료일")

    # ── 기본 가격 통계 ──────────────────────────────────────────────────────
    current_price: Optional[int] = Field(None, description="최종(최근) 유효 가격 (원). 데이터 없을 시 null")
    average_price: Optional[float] = Field(None, description="기간 평균 가격 (원). 데이터 없을 시 null")
    highest_price: Optional[int] = Field(None, description="기간 최고 가격 (원). 데이터 없을 시 null")
    lowest_price: Optional[int] = Field(None, description="기간 최저 가격 (원). 데이터 없을 시 null")

    # ── 변동성 지표 ─────────────────────────────────────────────────────────
    change_rate: Optional[float] = Field(
        None,
        description="기간 변동률 (첫 유효가격 대비 마지막 유효가격, %). 유효 데이터 2개 미만이면 null"
    )
    volatility: Optional[float] = Field(
        None,
        description="일별 가격 변동률의 표준편차. 유효 데이터 2개 미만이면 null"
    )

    # ── 위험 지수 ───────────────────────────────────────────────────────────
    risk_score: Optional[float] = Field(
        None,
        description="수급 위험 추정 지수 (0~1). 유효 데이터 2개 미만이면 null"
    )
    risk_level: Optional[str] = Field(
        None,
        description="위험 등급 (STABLE / CAUTION / RISK). 유효 데이터 2개 미만이면 null"
    )

    # ── 메타 정보 ───────────────────────────────────────────────────────────
    data_count: int = Field(..., description="분석에 사용된 유효 가격 데이터 수")
    data_quality: str = Field(
        ...,
        description="데이터 품질 (GOOD / LIMITED / INSUFFICIENT)"
    )
    limitations: List[str] = Field(
        ...,
        description="분석 한계 및 유의사항"
    )
    data_source: str = Field(
        default="KAMIS Open API (농산물유통정보)",
        description="데이터 출처"
    )
