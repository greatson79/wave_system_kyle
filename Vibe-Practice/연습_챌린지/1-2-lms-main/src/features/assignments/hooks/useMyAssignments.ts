'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  MyAssignmentsResponseSchema,
  type MyAssignmentsResponse,
} from '../lib/dto';

const fetchMyAssignments = async (): Promise<MyAssignmentsResponse> => {
  try {
    const { data } = await apiClient.get('/api/instructor/assignments');
    return MyAssignmentsResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useMyAssignments = () => {
  return useQuery({
    queryKey: ['instructor', 'assignments'],
    queryFn: fetchMyAssignments,
  });
};
