'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { formatDate } from '@/lib/utils/date';
import {
  getSubmissionStatusText,
  getSubmissionStatusColor,
} from '../lib/submission-status';
import type { AssignmentDetailResponse } from '../lib/dto';

type AssignmentSubmissionStatusProps = {
  assignment: AssignmentDetailResponse;
};

export const AssignmentSubmissionStatus = ({
  assignment,
}: AssignmentSubmissionStatusProps) => {
  const { submission } = assignment;

  if (!submission) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>제출 상태</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">아직 제출하지 않았습니다.</p>
        </CardContent>
      </Card>
    );
  }

  const statusText = getSubmissionStatusText(submission.status, submission.score);
  const statusColor = getSubmissionStatusColor(submission.status);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>제출 상태</CardTitle>
          <Badge className={statusColor}>{statusText}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {submission.status === 'resubmission_required' && (
          <Alert>
            <AlertDescription>
              재제출이 요청되었습니다. 피드백을 확인하고 다시 제출해주세요.
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">제출 일시</span>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">
                {formatDate(submission.submittedAt, 'yyyy년 MM월 dd일 HH:mm')}
              </span>
              {submission.isLate && (
                <Badge variant="outline">지각 제출</Badge>
              )}
            </div>
          </div>

          {submission.status === 'graded' && submission.gradedAt && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">채점 일시</span>
              <span className="text-sm font-medium">
                {formatDate(submission.gradedAt, 'yyyy년 MM월 dd일 HH:mm')}
              </span>
            </div>
          )}

          {submission.score !== null && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">점수</span>
              <span className="text-lg font-bold text-green-600">
                {submission.score}점
              </span>
            </div>
          )}
        </div>

        <div className="border-t pt-4">
          <h4 className="font-semibold mb-2">제출 내용</h4>
          <div className="bg-gray-50 p-4 rounded-md">
            <p className="text-sm whitespace-pre-wrap">
              {submission.submissionText}
            </p>
            {submission.submissionLink && (
              <div className="mt-2">
                <a
                  href={submission.submissionLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  링크: {submission.submissionLink}
                </a>
              </div>
            )}
          </div>
        </div>

        {submission.feedback && (
          <div className="border-t pt-4">
            <h4 className="font-semibold mb-2">피드백</h4>
            <div className="bg-blue-50 p-4 rounded-md">
              <p className="text-sm whitespace-pre-wrap">{submission.feedback}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
