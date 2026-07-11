'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CreateDifficultyRequestSchema,
  DifficultyResponseSchema,
  type CreateDifficultyRequest,
  type DifficultyResponse,
} from '../lib/dto';

const createDifficulty = async (
  data: CreateDifficultyRequest,
): Promise<DifficultyResponse> => {
  try {
    const validated = CreateDifficultyRequestSchema.parse(data);
    const { data: response } = await apiClient.post(
      '/api/operator/metadata/difficulties',
      validated,
    );
    return DifficultyResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '난이도 추가에 실패했습니다.');
    throw new Error(message);
  }
};

export const useCreateDifficulty = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createDifficulty,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'metadata', 'difficulties'] });
    },
  });
};
