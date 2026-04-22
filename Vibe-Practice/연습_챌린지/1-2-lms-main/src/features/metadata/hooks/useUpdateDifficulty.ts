'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  UpdateDifficultyRequestSchema,
  DifficultyResponseSchema,
  type UpdateDifficultyRequest,
  type DifficultyResponse,
} from '../lib/dto';

const updateDifficulty = async (
  difficultyId: string,
  data: UpdateDifficultyRequest,
): Promise<DifficultyResponse> => {
  try {
    const validated = UpdateDifficultyRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/operator/metadata/difficulties/${difficultyId}`,
      validated,
    );
    return DifficultyResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '난이도 수정에 실패했습니다.');
    throw new Error(message);
  }
};

export const useUpdateDifficulty = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ difficultyId, data }: { difficultyId: string; data: UpdateDifficultyRequest }) =>
      updateDifficulty(difficultyId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'metadata', 'difficulties'] });
    },
  });
};
