from typing import Dict, List, Optional
import httpx
from fastapi import HTTPException
from config import settings
from models.price import Product, PriceRecord, PriceResponse

# 농축수산물 품목 및 등급 코드표 기반 주요 품목 KAMIS 명세
SUPPORTED_PRODUCTS: Dict[str, Product] = {
    "rice": Product(
        key="rice",
        name="쌀",
        unit="20kg",
        item_category_code="100",  # 식량작물
        item_code="111",            # 쌀
        kind_code="01",            # 일반계
        product_cls_code="01",     # 소매
        product_rank_code="04"     # 상품
    ),
    "111": Product(
        key="111",
        name="쌀",
        unit="20kg",
        item_category_code="100",
        item_code="111",
        kind_code="01",
        product_cls_code="01",
        product_rank_code="04"
    ),
    "napa_cabbage": Product(
        key="napa_cabbage",
        name="배추",
        unit="1포기",
        item_category_code="200",  # 채소류
        item_code="211",            # 배추
        kind_code="01",            # 봄 / 여름 배추
        product_cls_code="01",     # 소매
        product_rank_code="04"     # 상품
    ),
    "211": Product(
        key="211",
        name="배추",
        unit="1포기",
        item_category_code="200",
        item_code="211",
        kind_code="01",
        product_cls_code="01",
        product_rank_code="04"
    ),
    "apple": Product(
        key="apple",
        name="사과",
        unit="10개",
        item_category_code="400",  # 과일류
        item_code="411",            # 사과
        kind_code="05",            # 후지
        product_cls_code="01",     # 소매
        product_rank_code="04"     # 상품
    ),
    "411": Product(
        key="411",
        name="사과",
        unit="10개",
        item_category_code="400",
        item_code="411",
        kind_code="05",
        product_cls_code="01",
        product_rank_code="04"
    )
}


def get_supported_products() -> List[Product]:
    unique_products: Dict[str, Product] = {}
    for p in SUPPORTED_PRODUCTS.values():
        if p.item_code not in unique_products:
            unique_products[p.item_code] = p
    return list(unique_products.values())


def get_product_by_key(product_key: str) -> Optional[Product]:
    target = product_key.strip()
    if target in SUPPORTED_PRODUCTS:
        return SUPPORTED_PRODUCTS[target]
    for prod in SUPPORTED_PRODUCTS.values():
        if prod.item_code == target or prod.key == target or prod.name == target:
            return prod
    return None


def _extract_val(val) -> str:
    if isinstance(val, list):
        return str(val[0]) if val else ""
    return str(val) if val is not None else ""


def _parse_price(price_val) -> Optional[int]:
    raw = _extract_val(price_val).strip().replace(",", "")
    if not raw or raw in ["-", ".", "None"]:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def _parse_date(yyyy_val, regday_val) -> Optional[str]:
    yyyy = _extract_val(yyyy_val).strip()
    regday = _extract_val(regday_val).strip()
    if not regday:
        return None
    if "-" in regday and len(regday) == 10:
        return regday
    if "/" in regday:
        parts = regday.split("/")
        if len(parts) == 2 and yyyy:
            return f"{yyyy}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        elif len(parts) == 3:
            return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    return None


async def fetch_period_prices(product: Product, start_date: str, end_date: str) -> PriceResponse:
    if not settings.KAMIS_API_KEY or not settings.KAMIS_API_ID:
        raise HTTPException(
            status_code=500,
            detail="KAMIS API 인증키(KAMIS_API_KEY / KAMIS_API_ID)가 설정되지 않았습니다. backend/.env 파일을 확인해주세요."
        )

    # KAMIS Open API periodProductList 호출
    params = {
        "action": "periodProductList",
        "p_productclscode": product.product_cls_code,
        "p_startday": start_date,
        "p_endday": end_date,
        "p_itemcategorycode": product.item_category_code,
        "p_itemcode": product.item_code,
        "p_kindcode": product.kind_code,
        "p_productrankcode": product.product_rank_code,
        "p_countrycode": "",
        "p_convert_kg_yn": "N",
        "p_cert_key": settings.KAMIS_API_KEY,
        "p_cert_id": settings.KAMIS_API_ID,
        "p_returntype": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.KAMIS_BASE_URL, params=params)
            response.raise_for_status()
            res_data = response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="KAMIS API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="KAMIS API 서버 통신 중 오류가 발생했습니다.")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="KAMIS API 서버 연결에 실패했습니다.")
    except Exception:
        raise HTTPException(status_code=502, detail="KAMIS API 응답 데이터를 해석하지 못했습니다.")

    data_section = res_data.get("data") if isinstance(res_data, dict) else None

    if not data_section or not isinstance(data_section, dict):
        return PriceResponse(
            product=product,
            start_date=start_date,
            end_date=end_date,
            records=[],
            message="해당 기간의 가격 데이터가 존재하지 않습니다."
        )

    error_code = data_section.get("error_code")
    if error_code and error_code != "000":
        if error_code == "001":
            raise HTTPException(status_code=401, detail="KAMIS API 인증에 실패했습니다. (API Key/ID 확인 필요)")
        raise HTTPException(status_code=502, detail=f"KAMIS API 처리 실패 (오류 코드: {error_code})")

    items = data_section.get("item")
    if not items or not isinstance(items, list):
        return PriceResponse(
            product=product,
            start_date=start_date,
            end_date=end_date,
            records=[],
            message="해당 기간의 가격 데이터가 존재하지 않습니다."
        )

    # '평균' (전국 평균) 데이터 추출 및 날짜별 매핑
    date_price_map: Dict[str, int] = {}
    
    for item in items:
        if not isinstance(item, dict):
            continue
        
        county = _extract_val(item.get("countyname")).strip()
        parsed_date = _parse_date(item.get("yyyy"), item.get("regday"))
        parsed_price = _parse_price(item.get("price"))

        if parsed_date and parsed_price is not None:
            if county == "평균":
                date_price_map[parsed_date] = parsed_price
            elif parsed_date not in date_price_map:
                date_price_map[parsed_date] = parsed_price

    records = [
        PriceRecord(date=dt, price=pr)
        for dt, pr in sorted(date_price_map.items(), key=lambda x: x[0])
    ]

    msg = "조회 성공" if records else "해당 기간의 가격 데이터가 존재하지 않습니다."
    return PriceResponse(
        product=product,
        start_date=start_date,
        end_date=end_date,
        records=records,
        message=msg
    )
