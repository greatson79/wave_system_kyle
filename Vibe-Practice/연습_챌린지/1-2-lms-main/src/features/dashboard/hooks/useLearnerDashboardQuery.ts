'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  LearnerDashboardResponseSchema,
  type LearnerDashboardResponse,
} from '../lib/dto';

const fetchLearnerDashboard = async (): Promise<LearnerDashboardResponse> => {
  try {
    const { data } = await apiClient.get('/api/dashboard/learner');
    return LearnerDashboardResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '대시보드 데이터를 불러오지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useLearnerDashboardQuery = () =>
  useQuery({
    queryKey: ['dashboard', 'learner'],
    queryFn: fetchLearnerDashboard,
    staleTime: 30 * 1000,
    refetchOnWindowFocus: true,
  });
