'use client';

import { InstructorDashboard } from '@/features/dashboard/components/instructor-dashboard';

export default function InstructorDashboardPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">강사 대시보드</h1>
      <InstructorDashboard />
    </div>
  );
}
