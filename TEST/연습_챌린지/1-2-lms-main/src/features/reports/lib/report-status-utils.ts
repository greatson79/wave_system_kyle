import type { ReportStatus } from '../backend/schema';

export const getReportStatusText = (status: ReportStatus): string => {
  const statusMap: Record<ReportStatus, string> = {
    received: '접수됨',
    investigating: '조사 중',
    resolved: '처리 완료',
  };
  return statusMap[status];
};

export const getReportStatusColor = (
  status: ReportStatus,
): 'default' | 'secondary' | 'destructive' => {
  const colorMap: Record<ReportStatus, 'default' | 'secondary' | 'destructive'> = {
    received: 'default',
    investigating: 'secondary',
    resolved: 'destructive',
  };
  return colorMap[status];
};

export const canTransitionStatus = (
  from: ReportStatus,
  to: ReportStatus,
): boolean => {
  const allowedTransitions: Record<ReportStatus, ReportStatus[]> = {
    received: ['investigating', 'resolved'],
    investigating: ['resolved'],
    resolved: [],
  };
  return allowedTransitions[from].includes(to);
};
