'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CategoriesListResponseSchema,
  type CategoriesListResponse,
} from '../lib/dto';

const getActiveCategories = async (): Promise<CategoriesListResponse> => {
  try {
    const { data } = await apiClient.get('/api/metadata/categories');
    return CategoriesListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '카테고리 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useActiveCategories = () => {
  return useQuery({
    queryKey: ['metadata', 'categories', 'active'],
    queryFn: getActiveCategories,
    staleTime: 5 * 60 * 1000, // 5분 캐시
  });
};
