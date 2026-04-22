'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { SubmissionConfirmDialog } from './submission-confirm-dialog';
import { SubmissionSuccessMessage } from './submission-success-message';
import { useSubmitAssignment } from '../hooks/useSubmitAssignment';
import { useResubmitAssignment } from '../hooks/useResubmitAssignment';
import {
  SubmitAssignmentRequestSchema,
  type SubmitAssignmentRequest,
} from '../lib/dto';

type SubmissionFormProps = {
  assignmentId: string;
  courseId: string;
  dueDate: string;
  isResubmit?: boolean;
  existingSubmission?: {
    submissionText: string;
    submissionLink: string | null;
  } | null;
};

export const SubmissionForm = ({
  assignmentId,
  courseId,
  dueDate,
  isResubmit = false,
  existingSubmission,
}: SubmissionFormProps) => {
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [submissionSuccess, setSubmissionSuccess] = useState<{
    isLate: boolean;
    submittedAt: string;
  } | null>(null);

  const submitMutation = useSubmitAssignment(assignmentId);
  const resubmitMutation = useResubmitAssignment(assignmentId);

  const mutation = isResubmit ? resubmitMutation : submitMutation;

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SubmitAssignmentRequest>({
    resolver: zodResolver(SubmitAssignmentRequestSchema),
    defaultValues: {
      submissionText: existingSubmission?.submissionText || '',
      submissionLink: existingSubmission?.submissionLink || '',
    },
  });

  const submissionText = watch('submissionText');
  const submissionLink = watch('submissionLink');

  const isLate = new Date() > new Date(dueDate);

  const onSubmit = handleSubmit(() => {
    setShowConfirmDialog(true);
  });

  const handleConfirm = () => {
    mutation.mutate(
      {
        submissionText,
        submissionLink: submissionLink || null,
      },
      {
        onSuccess: (data) => {
          setShowConfirmDialog(false);
          setSubmissionSuccess({
            isLate: data.isLate,
            submittedAt: data.submittedAt,
          });
        },
      },
    );
  };

  if (submissionSuccess) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>제출 완료</CardTitle>
        </CardHeader>
        <CardContent>
          <SubmissionSuccessMessage
            isLate={submissionSuccess.isLate}
            submittedAt={submissionSuccess.submittedAt}
            courseId={courseId}
            assignmentId={assignmentId}
            isResubmit={isResubmit}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{isResubmit ? '과제 재제출' : '과제 제출'}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            {isLate && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  마감일이 지났습니다. 지각 제출로 처리됩니다.
                </AlertDescription>
              </Alert>
            )}

            {mutation.isError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {mutation.error?.message || '제출에 실패했습니다.'}
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="submission-text">제출 내용 (필수)</Label>
              <Textarea
                id="submission-text"
                placeholder="과제 내용을 입력하세요..."
                rows={8}
                {...register('submissionText')}
              />
              {errors.submissionText && (
                <p className="text-sm text-destructive">
                  {errors.submissionText.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="submission-link">링크 (선택)</Label>
              <Input
                id="submission-link"
                type="url"
                placeholder="https://example.com"
                {...register('submissionLink')}
              />
              {errors.submissionLink && (
                <p className="text-sm text-destructive">
                  {errors.submissionLink.message}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={mutation.isPending}
            >
              {mutation.isPending
                ? '제출 중...'
                : isResubmit
                  ? '재제출하기'
                  : '제출하기'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <SubmissionConfirmDialog
        open={showConfirmDialog}
        onOpenChange={setShowConfirmDialog}
        onConfirm={handleConfirm}
        isResubmit={isResubmit}
        isLate={isLate}
        submissionText={submissionText}
        submissionLink={submissionLink}
      />
    </>
  );
};
