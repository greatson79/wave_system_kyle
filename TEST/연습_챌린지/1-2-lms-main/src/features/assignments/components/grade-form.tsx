'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { useGradeSubmission } from '../hooks/useGradeSubmission';
import { GradeConfirmDialog } from './grade-confirm-dialog';
import { RegradeConfirmDialog } from './regrade-confirm-dialog';
import type { SubmissionDetailResponse } from '../lib/dto';

interface GradeFormProps {
  submission: SubmissionDetailResponse;
}

export const GradeForm = ({ submission }: GradeFormProps) => {
  const router = useRouter();
  const { toast } = useToast();
  const [score, setScore] = useState<string>(submission.score?.toString() || '');
  const [feedback, setFeedback] = useState<string>(submission.feedback || '');
  const [showConfirm, setShowConfirm] = useState(false);
  const [showRegradeConfirm, setShowRegradeConfirm] = useState(false);

  const { mutate: gradeSubmission, isPending } = useGradeSubmission(submission.id);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const scoreNum = parseFloat(score);
    if (isNaN(scoreNum) || scoreNum < 0 || scoreNum > 100) {
      toast({
        title: '점수 오류',
        description: '점수는 0에서 100 사이의 값이어야 합니다.',
        variant: 'destructive',
      });
      return;
    }

    if (!feedback.trim()) {
      toast({
        title: '피드백 필요',
        description: '피드백은 필수 입력 항목입니다.',
        variant: 'destructive',
      });
      return;
    }

    if (submission.status === 'graded') {
      setShowRegradeConfirm(true);
    } else {
      setShowConfirm(true);
    }
  };

  const handleConfirm = () => {
    const scoreNum = parseFloat(score);
    gradeSubmission(
      { score: scoreNum, feedback: feedback.trim() },
      {
        onSuccess: (data) => {
          toast({
            title: '채점 완료',
            description: data.message,
          });
          router.push(`/instructor/assignments/${submission.assignmentId}/submissions`);
        },
        onError: (error) => {
          toast({
            title: '채점 실패',
            description: error.message,
            variant: 'destructive',
          });
        },
      },
    );
    setShowConfirm(false);
    setShowRegradeConfirm(false);
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>채점하기</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="score">점수 (0-100)</Label>
              <Input
                id="score"
                type="number"
                min="0"
                max="100"
                step="0.01"
                value={score}
                onChange={(e) => setScore(e.target.value)}
                placeholder="점수를 입력하세요"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="feedback">피드백</Label>
              <Textarea
                id="feedback"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="학습자에게 전달할 피드백을 작성하세요"
                rows={5}
                required
              />
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={isPending}>
                {submission.status === 'graded' ? '재채점 완료' : '채점 완료'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
              >
                취소
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <GradeConfirmDialog
        open={showConfirm}
        onOpenChange={setShowConfirm}
        onConfirm={handleConfirm}
        score={parseFloat(score) || 0}
      />

      <RegradeConfirmDialog
        open={showRegradeConfirm}
        onOpenChange={setShowRegradeConfirm}
        onConfirm={handleConfirm}
      />
    </>
  );
};
