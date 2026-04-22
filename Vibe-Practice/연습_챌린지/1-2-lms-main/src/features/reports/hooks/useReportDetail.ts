'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  ReportDetailResponseSchema,
  type ReportDetailResponse,
} from '../lib/dto';

const getReportDetail = async (reportId: string): Promise<ReportDetailResponse> => {
  try {
    const { data } = await apiClient.get(`/api/operator/reports/${reportId}`);
    return ReportDetailResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '신고 상세 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useReportDetail = (reportId: string) => {
  return useQuery({
    queryKey: ['operator', 'report', reportId],
    queryFn: () => getReportDetail(reportId),
    enabled: !!reportId,
  });
};
