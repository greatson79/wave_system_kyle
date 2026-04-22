'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { useRequestResubmission } from '../hooks/useRequestResubmission';
import type { SubmissionDetailResponse } from '../lib/dto';

interface RequestResubmissionFormProps {
  submission: SubmissionDetailResponse;
}

export const RequestResubmissionForm = ({ submission }: RequestResubmissionFormProps) => {
  const router = useRouter();
  const { toast } = useToast();
  const [score, setScore] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');

  const { mutate: requestResubmission, isPending } = useRequestResubmission(submission.id);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!feedback.trim()) {
      toast({
        title: '피드백 필요',
        description: '피드백은 필수 입력 항목입니다.',
        variant: 'destructive',
      });
      return;
    }

    let scoreNum: number | null = null;
    if (score.trim()) {
      scoreNum = parseFloat(score);
      if (isNaN(scoreNum) || scoreNum < 0 || scoreNum > 100) {
        toast({
          title: '점수 오류',
          description: '점수는 0에서 100 사이의 값이어야 합니다.',
          variant: 'destructive',
        });
        return;
      }
    }

    requestResubmission(
      {
        score: scoreNum,
        feedback: feedback.trim(),
      },
      {
        onSuccess: (data) => {
          toast({
            title: '재제출 요청 완료',
            description: data.message,
          });
          router.push(`/instructor/assignments/${submission.assignmentId}/submissions`);
        },
        onError: (error) => {
          toast({
            title: '재제출 요청 실패',
            description: error.message,
            variant: 'destructive',
          });
        },
      },
    );
  };

  if (!submission.assignmentAllowResubmit) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>재제출 요청</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            이 과제는 재제출이 허용되지 않습니다.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>재제출 요청</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="score">점수 (선택사항, 0-100)</Label>
            <Input
              id="score"
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={score}
              onChange={(e) => setScore(e.target.value)}
              placeholder="점수를 입력하세요 (선택사항)"
            />
            <p className="text-sm text-muted-foreground">
              점수를 입력하지 않으면 이전 점수가 유지됩니다.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="feedback">피드백</Label>
            <Textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="재제출이 필요한 이유를 작성하세요"
              rows={5}
              required
            />
          </div>

          <div className="flex gap-2">
            <Button type="submit" disabled={isPending}>
              재제출 요청
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
  );
};
