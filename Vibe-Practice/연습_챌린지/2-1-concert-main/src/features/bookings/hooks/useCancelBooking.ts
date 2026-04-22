'use client';

import { useMutation } from '@tanstack/react-query';
import { apiClient, isAxiosError } from '@/lib/remote/api-client';
import type { CancelBookingRequest, CancelBookingResponse } from '../lib/dto';

interface CancelBookingParams extends CancelBookingRequest {
  bookingId: string;
}

export const useCancelBooking = () => {
  return useMutation<CancelBookingResponse, Error & { code?: string }, CancelBookingParams>({
    mutationFn: async ({ bookingId, phone, password }: CancelBookingParams) => {
      try {
        const response = await apiClient.patch<CancelBookingResponse>(`/api/bookings/${bookingId}/cancel`, {
          phone,
          password,
        });
        return response.data;
      } catch (error) {
        if (isAxiosError(error)) {
          const errorData = error.response?.data;
          const errorMessage = errorData?.error?.message || 'Failed to cancel booking';
          const customError = new Error(errorMessage) as Error & { code?: string };
          customError.code = errorData?.error?.code;
          throw customError;
        }
        throw error;
      }
    },
  });
};
