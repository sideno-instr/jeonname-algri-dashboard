/**
 * FastAPI 백엔드 응답 모델에 일치하는 TypeScript 타입 정의
 */

export interface Product {
  key: string;
  name: string;
  unit: string;
  item_category_code: string;
  item_code: string;
  kind_code: string;
  product_cls_code: string;
  product_rank_code: string;
}

export interface PriceRecord {
  date: string;
  price: number;
}

export interface PriceResponse {
  product: Product;
  start_date: string;
  end_date: string;
  records: PriceRecord[];
  data_source: string;
  message: string;
}

export type RiskLevel = 'STABLE' | 'CAUTION' | 'RISK';
export type DataQuality = 'GOOD' | 'LIMITED' | 'INSUFFICIENT';

export interface AnalysisResponse {
  product: string;
  start_date: string;
  end_date: string;
  current_price: number | null;
  average_price: number | null;
  highest_price: number | null;
  lowest_price: number | null;
  change_rate: number | null;
  volatility: number | null;
  risk_score: number | null;
  risk_level: RiskLevel | string | null;
  data_count: number;
  data_quality: DataQuality | string;
  limitations: string[];
  data_source: string;
}

export interface AIReportResponse {
  summary: string;
  price_change_interpretation: string;
  risk_interpretation: string;
  recommended_action: string;
  recommended_checks?: string;
  limitations: string;
}
