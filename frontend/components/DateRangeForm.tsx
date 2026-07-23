'use client';

import React from 'react';

interface DateRangeFormProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onSubmit: () => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export default function DateRangeForm({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onSubmit,
  isLoading = false,
  disabled = false,
}: DateRangeFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!disabled && !isLoading) {
      onSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-end gap-3 w-full sm:w-auto">
      <div className="flex flex-col gap-1.5 w-full sm:w-auto">
        <label htmlFor="start-date" className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">
          시작일
        </label>
        <input
          id="start-date"
          type="date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
          disabled={disabled || isLoading}
          className="h-10 px-3 py-2 text-sm bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 rounded-lg shadow-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-zinc-900 dark:text-zinc-100"
        />
      </div>

      <div className="flex flex-col gap-1.5 w-full sm:w-auto">
        <label htmlFor="end-date" className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">
          종료일
        </label>
        <input
          id="end-date"
          type="date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
          disabled={disabled || isLoading}
          className="h-10 px-3 py-2 text-sm bg-white dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 rounded-lg shadow-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-zinc-900 dark:text-zinc-100"
        />
      </div>

      <button
        type="submit"
        disabled={disabled || isLoading}
        className="h-10 px-5 py-2 w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-medium text-sm rounded-lg shadow-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>조회 중...</span>
          </>
        ) : (
          <span>조회</span>
        )}
      </button>
    </form>
  );
}
