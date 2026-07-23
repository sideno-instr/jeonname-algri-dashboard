import {
  Product,
  PriceResponse,
  AnalysisResponse,
  AIReportResponse,
} from '@/types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * FastAPI 오류 응답을 처리하는 헬퍼 함수
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData && typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (errorData && typeof errorData.message === 'string') {
        errorMessage = errorData.message;
      }
    } catch {
      // JSON 파싱 실패 시 기본 HTTP status 메시지 사용
    }
    throw new Error(errorMessage);
  }
  return response.json() as Promise<T>;
}

/**
 * 지원되는 농산물 품목 목록 조회
 */
export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE_URL}/api/products`);
  return handleResponse<Product[]>(response);
}

/**
 * 지정된 품목과 기간에 대한 가격 시계열 데이터 조회
 */
export async function getPriceData(
  productKey: string,
  startDate: string,
  endDate: string
): Promise<PriceResponse> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });

  const response = await fetch(
    `${API_BASE_URL}/api/prices/${encodeURIComponent(productKey)}?${params.toString()}`
  );
  return handleResponse<PriceResponse>(response);
}

/**
 * 지정된 품목과 기간에 대한 단순 가격 분석 및 수급 위험 추정 지수 조회
 */
export async function getAnalysis(
  productKey: string,
  startDate: string,
  endDate: string
): Promise<AnalysisResponse> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });

  const response = await fetch(
    `${API_BASE_URL}/api/analysis/${encodeURIComponent(productKey)}?${params.toString()}`
  );
  return handleResponse<AnalysisResponse>(response);
}

/**
 * LLM(Gemini) 기반 한국어 AI 분석 보고서 생성 요청
 */
export async function createAIReport(
  productKey: string,
  startDate: string,
  endDate: string
): Promise<AIReportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/ai-report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      product_key: productKey,
      start_date: startDate,
      end_date: endDate,
    }),
  });
  return handleResponse<AIReportResponse>(response);
}
