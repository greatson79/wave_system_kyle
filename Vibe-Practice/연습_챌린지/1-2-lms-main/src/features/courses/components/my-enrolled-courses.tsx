'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { useMyEnrolledCourses } from '../hooks/useMyEnrolledCourses';
import { BookOpen, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

const LoadingState = () => (
  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
    {[1, 2, 3].map((i) => (
      <Card key={i}>
        <CardHeader>
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-1/2 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    ))}
  </div>
);

const EmptyState = () => (
  <div className="text-center py-12">
    <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
    <h3 className="text-xl font-semibold mb-2">수강 중인 코스가 없습니다</h3>
    <p className="text-muted-foreground mb-4">
      새로운 코스를 탐색하고 수강신청해보세요!
    </p>
    <Button asChild>
      <Link href="/courses">코스 둘러보기</Link>
    </Button>
  </div>
);

const ErrorState = ({ error, refetch }: { error: Error; refetch: () => void }) => (
  <div className="text-center py-12">
    <h3 className="text-xl font-semibold text-destructive mb-2">
      오류가 발생했습니다
    </h3>
    <p className="text-muted-foreground mb-4">{error.message}</p>
    <Button onClick={() => refetch()}>다시 시도</Button>
  </div>
);

export const MyEnrolledCourses = () => {
  const { data, isLoading, isError, error, refetch } = useMyEnrolledCourses();

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError) {
    return <ErrorState error={error as Error} refetch={refetch} />;
  }

  if (!data || data.courses.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {data.courses.map((course) => (
        <Card key={course.enrollmentId} className="flex flex-col">
          <CardHeader>
            <CardTitle className="line-clamp-2">{course.courseTitle}</CardTitle>
            <CardDescription>
              {course.categoryName} • {course.difficultyName}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 space-y-4">
            <p className="text-sm text-muted-foreground line-clamp-2">
              {course.courseDescription}
            </p>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">진행률</span>
                <span className="font-medium">{course.progress}%</span>
              </div>
              <Progress value={course.progress} />
              <p className="text-xs text-muted-foreground">
                {course.completedAssignments} / {course.totalAssignments} 과제 완료
              </p>
            </div>

            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>
                수강 시작: {format(new Date(course.enrolledAt), 'PPP', { locale: ko })}
              </span>
            </div>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button asChild className="flex-1">
              <Link href={`/courses/my/${course.courseId}`}>학습하기</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href={`/courses/my/${course.courseId}/grades`}>성적 보기</Link>
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};
