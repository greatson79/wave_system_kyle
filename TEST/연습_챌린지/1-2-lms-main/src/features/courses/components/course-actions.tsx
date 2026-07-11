'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useUpdateCourseStatus } from '../hooks/useUpdateCourseStatus';
import { ArchiveConfirmDialog } from './archive-confirm-dialog';
import { useToast } from '@/hooks/use-toast';

type CourseStatus = 'draft' | 'published' | 'archived';

interface CourseActionsProps {
  courseId: string;
  status: CourseStatus;
  assignmentsCount?: number;
}

export const CourseActions = ({
  courseId,
  status,
  assignmentsCount = 0,
}: CourseActionsProps) => {
  const [showArchiveDialog, setShowArchiveDialog] = useState(false);
  const { mutate: updateStatus, isPending } = useUpdateCourseStatus(courseId);
  const { toast } = useToast();

  const handlePublish = () => {
    updateStatus(
      { status: 'published' },
      {
        onSuccess: (data) => {
          toast({
            title: '성공',
            description: data.message,
          });
        },
        onError: (error) => {
          toast({
            title: '오류',
            description: error.message,
            variant: 'destructive',
          });
        },
      }
    );
  };

  const handleArchiveConfirm = () => {
    updateStatus(
      { status: 'archived' },
      {
        onSuccess: (data) => {
          toast({
            title: '성공',
            description: data.message,
          });
          setShowArchiveDialog(false);
        },
        onError: (error) => {
          toast({
            title: '오류',
            description: error.message,
            variant: 'destructive',
          });
        },
      }
    );
  };

  if (status === 'draft') {
    return (
      <Button onClick={handlePublish} disabled={isPending}>
        {isPending ? '처리 중...' : '게시'}
      </Button>
    );
  }

  if (status === 'published') {
    return (
      <>
        <Button
          onClick={() => setShowArchiveDialog(true)}
          variant="outline"
          disabled={isPending}
        >
          보관
        </Button>
        <ArchiveConfirmDialog
          open={showArchiveDialog}
          onOpenChange={setShowArchiveDialog}
          onConfirm={handleArchiveConfirm}
          assignmentsCount={assignmentsCount}
        />
      </>
    );
  }

  return (
    <div className="text-sm text-muted-foreground">
      보관된 코스는 재활성화할 수 없습니다.
    </div>
  );
};
