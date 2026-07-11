'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  AssignmentListResponseSchema,
  type AssignmentListResponse,
} from '../lib/dto';

const fetchCourseAssignments = async (
  courseId: string,
): Promise<AssignmentListResponse> => {
  try {
    const { data } = await apiClient.get(`/api/courses/${courseId}/assignments`);
    return AssignmentListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '과제 목록을 불러오지 못했습니다.');
    throw new Error(message);
  }
};

export const useCourseAssignments = (courseId: string) =>
  useQuery({
    queryKey: ['assignments', 'course', courseId],
    queryFn: () => fetchCourseAssignments(courseId),
    enabled: Boolean(courseId),
    staleTime: 60 * 1000,
  });
