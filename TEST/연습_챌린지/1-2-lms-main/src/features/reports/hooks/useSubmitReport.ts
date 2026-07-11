'use client';

import { useMutation } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  SubmitReportRequestSchema,
  SubmitReportResponseSchema,
  type SubmitReportRequest,
  type SubmitReportResponse,
} from '../lib/dto';

const submitReport = async (
  data: SubmitReportRequest,
): Promise<SubmitReportResponse> => {
  try {
    const validated = SubmitReportRequestSchema.parse(data);
    const { data: response } = await apiClient.post('/api/reports', validated);
    return SubmitReportResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '신고 접수에 실패했습니다.');
    throw new Error(message);
  }
};

export const useSubmitReport = () => {
  return useMutation({
    mutationFn: submitReport,
  });
};
