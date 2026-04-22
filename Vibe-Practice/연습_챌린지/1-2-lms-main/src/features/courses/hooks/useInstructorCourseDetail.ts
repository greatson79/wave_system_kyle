'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  InstructorCourseDetailResponseSchema,
  type InstructorCourseDetailResponse,
} from '../lib/dto';

const fetchInstructorCourseDetail = async (
  courseId: string,
): Promise<InstructorCourseDetailResponse> => {
  try {
    const { data } = await apiClient.get(`/api/instructor/courses/${courseId}`);
    return InstructorCourseDetailResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(
      error,
      '코스 정보를 불러오지 못했습니다.',
    );
    throw new Error(message);
  }
};

export const useInstructorCourseDetail = (courseId: string) =>
  useQuery({
    queryKey: ['instructor-course', courseId],
    queryFn: () => fetchInstructorCourseDetail(courseId),
    enabled: Boolean(courseId),
    staleTime: 60 * 1000,
  });
