'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CourseDetailResponseSchema,
  type CourseDetailResponse,
} from '../lib/dto';

const fetchCourseDetail = async (
  courseId: string,
): Promise<CourseDetailResponse> => {
  try {
    const { data } = await apiClient.get(`/api/courses/${courseId}`);
    return CourseDetailResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '코스 정보를 불러오지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useCourseDetail = (courseId: string) =>
  useQuery({
    queryKey: ['course', courseId],
    queryFn: () => fetchCourseDetail(courseId),
    enabled: Boolean(courseId),
    staleTime: 60 * 1000,
  });
