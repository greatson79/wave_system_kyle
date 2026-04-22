'use client';

import { use } from 'react';
import { AssignmentList } from '@/features/assignments/components/assignment-list';

type PageProps = {
  params: Promise<{ courseId: string }>;
};

export default function MyCoursePage({ params }: PageProps) {
  const { courseId } = use(params);

  return (
    <div className="container mx-auto px-4 py-8">
      <AssignmentList courseId={courseId} />
    </div>
  );
}
