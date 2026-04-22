'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useMyAssignments } from '@/features/assignments/hooks/useMyAssignments';
import { MyAssignmentsList } from '@/features/assignments/components/my-assignments-list';

export default function InstructorAssignmentsPage() {
  const { data, isLoading, error } = useMyAssignments();

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">내 과제</h1>
          <p className="text-muted-foreground mt-1">생성한 과제를 관리하고 제출물을 확인하세요.</p>
        </div>
        <Link href="/instructor/assignments/new">
          <Button>새 과제 만들기</Button>
        </Link>
      </div>

      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2 mt-2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {error && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-destructive">과제 목록을 불러오는 중 오류가 발생했습니다.</p>
          </CardContent>
        </Card>
      )}

      {data && <MyAssignmentsList assignments={data.assignments} />}
    </div>
  );
}
