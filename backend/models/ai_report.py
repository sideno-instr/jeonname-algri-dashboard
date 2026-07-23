"""
AI 분석 보고서 Pydantic 모델 정의

POST /api/ai-report 요청·응답 스키마
"""
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 요청 스키마
# ---------------------------------------------------------------------------
class AIReportRequest(BaseModel):
    """AI 분석 보고서 요청"""
    product_key: str = Field(..., description="품목 키 (예: napa_cabbage, rice, apple)")
    start_date: str = Field(..., description="분석 시작일 (YYYY-MM-DD)")
    end_date: str = Field(..., description="분석 종료일 (YYYY-MM-DD)")


# ---------------------------------------------------------------------------
# 응답 스키마
# ---------------------------------------------------------------------------
class AIReportResponse(BaseModel):
    """LLM이 생성한 한국어 분석 보고서"""

    summary: str = Field(
        ...,
        description="분석 결과 전체 요약 (2~3문장)"
    )
    price_change_interpretation: str = Field(
        ...,
        description="기간 가격 변동에 대한 한국어 해설"
    )
    risk_interpretation: str = Field(
        ...,
        description="수급 위험 추정 지수에 대한 한국어 해설"
    )
    recommended_action: str = Field(
        ...,
        description="농가·유통 담당자를 위한 참고 행동 제안 (확정적 자문 아님)"
    )
    limitations: str = Field(
        ...,
        description="분석 한계 및 유의사항 (LLM 생성)"
    )
