'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  PublishAssignmentResponseSchema,
  type PublishAssignmentResponse,
} from '../lib/dto';

const publishAssignment = async (
  assignmentId: string,
): Promise<PublishAssignmentResponse> => {
  try {
    const { data: response } = await apiClient.patch(
      `/api/instructor/assignments/${assignmentId}/publish`,
    );
    return PublishAssignmentResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 게시에 실패했습니다.');
    throw new Error(message);
  }
};

export const usePublishAssignment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: publishAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructor', 'assignments'] });
    },
  });
};
