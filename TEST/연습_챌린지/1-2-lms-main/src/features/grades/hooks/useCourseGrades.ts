'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CourseGradesResponseSchema,
  type CourseGradesResponse,
} from '../lib/dto';

const fetchCourseGrades = async (
  courseId: string
): Promise<CourseGradesResponse> => {
  try {
    const { data } = await apiClient.get(`/api/courses/${courseId}/grades`);
    return CourseGradesResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '성적 정보를 불러오지 못했습니다.');
    throw new Error(message);
  }
};

export const useCourseGrades = (courseId: string) =>
  useQuery({
    queryKey: ['grades', 'course', courseId],
    queryFn: () => fetchCourseGrades(courseId),
    enabled: Boolean(courseId),
    staleTime: 30 * 1000, // 30초 (성적 정보는 자주 변경되므로 짧게 설정)
  });
