'use client';

import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { TableCell, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import type { SubmissionItem } from '../lib/dto';

interface SubmissionRowProps {
  submission: SubmissionItem;
}

export function SubmissionRow({ submission }: SubmissionRowProps) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'submitted':
        return <Badge variant="secondary">제출됨</Badge>;
      case 'graded':
        return <Badge variant="default">채점 완료</Badge>;
      case 'resubmission_required':
        return <Badge variant="destructive">재제출 요청</Badge>;
      default:
        return null;
    }
  };

  return (
    <TableRow>
      <TableCell>{submission.learnerName}</TableCell>
      <TableCell>
        {format(new Date(submission.submittedAt), 'PPP p', { locale: ko })}
        {submission.isLate && (
          <Badge variant="outline" className="ml-2">
            지각
          </Badge>
        )}
      </TableCell>
      <TableCell>{getStatusBadge(submission.status)}</TableCell>
      <TableCell>{submission.score !== null ? `${submission.score}점` : '-'}</TableCell>
      <TableCell className="max-w-xs truncate">{submission.submissionText}</TableCell>
    </TableRow>
  );
}
