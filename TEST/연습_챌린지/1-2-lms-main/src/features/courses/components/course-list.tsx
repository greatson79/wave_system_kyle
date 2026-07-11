'use client';

import { CourseCard } from './course-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';
import type { CourseListResponse } from '../lib/dto';

type CourseListProps = {
  courses: CourseListResponse['courses'];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  onRetry?: () => void;
};

const CourseCardSkeleton = () => (
  <div className="space-y-3">
    <Skeleton className="h-[200px] w-full" />
  </div>
);

export const CourseList = ({
  courses,
  isLoading,
  isError,
  error,
  onRetry,
}: CourseListProps) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <CourseCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>{error?.message || '코스를 불러오는 중 오류가 발생했습니다.'}</span>
          {onRetry && (
            <Button onClick={onRetry} variant="outline" size="sm">
              재시도
            </Button>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">코스가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {courses.map((course) => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  );
};
