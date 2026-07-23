'use client';

import React from 'react';

interface SummaryCardProps {
  currentPrice: number | null;
  averagePrice: number | null;
  highestPrice: number | null;
  lowestPrice: number | null;
  changeRate: number | null;
  unit?: string;
}

export default function SummaryCard({
  currentPrice,
  averagePrice,
  highestPrice,
  lowestPrice,
  changeRate,
  unit = '원',
}: SummaryCardProps) {
  const formatPrice = (val: number | null): string => {
    if (val === null || val === undefined) return '-';
    return `${Math.round(val).toLocaleString()} ${unit}`;
  };

  const getChangeRateBadge = (rate: number | null) => {
    if (rate === null || rate === undefined) return <span className="text-zinc-400 font-normal">-</span>;
    
    if (rate > 0) {
      return (
        <span className="inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          ▲ +{rate.toFixed(2)}%
        </span>
      );
    } else if (rate < 0) {
      return (
        <span className="inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
          ▼ {rate.toFixed(2)}%
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
          - 0.00%
        </span>
      );
    }
  };

  const cards = [
    {
      title: '현재가',
      value: formatPrice(currentPrice),
      extra: getChangeRateBadge(changeRate),
      subtext: '변동률',
    },
    {
      title: '평균가',
      value: formatPrice(averagePrice),
      subtext: '기간 내 평균 가격',
    },
    {
      title: '최고가',
      value: formatPrice(highestPrice),
      subtext: '기간 내 최고 가격',
    },
    {
      title: '최저가',
      value: formatPrice(lowestPrice),
      subtext: '기간 내 최저 가격',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 w-full">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="flex flex-col p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-xs transition-shadow hover:shadow-md"
        >
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
            {card.title}
          </span>
          <div className="mt-1 flex items-baseline justify-between gap-1 flex-wrap">
            <span className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
              {card.value}
            </span>
            {card.extra && <div>{card.extra}</div>}
          </div>
          <span className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
            {card.subtext}
          </span>
        </div>
      ))}
    </div>
  );
}
