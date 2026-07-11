'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  UpdateAssignmentRequestSchema,
  UpdateAssignmentResponseSchema,
  type UpdateAssignmentRequest,
  type UpdateAssignmentResponse,
} from '../lib/dto';

const updateAssignment = async (
  assignmentId: string,
  data: UpdateAssignmentRequest,
): Promise<UpdateAssignmentResponse> => {
  try {
    const validated = UpdateAssignmentRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/instructor/assignments/${assignmentId}`,
      validated,
    );
    return UpdateAssignmentResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 수정에 실패했습니다.');
    throw new Error(message);
  }
};

export const useUpdateAssignment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ assignmentId, data }: { assignmentId: string; data: UpdateAssignmentRequest }) =>
      updateAssignment(assignmentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructor', 'assignments'] });
    },
  });
};
