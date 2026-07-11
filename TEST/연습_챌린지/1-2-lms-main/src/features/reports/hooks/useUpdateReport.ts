'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  UpdateReportRequestSchema,
  UpdateReportResponseSchema,
  type UpdateReportRequest,
  type UpdateReportResponse,
} from '../lib/dto';

const updateReport = async (
  reportId: string,
  data: UpdateReportRequest,
): Promise<UpdateReportResponse> => {
  try {
    const validated = UpdateReportRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/operator/reports/${reportId}`,
      validated,
    );
    return UpdateReportResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '신고 처리에 실패했습니다.');
    throw new Error(message);
  }
};

export const useUpdateReport = (reportId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateReportRequest) => updateReport(reportId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'report', reportId] });
      queryClient.invalidateQueries({ queryKey: ['operator', 'reports'] });
    },
  });
};
