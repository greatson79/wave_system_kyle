'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, Users, Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import type { MyCourseItem } from '../lib/dto';

interface MyCoursesCardProps {
  courses: MyCourseItem[];
}

const statusConfig = {
  draft: { label: '초안', variant: 'secondary' as const, color: 'text-gray-600' },
  published: { label: '공개', variant: 'default' as const, color: 'text-green-600' },
  archived: { label: '보관', variant: 'outline' as const, color: 'text-orange-600' },
};

export function MyCoursesCard({ courses }: MyCoursesCardProps) {
  const router = useRouter();

  if (courses.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            내 코스
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <BookOpen className="h-12 w-12 text-gray-300 dark:text-gray-600 mb-4" />
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              아직 개설한 코스가 없습니다
            </p>
            <Button
              onClick={() => router.push('/instructor/courses/new')}
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              코스 생성하기
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            내 코스
          </CardTitle>
          <Button
            onClick={() => router.push('/instructor/courses/new')}
            size="sm"
            variant="outline"
          >
            <Plus className="h-4 w-4 mr-2" />
            새 코스
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {courses.map((course) => {
            const config = statusConfig[course.status];
            return (
              <div
                key={course.courseId}
                className="flex items-start justify-between p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                onClick={() => router.push(`/instructor/courses/${course.courseId}/edit`)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-sm">{course.courseTitle}</h3>
                    <Badge variant={config.variant}>{config.label}</Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      수강생 {course.enrollmentsCount}명
                    </span>
                    <span>
                      생성일: {format(new Date(course.createdAt), 'yyyy.MM.dd', { locale: ko })}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
