'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient, extractApiErrorMessage } from '@/lib/remote/api-client';
import {
  CreateCourseRequestSchema,
  CreateCourseResponseSchema,
  type CreateCourseRequest,
  type CreateCourseResponse,
} from '../lib/dto';

const createCourse = async (
  data: CreateCourseRequest,
): Promise<CreateCourseResponse> => {
  try {
    const validated = CreateCourseRequestSchema.parse(data);
    const { data: response } = await apiClient.post(
      '/api/instructor/courses',
      validated,
    );
    return CreateCourseResponseSchema.parse(response);
  } catch (error) {
    const message = extractApiErrorMessage(error, '코스 생성에 실패했습니다.');
    throw new Error(message);
  }
};

export const useCreateCourse = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: createCourse,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['instructor', 'courses'] });
      router.push(`/instructor/courses/${data.courseId}/edit`);
    },
  });
};
