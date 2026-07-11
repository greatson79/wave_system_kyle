'use client';

import Link from 'next/link';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AssignmentStatusBadge } from './assignment-status-badge';
import { AssignmentActions } from './assignment-actions';
import type { MyAssignmentItem } from '../lib/dto';

interface MyAssignmentsListProps {
  assignments: MyAssignmentItem[];
}

export function MyAssignmentsList({ assignments }: MyAssignmentsListProps) {
  if (assignments.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">아직 생성한 과제가 없습니다.</p>
        <Link href="/instructor/assignments/new">
          <Button className="mt-4">첫 과제 만들기</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {assignments.map((assignment) => (
        <Card key={assignment.id}>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <CardTitle className="text-xl">
                  <Link
                    href={`/instructor/assignments/${assignment.id}/edit`}
                    className="hover:underline"
                  >
                    {assignment.title}
                  </Link>
                </CardTitle>
                <p className="text-sm text-muted-foreground">{assignment.courseTitle}</p>
              </div>
              <AssignmentStatusBadge status={assignment.status} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-sm font-medium">마감일</p>
                <p className="text-sm text-muted-foreground">
                  {format(new Date(assignment.dueDate), 'PPP', { locale: ko })}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">점수 비중</p>
                <p className="text-sm text-muted-foreground">{assignment.weight}%</p>
              </div>
              <div>
                <p className="text-sm font-medium">제출물</p>
                <p className="text-sm text-muted-foreground">
                  {assignment.submissionsCount}개
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">채점 완료</p>
                <p className="text-sm text-muted-foreground">
                  {assignment.gradedCount}/{assignment.submissionsCount}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link href={`/instructor/assignments/${assignment.id}/submissions`}>
                <Button variant="outline" size="sm">
                  제출물 보기
                </Button>
              </Link>
              <AssignmentActions assignmentId={assignment.id} status={assignment.status} />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
