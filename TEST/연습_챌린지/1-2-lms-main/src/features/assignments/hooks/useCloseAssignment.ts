'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CloseAssignmentResponseSchema,
  type CloseAssignmentResponse,
} from '../lib/dto';

const closeAssignment = async (
  assignmentId: string,
): Promise<CloseAssignmentResponse> => {
  try {
    const { data: response } = await apiClient.patch(
      `/api/instructor/assignments/${assignmentId}/close`,
    );
    return CloseAssignmentResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 마감에 실패했습니다.');
    throw new Error(message);
  }
};

export const useCloseAssignment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: closeAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructor', 'assignments'] });
    },
  });
};
