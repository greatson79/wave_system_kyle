'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import type { ConcertDetailResponse } from '../lib/dto';

/**
 * 콘서트 상세 정보 조회 React Query Hook
 * @param concertId - 콘서트 UUID
 */
export const useConcertDetailQuery = (concertId: string) => {
  return useQuery<ConcertDetailResponse>({
    queryKey: ['concerts', concertId],
    queryFn: async () => {
      try {
        const response = await apiClient.get<ConcertDetailResponse>(`/api/concerts/${concertId}`);
        return response.data;
      } catch (error) {
        throw new Error(extractApiErrorMessage(error, 'Failed to fetch concert detail'));
      }
    },
    enabled: !!concertId,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
};
