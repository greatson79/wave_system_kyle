'use client';

import { use } from 'react';
import { AssignmentDetail } from '@/features/assignments/components/assignment-detail';

type PageProps = {
  params: Promise<{ courseId: string; assignmentId: string }>;
};

export default function AssignmentDetailPage({ params }: PageProps) {
  const { assignmentId } = use(params);

  return (
    <div className="container mx-auto px-4 py-8">
      <AssignmentDetail assignmentId={assignmentId} />
    </div>
  );
}
