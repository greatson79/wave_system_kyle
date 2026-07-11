'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  EnrollmentStatusResponseSchema,
  type EnrollmentStatusResponse,
} from '../lib/dto';

const fetchEnrollmentStatus = async (
  courseId: string,
): Promise<EnrollmentStatusResponse> => {
  try {
    const { data } = await apiClient.get(
      `/api/courses/${courseId}/enrollment`,
    );
    return EnrollmentStatusResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '수강 여부를 확인하지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useEnrollmentStatus = (courseId: string) =>
  useQuery({
    queryKey: ['enrollment', courseId],
    queryFn: () => fetchEnrollmentStatus(courseId),
    enabled: Boolean(courseId),
    staleTime: 30 * 1000,
  });
