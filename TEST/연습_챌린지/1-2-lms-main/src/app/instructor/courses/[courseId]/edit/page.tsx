'use client';

import { use } from 'react';
import { useInstructorCourseDetail } from '@/features/courses/hooks/useInstructorCourseDetail';
import { CourseForm } from '@/features/courses/components/course-form';
import { CourseActions } from '@/features/courses/components/course-actions';
import { CourseStatusBadge } from '@/features/courses/components/course-status-badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useActiveCategories } from '@/features/metadata/hooks/useActiveCategories';
import { useActiveDifficulties } from '@/features/metadata/hooks/useActiveDifficulties';

interface EditCoursePageProps {
  params: Promise<{ courseId: string }>;
}

export default function EditCoursePage({ params }: EditCoursePageProps) {
  const { courseId } = use(params);
  const { data: course, isLoading, error } = useInstructorCourseDetail(courseId);
  const { data: categoriesData, isLoading: isCategoriesLoading } = useActiveCategories();
  const { data: difficultiesData, isLoading: isDifficultiesLoading } = useActiveDifficulties();

  // 로딩 상태 처리
  if (isLoading || isCategoriesLoading || isDifficultiesLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <Skeleton className="h-10 w-64 mb-2" />
        <Skeleton className="h-4 w-96 mb-8" />
        <div className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </div>
    );
  }

  // 에러 상태 처리
  if (error || !course || !categoriesData || !difficultiesData) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <div className="text-center">
          <p className="text-destructive">
            {error?.message || '데이터를 불러올 수 없습니다.'}
          </p>
        </div>
      </div>
    );
  }

  // API 데이터를 CourseForm이 요구하는 형식으로 변환
  const categories = categoriesData.categories.map((cat) => ({
    id: cat.id,
    name: cat.name,
  }));

  const difficulties = difficultiesData.difficulties.map((diff) => ({
    id: diff.id,
    name: diff.name,
    level: diff.level,
  }));

  const defaultValues = {
    title: course.title,
    description: course.description,
    categoryId: course.category.id,
    difficultyId: course.difficulty.id,
    curriculum: course.curriculum || '',
  };

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          <h1 className="text-3xl font-bold">코스 편집</h1>
          <CourseStatusBadge status={course.status as 'draft' | 'published' | 'archived'} />
        </div>
        <p className="text-muted-foreground">
          코스 정보를 수정하거나 상태를 변경할 수 있습니다.
        </p>
      </div>

      <div className="mb-8">
        <CourseActions
          courseId={courseId}
          status={course.status as 'draft' | 'published' | 'archived'}
        />
      </div>

      <CourseForm
        mode="edit"
        courseId={courseId}
        defaultValues={defaultValues}
        categories={categories}
        difficulties={difficulties}
      />
    </div>
  );
}
