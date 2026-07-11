'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

interface FeedbackDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  assignmentTitle: string;
  score: number;
  feedback: string;
  gradedAt: string;
}

export const FeedbackDetailDialog = ({
  open,
  onOpenChange,
  assignmentTitle,
  score,
  feedback,
  gradedAt,
}: FeedbackDetailDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{assignmentTitle} - 피드백</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b pb-4">
            <div>
              <p className="text-sm text-muted-foreground">점수</p>
              <p className="text-2xl font-bold">{score}점</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">채점 일시</p>
              <p className="text-sm">
                {format(new Date(gradedAt), 'yyyy년 M월 d일 HH:mm', { locale: ko })}
              </p>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium mb-2">강사 피드백</p>
            <div className="bg-muted rounded-lg p-4">
              <p className="text-sm whitespace-pre-wrap">{feedback}</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
