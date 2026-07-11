'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CreateAssignmentRequestSchema,
  CreateAssignmentResponseSchema,
  type CreateAssignmentRequest,
  type CreateAssignmentResponse,
} from '../lib/dto';

const createAssignment = async (
  data: CreateAssignmentRequest,
): Promise<CreateAssignmentResponse> => {
  try {
    const validated = CreateAssignmentRequestSchema.parse(data);
    const { data: response } = await apiClient.post(
      '/api/instructor/assignments',
      validated,
    );
    return CreateAssignmentResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 생성에 실패했습니다.');
    throw new Error(message);
  }
};

export const useCreateAssignment = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: createAssignment,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['instructor', 'assignments'] });
      router.push(`/instructor/assignments/${data.assignmentId}/edit`);
    },
  });
};
