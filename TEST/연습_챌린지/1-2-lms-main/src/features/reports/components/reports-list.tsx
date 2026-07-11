'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { useReportsList } from '../hooks/useReportsList';
import {
  getReportStatusText,
  getReportStatusColor,
  type ReportStatus,
  type TargetType,
} from '../lib/dto';

const targetTypeLabels: Record<TargetType, string> = {
  course: '코스',
  assignment: '과제',
  submission: '제출물',
  user: '사용자',
};

export function ReportsList() {
  const router = useRouter();
  const [status, setStatus] = useState<ReportStatus | undefined>(undefined);
  const [targetType, setTargetType] = useState<TargetType | undefined>(
    undefined
  );
  const [page, setPage] = useState(0);
  const limit = 20;

  const { data, isLoading, error } = useReportsList({
    status,
    targetType,
    limit,
    offset: page * limit,
  });

  const handleRowClick = (reportId: string) => {
    router.push(`/operator/reports/${reportId}`);
  };

  const handleNextPage = () => {
    if (data && page * limit + limit < data.total) {
      setPage((prev) => prev + 1);
    }
  };

  const handlePrevPage = () => {
    if (page > 0) {
      setPage((prev) => prev - 1);
    }
  };

  const handleStatusFilterChange = (value: string) => {
    setStatus(value === 'all' ? undefined : (value as ReportStatus));
    setPage(0);
  };

  const handleTargetTypeFilterChange = (value: string) => {
    setTargetType(value === 'all' ? undefined : (value as TargetType));
    setPage(0);
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>신고 목록</CardTitle>
        <div className="flex gap-4 mt-4">
          <div className="w-[200px]">
            <Select
              value={status || 'all'}
              onValueChange={handleStatusFilterChange}
            >
              <SelectTrigger>
                <SelectValue placeholder="상태 필터" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="received">접수됨</SelectItem>
                <SelectItem value="investigating">조사 중</SelectItem>
                <SelectItem value="resolved">처리 완료</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="w-[200px]">
            <Select
              value={targetType || 'all'}
              onValueChange={handleTargetTypeFilterChange}
            >
              <SelectTrigger>
                <SelectValue placeholder="대상 유형 필터" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 유형</SelectItem>
                <SelectItem value="course">코스</SelectItem>
                <SelectItem value="assignment">과제</SelectItem>
                <SelectItem value="submission">제출물</SelectItem>
                <SelectItem value="user">사용자</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>신고자</TableHead>
                  <TableHead>대상 유형</TableHead>
                  <TableHead>신고 사유</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>접수일</TableHead>
                  <TableHead>처리일</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.reports.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      신고 내역이 없습니다.
                    </TableCell>
                  </TableRow>
                ) : (
                  data?.reports.map((report) => (
                    <TableRow
                      key={report.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => handleRowClick(report.id)}
                    >
                      <TableCell>{report.reporter.name}</TableCell>
                      <TableCell>
                        {targetTypeLabels[report.targetType]}
                      </TableCell>
                      <TableCell className="max-w-[200px] truncate">
                        {report.reason}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getReportStatusColor(report.status)}>
                          {getReportStatusText(report.status)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {format(new Date(report.createdAt), 'PPP', {
                          locale: ko,
                        })}
                      </TableCell>
                      <TableCell>
                        {report.resolvedAt
                          ? format(new Date(report.resolvedAt), 'PPP', {
                              locale: ko,
                            })
                          : '-'}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>

            {data && data.total > limit && (
              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-muted-foreground">
                  {page * limit + 1}-
                  {Math.min((page + 1) * limit, data.total)} / {data.total}건
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handlePrevPage}
                    disabled={page === 0}
                  >
                    이전
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleNextPage}
                    disabled={page * limit + limit >= data.total}
                  >
                    다음
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
