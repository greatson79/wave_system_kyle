'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  GradeSubmissionRequestSchema,
  GradeSubmissionResponseSchema,
  type GradeSubmissionRequest,
  type GradeSubmissionResponse,
} from '../lib/dto';

const gradeSubmission = async (
  submissionId: string,
  data: GradeSubmissionRequest,
): Promise<GradeSubmissionResponse> => {
  try {
    const validated = GradeSubmissionRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/instructor/submissions/${submissionId}/grade`,
      validated,
    );
    return GradeSubmissionResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '채점에 실패했습니다.');
    throw new Error(message);
  }
};

export const useGradeSubmission = (submissionId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: GradeSubmissionRequest) => gradeSubmission(submissionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submission', submissionId] });
      queryClient.invalidateQueries({ queryKey: ['instructor', 'assignments'] });
    },
  });
};
