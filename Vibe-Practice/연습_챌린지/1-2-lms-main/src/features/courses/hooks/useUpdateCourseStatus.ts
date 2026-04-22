'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  UpdateCourseStatusRequestSchema,
  UpdateCourseStatusResponseSchema,
  type UpdateCourseStatusRequest,
  type UpdateCourseStatusResponse,
} from '../lib/dto';

const updateCourseStatus = async (
  courseId: string,
  data: UpdateCourseStatusRequest,
): Promise<UpdateCourseStatusResponse> => {
  try {
    const validated = UpdateCourseStatusRequestSchema.parse(data);
    const { data: response } = await apiClient.patch(
      `/api/instructor/courses/${courseId}/status`,
      validated,
    );
    return UpdateCourseStatusResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '코스 상태 변경에 실패했습니다.');
    throw new Error(message);
  }
};

export const useUpdateCourseStatus = (courseId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateCourseStatusRequest) => updateCourseStatus(courseId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructor', 'courses'] });
      queryClient.invalidateQueries({ queryKey: ['course', courseId] });
    },
  });
};
