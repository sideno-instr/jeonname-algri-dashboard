"""
analysis_chain 단위 테스트

테스트 구조:
  - MOCK 테스트 : LLM 을 실제로 호출하지 않고 체인 로직을 검증
  - LIVE 테스트 : 환경변수 GOOGLE_API_KEY 가 설정된 경우에만 실행
                  (pytest -m live 로 별도 실행)

실행 방법:
  # Mock 테스트만 (LLM 호출 없음)
  python tests/test_analysis_chain.py

  # pytest Mock 테스트만
  pytest tests/test_analysis_chain.py -v -m "not live"

  # pytest LLM 실제 호출 포함 (API 키 필요)
  pytest tests/test_analysis_chain.py -v -m live
"""
import asyncio
import json
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.price import PriceRecord
from models.analysis import AnalysisResponse
from models.ai_report import AIReportResponse
from services.analysis_service import compute_analysis
from chains.analysis_chain import _build_context, _parse_llm_output, run_analysis_chain

# ---------------------------------------------------------------------------
# 픽스처 헬퍼
# ---------------------------------------------------------------------------

def _make_analysis(prices: list[float], start="2024-01-01", end="2024-01-10") -> AnalysisResponse:
    from datetime import date, timedelta
    base = date.fromisoformat(start)
    records = [
        PriceRecord(date=(base + timedelta(days=i)).isoformat(), price=int(p))
        for i, p in enumerate(prices)
    ]
    return compute_analysis("배추", start, end, records)


def _fake_llm_json(**overrides) -> str:
    """테스트용 LLM 응답 JSON 문자열 생성."""
    base = {
        "summary": "테스트 요약입니다.",
        "price_change_interpretation": "가격 변동 해설.",
        "risk_interpretation": "위험 지수 해설.",
        "recommended_action": "참고 행동 제안.",
        "limitations": "분석 한계 안내.",
    }
    base.update(overrides)
    return json.dumps(base, ensure_ascii=False)


# ---------------------------------------------------------------------------
# TEST 1: _build_context — 계산 완료 케이스
# ---------------------------------------------------------------------------

def test_build_context_full():
    print("\n[TEST 1] _build_context: 계산 완료 케이스")
    analysis = _make_analysis([1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800])
    ctx = _build_context(analysis)

    # 내부 필드명(snake_case)이 노출되지 않아야 함
    assert "change_rate" not in ctx.lower(), "내부 필드명 change_rate가 프롬프트에 노출되면 안 됩니다"
    assert "risk_score" not in ctx.lower(), "내부 필드명 risk_score가 프롬프트에 노출되면 안 됩니다"

    # 통계 요약값은 포함되어야 함
    assert "배추" in ctx
    assert "위험" in ctx
    assert "평균" in ctx
    assert "최고" in ctx or "최저" in ctx

    # 원본 레코드 목록(10개 날짜+가격 시계열)이 통째로 포함되지 않는지 확인
    # → 컨텍스트는 집계된 통계만 포함하므로 개별 레코드 수(10)보다 줄 수가 훨씬 적음
    lines = ctx.strip().split("\n")
    assert len(lines) < 30, f"컨텍스트 줄 수가 너무 많습니다({len(lines)}줄). 원본 레코드가 포함된 것 같습니다."

    print(f"  컨텍스트 미리보기:\n{ctx[:300]}...")
    print("  PASS")


# ---------------------------------------------------------------------------
# TEST 2: _build_context — 데이터 부족 케이스
# ---------------------------------------------------------------------------

def test_build_context_insufficient():
    print("\n[TEST 2] _build_context: 데이터 부족 케이스")
    analysis = _make_analysis([1000])  # 1개만
    ctx = _build_context(analysis)
    assert "계산 불가" in ctx
    assert "데이터 부족" in ctx
    print(f"  {ctx}")
    print("  PASS")


# ---------------------------------------------------------------------------
# TEST 3: _parse_llm_output — 정상 JSON 파싱
# ---------------------------------------------------------------------------

def test_parse_llm_output_normal():
    print("\n[TEST 3] _parse_llm_output: 정상 JSON")
    raw = _fake_llm_json()
    result = _parse_llm_output(raw)
    assert isinstance(result, AIReportResponse)
    assert result.summary == "테스트 요약입니다."
    assert result.recommended_action == "참고 행동 제안."
    print("  PASS")


# ---------------------------------------------------------------------------
# TEST 4: _parse_llm_output — 마크다운 코드블록 처리
# ---------------------------------------------------------------------------

