'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  DifficultiesListResponseSchema,
  type DifficultiesListResponse,
} from '../lib/dto';

const getActiveDifficulties = async (): Promise<DifficultiesListResponse> => {
  try {
    const { data } = await apiClient.get('/api/metadata/difficulties');
    return DifficultiesListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '난이도 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useActiveDifficulties = () => {
  return useQuery({
    queryKey: ['metadata', 'difficulties', 'active'],
    queryFn: getActiveDifficulties,
    staleTime: 5 * 60 * 1000, // 5분 캐시
  });
};
