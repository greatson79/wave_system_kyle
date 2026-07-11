'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import type { GradesSummary } from '../lib/dto';
import { calculateCompletionRate } from '../lib/dto';

interface GradesSummaryProps {
  summary: GradesSummary;
}

export function GradesSummary({ summary }: GradesSummaryProps) {
  const completionRate = calculateCompletionRate(
    summary.totalAssignments,
    summary.gradedAssignments,
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>성적 요약</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">전체 과제</p>
            <p className="text-2xl font-bold">{summary.totalAssignments}개</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">채점 완료</p>
            <p className="text-2xl font-bold">{summary.gradedAssignments}개</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">총점</p>
            <p className="text-2xl font-bold">{summary.totalScore.toFixed(1)}점</p>
          </div>
          {summary.averageScore !== null && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">평균 점수</p>
              <p className="text-2xl font-bold">{summary.averageScore.toFixed(1)}점</p>
            </div>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">채점 완료율</span>
            <span className="font-medium">{completionRate.toFixed(1)}%</span>
          </div>
          <Progress value={completionRate} className="h-2" />
        </div>

        {summary.gradedAssignments === 0 && (
          <p className="text-sm text-muted-foreground text-center py-4">
            아직 채점된 과제가 없습니다
          </p>
        )}
      </CardContent>
    </Card>
  );
}
