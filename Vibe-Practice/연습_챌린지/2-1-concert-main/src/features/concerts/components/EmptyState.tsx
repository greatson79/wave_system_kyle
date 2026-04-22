'use client';

import { CalendarX } from 'lucide-react';

export const EmptyState = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <CalendarX className="w-16 h-16 text-muted-foreground mb-4" />
      <h3 className="text-xl font-semibold mb-2">
        현재 예약 가능한 콘서트가 없습니다
      </h3>
      <p className="text-muted-foreground max-w-md">
        새로운 콘서트가 곧 등록될 예정입니다.
      </p>
    </div>
  );
};
