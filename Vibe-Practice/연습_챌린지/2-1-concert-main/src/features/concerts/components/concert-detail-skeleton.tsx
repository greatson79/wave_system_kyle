'use client';

import { Skeleton } from '@/components/ui/skeleton';

export const ConcertDetailSkeleton = () => {
  return (
    <div data-testid="concert-detail-skeleton" className="container mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10" />
        <Skeleton className="h-8 w-32" />
      </div>

      <Skeleton className="w-full aspect-video rounded-lg" />

      <div className="space-y-4">
        <Skeleton className="h-10 w-3/4" />
        <div className="space-y-2">
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-5 w-1/2" />
        </div>
      </div>

      <div className="space-y-2">
        <Skeleton className="h-6 w-24" />
        <Skeleton className="h-20 w-full" />
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-16" />
        </div>
        <Skeleton className="h-5 w-1/3" />
      </div>

      <Skeleton className="h-12 w-full" />
    </div>
  );
};
