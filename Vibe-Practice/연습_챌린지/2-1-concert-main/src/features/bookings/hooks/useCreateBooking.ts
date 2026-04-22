'use client';

import { useMutation } from '@tanstack/react-query';
import { apiClient, isAxiosError } from '@/lib/remote/api-client';
import type { CreateBookingRequest, CreateBookingResponse } from '../backend/schema';

export const useCreateBooking = () => {
  return useMutation<CreateBookingResponse, Error & { code?: string; details?: unknown }, CreateBookingRequest>({
    mutationFn: async (data: CreateBookingRequest) => {
      try {
        const response = await apiClient.post<CreateBookingResponse>('/api/bookings', data);
        return response.data;
      } catch (error) {
        if (isAxiosError(error)) {
          const errorData = error.response?.data;
          const errorMessage = errorData?.error?.message || 'Failed to create booking';
          const customError = new Error(errorMessage) as Error & { code?: string; details?: unknown };
          customError.code = errorData?.error?.code;
          customError.details = errorData?.error?.details;
          throw customError;
        }
        throw error;
      }
    },
  });
};
