'use client';

import { useRouter } from 'next/navigation';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

interface SubmissionSuccessMessageProps {
  isLate: boolean;
  submittedAt: string;
  courseId: string;
  assignmentId: string;
  isResubmit?: boolean;
}

export const SubmissionSuccessMessage = ({
  isLate,
  submittedAt,
  courseId,
  assignmentId,
  isResubmit = false,
}: SubmissionSuccessMessageProps) => {
  const router = useRouter();

  const formattedDate = format(new Date(submittedAt), 'yyyy년 MM월 dd일 HH:mm', {
    locale: ko,
  });

  return (
    <div className="space-y-4">
      <Alert variant={isLate ? 'destructive' : 'default'}>
        {isLate ? (
          <AlertTriangle className="h-4 w-4" />
        ) : (
          <CheckCircle2 className="h-4 w-4" />
        )}
        <AlertTitle>
          {isResubmit
            ? '과제가 재제출되었습니다'
            : isLate
              ? '과제가 지각 제출되었습니다'
              : '과제가 제출되었습니다'}
        </AlertTitle>
        <AlertDescription>
          제출 일시: {formattedDate}
          {isLate && <div className="mt-2">마감일 이후 제출로 감점이 있을 수 있습니다.</div>}
        </AlertDescription>
      </Alert>

      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={() => router.push(`/courses/my/${courseId}`)}
        >
          과제 목록으로
        </Button>
        <Button
          onClick={() =>
            router.push(`/courses/my/${courseId}/assignments/${assignmentId}`)
          }
        >
          과제 상세 보기
        </Button>
      </div>
    </div>
  );
};
