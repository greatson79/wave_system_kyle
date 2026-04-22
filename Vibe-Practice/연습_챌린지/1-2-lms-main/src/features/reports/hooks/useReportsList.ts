'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  ReportsListResponseSchema,
  type ReportsListQuery,
  type ReportsListResponse,
} from '../lib/dto';

const getReportsList = async (
  query: ReportsListQuery,
): Promise<ReportsListResponse> => {
  try {
    const { data } = await apiClient.get('/api/operator/reports', {
      params: query,
    });
    return ReportsListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '신고 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useReportsList = (query: ReportsListQuery) => {
  return useQuery({
    queryKey: ['operator', 'reports', query],
    queryFn: () => getReportsList(query),
  });
};
