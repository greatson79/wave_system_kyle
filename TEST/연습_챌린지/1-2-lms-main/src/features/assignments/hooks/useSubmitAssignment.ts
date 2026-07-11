'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  SubmitAssignmentRequestSchema,
  SubmitAssignmentResponseSchema,
  type SubmitAssignmentRequest,
  type SubmitAssignmentResponse,
} from '../lib/dto';

const submitAssignment = async (
  assignmentId: string,
  data: SubmitAssignmentRequest,
): Promise<SubmitAssignmentResponse> => {
  try {
    const validated = SubmitAssignmentRequestSchema.parse(data);
    const { data: response } = await apiClient.post(
      `/api/assignments/${assignmentId}/submit`,
      validated,
    );
    return SubmitAssignmentResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 제출에 실패했습니다.');
    throw new Error(message);
  }
};

export const useSubmitAssignment = (assignmentId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SubmitAssignmentRequest) => submitAssignment(assignmentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignment', assignmentId] });
      queryClient.invalidateQueries({ queryKey: ['assignments', 'course'] });
    },
  });
};
