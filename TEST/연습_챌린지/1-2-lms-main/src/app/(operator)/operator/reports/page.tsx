'use client';

import { ReportsList } from '@/features/reports/components/reports-list';

export default function ReportsListPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">신고 관리</h1>
        <p className="text-muted-foreground mt-2">
          접수된 신고를 확인하고 처리할 수 있습니다.
        </p>
      </div>

      <ReportsList />
    </div>
  );
}
