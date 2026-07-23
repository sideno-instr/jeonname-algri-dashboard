"""
LangChain 기반 한국어 분석 보고서 생성 체인

처리 흐름:
  1. AnalysisResponse → 프롬프트용 요약 컨텍스트 생성 (숫자 지표만 포함, 원본 데이터 제외)
  2. ChatGoogleGenerativeAI 로 한국어 해설 생성
  3. JSON 파싱 → AIReportResponse 반환

설계 원칙:
  - LLM 객체는 실제 호출 시점에 생성 (API 키 없이도 앱 기동 가능)
  - 원본 레코드(전체 가격 시계열)는 프롬프트에 포함하지 않음
  - 제공되지 않은 원인(날씨, 재고 등)을 단정하지 않는 프롬프트 규칙 명시
"""
import json
import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings
from models.analysis import AnalysisResponse
from models.ai_report import AIReportResponse


# ---------------------------------------------------------------------------
# 시스템 프롬프트 (프롬프트 규칙 전체 포함)
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """당신은 농산물 가격 데이터를 분석하여 농가와 유통 담당자에게 쉬운 한국어로 설명하는 분석 도우미입니다.

[엄수해야 할 규칙]
1. 입력으로 제공된 가격 지표와 계산값만 근거로 사용하십시오.
2. 날씨, 생산량, 재고, 수입량, 정책, 질병 등 제공되지 않은 원인을 사실처럼 단정하지 마십시오.
3. 원인을 확인할 수 없으면 '추가 데이터가 필요합니다'라고 작성하십시오.
4. 가격 상승과 하락 모두 위험 가능성으로 설명할 수 있으나 과장하지 마십시오.
5. 투자, 정책, 금융 자문처럼 확정적으로 표현하지 마십시오.
6. 데이터가 부족하면 분석 한계를 먼저 설명하십시오.
7. 수급 위험 추정 지수는 가격 기반 교육용 지표임을 명시하십시오.
8. 응답은 짧고 명확하게 작성하십시오.

[출력 형식]
반드시 아래 JSON 형식으로만 응답하십시오. 마크다운 코드 블록 없이 순수 JSON만 출력하십시오.

{
  "summary": "전체 요약 (2~3문장)",
  "price_change_interpretation": "기간 가격 변동 해설",
  "risk_interpretation": "수급 위험 추정 지수 해설",
  "recommended_action": "농가·유통 담당자를 위한 참고 행동 제안 (확정적 자문 아님)",
  "limitations": "분석 한계 및 유의사항"
}"""


# ---------------------------------------------------------------------------
# 내부 헬퍼
# ---------------------------------------------------------------------------

def _build_context(analysis: AnalysisResponse) -> str:
    """
    AnalysisResponse → 프롬프트 컨텍스트 문자열 변환.
    원본 레코드(전체 시계열)는 포함하지 않고 요약 지표만 전달합니다.
    """
    lines = [
        f"품목: {analysis.product}",
        f"분석 기간: {analysis.start_date} ~ {analysis.end_date}",
        f"유효 데이터 수: {analysis.data_count}개",
        f"데이터 품질: {analysis.data_quality}",
    ]

    if analysis.current_price is not None:
        lines.append(f"최근 가격: {analysis.current_price:,}원")
    if analysis.average_price is not None:
        lines.append(f"평균 가격: {analysis.average_price:,.1f}원")
    if analysis.highest_price is not None:
        lines.append(f"최고 가격: {analysis.highest_price:,}원")
    if analysis.lowest_price is not None:
        lines.append(f"최저 가격: {analysis.lowest_price:,}원")

    if analysis.change_rate is not None:
        direction = "상승" if analysis.change_rate > 0 else ("하락" if analysis.change_rate < 0 else "유지")
        lines.append(f"기간 변동률: {analysis.change_rate:+.2f}% ({direction})")
    else:
        lines.append("기간 변동률: 계산 불가 (데이터 부족)")

    if analysis.volatility is not None:
        lines.append(f"일별 가격 변동성(표준편차): {analysis.volatility:.4f}")
    else:
        lines.append("일별 가격 변동성: 계산 불가 (데이터 부족)")

    if analysis.risk_score is not None:
        lines.append(f"수급 위험 추정 지수: {analysis.risk_score:.4f} (0=안정, 1=고위험)")
        lines.append(f"위험 등급: {analysis.risk_level}")
    else:
        lines.append("수급 위험 추정 지수: 계산 불가 (데이터 부족)")

    lines.append(f"데이터 출처: {analysis.data_source}")
    lines.append("\n[유의사항]")
    for lim in analysis.limitations:
        lines.append(f"- {lim}")

    return "\n".join(lines)


def _extract_text_from_content(content) -> str:
    """
    LangChain AIMessage.content 를 항상 순수 문자열로 정규화합니다.

    langchain-google-genai 최신 버전은 content 를 다음 두 형식 중 하나로 반환합니다.
      - str  : "{ \"summary\": ... }"
      - list : [{"type": "text", "text": "{ ... }"}, ...]
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                # {"type": "text", "text": "..."} 형식
                parts.append(str(block.get("text", "")))
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(content)


def _parse_llm_output(raw) -> AIReportResponse:
    """LLM 응답(str 또는 list)에서 JSON을 추출하여 AIReportResponse로 파싱합니다."""
    # content 형식 정규화 (str / list 모두 처리)
    raw_str = _extract_text_from_content(raw)

    # 코드 블록 제거 (LLM이 규칙을 어기고 마크다운을 추가한 경우 대비)
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw_str).strip()

    # JSON 객체 구간만 추출
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"LLM 응답에서 JSON을 찾을 수 없습니다. 원본: {raw_str[:300]}")

    data = json.loads(match.group())

    # 필수 필드 존재 여부 확인 후 기본값으로 대체
    required_fields = [
        "summary",
        "price_change_interpretation",
        "risk_interpretation",
        "recommended_action",
        "limitations",
    ]
    for field in required_fields:
        if field not in data:
            data[field] = "(LLM 응답에 해당 항목이 포함되지 않았습니다.)"

    return AIReportResponse(**data)


# ---------------------------------------------------------------------------
# 공개 체인 함수
# ---------------------------------------------------------------------------

async def run_analysis_chain(analysis: AnalysisResponse) -> AIReportResponse:
    """
    계산된 분석 결과(AnalysisResponse)를 받아 LLM 한국어 보고서를 생성합니다.

    Parameters
    ----------
    analysis : AnalysisResponse
        analysis_service.compute_analysis() 의 반환값

    Returns
    -------
    AIReportResponse

    Raises
    ------
    ValueError  : API 키 미설정
    RuntimeError: LLM 호출 실패
    """
    if not settings.GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY가 설정되지 않았습니다. backend/.env 파일을 확인해주세요."
        )

    # LLM 객체는 실제 호출 시점에 생성
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,      # 일관된 분석 결과를 위해 낮은 temperature
        max_output_tokens=1024,
    )

    context = _build_context(analysis)
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"아래 분석 지표를 바탕으로 한국어 분석 보고서를 작성해주세요.\n\n{context}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        # response.content 는 str 또는 list 로 올 수 있음 → _parse_llm_output 에서 정규화
        raw_content = response.content
    except Exception as exc:
        raise RuntimeError(f"LLM 호출 중 오류가 발생했습니다: {exc}") from exc

    return _parse_llm_output(raw_content)