def test_parse_llm_output_markdown_block():
    print("\n[TEST 4] _parse_llm_output: 마크다운 코드블록 감싸인 경우")
    raw = f"```json\n{_fake_llm_json()}\n```"
    result = _parse_llm_output(raw)
    assert result.summary == "테스트 요약입니다."
    print("  PASS")


# ---------------------------------------------------------------------------
# TEST 5: _parse_llm_output — 필수 필드 누락 시 기본값 대체
# ---------------------------------------------------------------------------

def test_parse_llm_output_missing_field():
    print("\n[TEST 5] _parse_llm_output: 필드 누락 시 기본값 삽입")
    incomplete = json.dumps({
        "summary": "요약만 있음",
        # 나머지 필드 누락
    }, ensure_ascii=False)
    result = _parse_llm_output(incomplete)
    assert result.summary == "요약만 있음"
    assert "(LLM 응답에 해당 항목이 포함되지 않았습니다.)" in result.price_change_interpretation
    print("  PASS")


# ---------------------------------------------------------------------------
# TEST 6: run_analysis_chain — LLM Mock 테스트 (실제 호출 없음)
# ---------------------------------------------------------------------------

def test_run_analysis_chain_mock():
    print("\n[TEST 6] run_analysis_chain: LLM Mock 테스트")
    analysis = _make_analysis([1000, 1100, 1300, 1500, 1800])

    fake_response = MagicMock()
    fake_response.content = _fake_llm_json(summary="Mock 요약입니다.")

    with patch("chains.analysis_chain.ChatGoogleGenerativeAI") as MockLLM:
        instance = MockLLM.return_value
        instance.ainvoke = AsyncMock(return_value=fake_response)

        # GOOGLE_API_KEY 패치
        with patch("chains.analysis_chain.settings") as mock_settings:
            mock_settings.GOOGLE_API_KEY = "fake-key"
            mock_settings.LLM_MODEL = "gemini-test"

            result = asyncio.run(run_analysis_chain(analysis))

    assert isinstance(result, AIReportResponse)
    assert result.summary == "Mock 요약입니다."
    print(f"  summary: {result.summary}")
    print("  PASS")


# ---------------------------------------------------------------------------
# TEST 7: run_analysis_chain — API 키 미설정 시 ValueError
# ---------------------------------------------------------------------------

def test_run_analysis_chain_no_api_key():
    print("\n[TEST 7] run_analysis_chain: API 키 미설정 → ValueError")
    analysis = _make_analysis([1000, 1100])

    with patch("chains.analysis_chain.settings") as mock_settings:
        mock_settings.GOOGLE_API_KEY = ""
        mock_settings.LLM_MODEL = "gemini-test"

        try:
            asyncio.run(run_analysis_chain(analysis))
            assert False, "ValueError가 발생해야 합니다"
        except ValueError as e:
            assert "GOOGLE_API_KEY" in str(e)
            print(f"  예외 메시지: {e}")
    print("  PASS")


# ---------------------------------------------------------------------------
# TEST 8: (LIVE) 실제 LLM 호출 — GOOGLE_API_KEY 환경변수 필요
# ---------------------------------------------------------------------------

def test_run_analysis_chain_live():
    """실제 LLM 호출 테스트. pytest -m live 로만 실행."""
    import os
    api_key = os.environ.get("GOOGLE_API_KEY") or ""
    if not api_key:
        print("\n[TEST 8] LIVE: GOOGLE_API_KEY 미설정, 건너뜁니다.")
        return

    print("\n[TEST 8] LIVE: 실제 LLM 호출")
    analysis = _make_analysis(
        [1000, 1050, 1100, 1200, 1150, 1300, 1250, 1400, 1380, 1500],
        start="2024-01-01", end="2024-01-10"
    )
    result = asyncio.run(run_analysis_chain(analysis))
    assert isinstance(result, AIReportResponse)
    assert len(result.summary) > 10
    print(f"  summary: {result.summary}")
    print(f"  risk_interpretation: {result.risk_interpretation}")
    print("  PASS (LIVE)")


# ---------------------------------------------------------------------------
# 직접 실행
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_build_context_full,
        test_build_context_insufficient,
        test_parse_llm_output_normal,
        test_parse_llm_output_markdown_block,
        test_parse_llm_output_missing_field,
        test_run_analysis_chain_mock,
        test_run_analysis_chain_no_api_key,
        test_run_analysis_chain_live,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*50}")
    print(f"결과: {passed} passed / {failed} failed")
    if failed:
        sys.exit(1)
