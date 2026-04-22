'use client';

import { CourseForm } from '@/features/courses/components/course-form';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent } from '@/components/ui/card';
import { useActiveCategories } from '@/features/metadata/hooks/useActiveCategories';
import { useActiveDifficulties } from '@/features/metadata/hooks/useActiveDifficulties';

export default function CreateCoursePage() {
  const { data: categoriesData, isLoading: isCategoriesLoading } = useActiveCategories();
  const { data: difficultiesData, isLoading: isDifficultiesLoading } = useActiveDifficulties();

  // 로딩 상태 처리
  if (isCategoriesLoading || isDifficultiesLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <Skeleton className="h-10 w-64 mb-4" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  // 에러 상태 처리
  if (!categoriesData || !difficultiesData) {
    return (
      <div className="container mx-auto max-w-2xl py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-destructive">
              메타데이터를 불러올 수 없습니다.
            </div>
          </CardContent>
        </Card>
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

  return (
    <div className="container mx-auto max-w-2xl py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">코스 생성</h1>
        <p className="text-muted-foreground mt-2">
          새로운 코스를 생성합니다. 생성 후 과제를 추가할 수 있습니다.
        </p>
      </div>
      <CourseForm
        mode="create"
        categories={categories}
        difficulties={difficulties}
      />
    </div>
  );
}
