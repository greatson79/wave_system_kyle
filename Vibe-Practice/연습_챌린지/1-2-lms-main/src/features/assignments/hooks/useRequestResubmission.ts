'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  RequestResubmissionRequestSchema,
  RequestResubmissionResponseSchema,
  type RequestResubmissionRequest,
  type RequestResubmissionResponse,
} from '../lib/dto';

const requestResubmission = async (
  submissionId: string,
  data: RequestResubmissionRequest,
): Promise<RequestResubmissionResponse> => {
  try {
    const validated = RequestResubmissionRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/instructor/submissions/${submissionId}/request-resubmission`,
      validated,
    );
    return RequestResubmissionResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '재제출 요청에 실패했습니다.');
    throw new Error(message);
  }
};

export const useRequestResubmission = (submissionId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RequestResubmissionRequest) =>
      requestResubmission(submissionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submission', submissionId] });
      queryClient.invalidateQueries({ queryKey: ['instructor', 'assignments'] });
    },
  });
};
