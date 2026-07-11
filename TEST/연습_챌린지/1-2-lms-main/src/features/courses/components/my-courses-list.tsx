'use client';

import Link from 'next/link';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
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
import { useMyCourses } from '../hooks/useMyCourses';
import { CourseStatusBadge } from './course-status-badge';
import { CourseActions } from './course-actions';

export const MyCoursesList = () => {
  const { data, isLoading, error } = useMyCourses();

  if (isLoading) {
    return (
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
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-4">{error.message}</p>
        <Button onClick={() => window.location.reload()}>재시도</Button>
      </div>
    );
  }

  if (!data || data.courses.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">
          아직 개설한 코스가 없습니다.
        </p>
        <Button asChild>
          <Link href="/instructor/courses/new">코스 생성하기</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {data.courses.map((course) => (
        <Card key={course.id} className="flex flex-col">
          <CardHeader>
            <div className="flex items-start justify-between gap-2">
              <CardTitle className="line-clamp-1">{course.title}</CardTitle>
              <CourseStatusBadge status={course.status} />
            </div>
            <CardDescription>
              {course.category.name} • {course.difficulty.name} • 수강생{' '}
              {course.enrollmentsCount}명
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1">
            <p className="text-sm text-muted-foreground line-clamp-3">
              {course.description}
            </p>
            <p className="text-xs text-muted-foreground mt-4">
              생성일:{' '}
              {format(new Date(course.createdAt), 'PPP', { locale: ko })}
            </p>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button asChild variant="outline" className="flex-1">
              <Link href={`/instructor/courses/${course.id}/edit`}>편집</Link>
            </Button>
            <CourseActions courseId={course.id} status={course.status} />
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};
