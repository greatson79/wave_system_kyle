'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  AssignmentSubmissionsResponseSchema,
  type AssignmentSubmissionsResponse,
} from '../lib/dto';

const fetchAssignmentSubmissions = async (
  assignmentId: string,
  filter: 'all' | 'ungraded' | 'late' | 'resubmission_required',
): Promise<AssignmentSubmissionsResponse> => {
  try {
    const { data } = await apiClient.get(
      `/api/instructor/assignments/${assignmentId}/submissions`,
      { params: { filter } },
    );
    return AssignmentSubmissionsResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '제출물 목록 조회에 실패했습니다.');
    throw new Error(message);
  }
};

export const useAssignmentSubmissions = (
  assignmentId: string,
  filter: 'all' | 'ungraded' | 'late' | 'resubmission_required' = 'all',
) => {
  return useQuery({
    queryKey: ['instructor', 'assignments', assignmentId, 'submissions', filter],
    queryFn: () => fetchAssignmentSubmissions(assignmentId, filter),
    enabled: !!assignmentId,
  });
};
