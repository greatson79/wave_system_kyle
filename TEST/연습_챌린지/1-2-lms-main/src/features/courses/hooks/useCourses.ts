'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CourseListQuerySchema,
  CourseListResponseSchema,
  type CourseListQuery,
  type CourseListResponse,
} from '../lib/dto';

const fetchCourses = async (
  params: CourseListQuery,
): Promise<CourseListResponse> => {
  try {
    const validated = CourseListQuerySchema.parse(params);
    const { data } = await apiClient.get('/api/courses', { params: validated });
    return CourseListResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '코스 목록을 불러오지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useCourses = (params: CourseListQuery) =>
  useQuery({
    queryKey: ['courses', params],
    queryFn: () => fetchCourses(params),
    staleTime: 60 * 1000,
  });
