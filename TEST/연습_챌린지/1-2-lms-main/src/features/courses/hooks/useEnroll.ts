'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import { EnrollResponseSchema, type EnrollResponse } from '../lib/dto';

const enrollCourse = async (courseId: string): Promise<EnrollResponse> => {
  try {
    const { data } = await apiClient.post(`/api/courses/${courseId}/enroll`);
    return EnrollResponseSchema.parse(data);
  } catch (error) {
    const message = extractApiErrorMessage(error, '수강신청에 실패했습니다.');
    throw new Error(message);
  }
};

export const useEnroll = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: enrollCourse,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['course', data.courseId] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      queryClient.invalidateQueries({
        queryKey: ['enrollment', data.courseId],
      });
    },
  });
};
