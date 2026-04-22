'use client';

import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink } from 'lucide-react';
import type { SubmissionDetailResponse } from '../lib/dto';
import { getSubmissionStatusText, getSubmissionStatusColor } from '../lib/submission-status-utils';

interface SubmissionDetailProps {
  submission: SubmissionDetailResponse;
}

export const SubmissionDetail = ({ submission }: SubmissionDetailProps) => {
  const statusText = getSubmissionStatusText(submission.status);
  const statusColor = getSubmissionStatusColor(submission.status);

  const badgeVariant = statusColor === 'success' ? 'default' : statusColor === 'warning' ? 'secondary' : 'default';

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>제출물 정보</CardTitle>
          <Badge variant={badgeVariant}>{statusText}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="text-sm font-medium text-muted-foreground">과제명</div>
          <div className="text-base">{submission.assignmentTitle}</div>
        </div>

        <div>
          <div className="text-sm font-medium text-muted-foreground">학습자</div>
          <div className="text-base">{submission.learnerName}</div>
        </div>

        <div>
          <div className="text-sm font-medium text-muted-foreground">제출 일시</div>
          <div className="text-base flex items-center gap-2">
            {format(new Date(submission.submittedAt), 'PPP p', { locale: ko })}
            {submission.isLate && (
              <Badge variant="destructive">지각 제출</Badge>
            )}
          </div>
        </div>

        <div>
          <div className="text-sm font-medium text-muted-foreground">제출 내용</div>
          <div className="text-base whitespace-pre-wrap">{submission.submissionText}</div>
        </div>

        {submission.submissionLink && (
          <div>
            <div className="text-sm font-medium text-muted-foreground">첨부 링크</div>
            <a
              href={submission.submissionLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-base text-primary hover:underline flex items-center gap-1"
            >
              {submission.submissionLink}
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        )}

        {submission.status === 'graded' && (
          <>
            <div>
              <div className="text-sm font-medium text-muted-foreground">점수</div>
              <div className="text-base font-semibold">{submission.score}점</div>
            </div>

            <div>
              <div className="text-sm font-medium text-muted-foreground">피드백</div>
              <div className="text-base whitespace-pre-wrap">{submission.feedback}</div>
            </div>

            {submission.gradedAt && (
              <div>
                <div className="text-sm font-medium text-muted-foreground">채점 일시</div>
                <div className="text-base">
                  {format(new Date(submission.gradedAt), 'PPP p', { locale: ko })}
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};
