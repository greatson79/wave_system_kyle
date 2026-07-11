'use client';

import { useState } from 'react';
import { TableCell, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { format, formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { MessageSquare } from 'lucide-react';
import type { GradeItem } from '../lib/dto';
import { FeedbackDetailDialog } from './feedback-detail-dialog';
import Link from 'next/link';

interface GradeRowProps {
  grade: GradeItem;
  courseId: string;
}

const getStatusBadge = (status: GradeItem['status']) => {
  switch (status) {
    case 'not_submitted':
      return <Badge variant="secondary">미제출</Badge>;
    case 'submitted':
      return <Badge variant="outline">제출 완료</Badge>;
    case 'graded':
      return <Badge variant="default">채점 완료</Badge>;
    case 'resubmission_required':
      return <Badge variant="destructive">재제출 요청</Badge>;
  }
};

export const GradeRow = ({ grade, courseId }: GradeRowProps) => {
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);

  const submittedAtText = grade.submittedAt
    ? formatDistanceToNow(new Date(grade.submittedAt), { addSuffix: true, locale: ko })
    : '-';

  const dueDateText = format(new Date(grade.dueDate), 'yyyy.MM.dd HH:mm', { locale: ko });

  return (
    <>
      <TableRow>
        <TableCell>
          <Link
            href={`/courses/my/${courseId}/assignments/${grade.assignmentId}`}
            className="hover:underline font-medium"
          >
            {grade.assignmentTitle}
          </Link>
          {grade.isLate && (
            <Badge variant="destructive" className="ml-2">
              지각
            </Badge>
          )}
        </TableCell>
        <TableCell className="text-sm text-muted-foreground">
          {submittedAtText}
        </TableCell>
        <TableCell className="text-sm text-muted-foreground">
          {dueDateText}
        </TableCell>
        <TableCell>
          {getStatusBadge(grade.status)}
        </TableCell>
        <TableCell>
          {grade.status === 'graded' && grade.score !== null ? (
            <span className="font-medium">{grade.score}점</span>
          ) : grade.status === 'submitted' ? (
            <span className="text-sm text-muted-foreground">채점 대기 중</span>
          ) : (
            <span className="text-sm text-muted-foreground">-</span>
          )}
        </TableCell>
        <TableCell>
          {grade.status === 'graded' && grade.feedback && grade.gradedAt ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFeedbackDialogOpen(true)}
            >
              <MessageSquare className="h-4 w-4 mr-1" />
              피드백 보기
            </Button>
          ) : (
            <span className="text-sm text-muted-foreground">-</span>
          )}
        </TableCell>
      </TableRow>

      {grade.status === 'graded' && grade.feedback && grade.gradedAt && grade.score !== null && (
        <FeedbackDetailDialog
          open={feedbackDialogOpen}
          onOpenChange={setFeedbackDialogOpen}
          assignmentTitle={grade.assignmentTitle}
          score={grade.score}
          feedback={grade.feedback}
          gradedAt={grade.gradedAt}
        />
      )}
    </>
  );
};
