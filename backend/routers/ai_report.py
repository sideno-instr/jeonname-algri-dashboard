"""
AI 분석 보고서 라우터

POST /api/ai-report
  1. KAMIS 가격 데이터 조회
  2. analysis_service 로 수급 위험 추정 지수 계산
  3. analysis_chain 으로 LLM 한국어 보고서 생성
  4. AIReportResponse 반환

계산/분석 로직은 각 서비스·체인에만 존재합니다.
"""
from fastapi import APIRouter, HTTPException

from models.ai_report import AIReportRequest, AIReportResponse
from services import kamis_service, analysis_service
from chains import analysis_chain

router = APIRouter(prefix="/api", tags=["ai-report"])


@router.post(
    "/ai-report",
    response_model=AIReportResponse,
    summary="AI 한국어 분석 보고서 생성",
    description=(
        "KAMIS 가격 데이터 → 수급 위험 추정 지수 계산 → LLM 한국어 해설 생성 순으로 처리합니다. "
        "LLM 호출 비용이 발생하므로 프론트엔드 자동 호출 없이 사용자 요청 시에만 실행하세요."
    ),
)
async def create_ai_report(body: AIReportRequest) -> AIReportResponse:
    # ── 1. 품목 유효성 검증 ────────────────────────────────────────────────
    product = kamis_service.get_product_by_key(body.product_key)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"존재하지 않거나 지원하지 않는 품목 키입니다: {body.product_key}",
        )

    # ── 2. 날짜 유효성 검증 ────────────────────────────────────────────────
    if body.start_date > body.end_date:
        raise HTTPException(
            status_code=422,
            detail="조회 시작일(start_date)이 종료일(end_date)보다 늦을 수 없습니다.",
        )

    # ── 3. KAMIS 가격 데이터 조회 ──────────────────────────────────────────
    price_response = await kamis_service.fetch_period_prices(
        product, body.start_date, body.end_date
    )

    # ── 4. 수급 위험 추정 지수 계산 ────────────────────────────────────────
    analysis_result = analysis_service.compute_analysis(
        product_name=product.name,
        start_date=body.start_date,
        end_date=body.end_date,
        records=price_response.records,
        data_source=price_response.data_source,
    )

    # ── 5. LLM 한국어 보고서 생성 ──────────────────────────────────────────
    try:
        report = await analysis_chain.run_analysis_chain(analysis_result)
    except ValueError as exc:
        # API 키 미설정 등 설정 오류
        raise HTTPException(
            status_code=503,
            detail=f"AI 분석 서비스를 사용할 수 없습니다: {exc}",
        ) from exc
    except RuntimeError as exc:
        # LLM 호출 실패
        raise HTTPException(
            status_code=503,
            detail=f"AI 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. ({exc})",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"예상치 못한 오류가 발생했습니다: {exc}",
        ) from exc

    return report
