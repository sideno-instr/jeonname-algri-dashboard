'use client';

import React from 'react';
import { AnalysisResponse } from '@/types';

interface RiskPanelProps {
  analysis: AnalysisResponse | null;
}

export default function RiskPanel({ analysis }: RiskPanelProps) {
  if (!analysis) return null;

  const {
    risk_score,
    risk_level,
    data_quality,
    limitations,
    volatility,
    data_count,
  } = analysis;

  // 위험 등급 텍스트 및 색상 매핑 (Requirement 8)
  const getRiskBadge = (level: string | null) => {
    const levelUpper = (level || '').toUpperCase();
    if (levelUpper === 'STABLE' || levelUpper === '안정') {
      return {
        text: '안정 (STABLE)',
        colorClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800',
        scoreColor: 'text-emerald-600 dark:text-emerald-400',
      };
    }
    if (levelUpper === 'CAUTION' || levelUpper === '주의') {
      return {
        text: '주의 (CAUTION)',
        colorClass: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 dark:border-amber-800',
        scoreColor: 'text-amber-600 dark:text-amber-400',
      };
    }
    if (levelUpper === 'RISK' || levelUpper === '위험') {
      return {
        text: '위험 (RISK)',
        colorClass: 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-300 dark:border-rose-800',
        scoreColor: 'text-rose-600 dark:text-rose-400',
      };
    }
    return {
      text: level || '알 수 없음',
      colorClass: 'bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-300 border-zinc-300 dark:border-zinc-700',
      scoreColor: 'text-zinc-600 dark:text-zinc-400',
    };
  };

  const riskBadge = getRiskBadge(risk_level);

  // 데이터 품질 뱃지
  const getDataQualityBadge = (quality: string) => {
    const qUpper = quality.toUpperCase();
    if (qUpper === 'GOOD') {
      return <span className="px-2 py-0.5 text-xs font-medium rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-900">양호 (GOOD)</span>;
    }
    if (qUpper === 'LIMITED') {
      return <span className="px-2 py-0.5 text-xs font-medium rounded-md bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-900">제한적 (LIMITED)</span>;
    }
    return <span className="px-2 py-0.5 text-xs font-medium rounded-md bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950 dark:text-rose-300 dark:border-rose-900">부족 (INSUFFICIENT)</span>;
  };

  return (
    <div className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-5 shadow-xs space-y-4">
      {/* 헤더 및 타이틀 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3">
        <div>
          {/* 필수 문구 1 */}
          <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100">
            수급 위험 추정 지수
          </h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
            가격 변동성 및 일별 가격 트렌드 기반의 단순 위험 추정 지표
          </p>
        </div>
        <div>
          <span className={`inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full border ${riskBadge.colorClass}`}>
            {riskBadge.text}
          </span>
        </div>
      </div>

      {/* 주요 지표 뷰 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-800">
          <span className="text-xs text-zinc-500 dark:text-zinc-400">위험 추정 점수 (0~1)</span>
          <div className={`text-xl font-bold mt-1 ${riskBadge.scoreColor}`}>
            {risk_score !== null ? risk_score.toFixed(4) : '-'}
          </div>
        </div>
        <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-800">
          <span className="text-xs text-zinc-500 dark:text-zinc-400">가격 변동성 (표준편차)</span>
          <div className="text-xl font-bold mt-1 text-zinc-900 dark:text-zinc-100">
            {volatility !== null ? volatility.toFixed(4) : '-'}
          </div>
        </div>
        <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-800">
          <span className="text-xs text-zinc-500 dark:text-zinc-400">데이터 품질 / 건수</span>
          <div className="flex items-center gap-2 mt-1">
            {getDataQualityBadge(data_quality)}
            <span className="text-xs text-zinc-500">({data_count}건)</span>
          </div>
        </div>
      </div>

      {/* 경고 및 면책 문구 (Requirement 필수 문구 2 & 3) */}
      <div className="p-3.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200/80 dark:border-amber-900/50 rounded-lg text-xs text-amber-900 dark:text-amber-200 space-y-1">
        <div className="flex items-center gap-1.5 font-semibold">
          <svg className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {/* 필수 문구 2 */}
          <span>가격 데이터만 활용한 교육용 추정 결과입니다.</span>
        </div>
        {/* 필수 문구 3 */}
        <p className="pl-5 text-amber-800 dark:text-amber-300">
          실제 공급량, 재고, 생산량, 기상 자료는 반영되지 않았습니다.
        </p>
      </div>

      {/* Requirement 9: 데이터 품질 및 limitations 화면에 표시 */}
      {limitations && limitations.length > 0 && (
        <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800">
          <span className="text-xs font-semibold text-zinc-600 dark:text-zinc-400 block mb-1">
            분석 한계 및 유의사항 (Limitations)
          </span>
          <ul className="list-disc list-inside text-xs text-zinc-500 dark:text-zinc-400 space-y-1">
            {limitations.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
