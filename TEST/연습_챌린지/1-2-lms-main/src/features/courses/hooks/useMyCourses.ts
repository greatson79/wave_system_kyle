'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  MyCoursesResponseSchema,
  type MyCoursesResponse,
} from '../lib/dto';

const fetchMyCourses = async (): Promise<MyCoursesResponse> => {
  try {
    const { data } = await apiClient.get('/api/instructor/courses');
    return MyCoursesResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '코스 목록을 불러오지 못했습니다.');
    throw new Error(message);
  }
};

export const useMyCourses = () =>
  useQuery({
    queryKey: ['instructor', 'courses'],
    queryFn: fetchMyCourses,
    staleTime: 30 * 1000, // 30초
  });
