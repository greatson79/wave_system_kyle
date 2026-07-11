'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CreateCategoryRequestSchema,
  CategoryResponseSchema,
  type CreateCategoryRequest,
  type CategoryResponse,
} from '../lib/dto';

const createCategory = async (
  data: CreateCategoryRequest,
): Promise<CategoryResponse> => {
  try {
    const validated = CreateCategoryRequestSchema.parse(data);
    const { data: response } = await apiClient.post(
      '/api/operator/metadata/categories',
      validated,
    );
    return CategoryResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '카테고리 추가에 실패했습니다.');
    throw new Error(message);
  }
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'metadata', 'categories'] });
    },
  });
};
