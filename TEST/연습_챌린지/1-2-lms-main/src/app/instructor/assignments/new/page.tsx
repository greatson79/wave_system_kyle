'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useCreateAssignment } from '@/features/assignments/hooks/useCreateAssignment';
import { AssignmentForm } from '@/features/assignments/components/assignment-form';
import type { CreateAssignmentRequest } from '@/features/assignments/lib/dto';
import { useMyCourses } from '@/features/courses/hooks/useMyCourses';

export default function CreateAssignmentPage() {
  const router = useRouter();
  const createMutation = useCreateAssignment();
  const { data: myCoursesData, isLoading, error } = useMyCourses();

  const handleSubmit = (data: CreateAssignmentRequest) => {
    const dueDateISO = new Date(data.dueDate).toISOString();
    createMutation.mutate(
      { ...data, dueDate: dueDateISO },
      {
        onSuccess: (response) => {
          if (response.weightWarning) {
            alert(response.weightWarning);
          }
        },
        onError: (error) => {
          alert(error.message);
        },
      },
    );
  };

  // 로딩 상태 처리
  if (isLoading) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <Skeleton className="h-10 w-64 mb-4" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  // 에러 상태 처리
  if (error || !myCoursesData) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-destructive">
              코스 목록을 불러올 수 없습니다.
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // API 데이터를 AssignmentForm이 요구하는 형식으로 변환
  const courses = myCoursesData.courses.map((course) => ({
    id: course.id,
    title: course.title,
  }));

  return (
    <div className="container mx-auto py-8 max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">새 과제 만들기</CardTitle>
        </CardHeader>
        <CardContent>
          <AssignmentForm
            courses={courses}
            onSubmit={handleSubmit}
            isSubmitting={createMutation.isPending}
          />
        </CardContent>
      </Card>
    </div>
  );
}
