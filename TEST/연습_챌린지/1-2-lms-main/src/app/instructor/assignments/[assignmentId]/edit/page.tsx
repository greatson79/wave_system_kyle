'use client';

import { use } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useUpdateAssignment } from '@/features/assignments/hooks/useUpdateAssignment';
import { useMyAssignments } from '@/features/assignments/hooks/useMyAssignments';
import { useState } from 'react';

interface EditAssignmentPageProps {
  params: Promise<{
    assignmentId: string;
  }>;
}

export default function EditAssignmentPage({ params }: EditAssignmentPageProps) {
  const { assignmentId } = use(params);
  const { data, isLoading } = useMyAssignments();
  const updateMutation = useUpdateAssignment();

  const assignment = data?.assignments.find((a) => a.id === assignmentId);

  const [title, setTitle] = useState(assignment?.title || '');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(
      {
        assignmentId,
        data: { title, description },
      },
      {
        onSuccess: () => {
          alert('과제가 성공적으로 수정되었습니다.');
        },
        onError: (error) => {
          alert(error.message);
        },
      },
    );
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-1/2" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!assignment) {
    return (
      <div className="container mx-auto py-8 max-w-3xl">
        <Card>
          <CardContent className="pt-6">
            <p className="text-destructive">과제를 찾을 수 없습니다.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">과제 수정</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="text-sm font-medium">제목</label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="과제 제목"
              />
            </div>
            <div>
              <label className="text-sm font-medium">설명</label>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="과제 설명"
                className="min-h-[200px]"
              />
            </div>
            <Button type="submit" disabled={updateMutation.isPending}>
              {updateMutation.isPending ? '저장 중...' : '저장'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
