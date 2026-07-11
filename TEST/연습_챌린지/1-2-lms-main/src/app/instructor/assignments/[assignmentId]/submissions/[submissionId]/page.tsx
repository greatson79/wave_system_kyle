'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useSubmissionDetail } from '@/features/assignments/hooks/useSubmissionDetail';
import { SubmissionDetail } from '@/features/assignments/components/submission-detail';
import { GradeForm } from '@/features/assignments/components/grade-form';
import { RequestResubmissionForm } from '@/features/assignments/components/request-resubmission-form';

interface PageProps {
  params: Promise<{
    assignmentId: string;
    submissionId: string;
  }>;
}

export default function SubmissionDetailPage({ params }: PageProps) {
  const router = useRouter();
  const { assignmentId, submissionId } = use(params);
  const { data: submission, isLoading, error } = useSubmissionDetail(submissionId);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error || !submission) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">제출물을 불러올 수 없습니다</h2>
          <p className="text-muted-foreground">{error?.message || '알 수 없는 오류가 발생했습니다.'}</p>
          <Button onClick={() => router.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            돌아가기
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-3xl font-bold">제출물 채점</h1>
      </div>

      <SubmissionDetail submission={submission} />

      <div className="grid gap-6 md:grid-cols-2">
        <GradeForm submission={submission} />
        <RequestResubmissionForm submission={submission} />
      </div>
    </div>
  );
}
