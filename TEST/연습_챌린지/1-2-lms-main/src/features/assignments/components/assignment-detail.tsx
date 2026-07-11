'use client';

import { useAssignmentDetail } from '../hooks/useAssignmentDetail';
import { AssignmentSubmissionStatus } from './assignment-submission-status';
import { SubmissionForm } from './submission-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { formatDate, formatDueStatus } from '@/lib/utils/date';
import { canSubmitAssignment } from '../lib/submission-status';
import { useRouter } from 'next/navigation';

type AssignmentDetailProps = {
  assignmentId: string;
};

export const AssignmentDetail = ({ assignmentId }: AssignmentDetailProps) => {
  const router = useRouter();
  const { data: assignment, isLoading, error, refetch } = useAssignmentDetail(assignmentId);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          <div className="flex flex-col gap-2">
            <p>{error.message}</p>
            <div className="flex gap-2">
              <Button onClick={() => refetch()} variant="outline" size="sm">
                재시도
              </Button>
              <Button
                onClick={() => router.push(`/courses/my/${assignment?.courseId || ''}`)}
                variant="outline"
                size="sm"
              >
                코스 페이지로 돌아가기
              </Button>
            </div>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (!assignment) {
    return (
      <Alert>
        <AlertDescription>과제를 찾을 수 없습니다.</AlertDescription>
      </Alert>
    );
  }

  const submissionCheck = canSubmitAssignment(
    assignment.status,
    assignment.dueDate,
    assignment.allowLate,
    assignment.allowResubmit,
    assignment.submission?.status || null,
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-2xl">{assignment.title}</CardTitle>
              <Badge variant={assignment.status === 'published' ? 'default' : 'secondary'}>
                {assignment.status === 'published' ? '진행 중' : '마감'}
              </Badge>
            </div>
            <p className="text-sm text-gray-600">{assignment.courseTitle}</p>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose max-w-none">
            <p className="whitespace-pre-wrap">{assignment.description}</p>
          </div>

          <div className="border-t pt-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">마감일</span>
              <div className="flex items-center gap-2">
                <span className="font-medium">
                  {formatDate(assignment.dueDate, 'yyyy년 MM월 dd일 HH:mm')}
                </span>
                <span className="text-sm text-gray-500">
                  ({formatDueStatus(assignment.dueDate)})
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">배점</span>
              <span className="font-medium">{assignment.weight}점</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">지각 허용</span>
              <Badge variant={assignment.allowLate ? 'default' : 'secondary'}>
                {assignment.allowLate ? '허용' : '불허'}
              </Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">재제출 허용</span>
              <Badge variant={assignment.allowResubmit ? 'default' : 'secondary'}>
                {assignment.allowResubmit ? '허용' : '불허'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <AssignmentSubmissionStatus assignment={assignment} />

      {assignment.canSubmit && submissionCheck.canSubmit ? (
        <Card>
          <CardContent className="pt-6">
            <div className="flex justify-center">
              <Button
                size="lg"
                onClick={() =>
                  router.push(
                    `/courses/my/${assignment.courseId}/assignments/${assignment.id}/submit`,
                  )
                }
              >
                {assignment.submission?.status === 'resubmission_required'
                  ? '재제출하기'
                  : '제출하기'}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Alert>
          <AlertDescription>
            {submissionCheck.reason || '제출할 수 없습니다.'}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};
