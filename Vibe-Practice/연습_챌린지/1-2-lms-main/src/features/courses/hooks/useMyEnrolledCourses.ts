'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  MyEnrolledCoursesResponseSchema,
  type MyEnrolledCoursesResponse,
} from '../lib/dto';

const fetchMyEnrolledCourses = async (): Promise<MyEnrolledCoursesResponse> => {
  try {
    const { data } = await apiClient.get('/api/learner/courses/enrolled');
    return MyEnrolledCoursesResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '수강 중인 코스 목록을 불러오지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useMyEnrolledCourses = () =>
  useQuery({
    queryKey: ['myEnrolledCourses'],
    queryFn: fetchMyEnrolledCourses,
    staleTime: 60 * 1000, // 1분
  });
