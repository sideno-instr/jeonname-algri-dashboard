"""
분석 API 라우터

GET /api/analysis/{product_key}
  → KAMIS에서 기간 가격 데이터를 조회한 뒤
    analysis_service.compute_analysis() 로 수급 위험 추정 지수를 계산하여 반환합니다.

계산 로직은 services/analysis_service.py 에만 존재합니다.
"""
from fastapi import APIRouter, HTTPException, Query

from models.analysis import AnalysisResponse
from services import kamis_service
from services import analysis_service

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get(
    "/analysis/{product_key}",
    response_model=AnalysisResponse,
    summary="수급 위험 추정 지수 조회",
    description=(
        "지정된 품목의 기간 가격 데이터를 KAMIS에서 조회한 뒤 "
        "단순 가격 분석과 수급 위험 추정 지수를 계산합니다. "
        "거래량·공급량 데이터가 없으므로 결과는 '추정' 값입니다."
    ),
)
async def get_analysis(
    product_key: str,
    start_date: str = Query(..., description="분석 시작일 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="분석 종료일 (YYYY-MM-DD)"),
):
    # 1. 품목 유효성 검증
    product = kamis_service.get_product_by_key(product_key)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"존재하지 않거나 지원하지 않는 품목 키입니다: {product_key}",
        )

    # 2. 날짜 유효성 검증
    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="조회 시작일(start_date)이 종료일(end_date)보다 늦을 수 없습니다.",
        )

    # 3. KAMIS API에서 가격 데이터 조회
    price_response = await kamis_service.fetch_period_prices(product, start_date, end_date)

    # 4. 분석 서비스 호출 (계산 로직은 서비스에만 존재)
    return analysis_service.compute_analysis(
        product_name=product.name,
        start_date=start_date,
        end_date=end_date,
        records=price_response.records,
        data_source=price_response.data_source,
    )
