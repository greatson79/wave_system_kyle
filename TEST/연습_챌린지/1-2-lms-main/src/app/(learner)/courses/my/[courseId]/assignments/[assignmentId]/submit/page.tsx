'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { SubmissionForm } from '@/features/assignments/components/submission-form';
import { useAssignmentDetail } from '@/features/assignments/hooks/useAssignmentDetail';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

type PageProps = {
  params: Promise<{
    courseId: string;
    assignmentId: string;
  }>;
};

export default function AssignmentSubmitPage({ params }: PageProps) {
  const { courseId, assignmentId } = use(params);
  const router = useRouter();
  const { data: assignment, isLoading, isError, error } = useAssignmentDetail(assignmentId);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <p>로딩 중...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isError || !assignment) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>오류 발생</AlertTitle>
          <AlertDescription>
            {error?.message || '과제 정보를 불러올 수 없습니다.'}
          </AlertDescription>
        </Alert>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => router.push(`/courses/my/${courseId}`)}
        >
          코스 페이지로 돌아가기
        </Button>
      </div>
    );
  }

  if (!assignment.canSubmit) {
    return (
      <div className="container mx-auto py-8">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>제출 불가</AlertTitle>
          <AlertDescription>
            {assignment.status === 'closed'
              ? '마감된 과제입니다.'
              : assignment.submission?.status === 'submitted'
                ? '이미 제출된 과제입니다. 강사가 재제출을 요청한 경우에만 재제출할 수 있습니다.'
                : assignment.submission?.status === 'graded'
                  ? '이미 채점된 과제입니다.'
                  : '제출할 수 없는 과제입니다.'}
          </AlertDescription>
        </Alert>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() =>
            router.push(`/courses/my/${courseId}/assignments/${assignmentId}`)
          }
        >
          과제 상세 보기
        </Button>
      </div>
    );
  }

  const isResubmit = assignment.submission?.status === 'resubmission_required';
  const dueDate = format(new Date(assignment.dueDate), 'yyyy년 MM월 dd일 HH:mm', {
    locale: ko,
  });

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>{assignment.title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-2">
                과제 설명
              </h3>
              <p className="text-sm whitespace-pre-wrap">{assignment.description}</p>
            </div>

            <div className="flex items-center gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">마감일: </span>
                <span className="font-medium">{dueDate}</span>
              </div>
              <div>
                <span className="text-muted-foreground">배점: </span>
                <span className="font-medium">{assignment.weight}점</span>
              </div>
            </div>

            {isResubmit && assignment.submission?.feedback && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>강사 피드백</AlertTitle>
                <AlertDescription className="whitespace-pre-wrap">
                  {assignment.submission.feedback}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        <SubmissionForm
          assignmentId={assignmentId}
          courseId={courseId}
          dueDate={assignment.dueDate}
          isResubmit={isResubmit}
          existingSubmission={
            isResubmit && assignment.submission
              ? {
                  submissionText: assignment.submission.submissionText,
                  submissionLink: assignment.submission.submissionLink,
                }
              : null
          }
        />
      </div>
    </div>
  );
}
