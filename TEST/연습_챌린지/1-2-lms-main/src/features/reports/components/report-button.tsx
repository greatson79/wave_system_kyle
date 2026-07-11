'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ReportDialog } from './report-dialog';
import type { TargetType } from '../lib/dto';

interface ReportButtonProps {
  targetType: TargetType;
  targetId: string;
  disabled?: boolean;
  size?: 'default' | 'sm' | 'lg' | 'icon';
  variant?: 'default' | 'outline' | 'ghost' | 'destructive' | 'link';
}

export function ReportButton({
  targetType,
  targetId,
  disabled = false,
  size = 'default',
  variant = 'outline',
}: ReportButtonProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleOpenDialog = () => {
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
  };

  return (
    <>
      <Button
        onClick={handleOpenDialog}
        disabled={disabled}
        size={size}
        variant={variant}
      >
        신고하기
      </Button>

      <ReportDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        targetType={targetType}
        targetId={targetId}
        onSuccess={handleCloseDialog}
      />
    </>
  );
}
