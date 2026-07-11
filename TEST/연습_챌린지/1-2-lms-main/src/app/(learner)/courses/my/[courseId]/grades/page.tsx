'use client';

import { use } from 'react';
import { GradesSummary } from '@/features/grades/components/grades-summary';
import { GradesTable } from '@/features/grades/components/grades-table';
import { useCourseGrades } from '@/features/grades/hooks/useCourseGrades';

interface GradesPageProps {
  params: Promise<{ courseId: string }>;
}

export default function GradesPage({ params }: GradesPageProps) {
  const { courseId } = use(params);
  const { data } = useCourseGrades(courseId);

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">성적</h1>
        {data && (
          <p className="text-muted-foreground">{data.courseTitle}</p>
        )}
      </div>

      {data && <GradesSummary summary={data.summary} />}
      <GradesTable courseId={courseId} />
    </div>
  );
}
