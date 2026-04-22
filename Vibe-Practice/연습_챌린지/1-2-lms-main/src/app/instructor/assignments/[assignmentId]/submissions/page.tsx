'use client';

import { use, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useAssignmentSubmissions } from '@/features/assignments/hooks/useAssignmentSubmissions';
import { SubmissionsTable } from '@/features/assignments/components/submissions-table';

interface AssignmentSubmissionsPageProps {
  params: Promise<{
    assignmentId: string;
  }>;
}

export default function AssignmentSubmissionsPage({ params }: AssignmentSubmissionsPageProps) {
  const { assignmentId } = use(params);
  const [filter, setFilter] = useState<'all' | 'ungraded' | 'late' | 'resubmission_required'>('all');
  const { data, isLoading, error } = useAssignmentSubmissions(assignmentId, filter);

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/instructor/assignments">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">
            {data?.assignmentTitle || '과제 제출물'}
          </h1>
          <p className="text-muted-foreground mt-1">학습자들의 제출물을 확인하고 채점하세요.</p>
        </div>
      </div>

      {isLoading && (
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      )}

      {error && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-destructive">제출물 목록을 불러오는 중 오류가 발생했습니다.</p>
          </CardContent>
        </Card>
      )}

      {data && (
        <Card>
          <CardHeader>
            <CardTitle>제출물 목록</CardTitle>
          </CardHeader>
          <CardContent>
            <SubmissionsTable
              submissions={data.submissions}
              onFilterChange={setFilter}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
