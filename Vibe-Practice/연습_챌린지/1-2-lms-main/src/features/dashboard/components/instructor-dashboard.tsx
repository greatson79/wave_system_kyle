'use client';

import { useInstructorDashboard } from '../hooks/useInstructorDashboard';
import { MyCoursesCard } from './my-courses-card';
import { PendingGradingBadge } from './pending-grading-badge';
import { RecentSubmissionsCard } from './recent-submissions-card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle } from 'lucide-react';

export function InstructorDashboard() {
  const { data, isLoading, isError, error, refetch } = useInstructorDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>
            {error instanceof Error
              ? error.message
              : '대시보드 정보를 불러오지 못했습니다.'}
          </span>
          <Button
            onClick={() => refetch()}
            size="sm"
            variant="outline"
            className="ml-4"
          >
            재시도
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <PendingGradingBadge count={data.pendingGradingCount} />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <MyCoursesCard courses={data.courses} />
        <RecentSubmissionsCard submissions={data.recentSubmissions} />
      </div>
    </div>
  );
}
