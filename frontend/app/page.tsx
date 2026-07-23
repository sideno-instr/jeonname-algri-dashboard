'use client';

import React, { useEffect, useState, useCallback } from 'react';
import ProductSelector from '@/components/ProductSelector';
import DateRangeForm from '@/components/DateRangeForm';
import SummaryCard from '@/components/SummaryCard';
import PriceChart from '@/components/PriceChart';
import RiskPanel from '@/components/RiskPanel';
import AIReportPanel from '@/components/AIReportPanel';

import { getProducts, getPriceData, getAnalysis, createAIReport } from '@/lib/api';
import {
  Product,
  PriceResponse,
  AnalysisResponse,
  AIReportResponse,
} from '@/types';

// 최근 30일 기본 날짜 구하기 (YYYY-MM-DD)
function getDefaultDates() {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - 30);

  const formatDate = (d: Date) => {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  return {
    startDate: formatDate(start),
    endDate: formatDate(end),
  };
}

export default function Home() {
  // 기본 30일 기간 생성
  const defaultDates = getDefaultDates();

  // 상태 정의
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProductKey, setSelectedProductKey] = useState<string>('');
  const [startDate, setStartDate] = useState<string>(defaultDates.startDate);
  const [endDate, setEndDate] = useState<string>(defaultDates.endDate);

  // 데이터 응답 상태
  const [priceData, setPriceData] = useState<PriceResponse | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
  const [aiReport, setAiReport] = useState<AIReportResponse | null>(null);

  // 로딩 상태
  const [isProductsLoading, setIsProductsLoading] = useState<boolean>(true);
  const [isDataLoading, setIsDataLoading] = useState<boolean>(false);
  const [isAiLoading, setIsAiLoading] = useState<boolean>(false);

  // 오류 상태 (Requirement 16: 백엔드 오류 vs LLM 오류 구분)
  const [backendError, setBackendError] = useState<string | null>(null);
  const [llmError, setLlmError] = useState<string | null>(null);

  // 1. 페이지 로딩 시 품목 목록만 조회 (Requirement 1 & 2)
  useEffect(() => {
    async function loadProducts() {
      setIsProductsLoading(true);
      setBackendError(null);
      try {
        const fetchedProducts = await getProducts();
        setProducts(fetchedProducts);

        // 첫 번째 품목을 기본 선택값으로 사용 (Requirement 2)
        if (fetchedProducts.length > 0) {
          setSelectedProductKey(fetchedProducts[0].key);
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : '품목 목록을 가져오는 데 실패했습니다.';
        setBackendError(`[백엔드 데이터 오류] ${msg}`);
      } finally {
        setIsProductsLoading(false);
      }
    }

    loadProducts();
  }, []);

  // 4. 사용자가 조회 버튼을 누르면 가격 데이터와 분석 데이터를 가져옴 (Requirement 4)
  const handleSearch = useCallback(async () => {
    if (!selectedProductKey) {
      setBackendError('[백엔드 데이터 오류] 품목을 선택해 주세요.');
      return;
    }

    setIsDataLoading(true);
    setBackendError(null);
    setLlmError(null);
    setAiReport(null); // 조회 변경 시 기존 AI 보고서 초기화

    try {
      // 가격 데이터 및 단순 가격 분석 / 수급 위험 병렬 요청
      const [fetchedPrice, fetchedAnalysis] = await Promise.all([
        getPriceData(selectedProductKey, startDate, endDate),
        getAnalysis(selectedProductKey, startDate, endDate),
      ]);

      setPriceData(fetchedPrice);
      setAnalysisData(fetchedAnalysis);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '가격 및 분석 데이터 조회 중 오류가 발생했습니다.';
      setBackendError(`[백엔드 데이터 오류] ${msg}`);
      setPriceData(null);
      setAnalysisData(null);
    } finally {
      setIsDataLoading(false);
    }
  }, [selectedProductKey, startDate, endDate]);

  // 11. 사용자가 'AI 분석 생성' 버튼을 눌렀을 때만 POST /api/ai-report 호출 (Requirement 11)
  const handleCreateAIReport = async () => {
    if (!selectedProductKey) return;

    setIsAiLoading(true);
    setLlmError(null);

    try {
      const report = await createAIReport(selectedProductKey, startDate, endDate);
      setAiReport(report);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'AI 분석 보고서 생성에 실패했습니다.';
      setLlmError(msg);
    } finally {
      setIsAiLoading(false);
    }
  };

  // 선택된 품목 객체
  const selectedProduct = products.find((p) => p.key === selectedProductKey);

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 font-sans antialiased selection:bg-emerald-500 selection:text-white">
      {/* 헤더 */}
      <header className="sticky top-0 z-20 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold text-lg shadow-xs">
              🌾
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                농산물 단일 가격 변동 및 수급 위험 분석
              </h1>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 hidden sm:block">
                전라남도 농산물 가격 시계열 데이터 및 AI 실습 대시보드
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 영역 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 overflow-x-hidden">
        {/* 상단 컨트롤 바 (품목 선택 & 날짜 지정 & 조회) */}
        <section className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 sm:p-5 shadow-xs">
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-end gap-3 w-full lg:w-auto">
              <ProductSelector
                products={products}
                selectedKey={selectedProductKey}
                onSelect={setSelectedProductKey}
                disabled={isProductsLoading || isDataLoading}
              />
              <DateRangeForm
                startDate={startDate}
                endDate={endDate}
                onStartDateChange={setStartDate}
                onEndDateChange={setEndDate}
                onSubmit={handleSearch}
                isLoading={isDataLoading}
                disabled={isProductsLoading || !selectedProductKey}
              />
            </div>
            {selectedProduct && (
              <div className="text-xs text-zinc-500 dark:text-zinc-400 self-start lg:self-end">
                선택된 품목: <span className="font-semibold text-emerald-600 dark:text-emerald-400">{selectedProduct.name}</span> ({selectedProduct.unit})
              </div>
            )}
          </div>
        </section>

        {/* 백엔드 데이터 오류 메시지 (Requirement 16) */}
        {backendError && (
          <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 rounded-xl text-rose-800 dark:text-rose-200 text-xs flex items-start gap-2">
            <svg className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1 font-medium">{backendError}</div>
          </div>
        )}

        {/* 대시보드 데이터 미조회 안내 */}
        {!priceData && !isDataLoading && !backendError && (
          <div className="p-12 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-900">
            <div className="w-12 h-12 rounded-full bg-emerald-50 dark:bg-emerald-950 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mx-auto mb-3">
              📊
            </div>
            <h3 className="text-sm font-bold text-zinc-800 dark:text-zinc-200">
              품목과 기간을 선택한 후 [조회] 버튼을 눌러주세요.
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 max-w-md mx-auto">
              초기 화면에서는 품목 목록만 로딩되며, 조회 시 해당 품목의 시계열 가격 데이터와 수급 위험 지수를 확인하실 수 있습니다.
            </p>
          </div>
        )}

        {/* 대시보드 결과 영역 */}
        {priceData && analysisData && (
          <div className="space-y-6">
            {/* 1. 요약 카드 (현재가, 평균가, 최고가, 최저가, 변동률) */}
            <section>
              <SummaryCard
                currentPrice={analysisData.current_price}
                averagePrice={analysisData.average_price}
                highestPrice={analysisData.highest_price}
                lowestPrice={analysisData.lowest_price}
                changeRate={analysisData.change_rate}
                unit={priceData.product?.unit || '원'}
              />
            </section>

            {/* 2. Recharts 가격 차트 & 수급 위험 패널 (2열 그리드) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-7">
                <PriceChart
                  records={priceData.records}
                  unit={priceData.product?.unit || '원'}
                />
              </div>
              <div className="lg:col-span-5">
                <RiskPanel analysis={analysisData} />
              </div>
            </div>

            {/* 3. AI 분석 패널 */}
            <section>
              <AIReportPanel
                report={aiReport}
                onRequestReport={handleCreateAIReport}
                isLoading={isAiLoading}
                llmError={llmError}
                hasPriceData={!!priceData && priceData.records.length > 0}
              />
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
