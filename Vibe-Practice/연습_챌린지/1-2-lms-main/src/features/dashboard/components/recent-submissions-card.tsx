'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, User } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import type { RecentSubmissionItem } from '../lib/dto';

interface RecentSubmissionsCardProps {
  submissions: RecentSubmissionItem[];
}

const statusConfig = {
  submitted: { label: '제출됨', variant: 'secondary' as const },
  graded: { label: '채점완료', variant: 'default' as const },
  resubmission_required: { label: '재제출 필요', variant: 'outline' as const },
};

export function RecentSubmissionsCard({ submissions }: RecentSubmissionsCardProps) {
  const router = useRouter();

  if (submissions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            최근 제출물
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FileText className="h-12 w-12 text-gray-300 dark:text-gray-600 mb-4" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              최근 제출된 과제가 없습니다
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          최근 제출물
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {submissions.map((submission) => {
            const config = statusConfig[submission.status];
            return (
              <div
                key={submission.submissionId}
                className="flex items-start justify-between p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                onClick={() =>
                  router.push(
                    `/instructor/courses/${submission.courseId}/assignments/${submission.assignmentId}/submissions/${submission.submissionId}`,
                  )
                }
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <h3 className="font-semibold text-sm">{submission.assignmentTitle}</h3>
                    <Badge variant={config.variant}>{config.label}</Badge>
                    {submission.isLate && (
                      <Badge variant="destructive" className="text-xs">
                        지각
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 flex-wrap">
                    <span className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {submission.learnerName}
                    </span>
                    <span>{submission.courseTitle}</span>
                    <span>
                      {formatDistanceToNow(new Date(submission.submittedAt), {
                        addSuffix: true,
                        locale: ko,
                      })}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
