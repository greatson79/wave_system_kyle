'use client';

import { useCourseAssignments } from '../hooks/useCourseAssignments';
import { AssignmentCard } from './assignment-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

type AssignmentListProps = {
  courseId: string;
};

export const AssignmentList = ({ courseId }: AssignmentListProps) => {
  const { data, isLoading, error, refetch } = useCourseAssignments(courseId);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          <div className="flex flex-col gap-2">
            <p>{error.message}</p>
            <Button onClick={() => refetch()} variant="outline" size="sm">
              재시도
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (!data || data.assignments.length === 0) {
    return (
      <Alert>
        <AlertDescription>과제가 아직 없습니다.</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">{data.courseTitle} - 과제 목록</h2>
      <div className="grid gap-4">
        {data.assignments.map((assignment) => (
          <AssignmentCard
            key={assignment.id}
            assignment={assignment}
            courseId={courseId}
          />
        ))}
      </div>
    </div>
  );
};
