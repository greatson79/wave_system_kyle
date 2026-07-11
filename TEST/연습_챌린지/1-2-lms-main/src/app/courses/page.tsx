'use client';

import { useState } from 'react';
import { CourseFilter } from '@/features/courses/components/course-filter';
import { CourseList } from '@/features/courses/components/course-list';
import { useCourses } from '@/features/courses/hooks/useCourses';
import type { CourseListQuery } from '@/features/courses/lib/dto';

export default function CoursesPage() {
  const [filters, setFilters] = useState<CourseListQuery>({
    search: '',
    categoryId: undefined,
    difficultyId: undefined,
    sort: 'latest',
    limit: 20,
    offset: 0,
  });

  const { data, isLoading, isError, error, refetch } = useCourses(filters);

  const handleSearchChange = (value: string) => {
    setFilters((prev) => ({ ...prev, search: value, offset: 0 }));
  };

  const handleCategoryChange = (value: string) => {
    setFilters((prev) => ({
      ...prev,
      categoryId: value === 'all' ? undefined : value,
      offset: 0,
    }));
  };

  const handleDifficultyChange = (value: string) => {
    setFilters((prev) => ({
      ...prev,
      difficultyId: value === 'all' ? undefined : value,
      offset: 0,
    }));
  };

  const handleSortChange = (value: 'latest' | 'popular') => {
    setFilters((prev) => ({ ...prev, sort: value, offset: 0 }));
  };

  const handleReset = () => {
    setFilters({
      search: '',
      categoryId: undefined,
      difficultyId: undefined,
      sort: 'latest',
      limit: 20,
      offset: 0,
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">코스 카탈로그</h1>
        <p className="text-muted-foreground">
          다양한 코스를 탐색하고 수강신청하세요.
        </p>
      </div>

      <div className="mb-8">
        <CourseFilter
          search={filters.search || ''}
          categoryId={filters.categoryId || 'all'}
          difficultyId={filters.difficultyId || 'all'}
          sort={filters.sort}
          onSearchChange={handleSearchChange}
          onCategoryChange={handleCategoryChange}
          onDifficultyChange={handleDifficultyChange}
          onSortChange={handleSortChange}
          onReset={handleReset}
        />
      </div>

      <CourseList
        courses={data?.courses || []}
        isLoading={isLoading}
        isError={isError}
        error={error}
        onRetry={() => refetch()}
      />
    </div>
  );
}
