'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, isAxiosError } from '@/lib/remote/api-client';
import type { BookingDetailResponse } from '../lib/dto';

export const useBookingDetail = (bookingId: string) => {
  return useQuery<BookingDetailResponse, Error & { code?: string }>({
    queryKey: ['bookings', bookingId],
    queryFn: async () => {
      try {
        const response = await apiClient.get<BookingDetailResponse>(`/api/bookings/${bookingId}`);
        return response.data;
      } catch (error) {
        if (isAxiosError(error)) {
          const errorData = error.response?.data;
          const errorMessage = errorData?.error?.message || 'Failed to fetch booking detail';
          const customError = new Error(errorMessage) as Error & { code?: string };
          customError.code = errorData?.error?.code;
          throw customError;
        }
        throw error;
      }
    },
    enabled: !!bookingId,
    staleTime: 5 * 60 * 1000, // 5분
    gcTime: 10 * 60 * 1000, // 10분
    retry: 1,
  });
};
