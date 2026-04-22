'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle } from 'lucide-react';

interface SubmissionConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  isResubmit?: boolean;
  isLate?: boolean;
  submissionText: string;
  submissionLink?: string | null;
}

export const SubmissionConfirmDialog = ({
  open,
  onOpenChange,
  onConfirm,
  isResubmit = false,
  isLate = false,
  submissionText,
  submissionLink,
}: SubmissionConfirmDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {isResubmit ? '과제를 재제출하시겠습니까?' : '과제를 제출하시겠습니까?'}
          </DialogTitle>
          <DialogDescription>
            제출한 내용을 확인해주세요. {isResubmit ? '재제출' : '제출'} 후에는 강사가 확인할 수 있습니다.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {isLate && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                마감일이 지났습니다. 지각 제출로 처리됩니다.
              </AlertDescription>
            </Alert>
          )}

          <div>
            <h4 className="text-sm font-medium mb-2">제출 내용</h4>
            <div className="rounded-md border p-3 bg-muted/50 text-sm whitespace-pre-wrap break-words">
              {submissionText}
            </div>
          </div>

          {submissionLink && (
            <div>
              <h4 className="text-sm font-medium mb-2">제출 링크</h4>
              <div className="rounded-md border p-3 bg-muted/50 text-sm break-all">
                <a
                  href={submissionLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {submissionLink}
                </a>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            취소
          </Button>
          <Button onClick={onConfirm}>
            {isResubmit ? '재제출' : '제출'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
