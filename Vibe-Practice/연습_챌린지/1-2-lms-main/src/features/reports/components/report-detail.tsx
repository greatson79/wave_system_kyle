'use client';

import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { useReportDetail } from '../hooks/useReportDetail';
import {
  getReportStatusText,
  getReportStatusColor,
  type TargetType,
} from '../lib/dto';

interface ReportDetailProps {
  reportId: string;
}

const targetTypeLabels: Record<TargetType, string> = {
  course: '코스',
  assignment: '과제',
  submission: '제출물',
  user: '사용자',
};

export function ReportDetail({ reportId }: ReportDetailProps) {
  const { data: report, isLoading, error } = useReportDetail(reportId);

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-[200px]" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return (
      <Alert>
        <AlertDescription>신고 정보를 찾을 수 없습니다.</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>신고 상세 정보</CardTitle>
          <Badge variant={getReportStatusColor(report.status)}>
            {getReportStatusText(report.status)}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm font-medium text-muted-foreground mb-1">
              신고자
            </div>
            <div>{report.reporter.name}</div>
          </div>

          <div>
            <div className="text-sm font-medium text-muted-foreground mb-1">
              대상 유형
            </div>
            <div>{targetTypeLabels[report.targetType]}</div>
          </div>

          <div>
            <div className="text-sm font-medium text-muted-foreground mb-1">
              접수일
            </div>
            <div>
              {format(new Date(report.createdAt), 'PPpp', { locale: ko })}
            </div>
          </div>

          {report.resolvedAt && (
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">
                처리일
              </div>
              <div>
                {format(new Date(report.resolvedAt), 'PPpp', { locale: ko })}
              </div>
            </div>
          )}
        </div>

        <Separator />

        <div>
          <div className="text-sm font-medium text-muted-foreground mb-1">
            신고 사유
          </div>
          <div>{report.reason}</div>
        </div>

        <div>
          <div className="text-sm font-medium text-muted-foreground mb-1">
            신고 내용
          </div>
          <div className="whitespace-pre-wrap rounded-md border p-4 bg-muted/30">
            {report.content}
          </div>
        </div>

        {report.targetInfo && (
          <>
            <Separator />
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">
                대상 정보
              </div>
              <div className="rounded-md border p-3 bg-muted/30">
                {report.targetInfo.title && (
                  <div className="text-sm">
                    <span className="font-medium">제목:</span>{' '}
                    {report.targetInfo.title}
                  </div>
                )}
                {report.targetInfo.name && (
                  <div className="text-sm">
                    <span className="font-medium">이름:</span>{' '}
                    {report.targetInfo.name}
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {report.actionTaken && (
          <>
            <Separator />
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">
                조치 내용
              </div>
              <div className="whitespace-pre-wrap rounded-md border p-4 bg-muted/30">
                {report.actionTaken}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
