from typing import List
from pydantic import BaseModel, Field


class Product(BaseModel):
    key: str = Field(..., description="품목 식별키")
    name: str = Field(..., description="품목명")
    unit: str = Field(..., description="단위")
    item_category_code: str = Field(..., description="부류 코드")
    item_code: str = Field(..., description="품목 코드")
    kind_code: str = Field(..., description="품종 코드")
    product_cls_code: str = Field("01", description="구분 (01:소매, 02:도매)")
    product_rank_code: str = Field("04", description="등급 (04:상, 05:중)")


class PriceRecord(BaseModel):
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    price: int = Field(..., description="가격 (원)")


class PriceResponse(BaseModel):
    product: Product
    start_date: str
    end_date: str
    records: List[PriceRecord]
    data_source: str = "KAMIS Open API"
    message: str = "조회 성공"
