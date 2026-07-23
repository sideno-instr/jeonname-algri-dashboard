'use client';

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { PriceRecord } from '@/types';

interface PriceChartProps {
  records: PriceRecord[];
  unit?: string;
}

export default function PriceChart({ records, unit = '원' }: PriceChartProps) {
  // 15. 데이터가 없으면 빈 차트를 그리지 말고 안내 문구를 표시한다.
  if (!records || records.length === 0) {
    return (
      <div className="w-full h-72 flex flex-col items-center justify-center p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl text-center">
        <svg
          className="w-12 h-12 text-zinc-300 dark:text-zinc-600 mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <p className="text-base font-semibold text-zinc-700 dark:text-zinc-300">
          해당 기간의 가격 데이터가 없습니다.
        </p>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
          다른 기간을 지정하여 조회를 진행해 주시기 바랍니다.
        </p>
      </div>
    );
  }

  // Y축 최소값, 최대값 약간의 여백 계산
  const prices = records.map((r) => r.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const yDomain = [
    Math.floor(minPrice * 0.95),
    Math.ceil(maxPrice * 1.05),
  ];

  return (
    <div className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 sm:p-6 shadow-xs">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
          일별 가격 추이
        </h3>
        <span className="text-xs text-zinc-500 dark:text-zinc-400">
          단위: {unit}
        </span>
      </div>
      <div className="w-full h-72 sm:h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={records} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" className="dark:opacity-20" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              domain={yDomain}
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${value.toLocaleString()}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                borderColor: '#e5e7eb',
                borderRadius: '0.5rem',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                fontSize: '0.875rem',
              }}
              formatter={(value) => {
                if (value === undefined || value === null) return ['-', '가격'];
                const num = typeof value === 'number' ? value : Number(value);
                return [`${isNaN(num) ? value : num.toLocaleString()} ${unit}`, '가격'];
              }}
              labelFormatter={(label) => `날짜: ${label}`}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#059669"
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#059669', strokeWidth: 0 }}
              activeDot={{ r: 6, fill: '#047857' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
