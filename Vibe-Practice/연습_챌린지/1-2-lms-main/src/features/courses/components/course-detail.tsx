'use client';

import { useCourseDetail } from '../hooks/useCourseDetail';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EnrollButton } from './enroll-button';
import { AlertCircle, Users, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { useRouter } from 'next/navigation';

type CourseDetailProps = {
  courseId: string;
};

export const CourseDetail = ({ courseId }: CourseDetailProps) => {
  const router = useRouter();
  const { data: course, isLoading, isError, error } = useCourseDetail(courseId);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[200px] w-full" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>
            {error?.message || '코스 정보를 불러오는 중 오류가 발생했습니다.'}
          </span>
          <Button
            onClick={() => router.push('/courses')}
            variant="outline"
            size="sm"
          >
            목록으로
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">코스를 찾을 수 없습니다.</p>
        <Button onClick={() => router.push('/courses')} variant="outline">
          목록으로
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <CardTitle className="text-3xl mb-4">{course.title}</CardTitle>
              <div className="flex flex-wrap gap-2 mb-4">
                <Badge variant="secondary">{course.category.name}</Badge>
                <Badge variant="outline">{course.difficulty.name}</Badge>
              </div>
              <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span>{course.enrollmentsCount}명 수강 중</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span>
                    {format(new Date(course.createdAt), 'PPP', { locale: ko })}
                  </span>
                </div>
              </div>
            </div>
            <EnrollButton courseId={courseId} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold mb-2">코스 소개</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {course.description}
              </p>
            </div>

            {course.curriculum && (
              <div>
                <h3 className="text-xl font-semibold mb-2">커리큘럼</h3>
                <p className="text-muted-foreground whitespace-pre-wrap">
                  {course.curriculum}
                </p>
              </div>
            )}

            <div>
              <h3 className="text-xl font-semibold mb-2">강사 정보</h3>
              <p className="text-muted-foreground">{course.instructor.name}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
