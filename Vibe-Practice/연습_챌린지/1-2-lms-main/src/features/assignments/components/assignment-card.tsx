'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate, isDueSoon } from '@/lib/utils/date';
import {
  getSubmissionStatusText,
  getSubmissionStatusColor,
} from '../lib/submission-status';
import type { AssignmentItem } from '../lib/dto';

type AssignmentCardProps = {
  assignment: AssignmentItem;
  courseId: string;
};

export const AssignmentCard = ({
  assignment,
  courseId,
}: AssignmentCardProps) => {
  const isDueSoonFlag = isDueSoon(assignment.dueDate);
  const submissionStatusText = getSubmissionStatusText(
    assignment.submissionStatus === 'not_submitted'
      ? null
      : assignment.submissionStatus,
    assignment.score,
  );
  const submissionStatusColor = getSubmissionStatusColor(
    assignment.submissionStatus === 'not_submitted'
      ? null
      : assignment.submissionStatus,
  );

  return (
    <Link href={`/courses/my/${courseId}/assignments/${assignment.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between">
            <CardTitle className="text-lg">{assignment.title}</CardTitle>
            {isDueSoonFlag && (
              <Badge variant="destructive" className="ml-2">
                마감 임박
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">마감일</span>
              <span className="font-medium">
                {formatDate(assignment.dueDate, 'yyyy년 MM월 dd일 HH:mm')}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">배점</span>
              <span className="font-medium">{assignment.weight}점</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">제출 상태</span>
              <span className={`font-medium ${submissionStatusColor}`}>
                {submissionStatusText}
              </span>
            </div>
            {assignment.isLate && (
              <Badge variant="outline" className="mt-2">
                지각 제출
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};
