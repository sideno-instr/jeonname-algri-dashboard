'use client';

import React from 'react';
import { AIReportResponse } from '@/types';

interface AIReportPanelProps {
  report: AIReportResponse | null;
  onRequestReport: () => void;
  isLoading: boolean;
  llmError: string | null;
  hasPriceData: boolean;
}

export default function AIReportPanel({
  report,
  onRequestReport,
  isLoading,
  llmError,
  hasPriceData,
}: AIReportPanelProps) {
  return (
    <div className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5 shadow-xs space-y-4">
      {/* 헤더 및 생성 버튼 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-100 dark:border-zinc-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-purple-500"></span>
            <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
              AI 분석 보고서 (Gemini)
            </h3>
          </div>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
            LLM 기반 심층 수급 및 가격 해설 보고서 (생성 버튼을 누를 때만 동작합니다)
          </p>
        </div>

        <button
          type="button"
          onClick={onRequestReport}
          disabled={isLoading || !hasPriceData}
          className="h-10 px-4 py-2 bg-purple-600 hover:bg-purple-700 active:bg-purple-800 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>AI 분석 생성 중...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>AI 분석 생성</span>
            </>
          )}
        </button>
      </div>

      {/* Requirement 16: LLM 오류 구분 표시 */}
      {llmError && (
        <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 rounded-lg text-rose-800 dark:text-rose-200 text-xs space-y-1">
          <div className="flex items-center gap-1.5 font-bold text-rose-700 dark:text-rose-300">
            <svg className="w-4 h-4 text-rose-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>[AI 분석 LLM 오류]</span>
          </div>
          <p className="pl-5 text-rose-700 dark:text-rose-300">{llmError}</p>
        </div>
      )}

      {/* AI 보고서 결과 (Requirement 13 & 14: 5가지 구역 구분, raw JSON 방지) */}
      {!report && !isLoading && !llmError && (
        <div className="p-8 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg bg-zinc-50/50 dark:bg-zinc-800/30">
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            상단의 <strong className="text-purple-600 dark:text-purple-400 font-semibold">'AI 분석 생성'</strong> 버튼을 클릭하여 Gemini 분석 보고서를 생성할 수 있습니다.
          </p>
        </div>
      )}

      {report && (
        <div className="space-y-4 pt-1">
          {/* 1. summary */}
          <div className="p-4 rounded-lg bg-purple-50/70 dark:bg-purple-950/30 border border-purple-100 dark:border-purple-900/50">
            <h4 className="text-xs font-bold text-purple-900 dark:text-purple-200 uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <span>📌 전체 요약 (Summary)</span>
            </h4>
            <p className="text-xs leading-relaxed text-purple-950 dark:text-purple-100 font-medium">
              {report.summary}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* 2. price_change_interpretation */}
            <div className="p-3.5 rounded-lg bg-zinc-50 dark:bg-zinc-800/60 border border-zinc-100 dark:border-zinc-800">
              <h4 className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                📈 가격 변동 해설
              </h4>
              <p className="text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
                {report.price_change_interpretation}
              </p>
            </div>

            {/* 3. risk_interpretation */}
            <div className="p-3.5 rounded-lg bg-zinc-50 dark:bg-zinc-800/60 border border-zinc-100 dark:border-zinc-800">
              <h4 className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                ⚠️ 위험 지수 해설
              </h4>
              <p className="text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
                {report.risk_interpretation}
              </p>
            </div>
          </div>

          {/* 4. recommended_checks / recommended_action */}
          <div className="p-3.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40">
            <h4 className="text-xs font-semibold text-emerald-800 dark:text-emerald-300 mb-1">
              💡 권장 점검 사항 (Recommended Checks)
            </h4>
            <p className="text-xs leading-relaxed text-emerald-950 dark:text-emerald-200">
              {report.recommended_checks || report.recommended_action}
            </p>
          </div>

          {/* 5. limitations */}
          <div className="p-3.5 rounded-lg bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-100 dark:border-zinc-800">
            <h4 className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 mb-1">
              🔍 AI 분석 한계 (Limitations)
            </h4>
            <p className="text-xs leading-relaxed text-zinc-500 dark:text-zinc-400">
              {report.limitations}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
