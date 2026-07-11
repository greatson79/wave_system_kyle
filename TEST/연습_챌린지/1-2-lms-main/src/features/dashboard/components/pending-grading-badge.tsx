'use client';

import { Badge } from '@/components/ui/badge';
import { CheckCircle2, AlertCircle } from 'lucide-react';

interface PendingGradingBadgeProps {
  count: number;
}

export function PendingGradingBadge({ count }: PendingGradingBadgeProps) {
  if (count === 0) {
    return (
      <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
        <CheckCircle2 className="h-5 w-5" />
        <span className="text-sm font-medium">
          모든 제출물이 채점 완료되었습니다
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
        채점 대기:
      </span>
      <Badge variant="destructive" className="text-sm font-semibold">
        {count}
      </Badge>
    </div>
  );
}
