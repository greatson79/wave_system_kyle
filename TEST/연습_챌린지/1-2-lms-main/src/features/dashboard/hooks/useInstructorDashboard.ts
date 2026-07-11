'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  InstructorDashboardResponseSchema,
  type InstructorDashboardResponse,
} from '../lib/dto';

const fetchInstructorDashboard = async (): Promise<InstructorDashboardResponse> => {
  try {
    const { data } = await apiClient.get('/api/dashboard/instructor');
    return InstructorDashboardResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '대시보드 정보를 불러오지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useInstructorDashboard = () =>
  useQuery({
    queryKey: ['dashboard', 'instructor'],
    queryFn: fetchInstructorDashboard,
    staleTime: 60 * 1000,
    refetchOnWindowFocus: true,
  });
