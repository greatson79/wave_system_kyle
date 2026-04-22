'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { usePublishAssignment } from '../hooks/usePublishAssignment';
import { useCloseAssignment } from '../hooks/useCloseAssignment';
import { PublishConfirmDialog } from './publish-confirm-dialog';
import { CloseConfirmDialog } from './close-confirm-dialog';

interface AssignmentActionsProps {
  assignmentId: string;
  status: 'draft' | 'published' | 'closed';
}

export function AssignmentActions({ assignmentId, status }: AssignmentActionsProps) {
  const [publishDialogOpen, setPublishDialogOpen] = useState(false);
  const [closeDialogOpen, setCloseDialogOpen] = useState(false);

  const publishMutation = usePublishAssignment();
  const closeMutation = useCloseAssignment();

  const handlePublish = () => {
    publishMutation.mutate(assignmentId, {
      onSuccess: () => {
        setPublishDialogOpen(false);
      },
    });
  };

  const handleClose = () => {
    closeMutation.mutate(assignmentId, {
      onSuccess: () => {
        setCloseDialogOpen(false);
      },
    });
  };

  if (status === 'draft') {
    return (
      <>
        <Button onClick={() => setPublishDialogOpen(true)} disabled={publishMutation.isPending}>
          {publishMutation.isPending ? '게시 중...' : '게시'}
        </Button>
        <PublishConfirmDialog
          open={publishDialogOpen}
          onOpenChange={setPublishDialogOpen}
          onConfirm={handlePublish}
        />
      </>
    );
  }

  if (status === 'published') {
    return (
      <>
        <Button onClick={() => setCloseDialogOpen(true)} disabled={closeMutation.isPending} variant="destructive">
          {closeMutation.isPending ? '마감 중...' : '마감'}
        </Button>
        <CloseConfirmDialog
          open={closeDialogOpen}
          onOpenChange={setCloseDialogOpen}
          onConfirm={handleClose}
        />
      </>
    );
  }

  return <p className="text-sm text-muted-foreground">마감된 과제입니다.</p>;
}
