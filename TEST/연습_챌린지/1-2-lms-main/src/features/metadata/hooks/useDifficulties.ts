'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  DifficultiesListResponseSchema,
  type DifficultiesListResponse,
} from '../lib/dto';

const getDifficulties = async (): Promise<DifficultiesListResponse> => {
  try {
    const { data } = await apiClient.get('/api/operator/metadata/difficulties');
    return DifficultiesListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '난이도 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useDifficulties = () => {
  return useQuery({
    queryKey: ['operator', 'metadata', 'difficulties'],
    queryFn: getDifficulties,
  });
};
