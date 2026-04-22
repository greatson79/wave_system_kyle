'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ReportDetail } from '@/features/reports/components/report-detail';
import { ReportActionForm } from '@/features/reports/components/report-action-form';
import { useReportDetail } from '@/features/reports/hooks/useReportDetail';

interface ReportDetailPageProps {
  params: Promise<{
    reportId: string;
  }>;
}

export default function ReportDetailPage({ params }: ReportDetailPageProps) {
  const router = useRouter();
  const { reportId } = use(params);
  const { data: report } = useReportDetail(reportId);

  const handleBack = () => {
    router.push('/operator/reports');
  };

  const handleActionSuccess = () => {
    // 처리 완료 후 목록으로 돌아가지 않고, 현재 페이지에서 업데이트된 내용을 보여줌
  };

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">신고 상세</h1>
          <p className="text-muted-foreground mt-2">
            신고 내용을 확인하고 처리할 수 있습니다.
          </p>
        </div>
        <Button variant="outline" onClick={handleBack}>
          목록으로 돌아가기
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <ReportDetail reportId={reportId} />
        </div>

        <div>
          {report && (
            <ReportActionForm
              reportId={reportId}
              currentStatus={report.status}
              onSuccess={handleActionSuccess}
            />
          )}
        </div>
      </div>
    </div>
  );
}
