'use client';

import { LearnerDashboardSummary } from '@/features/dashboard/components/learner-dashboard-summary';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { BookOpen } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">학습 대시보드</h1>
        <Button asChild variant="outline">
          <Link href="/courses" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            모든 코스 보기
          </Link>
        </Button>
      </div>
      <LearnerDashboardSummary />
    </div>
  );
}
