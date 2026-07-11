'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  UpdateCategoryRequestSchema,
  CategoryResponseSchema,
  type UpdateCategoryRequest,
  type CategoryResponse,
} from '../lib/dto';

const updateCategory = async (
  categoryId: string,
  data: UpdateCategoryRequest,
): Promise<CategoryResponse> => {
  try {
    const validated = UpdateCategoryRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/operator/metadata/categories/${categoryId}`,
      validated,
    );
    return CategoryResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '카테고리 수정에 실패했습니다.');
    throw new Error(message);
  }
};

export const useUpdateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ categoryId, data }: { categoryId: string; data: UpdateCategoryRequest }) =>
      updateCategory(categoryId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator', 'metadata', 'categories'] });
    },
  });
};
