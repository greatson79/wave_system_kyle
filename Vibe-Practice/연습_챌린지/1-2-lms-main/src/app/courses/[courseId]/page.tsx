'use client';

import { CourseDetail } from '@/features/courses/components/course-detail';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { use } from 'react';

type CourseDetailPageProps = {
  params: Promise<{ courseId: string }>;
};

export default function CourseDetailPage({ params }: CourseDetailPageProps) {
  const router = useRouter();
  const resolvedParams = use(params);

  return (
    <div className="container mx-auto px-4 py-8">
      <Button
        onClick={() => router.push('/courses')}
        variant="ghost"
        className="mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        목록으로
      </Button>

      <CourseDetail courseId={resolvedParams.courseId} />
    </div>
  );
}
