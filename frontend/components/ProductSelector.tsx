'use client';

import React from 'react';
import { Product } from '@/types';

interface ProductSelectorProps {
  products: Product[];
  selectedKey: string;
  onSelect: (key: string) => void;
  disabled?: boolean;
}

export default function ProductSelector({
  products,
  selectedKey,
  onSelect,
  disabled = false,
}: ProductSelectorProps) {
  return (
    <div className="flex flex-col gap-1.5 w-full sm:w-auto">
      <label htmlFor="product-select" className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">
        품목 선택
      </label>
      <select
        id="product-select"
        value={selectedKey}
        onChange={(e) => onSelect(e.target.value)}
        disabled={disabled || products.length === 0}
        className="h-10 px-3 py-2 text-sm bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 rounded-lg shadow-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-zinc-900 dark:text-zinc-100"
      >
        {products.length === 0 ? (
          <option value="">품목 불러오는 중...</option>
        ) : (
          products.map((product) => (
            <option key={product.key} value={product.key}>
              {product.name} ({product.unit})
            </option>
          ))
        )}
      </select>
    </div>
  );
}
