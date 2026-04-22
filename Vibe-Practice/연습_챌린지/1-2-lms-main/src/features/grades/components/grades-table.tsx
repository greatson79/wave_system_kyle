'use client';

import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { useCourseGrades } from '../hooks/useCourseGrades';
import { GradeRow } from './grade-row';

interface GradesTableProps {
  courseId: string;
}

export const GradesTable = ({ courseId }: GradesTableProps) => {
  const { data, isLoading, error } = useCourseGrades(courseId);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>과제별 성적</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>과제별 성적</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error.message || '성적 정보를 불러오지 못했습니다.'}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.grades.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>과제별 성적</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            등록된 과제가 없습니다
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>과제별 성적</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>과제명</TableHead>
                <TableHead>제출일</TableHead>
                <TableHead>마감일</TableHead>
                <TableHead>상태</TableHead>
                <TableHead>점수</TableHead>
                <TableHead>피드백</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.grades.map((grade) => (
                <GradeRow key={grade.assignmentId} grade={grade} courseId={courseId} />
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};
