'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  UpdateCourseRequestSchema,
  UpdateCourseResponseSchema,
  type UpdateCourseRequest,
  type UpdateCourseResponse,
} from '../lib/dto';

const updateCourse = async (
  courseId: string,
  data: UpdateCourseRequest,
): Promise<UpdateCourseResponse> => {
  try {
    const validated = UpdateCourseRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/instructor/courses/${courseId}`,
      validated,
    );
    return UpdateCourseResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '코스 수정에 실패했습니다.');
    throw new Error(message);
  }
};

export const useUpdateCourse = (courseId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateCourseRequest) => updateCourse(courseId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructor', 'courses'] });
      queryClient.invalidateQueries({ queryKey: ['course', courseId] });
    },
  });
};
