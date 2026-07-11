'use client';

import { MyEnrolledCourses } from '@/features/courses/components/my-enrolled-courses';

export default function MyCoursesPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">내 코스</h1>
        <p className="text-muted-foreground">
          수강 중인 코스와 학습 진행 상황을 확인하세요.
        </p>
      </div>

      <MyEnrolledCourses />
    </div>
  );
}
