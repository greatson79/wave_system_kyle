'use client';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface ArchiveConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  assignmentsCount?: number;
}

export const ArchiveConfirmDialog = ({
  open,
  onOpenChange,
  onConfirm,
  assignmentsCount = 0,
}: ArchiveConfirmDialogProps) => {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>코스를 보관하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            {assignmentsCount > 0 ? (
              <>
                이 작업은 되돌릴 수 없습니다. 보관된 코스는 다시 활성화할 수 없습니다.
                <br />
                <br />
                <strong className="text-orange-600">
                  {assignmentsCount}개의 과제가 자동으로 마감됩니다.
                </strong>
              </>
            ) : (
              '이 작업은 되돌릴 수 없습니다. 보관된 코스는 다시 활성화할 수 없습니다.'
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>취소</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>확인</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
