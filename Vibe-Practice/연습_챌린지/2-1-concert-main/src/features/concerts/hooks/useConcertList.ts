'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/remote/api-client';
import {
  ConcertListResponseSchema,
  type ConcertListResponse,
} from '@/features/concerts/lib/dto';

const fetchConcertList = async (): Promise<ConcertListResponse> => {
  const response = await apiClient.get('/api/concerts');

  // 응답 스키마 검증
  const parsed = ConcertListResponseSchema.safeParse(response.data);

  if (!parsed.success) {
    throw new Error('Invalid concert list response format');
  }

  return parsed.data;
};

export const useConcertList = () => {
  return useQuery({
    queryKey: ['concerts'],
    queryFn: fetchConcertList,
    staleTime: 1000 * 60 * 5, // 5분 캐싱
    gcTime: 1000 * 60 * 10, // 10분 가비지 컬렉션
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};
