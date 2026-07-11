'use client';

import { useMutation } from '@tanstack/react-query';
import { apiClient, isAxiosError } from '@/lib/remote/api-client';
import type { LookupBookingsRequest, LookupBookingsResponse } from '../lib/dto';

export const useLookupBookings = () => {
  return useMutation<LookupBookingsResponse, Error & { code?: string }, LookupBookingsRequest>({
    mutationFn: async (data: LookupBookingsRequest) => {
      try {
        const response = await apiClient.post<LookupBookingsResponse>('/api/bookings/lookup', data);
        return response.data;
      } catch (error) {
        if (isAxiosError(error)) {
          const errorData = error.response?.data;
          const errorMessage = errorData?.error?.message || 'Failed to lookup bookings';
          const customError = new Error(errorMessage) as Error & { code?: string };
          customError.code = errorData?.error?.code;
          throw customError;
        }
        throw error;
      }
    },
  });
};
