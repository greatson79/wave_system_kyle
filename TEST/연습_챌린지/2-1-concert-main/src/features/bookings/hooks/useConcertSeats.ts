'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, isAxiosError } from '@/lib/remote/api-client';
import type { SeatsResponse } from '../backend/schema';

export const useConcertSeats = (concertId: string) => {
  return useQuery<SeatsResponse>({
    queryKey: ['concerts', concertId, 'seats'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<SeatsResponse>(`/api/concerts/${concertId}/seats`);
        return response.data;
      } catch (error) {
        if (isAxiosError(error)) {
          const message = error.response?.data?.error?.message || 'Failed to fetch seats';
          throw new Error(message);
        }
        throw error;
      }
    },
    enabled: !!concertId,
    staleTime: 30 * 1000,
    gcTime: 5 * 60 * 1000,
    retry: 1,
  });
};
