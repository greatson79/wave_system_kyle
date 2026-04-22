'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  ResubmitAssignmentRequestSchema,
  SubmitAssignmentResponseSchema,
  type ResubmitAssignmentRequest,
  type SubmitAssignmentResponse,
} from '../lib/dto';

const resubmitAssignment = async (
  assignmentId: string,
  data: ResubmitAssignmentRequest,
): Promise<SubmitAssignmentResponse> => {
  try {
    const validated = ResubmitAssignmentRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/assignments/${assignmentId}/submit`,
      validated,
    );
    return SubmitAssignmentResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 재제출에 실패했습니다.');
    throw new Error(message);
  }
};

export const useResubmitAssignment = (assignmentId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ResubmitAssignmentRequest) => resubmitAssignment(assignmentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignment', assignmentId] });
      queryClient.invalidateQueries({ queryKey: ['assignments', 'course'] });
    },
  });
};
