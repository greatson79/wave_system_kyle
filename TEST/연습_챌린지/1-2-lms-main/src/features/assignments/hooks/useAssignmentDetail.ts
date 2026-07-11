'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  AssignmentDetailResponseSchema,
  type AssignmentDetailResponse,
} from '../lib/dto';

const fetchAssignmentDetail = async (
  assignmentId: string,
): Promise<AssignmentDetailResponse> => {
  try {
    const { data } = await apiClient.get(`/api/assignments/${assignmentId}`);
    return AssignmentDetailResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 정보를 불러오지 못했습니다.');
    throw new Error(message);
  }
};

export const useAssignmentDetail = (assignmentId: string) =>
  useQuery({
    queryKey: ['assignment', assignmentId],
    queryFn: () => fetchAssignmentDetail(assignmentId),
    enabled: Boolean(assignmentId),
    staleTime: 60 * 1000,
  });
