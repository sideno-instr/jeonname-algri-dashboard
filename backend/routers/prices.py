from typing import List
from fastapi import APIRouter, HTTPException, Query
from models.price import Product, PriceResponse
from services import kamis_service

router = APIRouter(prefix="/api", tags=["prices"])


@router.get("/products", response_model=List[Product])
def list_products():
    return kamis_service.get_supported_products()


@router.get("/prices/{product_key}", response_model=PriceResponse)
async def get_period_prices(
    product_key: str,
    start_date: str = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="조회 종료일 (YYYY-MM-DD)")
):
    product = kamis_service.get_product_by_key(product_key)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"존재하지 않거나 지원하지 않는 품목 키입니다: {product_key}"
        )

    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="조회 시작일(start_date)이 종료일(end_date)보다 늦을 수 없습니다."
        )

    return await kamis_service.fetch_period_prices(product, start_date, end_date)
